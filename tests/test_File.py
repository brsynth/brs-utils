"""
Created on Jul 14 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from brs_utils import file_length
from pathlib import Path

class Test_File(TestCase):

    def test_empty_file(self):
        self.assertEqual(file_length('data/empty_file.txt'), 0)

    def test_1l_file(self):
        self.assertEqual(file_length('data/1l_file.txt'), 1)

    def test_100l_file(self):
        self.assertEqual(file_length('data/100l_file.txt'), 100)
