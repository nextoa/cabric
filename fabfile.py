# -*- coding: utf-8 -*-

from fabric.api import *

import os


def hello():
    run('echo hello')
    pass


def lol():
    local('echo lol....')
    pass
