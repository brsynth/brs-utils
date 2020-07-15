"""
Created on Jul 14 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from brs_utils import download, extract_gz, download_and_extract_gz
from tempfile import NamedTemporaryFile, TemporaryDirectory
from hashlib import sha256
from pathlib import Path
from os import path as os_path

class Test_Download(TestCase):

    def setUp(self):
        self._url = 'https://github.com/brsynth/rpCache-data/raw/master/cache.tar.gz'

    def test_download(self):
        with NamedTemporaryFile() as tempf:
            download(self._url,
                     tempf.name)
            self.assertEqual(
                sha256(Path(tempf.name).read_bytes()).hexdigest(),
                'b524d5ea71c4e3f8a98f0a40c25d085897ecadcbb660a88770f1f6947a4403b7'
                            )

    def test_extract_gz(self):
        with TemporaryDirectory() as tempd:
            extract_gz('data/data.gz', tempd)
            self.assertEqual(
                sha256(Path(tempd+'/test_Download.py').read_bytes()).hexdigest(),
                '504676268634b8c340a11e202b4d9c7cc08f9daea749f4c9cf5db9294772bc39'
                            )

    def test_download_and_extract_gz(self):
        with TemporaryDirectory() as tempd:
            download_and_extract_gz(self._url, tempd)
            self.assertEqual(
                sha256(Path(tempd+'/mnxm_strc.pickle').read_bytes()).hexdigest(),
                'd7c32032677ea4e5caa586a563c68c132e6e3afdc616c4ed8af2b6659a8fbca5'
                            )
