from typing import Any, Dict, Optional

from encoders import NBoWEncoder
from .model import Model

import tensorflow as tf
import numpy as np


class NeuralBoWModel_V1(Model):
    @classmethod
    def get_default_hyperparameters(cls) -> Dict[str, Any]:
        hypers = {}
        for label in ["code", "query"]:
            hypers.update({f'{label}_{key}': value
                           for key, value in NBoWEncoder.get_default_hyperparameters().items()})
        model_hypers = {
            'code_use_subtokens': False,
            'code_mark_subtoken_end': False,
            'loss': 'cosine',
            'batch_size': 1000
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

    def _make_model(self, is_train: bool) -> None:
        """
        Create the actual model.

        Note: This has to create self.ops['code_representations'] and self.ops['query_representations'],
        tensors of the same shape and rank 2.
        """
        self._placeholders['dropout_keep_rate'] = tf.compat.v1.placeholder(tf.float32,
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
            for (language, language_metadata) in sorted(self._per_code_language_metadata.items(), key=lambda kv: kv[0]):
                with tf.variable_scope(language):
                    self._code_encoders[language] = self._code_encoder_type(label="code",
                                                                            hyperparameters=self.hyperparameters,
                                                                            metadata=language_metadata)
                    language_encoders.append(tf.matmul(
                        self._code_encoders[language].make_model(
                            is_train=is_train),
                        tf.get_variable(name=language, shape=[self._code_encoders[language].output_representation_size,
                                               self._code_encoders[language].output_representation_size], initializer=tf.random_normal_initializer()),
                        transpose_a=False, transpose_b=False))
            self._ops['code_representations'] = tf.concat(
                language_encoders, axis=0)

        with tf.variable_scope("query_encoder"):
            self._query_encoder = self._query_encoder_type(label="query",
                                                           hyperparameters=self.hyperparameters,
                                                           metadata=self._query_metadata)
            self._ops['query_representations'] = self._query_encoder.make_model(
                is_train=is_train)

        code_representation_size = next(
            iter(self._code_encoders.values())).output_representation_size
        query_representation_size = self._query_encoder.output_representation_size
        assert code_representation_size == query_representation_size, \
            f'Representations produced for code ({code_representation_size}) and query ({query_representation_size}) cannot differ!'

        #with tf.variable_scope("query_code_bilinear"):
        #      self.ops['bilinear_matrix'] = tf.get_variable(name='bilinear_matrix', shape=[query_representation_size, query_representation_size], initializer=tf.random_normal_initializer())
  