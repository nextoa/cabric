# -*- coding: utf-8 -*-

from fabric.api import *



def hello_local():
    local('echo "hello fabric,I am local host."')
    pass


