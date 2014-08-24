# -*- coding: utf-8 -*-

from fabric.api import *
import os

env.use_ssh_config = True
env.hosts=['root@vpn.ez.co']

def hello_remote():
    run('echo "hello fabric, I am remote host."')

    # demo2:get return value


    # demo3:use return value

    pass



