# -*- coding: utf-8 -*-

import os
from cabric.utils import parse_hosts
from fabric.decorators import task
from fabric.context_managers import env


@task
def ez(curr):
    """

    :param curr: which env to use

      ..note::
        if you use `ol` as value, cabric will translate `online`


    :return:
    """

    current_path = './config/fabric'
    curr = 'online' if curr == 'ol' else curr
    env_file = os.path.join(current_path, curr + '.conf')
    env.use_ssh_config = True
    env.hosts = parse_hosts(env_file)
    pass
