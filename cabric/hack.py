# -*- coding: utf-8 -*-

import os

from fabric.context_managers import env
from fabric.decorators import task

from cabric.utils import parse_hosts


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
    env.hosts, env_host_names = parse_hosts(env_file)
    pass
