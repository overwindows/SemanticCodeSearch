import fileinput
import sys
import torch
import pickle
import re
import shutil
import os
import model_restore_helper
import pandas as pd

from dataextraction.python.parse_python_data import tokenize_docstring_from_string
from collections import namedtuple
from fairseq import data, options, tasks, tokenizer, utils
from fairseq.sequence_generator import SequenceGenerator
from fairseq.utils import import_user_module
from annoy import AnnoyIndex
from docopt import docopt
from dpu_utils.utils import RichPath
from tqdm import tqdm

Batch = namedtuple('Batch', 'ids src_tokens src_lengths, src_strs')
Translation = namedtuple('Translation', 'src_str hypos pos_scores alignments')


class CodeSearch(object):
    def __init__(self):
        self.args = None
        self.local_model_path = 'neuralbow_hybrid-2020-07-05-13-43-57_model_best.pkl.gz'
        self.indices = {}
        self.definitions = {}
        self.model = None

    def search(self, query, language='python', topk=20):
        predictions = []
        query_embedding = self.model.get_query_representations([{'docstring_tokens': tokenize_docstring_from_string(query),
                                                                 'language': language}])[0]
        idxs, distances = self.indices[language].get_nns_by_vector(
            query_embedding, topk, search_k=10000, include_distances=True)
        for i, idx in enumerate(idxs):
            # print(self.definitions[idx].keys())
            predictions.append(
                {"id": self.definitions[language][idx]['sha'],
                 "name": self.definitions[language][idx]['identifier'],
                 "description": self.definitions[language][idx]['function'],
                 "categories": [language],
                 "subscriptions": [{"name": "Professional", "price": distances[i]}]
                 })
        return predictions

    def load_model(self):
        model_path = RichPath.create(self.local_model_path, None)
        print("Restoring model from %s" % model_path)
        self.model = model_restore_helper.restore(
            path=model_path,
            is_train=False,
            hyper_overrides={})

        for language in ['python', 'go', 'javascript', 'java', 'php', 'ruby']:
            # for language in ['python']:
            print("Loading language: %s" % language)
            self.definitions[language] = pickle.load(
                open('../resources/data/{}_dedupe_definitions_v2.pkl'.format(language), 'rb'))

            if os.path.exists('/datadrive/{}.ann'.format(language)):
                self.indices[language] = AnnoyIndex(128, 'angular')
                self.indices[language].load(
                    '/datadrive/{}.ann'.format(language))
            else:
                indexes = [{'code_tokens': d['function_tokens'],
                            'language': d['language']} for d in tqdm(self.definitions[language])]
                code_representations = self.model.get_code_representations(
                    indexes)
                print(code_representations[0].shape)
                self.indices[language] = AnnoyIndex(
                    code_representations[0].shape[0], 'angular')
                for index, vector in tqdm(enumerate(code_representations)):
                    assert vector is not None
                    self.indices[language].add_item(index, vector)
                self.indices[language].build(1000)
                self.indices[language].save(
                    '/datadrive/{}.ann'.format(language))
