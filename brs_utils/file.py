"""
Created on June 16 2020

@author: Joan Hérisson
"""
from glob import glob
from os import (
    makedirs,
    remove,
    path as os_path,
    walk,
    stat as os_stat
)
from pathlib import (
    PurePath
)
from requests import get as r_get
from tempfile import (
    NamedTemporaryFile,
    mkdtemp
)
from tarfile  import open as tf_open
from gzip     import (
    open        as gz_open
)
from shutil import (
    copyfileobj,
    rmtree,
    chown
)
from ast import literal_eval
from typing import (
    Dict,
    List
)
from logging import (
    Logger,
    getLogger
)
from hashlib import (
    sha256,
    sha512
)
from pathlib import Path
from zipfile import ZipFile
from csv import reader as csv_reader


def read_sep_file(
    filename: str,
    sep: str=',',
    comment: str='#'
) -> List[List[str]]:
    '''Read file with a specific separator
    
    Parameters
    ----------
    filename: str
        Filename to read data from
    separator: str
        Separator which splits the line
    comment: str
        Lines start with 'comment' will be ignored

    Parameters
    ----------
    lines: List[List[str]]
        Each line of the input file is represented as a list of string.
        All lines of input file are put together into a list.
    '''
    f = open(filename)
    f_read = csv_reader(f, delimiter=sep)
    res = [line for line in f_read if not line[0].startswith('#')]
    f.close()
    return res

def read_tsv(filename: str) -> List[List[str]]:
    '''Read TSV file
    
    Parameters
    ----------
    filename: str
        Filename to read data from

    Parameters
    ----------
    lines: List[List[str]]
        Each line of the input file is represented as a list of string.
        All lines of input file are put together into a list.
    '''
    return read_sep_file(filename=filename, sep='\t')

def read_csv(filename: str) -> List[List[str]]:
    '''Read CSV file
    
    Parameters
    ----------
    filename: str
        Filename to read data from

    Parameters
    ----------
    lines: List[List[str]]
        Each line of the input file is represented as a list of string.
        All lines of input file are put together into a list.
    '''
    return read_sep_file(filename=filename, sep=',')

def unzip(
    file: str,
    dir: str
) -> None:
    '''Unzip the given file.

    Parameters
    ----------
    file: str
        Filename to unzip
    dir: str
        Directory to unzip into
    '''
    with ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(dir)


def download_and_unzip(
    url: str,
    dir: str
) -> None:
    '''Download file from URL and unzip it.

    Parameters
    ----------
    url: str
        URL of the file to download
    dir: str
        Directory to unzip into
    '''
    filename = download(url)
    unzip(filename, dir)
    remove(filename)


def check_file_size(
    filename: str,
    size: int,
    logger: Logger = getLogger(__name__)
) -> bool:
    logger.debug('file: {fname}'.format(fname=filename))
    logger.debug('-- SIZE')
    s = os_stat(filename).st_size
    logger.debug('computed: {size}'.format(size=s))
    logger.debug('stored: {size}'.format(size=size))
    logger.debug('--')
    return s == size


def check_sha(
    filename: str,
    sum: str,
    logger: Logger = getLogger(__name__)
) -> bool:

    return sum == sha512(
        Path(filename).read_bytes()
    ).hexdigest()


def chown_r(
    path: str,
    user,
    group = -1,
    logger: Logger = getLogger(__name__)
):
    """
    Recursively belongs path folder to uid:gid.

    Parameters
    ----------
    path: str
        Path to the folder to own.
    uid: int
        User ID.
    gid: int
        Group ID.
    """
    try:
        for dirpath, dirnames, filenames in walk(path):
            chown(dirpath, user, group)
            for filename in filenames:
                chown(os_path.join(dirpath, filename), user)
    except Exception as e:
        logger.error(e)


def download(
    url: str,
    file: str = ""
) -> str:
    """
    Download a file from 'url' and save it as 'file'.

    Parameters:
    url  -- URL the file is downloaded from
    file -- (Optional) filename the downloaded file is saved into (default: "")

    Returns:
    A filename where the downloaded file has stored into
    """
    r = r_get(url)
    if not file:
        f = NamedTemporaryFile(
            mode='wb',
            delete=False
        )
        file = f.name
    else:
        f = open(file, 'wb')
    f.write(r.content)
    f.close()
    return file


def extract_tar_gz(
      file: str,
       dir: str,
    member: str = '',
    delete: bool = False
) -> None:
    if not dir:
        dir = mkdtemp()
    if not os_path.exists(dir):
        makedirs(dir, exist_ok=True)
    tar = tf_open(file, mode='r:gz')
    if member == '':
        tar.extractall(dir)
    else:
        tar.extract(member, dir)
    tar.close()
    if delete:
        rmtree(dir)
    return dir


