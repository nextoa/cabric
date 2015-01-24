# -*- coding: utf-8 -*-


from fabric.api import *

import os
from os.path import isfile, join


def dump_codes(root='.', end_with=None, ex_dir='.git __pycache__ .idea', ex_endswith='.pyc .DS_Store'):
    # if end_with:
    # onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f) and f.endswith('.' + end_with))]
    # else:
    # onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    # f = []
    #
    # for (dirpath, dirnames, filenames) in walk(mypath):
    # f.extend(filenames)
    # break
    #
    # print(f)


    exclude_dir = ex_dir.split(' ')
    exclude_files = ex_endswith.split(' ')

    for path, subdirs, files in os.walk(root):

        for d in exclude_dir:
            if path.find(d + '/') > -1 or path == root + '/' + d:
                break
        else:
            for name in files:
                for f in exclude_files:
                    if name.endswith(f):
                        break
                else:
                    real_path = os.path.join(path, name)
                    print("\n\n===================" + real_path + "===================\n\n")
                    with open(real_path, 'r') as fh:
                        print(fh.read())

    pass

