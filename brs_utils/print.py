"""
Created on June 16 2020

@author: Joan Hérisson
"""

from sys import stdout as sys_stdout
from logging import(
    Logger,
    getLogger,
    StreamHandler
)
from colored import fg, bg, attr


def print_OK_adv(logger: Logger=getLogger(__name__)) -> None:
    logger.info(
        '{color}{typo} OK{rst}'.format(
            color=fg('green'),
            typo=attr('bold'),
            rst=attr('reset')
        )
    )


def print_title_adv(
    txt: str,
    logger: Logger=getLogger(__name__),
    waiting: bool=False
) -> None:
    if waiting:
        StreamHandler.terminator = ""
    logger.info(
        '{color}{typo}{txt}{rst}'.format(
            color=fg('white'),
            typo=attr('bold'),
            rst=attr('reset'),
            txt=txt
        )
    )
    StreamHandler.terminator = "\n"


def print_OK(time=-1):
    sys_stdout.write("\033[0;32m") # Green
    print(" OK", end = '', flush=True)
    sys_stdout.write("\033[0;0m") # Reset
    if time!=-1: print(" (%.2fs)" % time, end = '', flush=True)
    print()

def print_FAILED():
    sys_stdout.write("\033[1;31m") # Red
    print(" Failed")
    sys_stdout.write("\033[0;0m") # Reset
    print()


from logging import (
    Logger,
    getLogger,
    StreamHandler
)
from colored import (
    attr as c_attr,
    fg as c_fg,
    bg as c_bg
)

def print_start(
    logger: Logger=getLogger(__name__),
    msg: str='Start process',
) -> None:
    StreamHandler.terminator = ""
    logger.info(
        '{color}{typo}{msg}{rst}'.format(
            color=c_fg('white'),
            typo=c_attr('bold'),
            msg=msg,
            rst=c_attr('reset')
        )
    )

def print_progress(
    logger: Logger=getLogger(__name__),
    msg: str='.',
) -> None:
    logger.info(
        '{color}{msg}'.format(
            color=c_fg('white'),
            msg=msg
        )
    )

def print_end(
    logger: Logger=getLogger(__name__),
    msg: str='OK',
) -> None:
    StreamHandler.terminator = "\n"
    logger.info(
        '{color}{typo} {msg}{rst}'.format(
            color=c_fg('green'),
            typo=c_attr('bold'),
            msg=msg,
            rst=c_attr('reset')
        )
    )
