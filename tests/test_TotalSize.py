"""
Created on June 17 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from brs_utils import total_size


class Test_TotalSize(TestCase):

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
