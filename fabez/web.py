# -*- coding: utf-8 -*-


# used for python web world, django and tornado

from fabric.api import *
import shutil

import os


def web_fetch_app():
    """
    get current apps
    return:
    """
    current_path = local('pwd', capture=True)
    files = os.listdir(current_path)

    filters = ['web', 'config', 'docs', 'resources', 'templates', 'static']

    apps = [v for v in files if v not in filters and os.path.isdir(v) and not v.startswith('_') and not v.startswith('.')]

    return apps, current_path


def web_sync_config():
    """
    sync config.py files to web-app dirs
    :return:
    """
    apps, root = web_fetch_app()
    for v in apps:
        shutil.copy('config.py', os.path.join(root, v, 'config.py'))

    pass


def web_create_app(app_name):
    """
    create tornado style web app
    :param app_name:
    :return:
    """
    root = local('pwd', capture=True)
    current_path = os.path.join(root, app_name)

    if os.path.isdir(current_path):

        pass

    pass


def web_sync_static(clean=False):
    """
    this feature is a wrapper for  django manage.py collectstatic
    :return:
    """

    python_path = None

    pypy = local('which pypy', capture=True)
    python3 = local('which python3', capture=True)

    if pypy:
        python_path = pypy
    elif python3:
        python_path = python3
    else:
        python_path = 'python'

    cmd = '{} manage.py collectstatic'.format(python_path)

    if clean:
        cmd += ' -c'

    os.system(cmd)

    pass

