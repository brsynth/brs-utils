"""
Created on June 17 2020

@author: Joan Hérisson
"""

import unittest

from sys import path as sys_path
from sys import exit as sys_exit
sys_path.insert(0, '/home/src')
from rplibs import rpSBML

# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
class Test_rpSBML(unittest.TestCase):

    def __init__(self, testname):
        super(Test_rpSBML, self).__init__(testname)

    def test_initEmpty(self):
        rpsbml = rpSBML('rpSBML_test')
