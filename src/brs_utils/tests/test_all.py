"""
Created on June 17 2020

@author: Joan Hérisson
"""

import unittest

from sys import path as sys_path
from sys import exit as sys_exit
from sys import _getframe
sys_path.insert(0, '/home/src')
from brs_utils import rpSBML, total_size, check_nb_args

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

    def test_checknbargs_0_0(self):
        self.assertEqual(True,
                         check_nb_args(f_name=_getframe().f_code.co_name, nb_args=0))

    def test_checknbargs_0_1(self):
        self.assertRaises(TypeError,
                          check_nb_args, f_name=_getframe().f_code.co_name, nb_args=1)

    def test_checknbargs_1_0(self):
        self.assertRaises(TypeError,
                          check_nb_args, 1, f_name=_getframe().f_code.co_name, nb_args=0)

    def test_checknbargs_1_1(self):
        self.assertEqual(True,
                         check_nb_args(1, f_name=self.test_checknbargs_0_0.__name__, nb_args=1))

    def test_checknbargs_1_2(self):
        self.assertRaises(TypeError,
                          check_nb_args, 1, f_name=_getframe().f_code.co_name, nb_args=2)