def compress_tar_gz(
       path:  str,
    outFile:  str = '',
     delete: bool = False
) -> str:
    """
    Compress 'path' into tar.gz format.

    Parameters:
    path    -- file or folder to compress
    outFile -- (Optional) path of compressed file (default: ""), otherwise file is compressed in place
    delete  -- (Optional) the original path is deleted after compression (default: False)

    Returns:
    The archive filename
    """
    if not outFile:
        f = NamedTemporaryFile(
            mode='wb',
            delete=False
        )
        outFile = f.name
    else:
        f = open(outFile, 'wb')
    with tf_open(fileobj=f, mode='w:gz') as tar:
        tar.add(
            path,
            arcname = os_path.basename(path)
        )
        tar.close()
    if delete:
        if os_path.isfile(path):
            remove(path)
        else:
            rmtree(path)
    return outFile


def compress_gz(
     inFile:  str,
    outFile:  str = '',
     delete: bool = False
) -> str:
    """
    Compress 'inFile' into gzip format.

    Parameters:
    inFile  -- file to compress
    outFile -- (Optional) path of compressed file (default: ""), otherwise file is compressed in place
    delete  -- (Optional) the original path is deleted after compression (default: False)

    Returns:
    The archive filename
    """
    if not outFile:
        outFile = inFile+'.gz'
    with open(inFile, 'rb') as f_in, gz_open(outFile, 'wb') as f_out:
        f_out.writelines(f_in)
        f_in.close()
        f_out.close()
    if delete:
        remove(inFile)

    return outFile


def extract_gz_to_string(filename: str) -> str:
    gz = gz_open(filename, mode='rb')
    decode = gz.read().decode()
    gz.close()
    return decode


def extract_gz(
    file: str,
    path: str
) -> str:
    outfile = os_path.join(path, os_path.basename(file[:-3]))
    makedirs(path, exist_ok=True)
    with gz_open(file, 'rb') as f_in, open(outfile, 'wb') as f_out:
        copyfileobj(f_in, f_out)
        f_in.close()
        f_out.close()
    return outfile


def download_and_extract_tar_gz(
    url: str,
    dir: str,
    member: str = ''
) -> None:
    filename = download(url)
    extract_tar_gz(filename, dir, member)
    remove(filename)


def download_and_extract_gz(
    url: str,
    path: str
) -> None:
    filename = download(url)
    extract_gz(filename, path)
    remove(filename)


def file_length(filename: str) -> int:
    with open(filename, 'rb') as f:
        n = sum(1 for line in f)
        f.close()
    return n


def read_dict(filename: str) -> Dict:
    d = {}
    with open(filename, 'r') as f:
        s = f.read()
        f.close()
        d = literal_eval(s)
    return d


def hash_dir(
    dir1: str,
    recursive: bool=False,
    chunk: int=65536
) -> str:
    '''Return an hexadigest from sha256 of file an name of files/folders excepted the name of root directory

    :param dir1: A path of a directory
    :param recursive: Recursively compare directory
    :param chunk: Chunk read files 

    :type dir1: str
    :type recursive: bool
    :type chunk: int

    :return: An hexadigest tag
    :rtype: str
    '''
    files = []
    if recursive:
        files = glob(
            os_path.join(dir1, '**', '*'),
            recursive=recursive
        )
    else:
        files = glob(
            os_path.join(dir1, '*'),
            recursive=recursive
        )
    root_dir = os_path.basename(dir1)
    h = sha256()
    for path in files:

        parts = PurePath(path).parts
        parts = parts[parts.index(root_dir):]
        if len(parts) > 1:
            parts = parts[1:]
        
        for part in parts: 
            h.update(os_path.basename(part).encode('utf8'))
        if os_path.isfile(path):
            with open(path, 'rb') as fid:
                while True:
                    data = fid.read(65536) # read stuff in 64kb chunks!
                    if not data:
                        break
                    h.update(data)
    return h.hexdigest()


def compare_dir(
    dir1: str,
    dir2: str,
    recursive: bool=False
) -> bool:
    '''Compare two directories taking account tree and file composition

    :param dir1: A first directory
    :param dir2: A second directory
    :param recursive: Check recursivly content of directory

    :type dir1: str
    :type dir2: str
    :type recursive: bool

    :return: Success or not of equality between the directories
    :rtype: bool
    '''
    return hash_dir(dir1, recursive) == hash_dir(dir2, recursive)
