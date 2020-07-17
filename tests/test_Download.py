"""
Created on Jul 14 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from brs_utils import download, extract_gz, download_and_extract_gz
from tempfile import NamedTemporaryFile, TemporaryDirectory
from hashlib import sha256
from pathlib import Path

class Test_Download(TestCase):

    def setUp(self):
        self._url = 'https://github.com/brsynth/rpCache-data/raw/master/deprecatedMNXM_mnxm.pickle.tar.gz'

    def test_download(self):
        with NamedTemporaryFile() as tempf:
            download(self._url,
                     tempf.name)
            self.assertEqual(
                sha256(Path(tempf.name).read_bytes()).hexdigest(),
                '6803e0611c3890807351cacf3e02a38082bfe95d0c3ee3d23071fdae0b8bced6'
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
                sha256(Path(tempd+'/deprecatedMNXM_mnxm.pickle').read_bytes()).hexdigest(),
                '45d90e3da807f464a02cc0cea8a2544b3cce5e476d370fedbfade981f2273308'
                            )
