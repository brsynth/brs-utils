from logging import (
    Logger,
    getLogger
)
import re

def comp_succ(
    string: str,
    char: str,
    logger: Logger=getLogger()
) -> str:
    """
    Compress a succession of 'char' into one single occurence.

    Parameters
    ----------
    string : str
        A string to compress succession of a char
    char: str
        A char to compression succession of.

    logger : Logger, optional

    Returns
    -------
    String
        String without successions of 'char'.

    """    
    pattern = char + '{2,}'
    return re.sub(pattern, char, string)
