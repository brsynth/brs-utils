"""
Created on Apr 14 2022

@author: Joan Hérisson
"""

from unittest import TestCase
from brs_utils import (
    comp_succ
)


class Test_String(TestCase):

    def test_comp_succ(self):
        string = 'H__H'
        self.assertEqual(
            comp_succ(string, '_'),
            'H_H'
        )

    def test_comp_succ_wo_succ(self):
        string = 'H_H'
        self.assertEqual(
            comp_succ(string, '_'),
            'H_H'
        )
