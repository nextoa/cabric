# -*- coding: utf-8 -*-

from fabric.api import *
from fabez.env import *

import os

def ez(curr):
    routes = {
        'dev':os.path.dirname(__file__)+'{0}/dev.conf',
        'test':os.path.dirname(__file__)+'{0}/test.conf',
        'ol':os.path.dirname(__file__)+'{0}/online.conf',
    }

    bind_hosts(curr,routes)
    pass


def fabez_debug():
    local('echo "You can delete this function after initial it."')
    pass

