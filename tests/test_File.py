"""
Created on Jul 14 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from brs_utils import file_length, read_dict, download, extract_gz, extract_tar_gz, extract_gz_to_string, download_and_extract_tar_gz
from tempfile  import NamedTemporaryFile, TemporaryDirectory
from pathlib   import Path
from hashlib   import sha256
from json      import dumps as json_dumps
from os        import path  as os_path

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
        with TemporaryDirectory() as tempd:
            filename = tempd+'/dict'
            self._create_file_from_dict(filename, self._d)
            dict = read_dict(filename)
            self.assertDictEqual(dict, self._d)

    DOWNLOAD_URL    = 'https://github.com/brsynth/brs-utils/raw/master/tests/data/data.tar.gz'
    DOWNLOAD_HASH   = '451f23622ee6df7b96648039db374e7baa8c41495e4dbf91dbf232950db65a13'
    DOWNLOAD_HASHES = {'test_rpSBML.py':    '2031eefaf7305428e10f5a3c6ab485085d69979b8be6a1e3b2e375349ec7b9bd',
                       'test_TotalSize.py': '6a81f09015f516b8cfed8f39badbac3380e758df625c0ce3b9c87a79745813e2',
                       'test_Download.py':  '504676268634b8c340a11e202b4d9c7cc08f9daea749f4c9cf5db9294772bc39'}

    def test_download(self):
        with NamedTemporaryFile() as tempf:
            download(Test_File.DOWNLOAD_URL,
                     tempf.name)
            self.assertEqual(
                sha256(Path(tempf.name).read_bytes()).hexdigest(),
                       Test_File.DOWNLOAD_HASH)

    def test_download_and_extract_tar_gz(self):
        with TemporaryDirectory() as tempd:
            download_and_extract_tar_gz(Test_File.DOWNLOAD_URL, tempd)
            for member in Test_File.DOWNLOAD_HASHES:
                self.assertEqual(Test_File.DOWNLOAD_HASHES[member],
                                 sha256(Path(tempd+'/'+member).read_bytes()).hexdigest())

    def test_download_and_extract_tar_gz_member(self):
        _member = 'test_rpSBML.py'
        with TemporaryDirectory() as tempd:
            download_and_extract_tar_gz(Test_File.DOWNLOAD_URL, tempd, _member)
            for member in Test_File.DOWNLOAD_HASHES:
                m = tempd+'/'+member
                if member == _member:
                    self.assertEqual(Test_File.DOWNLOAD_HASHES[_member],
                                     sha256(Path(m).read_bytes()).hexdigest())
                else:
                    self.assertFalse(Path(m).exists())

    def test_extract_gz(self):
        with TemporaryDirectory() as tempd:
            extract_gz('data/data.tar.gz', tempd)
            self.assertEqual(
                sha256(Path(tempd+'/data.tar').read_bytes()).hexdigest(),
                'd3eb1c4b3604e6863fb4c4da930b4df74217fcf95c78439bc721ea83ce280f19'
                            )

    def test_extract_gz_to_string(self):
        s = extract_gz_to_string('data/data.tar.gz')
        self.assertEqual(
            sha256(s.encode()).hexdigest(),
            'd3eb1c4b3604e6863fb4c4da930b4df74217fcf95c78439bc721ea83ce280f19'
                        )

    def test_extract_tar_gz_file(self):
        with TemporaryDirectory() as tempd:
            extract_tar_gz('data/data.tar.gz', tempd, 'test_rpSBML.py')
            self.assertEqual(
                sha256(Path(tempd+'/test_rpSBML.py').read_bytes()).hexdigest(),
                '2031eefaf7305428e10f5a3c6ab485085d69979b8be6a1e3b2e375349ec7b9bd'
                            )
            self.assertFalse(Path(tempd+'/test_Download.py').exists())

    def test_extract_tar_gz(self):
        with TemporaryDirectory() as tempd:
            extract_tar_gz('data/data.tar.gz', tempd)
            self.assertEqual(
                sha256(Path(tempd+'/test_Download.py').read_bytes()).hexdigest(),
                '504676268634b8c340a11e202b4d9c7cc08f9daea749f4c9cf5db9294772bc39'
                            )
