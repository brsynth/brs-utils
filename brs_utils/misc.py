"""
Created on June 16 2020

@author: Joan Hérisson
"""

from sys import (
    getsizeof,
    stderr
)
from os import (
    devnull,
)
from collections import deque
from itertools import chain
try:
    from reprlib import repr
except ImportError:
    pass
from logging import (
    Logger,
    getLogger
)
from subprocess import (
    run,
    DEVNULL
)  # nosec
from argparse import (
    ArgumentTypeError,
    ArgumentParser,
    Namespace
)
from colored import fg, bg, attr
import multiprocessing.pool
import functools

from brs_utils import create_logger


def subprocess_call(
    cmd: str,
    stdout = None,
    stderr = None,
    logger: Logger = getLogger(__name__)
) -> int:
    if stdout is None:
        stdout = DEVNULL if logger.level > 10 else None
    if stderr is None:
        stderr = DEVNULL if logger.level > 10 else None
    try:
        CPE = run(
            cmd.split(),
            stdout=stdout,
            stderr=stderr,
            shell=False
        )  # nosec
        logger.debug(CPE)
        return CPE
    except OSError as e:
        logger.error(e)
        logger.debug(CPE)
        return CPE

def total_size(o, handlers={}, verbose=False):
    """ Returns the approximate memory footprint an object and all of its contents.

    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    To search other containers, add handlers to iterate over their contents:

        handlers = {SomeContainerClass: iter,
                    OtherContainerClass: OtherContainerClass.get_elements}

    """
    dict_handler = lambda d: chain.from_iterable(d.items())
    all_handlers = {
            tuple: iter,
             list: iter,
            deque: iter,
             dict: dict_handler,
              set: iter,
        frozenset: iter,
    }
    all_handlers.update(handlers)     # user handlers take precedence
    seen = set()                      # track which object id's have already been seen
    default_size = getsizeof(0)       # estimate sizeof object without __sizeof__

    def sizeof(o):
        if id(o) in seen:       # do not double count the same object
            return 0
        seen.add(id(o))
        s = getsizeof(o, default_size)

        if verbose:
            print(s, type(o), repr(o), file=stderr)

        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(
                    map(
                        sizeof,
                        handler(o)
                    )
                )
                break
        return s

    return sizeof(o)

def check_nb_args(*args, f_name, nb_args):
    if len(args) < nb_args:
        raise TypeError(f_name+' missing '+str(nb_args)+' required positional argument')
    elif len(args) > nb_args:
        raise TypeError(f_name+' takes '+str(nb_args)+' positional arguments but '+str(len(args))+' were given')
    return True

def timeout(max_timeout):
    """Timeout decorator, parameter in seconds."""
    def timeout_decorator(item):
        """Wrap the original function."""
        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            pool = multiprocessing.pool.ThreadPool(processes=1)
            async_result = pool.apply_async(item, args, kwargs)
            # raises a TimeoutError if execution exceeds max_timeout
            return async_result.get(max_timeout)
        return func_wrapper
    return timeout_decorator

def arg_range(mini, maxi):
    """Return function handle of an argument type function for 
       ArgumentParser checking a float range: mini <= arg <= maxi
         mini - minimum acceptable argument
         maxi - maximum acceptable argument"""

    # Define the function with default arguments
    def arg_range_checker(arg):
        """New Type function for argparse - a float within predefined range."""

        type_ = type(mini)
        try:
            f = type_(arg)
        except ValueError:    
            raise ArgumentTypeError(f"must be a {type_} number")
        if f < mini or f > maxi:
            raise ArgumentTypeError(f"must be in range [{str(mini)}..{str(maxi)}]")
        return f

    # Return function handle to checking function
    return arg_range_checker

def init(
    parser: ArgumentParser,
    args: Namespace,
    version: str
) -> Logger:
    if args.log.lower() in ['silent', 'quiet'] or args.silent:
        args.log = 'CRITICAL'

    # Create logger
    logger = create_logger(parser.prog, args.log)

    logger.info(
        '{color}{typo}{prog} {version}{rst}{color}{rst}\n'.format(
            prog = logger.name,
            version = version,
            color=fg('white'),
            typo=attr('bold'),
            rst=attr('reset')
        )
    )
    logger.debug(args)

    return logger
