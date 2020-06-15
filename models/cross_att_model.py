from typing import Any, Dict, Optional

from encoders import NBoWEncoder
from models import Model

import random
import numpy as np
import tensorflow as tf

import math
from utils.tfutils import pool_sequence_embedding
from collections import defaultdict, OrderedDict
from typing import List, Dict, Any, Iterable, Tuple, Optional, Union, Callable, Type, DefaultDict



class CrossAttentionModel(Model):
    @classmethod
    def get_default_hyperparameters(cls) -> Dict[str, Any]:
        hypers = {}
        for label in ["code", "query"]:
            hypers.update({f'{label}_{key}': value
                           for key, value in NBoWEncoder.get_default_hyperparameters().items()})
        model_hypers = {
            'learning_rate': 5e-4,
            'code_use_subtokens': False,
            'code_mark_subtoken_end': False,
            'loss': 'softmax',
            'batch_size': 128,
        }
        hypers.update(super().get_default_hyperparameters())
        hypers.update(model_hypers)
        return hypers

    def __init__(self,
                 hyperparameters: Dict[str, Any],
                 run_name: str = None,
                 model_save_dir: Optional[str] = None,
                 log_save_dir: Optional[str] = None):
        super().__init__(
            hyperparameters,
            code_encoder_type=NBoWEncoder,
            query_encoder_type=NBoWEncoder,
            run_name=run_name,
            model_save_dir=model_save_dir,
            log_save_dir=log_save_dir)

    def make_model(self, is_train: bool):
        with self._sess.graph.as_default():
            random.seed(self.hyperparameters['seed'])
            np.random.seed(self.hyperparameters['seed'])
            tf.set_random_seed(self.hyperparameters['seed'])

            self._make_model(is_train=is_train)
            self._make_loss()
            if is_train:
                self._make_training_step()
                self._summary_writer = tf.summary.FileWriter(
                    self._tensorboard_dir, self._sess.graph)

    def _make_model(self, is_train: bool) -> None:
        """
        Create the actual model.

        Note: This has to create self.ops['code_representations'] and self.ops['query_representations'],
        tensors of the same shape and rank 2.
        """
        self._placeholders['dropout_keep_rate'] = tf.placeholder(tf.float32,
                                                                 shape=(),
                                                                 name='dropout_keep_rate')
        self._placeholders['sample_loss_weights'] = \
            tf.placeholder_with_default(input=np.ones(shape=[self.hyperparameters['batch_size']],
                                                      dtype=np.float32),
                                        shape=[
                                            self.hyperparameters['batch_size']],
                                        name='sample_loss_weights')

        with tf.variable_scope("code_encoder"):
            language_encoders = []
            language_encoder_masks = []

            for (language, language_metadata) in sorted(self._per_code_language_metadata.items(), key=lambda kv: kv[0]):
                with tf.variable_scope(language):
                    self._code_encoders[language] = self._code_encoder_type(label="code",
                                                                            hyperparameters=self.hyperparameters,
                                                                            metadata=language_metadata)
                    language_encoder, language_encoder_mask, language_encoder_lens = self._code_encoders[language].build_model(
                        is_train=is_train)

                    language_encoders.append(language_encoder)
                    language_encoder_masks.append(language_encoder_mask)
            self.ops['code_representations'] = tf.concat(
                language_encoders, axis=0)
            self.ops['code_representation_masks'] = tf.concat(
                language_encoder_masks, axis=0)
        with tf.variable_scope("query_encoder"):
            self._query_encoder = self._query_encoder_type(label="query",
                                                           hyperparameters=self.hyperparameters,
                                                           metadata=self._query_metadata)
            self.ops['query_representations'], self.ops['query_representation_masks'], query_sequence_lengths = self._query_encoder.build_model(
                is_train=is_train)
        '''
        code_representation_size = next(
            iter(self.__code_encoders.values())).output_representation_size
        query_representation_size = self.__query_encoder.output_representation_size
        assert code_representation_size == query_representation_size, \
            f'Representations produced for code ({code_representation_size}) and query ({query_representation_size}) cannot differ!'
        '''
        # There is a tricky here, we generated negtive samples based on the positive smapels in the batch.
        # query: [B,F,H] -> [B,B,F,H] -> [B*B,F,H]
        # code:  [B,T,H] -> [B,B,T,H] -> [B*B,T,H]
        query_shape = tf.shape(self.ops['query_representations'])
        code_shape = tf.shape(self.ops['code_representations'])
        #print(self.ops['query_representations'].shape, self.ops['code_representations'].shape)

        '''
        Tricky here!
        '''
        self.ops['query_representations'] = tf.reshape(tf.tile(tf.expand_dims(self.ops['query_representations'], 0), [
                                                       code_shape[0], 1, 1, 1]), [-1, 30, 128])
        self.ops['query_representation_masks'] = tf.reshape(tf.tile(tf.expand_dims(
            self.ops['query_representation_masks'], 0), [code_shape[0], 1, 1]), [-1, 30])

        self.ops['code_representations'] = tf.reshape(tf.tile(tf.expand_dims(self.ops['code_representations'], 1), [
                                                      1, code_shape[0], 1, 1]), [-1, 200, 128])
        self.ops['code_representation_masks'] = tf.reshape(tf.tile(tf.expand_dims(
            self.ops['code_representation_masks'], 1), [1, code_shape[0], 1]), [-1, 200])
        #print(self.ops['query_representations'].shape, self.ops['code_representations'].shape)

        with tf.variable_scope("cross_encoder"):
            # Create attention mask [B,F,T]
            # [B,F] -> [B,F,T], [B,T] -> [B,F,T], [B,F,T]*[B,F,T]
            query_mask_shape = tf.shape(self.ops['query_representation_masks'])
            code_mask_shape = tf.shape(self.ops['code_representation_masks'])
            print(self.ops['query_representations'].shape,
                  self.ops['code_representations'].shape)
            attention_mask = tf.tile(tf.expand_dims(self.ops['query_representation_masks'], 2), [
                                     1, 1, code_mask_shape[-1]]) * tf.tile(tf.expand_dims(self.ops['code_representation_masks'], 1), [1, query_mask_shape[-1], 1])
            # print(attention_mask)
            # [B,F,H]
            with tf.variable_scope("attention_layer"):
                output_layer = self.attention_layer(
                    self.ops['query_representations'], self.ops['code_representations'], attention_mask)
                pool_output = pool_sequence_embedding("weighted_mean",
                                                      sequence_token_embeddings=output_layer,
                                                      sequence_lengths=query_sequence_lengths,
                                                      sequence_token_masks=self.ops['query_representation_masks'])

            output_weights = tf.get_variable('output_weights', [
                                             128, 1], initializer=tf.truncated_normal_initializer(stddev=0.02))
            output_bias = tf.get_variable(
                'output_bias', [1], initializer=tf.truncated_normal_initializer(stddev=0.02))

            # [B,1]
            # print(output_weights, output_bias)
            self.ops['logits'] = tf.nn.bias_add(
                tf.matmul(pool_output, output_weights), output_bias)

    def reshape_to_matrix(self, input_tensor):
        width = input_tensor.shape[-1]
        output_tensor = tf.reshape(input_tensor, [-1, width])
        return output_tensor

    def attention_layer(self, from_tensor, to_tensor, attention_mask, hidden_size=128):
        # from_tensor --> [B,F,H]
        # to_tensor   --> [B,T,H]
        #print('attention layer.')
        #print(from_tensor, to_tensor)
        from_shape = tf.shape(from_tensor)
        to_shape = tf.shape(to_tensor)
        # Reshap
        with tf.variable_scope('reshape_to_matrix'):
            # [BxF,H]
            from_tensor_2d = self.reshape_to_matrix(from_tensor)
            # [BxT,H]
            to_tensor_2d = self.reshape_to_matrix(to_tensor)
        # print(from_tensor_2d)
        # [B*F,H]*[H,H] -> [B*F, H]
        query_layer = tf.layers.dense(
            from_tensor_2d, hidden_size, name='query', kernel_initializer=tf.random_normal_initializer())
        # [B*T, H]
        key_layer = tf.layers.dense(
            to_tensor_2d, hidden_size, name='key', kernel_initializer=tf.random_normal_initializer())
        # [B*T, H]
        value_layer = tf.layers.dense(
            to_tensor_2d, hidden_size, name='value', kernel_initializer=tf.random_normal_initializer())

        # [B*F, H] -> [B,F,H]
        with tf.variable_scope('reshape_from_matrix'):
            # print(query_layer)
            # print(key_layer)
            # print(value_layer)
            #print(from_tensor.shape, to_tensor.shape)
            query_layer = tf.reshape(
                query_layer, [-1, from_tensor.shape[1], hidden_size])
            key_layer = tf.reshape(
                key_layer, [-1, to_tensor.shape[1], hidden_size])
            value_layer = tf.reshape(
                value_layer, [-1, to_tensor.shape[1], hidden_size])
        # [B,F,H] * [B,H,T] -> [B,F,T]
        # print(query_layer, key_layer, value_layer)
        attention_scores = tf.matmul(query_layer, key_layer, transpose_b=True)
        attention_scores = tf.multiply(
            attention_scores, 1.0 / math.sqrt(float(hidden_size)))
        #print(attention_scores.shape, attention_mask.shape)
        #attention_mask = tf.expand_dims(attention_mask, axis=[1])

        adder = (1.0 - tf.cast(attention_mask, tf.float32)) * -10000.0
        attention_scores += adder

        attention_probs = tf.nn.softmax(attention_scores)
        # attention_probs = dropout(
        #    attention_probs, attention_probs_dropout_prob)
        # [B,F,T] * [B,T,H] --> [B,F,H]
        #print(attention_probs.shape, value_layer.shape)
        context_layer = tf.matmul(attention_probs, value_layer)

        return context_layer

    def _make_loss(self) -> None:
        if self.hyperparameters['loss'] == 'softmax':
            '''
            logits = tf.matmul(self.ops['query_representations'],
                               self.ops['code_representations'],
                               transpose_a=False,
                               transpose_b=True,
                               name='code_query_cooccurrence_logits',
                               )  # B x B
            '''
            B = tf.shape(self.ops['query_representations'])[0]
            # print(self.ops['logits'].shape)
            # assert self.hyperparameters['batch_size'] == 8
            logits = tf.reshape(self.ops['logits'], [self.hyperparameters['batch_size'], self.hyperparameters['batch_size']])
            similarity_scores = logits
            #print(self.ops['query_representations'].shape)
            per_sample_loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
                labels=tf.range(self.hyperparameters['batch_size']),  # [0, 1, 2, 3, ..., n]
                logits=logits
            )
        elif self.hyperparameters['loss'] == 'triplet':
            query_reps = self.ops['query_representations']  # BxD
            code_reps = self.ops['code_representations']    # BxD

            query_reps = tf.broadcast_to(query_reps, shape=[tf.shape(
                query_reps)[0], tf.shape(query_reps)[0], tf.shape(query_reps)[1]])  # B*xBxD
            code_reps = tf.broadcast_to(code_reps, shape=[tf.shape(
                code_reps)[0], tf.shape(code_reps)[0], tf.shape(code_reps)[1]])  # B*xBxD
            code_reps = tf.transpose(code_reps, perm=(1, 0, 2))  # BxB*xD

            all_pair_distances = tf.norm(
                query_reps - code_reps, axis=-1)  # BxB
            similarity_scores = -all_pair_distances

            correct_distances = tf.expand_dims(
                tf.diag_part(all_pair_distances), axis=-1)  # Bx1

            pointwise_loss = tf.nn.relu(
                correct_distances - all_pair_distances + self.hyperparameters['margin'])  # BxB
            pointwise_loss *= (1 - tf.eye(tf.shape(pointwise_loss)[0]))

            per_sample_loss = tf.reduce_sum(pointwise_loss, axis=-1) / (tf.reduce_sum(
                tf.cast(tf.greater(pointwise_loss, 0), dtype=tf.float32), axis=-1) + 1e-10)  # B
        else:
            raise Exception(
                f'Unrecognized loss-type "{self.hyperparameters["loss"]}"')

        per_sample_loss = per_sample_loss * \
            self.placeholders['sample_loss_weights']
        self.ops['loss'] = tf.reduce_sum(
            per_sample_loss) / tf.reduce_sum(self.placeholders['sample_loss_weights'])

        # extract the logits from the diagonal of the matrix, which are the logits corresponding to the ground-truth
        correct_scores = tf.diag_part(similarity_scores)
        # compute how many queries have bigger logits than the ground truth (the diagonal) -> which will be incorrectly ranked
        compared_scores = similarity_scores >= tf.expand_dims(
            correct_scores, axis=-1)
        # for each row of the matrix (query), sum how many logits are larger than the ground truth
        # ...then take the reciprocal of that to get the MRR for each individual query (you will need to take the mean later)
        self.ops['mrr'] = 1 / \
            tf.reduce_sum(tf.to_float(compared_scores), axis=1)

    def get_representations_logits(self, query_code_data):
        def code_data_loader(sample_to_parse, result_holder):
            code_tokens = sample_to_parse['code_tokens']
            language = sample_to_parse['language']
            if language.startswith('python'):
                language = 'python'

            if code_tokens is not None:
                function_name = sample_to_parse.get('func_name')
                return self._code_encoder_type.load_data_from_sample(
                    "code",
                    self.hyperparameters,
                    self._per_code_language_metadata[language],
                    code_tokens,
                    function_name,
                    result_holder=result_holder,
                    is_test=True)
            else:
                return False

        def query_data_loader(sample_to_parse, result_holder):
            function_name = sample_to_parse.get('func_name')
            return self._query_encoder_type.load_data_from_sample(
                "query",
                self.hyperparameters,
                self._query_metadata,
                [d.lower() for d in sample_to_parse['docstring_tokens']],
                function_name,
                result_holder=result_holder,
                is_test=True)

        return self._compute_representations_logits_batched(query_code_data,
                                                      query_data_loader_fn=code_data_loader,
                                                      code_data_loader_fn=query_data_loader,
                                                      model_representation_op=self._ops['logits'])

    def _compute_representations_logits_batched(self,
                                          raw_data: List[Dict[str, Any]],
                                          query_data_loader_fn: Callable[[Dict[str, Any], Dict[str, Any]], bool],
                                          code_data_loader_fn: Callable[[Dict[str, Any], Dict[str, Any]], bool],
                                          model_representation_op: tf.Tensor) -> List[Optional[np.ndarray]]:
        """Return a list of vector representation of each datapoint or None if the representation for that datapoint
        cannot be computed.

        Args:
            raw_data: a list of raw data point as dictionanries.
            data_loader_fn: A function f(in, out) that attempts to load/preprocess the necessary data from
             in and store it in out, returning a boolean success value. If it returns False, the sample is
             skipped and no representation is computed.
            model_representation_op: An op in the computation graph that represents the desired
             representations.
            representation_type: type of the representation we are interested in (either code or query)

        Returns:
             A list of either a 1D numpy array of the representation of the i-th element in data or None if a
             representation could not be computed.
        """
        tensorized_data = defaultdict(list)  # type: Dict[str, List[Dict[str, Any]]]
        sample_to_tensorised_data_id = []  # type: List[Optional[SampleId]]
        for raw_sample in raw_data:
            language = raw_sample['language']
            if language.startswith('python'):
                language = 'python'
            sample: Dict = {}

            query_valid_example = query_data_loader_fn(raw_sample, sample)
            code_valid_example  = code_data_loader_fn(raw_sample, sample)

            if query_valid_example and code_valid_example:
                sample_to_tensorised_data_id.append((language, len(tensorized_data[language])))
                tensorized_data[language].append(sample)
            else:
                sample_to_tensorised_data_id.append(None)

        assert len(sample_to_tensorised_data_id) == len(raw_data)

        data_generator = self._split_data_into_minibatches(tensorized_data,
                                                            is_train=False,
                                                            include_query=True,
                                                            include_code=True,
                                                            drop_incomplete_final_minibatch=False)

        computed_representations = []
        original_tensorised_data_ids = []  # type: List[SampleId]
        for minibatch_counter, (batch_data_dict, samples_in_batch, samples_used_so_far, batch_original_tensorised_data_ids) in enumerate(data_generator):
            #print(samples_in_batch)
            op_results = self._sess.run(model_representation_op, feed_dict=batch_data_dict)
            #print(op_results.shape)
            computed_representations.append(op_results)
            original_tensorised_data_ids.extend(batch_original_tensorised_data_ids)
        computed_representations = np.concatenate(computed_representations, axis=0)
        #print("len(computed_representations): {}".format(len(computed_representations)))
        return computed_representations

        #print("len(computed_representations): {}".format(len(computed_representations)))
        tensorised_data_id_to_representation_idx = {tensorised_data_id: repr_idx
                                                    for (repr_idx, tensorised_data_id) in enumerate(original_tensorised_data_ids)}
        reordered_representations: List = []
        for tensorised_data_id in sample_to_tensorised_data_id:
            if tensorised_data_id is None:
                reordered_representations.append(None)
            else:
                reordered_representations.append(computed_representations[tensorised_data_id_to_representation_idx[tensorised_data_id]])
        return reordered_representations  