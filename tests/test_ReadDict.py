"""
Created on June 17 2020

@author: Joan Hérisson
"""

from unittest import TestCase
import json

from brs_utils import read_dict


class Test_ReadDict(TestCase):

    d = {'a': 1, 'b': 2}

    def _create_file_from_dict(self, filename, dict):
        with open(filename, 'w') as f:
            f.write(json.dumps(dict))

    def test_readdict_ok(self):
        filename = 'dict'
        self._create_file_from_dict(filename, self.d)
        dict = read_dict(filename)
        self.assertDictEqual(dict, self.d)
