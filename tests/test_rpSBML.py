"""
Created on June 17 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from brs_utils import rpSBML

# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
class Test_rpSBML(TestCase):

    def test_initEmpty(self):
        rpsbml = rpSBML('rpSBML_test')
