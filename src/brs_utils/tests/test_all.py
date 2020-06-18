"""
Created on June 17 2020

@author: Joan Hérisson
"""

import unittest

from sys import path as sys_path
from sys import exit as sys_exit
sys_path.insert(0, '/home/src')
from brs_utils import rpSBML, total_size

# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
class Test_rpSBML(unittest.TestCase):

    def __init__(self, testname):
        super(Test_rpSBML, self).__init__(testname)

    def test_initEmpty(self):
        rpsbml = rpSBML('rpSBML_test')

class Test_misc(unittest.TestCase):

    def __init__(self, testname):
        super(Test_misc, self).__init__(testname)

    def test_totalsize_int(self):
        size = total_size(int(1))
        self.assertEqual(size, 28)

    def test_totalsize_float(self):
        size = total_size(float(1))
        self.assertEqual(size, 24)

    def test_totalsize_str(self):
        msg = 'this is a test'
        size = total_size(str(msg))
        self.assertEqual(size, 49+len(msg))
