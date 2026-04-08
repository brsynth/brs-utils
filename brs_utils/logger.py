"""
Created on Feb 4 2021

@author: Joan Hérisson
"""

from colorlog import ColoredFormatter
from colored import fg, attr
from logging import Logger, getLogger, StreamHandler, FileHandler
from argparse import Namespace, ArgumentParser


def init(parser: ArgumentParser, args: Namespace, version: str) -> Logger:
    if args.log.lower() in ["silent", "quiet"] or args.silent:
        args.log = "CRITICAL"

    # Create logger
    logger = create_logger(parser.prog, args.log)

    logger.info(
        "{color}{typo}{prog} {version}{rst}{color}{rst}\n".format(
            prog=logger.name,
            version=version,
            color=fg("white"),
            typo=attr("bold"),
            rst=attr("reset"),
        )
    )
    logger.debug(args)

    return logger


def create_logger(
    name: str = __name__,
    log_level: str = "def_info",
    log_file: str = "",
    no_color: bool = False,
) -> Logger:
    """
    Create a logger with name and log_level.

    Parameters
    ----------
    name : str
        A string containing the name that the logger will print out

    log_level : str
        A string containing the verbosity of the logger

    log_file : str
        A string containing the path to the log file. If empty, no file is created.

    no_color : bool
        If True, the logger will not use colors.

    Returns
    -------
    Logger
        The logger object.

    """
    logger = getLogger(name)

    if no_color:
        log_format = ""
    else:
        log_format = "%(log_color)s"

    if log_level.startswith("def_"):
        log_format += "%(message)s%(reset)s"
        log_level = log_level[4:]
    else:
        log_format += "%(levelname)-8s | %(asctime)s.%(msecs)03d %(module)s - %(funcName)s(): %(message)s%(reset)s"

    formatter = ColoredFormatter(log_format)
    handler = StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if log_file:
        handler = FileHandler(log_file)
        logger.addHandler(handler)
    logger.setLevel(log_level.upper())

    return logger
