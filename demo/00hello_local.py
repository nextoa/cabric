# -*- coding: utf-8 -*-

from fabric.api import *



def hello_local():
    local('echo "hello fabric,I am local host."')
    pass




def hello_local2():

    "this is comment"
    pass