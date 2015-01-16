# -*- coding: utf-8 -*-

import os


def _detected_ssh_private_key_type(path):
    """
    detected ssh_key type
    :return:
    """

    fp = open(os.path.expanduser(path))
    key = fp.read()
    pos = key.find("\n")

    key_type = None
    if key[0:pos].find('DSA') > -1:
        key_type = 'dsa'
    elif key[0:pos].find('RSA') > -1:
        key_type = 'rsa'

    pass



def _detected_ssh_public_key_type(path):
    """
    detected ssh_key type
    :return:
    """

    fp = open(os.path.expanduser(path))
    key = fp.read()
    pos = key.find("\n")

    key_type = None

    if key[0:7].find('ssh-dsa') > -1:
        key_type = 'ssh-dsa'
    elif key[0:7].find('ssh-dsa') > -1:
        key_type = 'ssh-rsa'
    pass

