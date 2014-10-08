# -*- coding: utf-8 -*-

from fabric.api import *
from fabez.env import *
from fabez.cmd import *
from fabez.server import *

import os

def ez(curr):
    routes = {
        'dev':os.path.dirname(__file__)+'/config/fabez/dev.conf',
        'test':os.path.dirname(__file__)+'/config/fabez/test.conf',
        'ol':os.path.dirname(__file__)+'/config/fabez/online.conf',
    }

    bind_hosts(curr,routes)
    pass


def fabez_debug():
    local('echo "This message is from ."')
    pass



def install(pubkey=None):
    server_gitolite(pubkey)
    pass
