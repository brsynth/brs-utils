"""
Created on June 17 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from sys import _getframe
from brs_utils import check_nb_args


class Test_CheckNbArgs(TestCase):

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
