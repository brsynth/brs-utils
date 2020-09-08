"""
Created on June 16 2020

@author: Joan Hérisson
"""

from os       import makedirs
from os       import path as os_path
from requests import get         as r_get
from tempfile import NamedTemporaryFile
from tarfile  import open        as tf_open
from gzip     import open        as gz_open
from gzip     import decompress  as gz_decompress
from shutil   import copyfileobj as shutil_copyfileobj


def download(url, file):
    r = r_get(url)
    open(file, 'wb').write(r.content)

def extract_tar_gz(file, path):
    makedirs(path, exist_ok=True)
    tar = tf_open(file, mode='r:gz')
    tar.extractall(path)
    tar.close()

def extract_gz_to_string(file):
    gz = gz_open(file, mode='rb')
    return gz.read().decode()

def extract_gz(file, path):
    outfile = path+'/'+os_path.basename(file[:-3])
    makedirs(path, exist_ok=True)
    with gz_open(file, 'rb') as f_in:
        with open(outfile, 'wb') as f_out:
            shutil_copyfileobj(f_in, f_out)
    return outfile

def download_and_extract_tar_gz(url, path):
    with NamedTemporaryFile() as tempf:
        download(url, tempf.name)
        extract_tar_gz(tempf.name, path)

def download_and_extract_gz(url, path):
    with NamedTemporaryFile() as tempf:
        download(url, tempf.name)
        extract_gz(tempf.name, path)

def file_length(filename):
    with open(filename, 'rb') as f:
        n = sum(1 for line in f)
    return n

from ast import literal_eval
def read_dict(filename):
    d = {}
    with open(filename, 'r') as f:
        s = f.read()
        d = literal_eval(s)
    return d
