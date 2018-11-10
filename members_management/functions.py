# functions.py
# Python3
# author : Fafadji GNOFAME
# Date : 09 mars 2018
# Version : 1.0
# Description :  fonctions diverses

import os, errno

def create_path_n_file_if_needed(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise        