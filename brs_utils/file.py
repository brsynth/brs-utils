"""
Created on June 16 2020

@author: Joan Hérisson
"""

from os import makedirs
from requests import get as r_get
from tempfile import NamedTemporaryFile
from tarfile import open as tf_open


def download(url, file):
    r = r_get(url)
    open(file, 'wb').write(r.content)

def extract_gz(file, path):
    print(path)
    makedirs(path, exist_ok=True)
    tar = tf_open(file, mode="r:gz")
    tar.extractall(path)
    tar.close()

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
