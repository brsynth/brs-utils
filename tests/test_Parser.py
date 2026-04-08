"""
Created on June 17 2020

@author: Joan Hérisson
"""

from unittest import TestCase

from brs_utils import build_args_parser


class Test_Parser(TestCase):

    def test_call(self):
        def add_args(parser):
            parser.add_argument(
                "--test", "-t", action="store_true", default=False, help="Test argument"
            )
            return parser

        build_args_parser(
            prog="test",
            version="0.1",
            description="Test parser",
            epilog="Test parser",
            m_add_args=add_args,
        )
        self.assertTrue(True)
