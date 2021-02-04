"""
Created on June 17 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from brs_utils import create_logger


class Test_Logger(TestCase):

    def test_call(self):
        logger = create_logger('TEST', 'INFO')
        self.assertTrue(True)
