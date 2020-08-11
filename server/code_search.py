""" 
Conditional patch generation with the auto-regressive model.Batches data on-the-fly.
"""
from collections import namedtuple
import fileinput
import sys

import torch

from fairseq import data, options, tasks, tokenizer, utils
from fairseq.sequence_generator import SequenceGenerator
from fairseq.utils import import_user_module

Batch = namedtuple('Batch', 'ids src_tokens src_lengths, src_strs')
Translation = namedtuple('Translation', 'src_str hypos pos_scores alignments')


class PatchGen(object):
    def __init__(self):
        self.args = None

    def buffered_read(self, input, buffer_size):
        buffer = []
        with fileinput.input(files=[input], openhook=fileinput.hook_encoded("utf-8")) as h:
            for src_str in h:
                buffer.append(src_str.strip())
                if len(buffer) >= buffer_size:
                    yield buffer
                    buffer = []

        if len(buffer) > 0:
            yield buffer

    def make_batches(self, lines, args, task, max_positions):
        tokens = [
            task.source_dictionary.encode_line(
                src_str, add_if_not_exist=False, copy_ext_dict=args.copy_ext_dict).long()
            for src_str in lines
        ]
        lengths = torch.LongTensor([t.numel() for t in tokens])
        itr = task.get_batch_iterator(
            dataset=task.build_dataset_for_inference(tokens, lengths),
            max_tokens=args.max_tokens,
            max_sentences=args.max_sentences,
            max_positions=max_positions,
        ).next_epoch_itr(shuffle=False)
        for batch in itr:
            yield Batch(
                ids=batch['id'],
                src_tokens=batch['net_input']['src_tokens'], src_lengths=batch['net_input']['src_lengths'],
                src_strs=[lines[i] for i in batch['id']],
            )

    def load_model(self, args):
        self.args = args
        import_user_module(args)

        if args.buffer_size < 1:
            args.buffer_size = 1
        if args.max_tokens is None and args.max_sentences is None:
            args.max_sentences = 1

        assert not args.sampling or args.nbest == args.beam, \
            '--sampling requires --nbest to be equal to --beam'
        assert not args.max_sentences or args.max_sentences <= args.buffer_size, \
            '--max-sentences/--batch-size cannot be larger than --buffer-size'

        print(args)

        use_cuda = torch.cuda.is_available() and not args.cpu

        # Setup task, e.g., translation
        task = tasks.setup_task(args)

        # Load ensemble
        print('| loading model(s) from {}'.format(args.path))
        models, _model_args = utils.load_ensemble_for_inference(
            args.path.split(':'), task, model_arg_overrides=eval(args.model_overrides),
        )
        args.copy_ext_dict = getattr(_model_args, "copy_attention", False)

        # Set dictionaries
        src_dict = task.source_dictionary
        tgt_dict = task.target_dictionary

        # Optimize ensemble for generation
        for model in models:
            model.make_generation_fast_(
                beamable_mm_beam_size=None if args.no_beamable_mm else args.beam,
                need_attn=args.print_alignment,
            )
            if args.fp16:
                model.half()
            if use_cuda:
                model.cuda()

        # Initialize generator
        generator = task.build_generator(args)

        # Load alignment dictionary for unknown word replacement
        # (None if no unknown word replacement, empty if no path to align dictionary)
        align_dict = utils.load_align_dict(args.replace_unk)
        if align_dict is None and args.copy_ext_dict:
            align_dict = {}

        max_positions = utils.resolve_max_positions(
            task.max_positions(),
            *[model.max_positions() for model in models]
        )

        self.task = task
        self.max_positions = max_positions
        self.generator = generator
        self.models = models

        self.tgt_dict = tgt_dict
        self.align_dict = align_dict
        self.src_dict = src_dict

    # TODO: AST parser
    def generate_patch(self, str_code):
        # if args.buffer_size > 1:
        #    print('| Sentence buffer size:', args.buffer_size)
        #print('| Type the input sentence and press return:')
        start_id = 0
        src_strs = []
        use_cuda = torch.cuda.is_available()

        results = []
        inputs = [str_code]
        for batch in self.make_batches(inputs, self.args, self.task, self.max_positions):
            src_tokens = batch.src_tokens
            src_lengths = batch.src_lengths
            src_strs.extend(batch.src_strs)
            if use_cuda:
                src_tokens = src_tokens.cuda()
                src_lengths = src_lengths.cuda()

            sample = {
                'net_input': {
                    'src_tokens': src_tokens,
                    'src_lengths': src_lengths,
                },
            }
            translations = self.task.inference_step(
                self.generator, self.models, sample)
            for i, (id, hypos) in enumerate(zip(batch.ids.tolist(), translations)):
                src_tokens_i = utils.strip_pad(
                    src_tokens[i], self.tgt_dict.pad())
                results.append((start_id + id, src_tokens_i, hypos))

        # sort output to match input order
        for id, src_tokens, hypos in sorted(results, key=lambda x: x[0]):
            if self.src_dict is not None:
                src_str = self.src_dict.string(
                    src_tokens, self.args.remove_bpe)
                print('S-{}\t{}'.format(id, src_str))

            # Process top predictions
            # print('nbest:{}'.format(self.args.nbest))
            for hypo in hypos[:min(len(hypos), self.args.nbest)]:
                hypo_tokens, hypo_str, alignment = utils.post_process_prediction(
                    hypo_tokens=hypo['tokens'].int().cpu(),
                    src_str=src_strs[id],
                    alignment=hypo['alignment'].int().cpu(
                    ) if hypo['alignment'] is not None else None,
                    align_dict=self.align_dict,
                    tgt_dict=self.tgt_dict,
                    remove_bpe=self.args.remove_bpe,
                )
                print('H-{}\t{}\t{}'.format(id, hypo['score'], hypo_str))
                print('P-{}\t{}'.format(
                    id,
                    ' '.join(map(lambda x: '{:.4f}'.format(
                        x), hypo['positional_scores'].tolist()))
                ))
                if self.args.print_alignment:
                    print('A-{}\t{}'.format(
                        id,
                        ' '.join(map(lambda x: str(utils.item(x)), alignment))
                    ))

            # update running id counter
            start_id += len(results)
            return hypo_str
