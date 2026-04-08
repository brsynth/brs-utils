"""
Created on Feb 4 2021

@author: Joan Hérisson
"""
from argparse import ArgumentParser

def build_args_parser(
    prog: str,
    version: str = "unknown",
    description: str = "",
    epilog: str = "",
    m_add_args=None
) -> ArgumentParser:

    parser = ArgumentParser(prog=prog, description=description, epilog=epilog)

    # Build Parser with rptools common arguments
    if m_add_args:
        parser = m_add_args(parser)
    parser = add_arguments(parser, version=version)

    return parser


def add_arguments(parser: ArgumentParser, version: str) -> ArgumentParser:
    parser.add_argument(
        '--log', '-l',
        metavar='ARG',
        type=str,
        choices=[
            'debug', 'info', 'warning', 'error', 'critical', 'silent', 'quiet',
            'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'SILENT', 'QUIET'
        ],
        default='def_info',
        help='Adds a console logger for the specified level (default: error)'
    )
    parser.add_argument(
        '--log_file',
        type=str,
        default='',
        help='Filename where to put logs'
    )
    parser.add_argument(
        '--silent', '-s',
        action='store_true',
        default=False,
        help='run %(prog)s silently'
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {}".format(version),
        help="show the version number and exit",
    )
    return parser
