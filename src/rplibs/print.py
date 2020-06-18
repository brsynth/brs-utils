"""
Created on June 16 2020

@author: Joan Hérisson
"""


def print_OK(time=-1):
    sys.stdout.write("\033[0;32m") # Green
    print(" OK", end = '', flush=True)
    sys.stdout.write("\033[0;0m") # Reset
    if time!=-1: print(" (%.2fs)" % time, end = '', flush=True)
    print()

def print_FAILED():
    sys.stdout.write("\033[1;31m") # Red
    print(" Failed")
    sys.stdout.write("\033[0;0m") # Reset
    print()
