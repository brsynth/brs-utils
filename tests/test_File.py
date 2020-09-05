"""
Created on Jul 14 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from brs_utils import file_length, read_dict, download, extract_gz, download_and_extract_gz
from tempfile  import NamedTemporaryFile, TemporaryDirectory
from pathlib   import Path
from hashlib   import sha256
from json      import dumps as json_dumps

class Test_File(TestCase):

    def test_empty_file(self):
        self.assertEqual(file_length('data/empty_file.txt'), 0)

    def test_1l_file(self):
        self.assertEqual(file_length('data/1l_file.txt'), 1)

    def test_100l_file(self):
        self.assertEqual(file_length('data/100l_file.txt'), 100)

    _d = {'a': 1, 'b': 2}

    def _create_file_from_dict(self, filename, dict):
        with open(filename, 'w') as f:
            f.write(json_dumps(dict))

    def test_readdict_ok(self):
        filename = 'dict'
        self._create_file_from_dict(filename, self._d)
        dict = read_dict(filename)
        self.assertDictEqual(dict, self._d)

    _url = 'https://gitlab.com/breakthewall/rpcache-data/-/raw/master/metanetx/comp_xref.tsv.gz'

    def test_download(self):
        with NamedTemporaryFile() as tempf:
            download(self._url,
                     tempf.name)
            self.assertEqual(
                sha256(Path(tempf.name).read_bytes()).hexdigest(),
                '7b9a3931d850821b7d5b443767f8c5282fd879ab71eb455c8809c009f8ca7dd7'
                            )

    def test_extract_gz(self):
        with TemporaryDirectory() as tempd:
            extract_gz('data/data.gz', tempd)
            self.assertEqual(
                sha256(Path(tempd+'/test_Download.py').read_bytes()).hexdigest(),
                '504676268634b8c340a11e202b4d9c7cc08f9daea749f4c9cf5db9294772bc39'
                            )
