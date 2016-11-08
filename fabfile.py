# -*- coding: utf-8 -*-

from fabric.api import *

import os

@hosts(['root@115.159.225.232'])
def hello():
    run('echo hello')
    pass


def lol():
    local('echo lol....')
    pass
