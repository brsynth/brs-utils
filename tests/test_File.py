"""
Created on Jul 14 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from brs_utils import file_length, read_dict
from pathlib import Path
from json import dumps as json_dumps

class Test_File(TestCase):

    def test_empty_file(self):
        self.assertEqual(file_length('data/empty_file.txt'), 0)

    def test_1l_file(self):
        self.assertEqual(file_length('data/1l_file.txt'), 1)

    def test_100l_file(self):
        self.assertEqual(file_length('data/100l_file.txt'), 100)

    d = {'a': 1, 'b': 2}

    def _create_file_from_dict(self, filename, dict):
        with open(filename, 'w') as f:
            f.write(json_dumps(dict))

    def test_readdict_ok(self):
        filename = 'dict'
        self._create_file_from_dict(filename, self.d)
        dict = read_dict(filename)
        self.assertDictEqual(dict, self.d)
