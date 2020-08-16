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

import pickle
import re
import shutil
import sys

from annoy import AnnoyIndex
from docopt import docopt
from dpu_utils.utils import RichPath
import pandas as pd
from tqdm import tqdm

from dataextraction.python.parse_python_data import tokenize_docstring_from_string
import model_restore_helper

Batch = namedtuple('Batch', 'ids src_tokens src_lengths, src_strs')
Translation = namedtuple('Translation', 'src_str hypos pos_scores alignments')


class CodeSearch(object):
    def __init__(self):
        self.args = None
        self.local_model_path = 'neuralbow_hybrid-2020-07-05-13-43-57_model_best.pkl.gz'
        self.indices = None
        self.definitions = None

    def query_model(self, query, model, language='python', topk=100):
        predictions = []
        query_embedding = model.get_query_representations([{'docstring_tokens': tokenize_docstring_from_string(query),
                                                            'language': language}])[0]
        idxs, distances = self.indices.get_nns_by_vector(
            query_embedding, topk, search_k=1000000, include_distances=True)
        for idx in idxs:
            predictions.append(
                (query, language, self.definitions[idx]['identifier'], self.definitions[idx]['url']))

        return predictions

    def load_model(self):
        model_path = RichPath.create(self.local_model_path, None)
        print("Restoring model from %s" % model_path)
        model = model_restore_helper.restore(
            path=model_path,
            is_train=False,
            hyper_overrides={})

        for language in ['python']:
            print("Evaluating language: %s" % language)
            definitions = pickle.load(
                open('../resources/data/{}_dedupe_definitions_v2.pkl'.format(language), 'rb'))
            indexes = [{'code_tokens': d['function_tokens'],
                        'language': d['language']} for d in tqdm(definitions)]
            code_representations = model.get_code_representations(
                indexes[:10])
            indices = AnnoyIndex(code_representations[0].shape[0], 'angular')
            for index, vector in tqdm(enumerate(code_representations)):
                assert vector is not None
                indices.add_item(index, vector)
            indices.build(1)
