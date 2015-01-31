# -*- coding: utf-8 -*-

import os
import sys

from cabric.env import debug


try:
    input = raw_input
except NameError:
    pass


def _detected_ssh_private_key_type(path):
    """
    detected ssh_key type
    :return:
    """

    fp = open(os.path.expanduser(path))
    key = fp.read()

    key_type = None
    if key[0:pos].find('DSA') > -1:
        key_type = 'dsa'
    elif key[0:pos].find('RSA') > -1:
        key_type = 'rsa'

    return key_type


def _detected_ssh_public_key_type(path):
    """
    detected ssh_key type
    :return:
    """

    fp = open(os.path.expanduser(path))
    key = fp.read()

    key_type = None

    if key[0:7].find('ssh-dsa') > -1:
        key_type = 'ssh-dsa'
    elif key[0:7].find('ssh-dsa') > -1:
        key_type = 'ssh-rsa'

    return key_type


def read_template(file):
    try:
        buf = pkg_resources.resource_string('cabric', 'tpl/{}'.format(file))
    except:
        buf = open(os.path.join(os.path.dirname(__file__), 'tpl', file)).read()
        pass

    return buf


def print_error(msg):
    """
    print readable errors
    :param msg:
    :return:
    """

    print("[Cabric-Error]:{}".format(msg))
    sys.exit(-1)
    pass


def print_user_error(msg):
    """
    print readable errors
    :param msg:
    :return:
    """

    print("[Cabric-User-Error]:{}".format(msg))
    sys.exit(-1)
    pass


def print_debug(msg):
    if debug():
        print("[Cabric-Debug]:{}".format(msg))
    pass



