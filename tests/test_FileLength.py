"""
Created on Jul 14 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from brs_utils import download, extract_gz, download_and_extract_gz, file_length
from tempfile import NamedTemporaryFile, TemporaryDirectory
from hashlib import sha256
from pathlib import Path
from os import path as os_path

class Test_FileLength(TestCase):

    def test_empty_file(self):
        self.assertEqual(file_length('data/empty_file.txt'), 0)

    def test_1l_file(self):
        self.assertEqual(file_length('data/1l_file.txt'), 1)

    def test_100l_file(self):
        self.assertEqual(file_length('data/100l_file.txt'), 100)
