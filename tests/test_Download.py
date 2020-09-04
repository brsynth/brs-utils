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
        self._url = 'https://gitlab.com/breakthewall/rpcache-data/-/raw/master/deprecatedMNXM_mnxm.json.gz'

    def test_download(self):
        with NamedTemporaryFile() as tempf:
            download(self._url,
                     tempf.name)
            self.assertEqual(
                sha256(Path(tempf.name).read_bytes()).hexdigest(),
                '169cd9e7b215c2dbafabb97c6663938e986cdf8e5fbcacc0840eb1b26f7cd786'
                            )

    def test_extract_gz(self):
        with TemporaryDirectory() as tempd:
            extract_gz('data/data.gz', tempd)
            self.assertEqual(
                sha256(Path(tempd+'/test_Download.py').read_bytes()).hexdigest(),
                '504676268634b8c340a11e202b4d9c7cc08f9daea749f4c9cf5db9294772bc39'
                            )

    # def test_download_and_extract_gz(self):
    #     with TemporaryDirectory() as tempd:
    #         download_and_extract_gz(self._url, tempd)
    #         self.assertEqual(
    #             sha256(Path(tempd+'/deprecatedMNXM_mnxm.pickle').read_bytes()).hexdigest(),
    #             '45d90e3da807f464a02cc0cea8a2544b3cce5e476d370fedbfade981f2273308'
    #                         )