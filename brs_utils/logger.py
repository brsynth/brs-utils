"""
Created on Feb 4 2021

@author: Joan Hérisson
"""

from colorlog import ColoredFormatter
from logging import (
    Logger,
    getLogger,
    StreamHandler
)
from argparse import ArgumentParser


def create_logger(
    name: str = __name__,
    log_level: str = 'def_info'
    ) -> Logger:
    """
    Create a logger with name and log_level.

    Parameters
    ----------
    name : str
        A string containing the name that the logger will print out

    log_level : str
        A string containing the verbosity of the logger

    Returns
    -------
    Logger
        The logger object.

    """    
    logger  = getLogger(name)
    handler = StreamHandler()

    if log_level.startswith('def_'):
        log_format = '%(log_color)s%(message)s%(reset)s'
        log_level  = log_level[4:]
    else:
        log_format = '%(log_color)s%(levelname)-8s | %(asctime)s.%(msecs)03d %(module)s - %(funcName)s(): %(message)s%(reset)s'
 
    formatter = ColoredFormatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(log_level.upper())

    return logger


def add_arguments(parser: ArgumentParser) -> ArgumentParser:
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
    return parser
