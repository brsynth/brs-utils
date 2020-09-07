"""
Created on June 17 2020

@author: Joan Hérisson
"""

from unittest import TestCase
from tempfile  import NamedTemporaryFile, TemporaryDirectory
import os.path as os_path
from pathlib   import Path

from brs_utils import rpSBML

# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
class Test_rpSBML(TestCase):

    def test_initEmpty(self):
        rpsbml = rpSBML('rpSBML_test')

    def test_mergeModels(self):
         with TemporaryDirectory() as tmpd:
            rpSBML.mergeSBMLFiles('data/rp_1_2_sbml.xml', 'data/e_coli_core_model_sbml.xml', tmpd)
            self.assertEqual(sha256(Path(os_path.join(tmpd, 'target.xml'))).read_bytes()).hexdigest(),
                            'b80f6deff575c704a8f02c2cd9ab09b1725f732e861307e9f4ece4bab8152e84')

