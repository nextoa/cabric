# -*- coding: utf-8 -*-


# used for python web world, django and tornado

from fabric.api import *
from cabric.lib import read_template
import shutil

import os
import re


def web_fetch_app():
    """
    get current apps
    return:
    """
    current_path = os.getcwd()
    files = os.listdir(current_path)

    filters = ['web', 'config', 'docs', 'resources', 'templates', 'static', 'sketch']

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
    root = os.getcwd()
    current_path = os.path.join(root, app_name)

    # limit for file
    if os.path.isfile(current_path):
        raise Exception("{} is a file,can't create app,please set another name or delete it.".format(app_name))

    # create dir when not exist
    if not os.path.exists(current_path):
        os.mkdir(current_path, mode=0755)

    static_path = os.path.join(current_path, 'static')
    template_path = os.path.join(current_path, 'templates')
    # create dir
    for v in [static_path, template_path]:
        if not os.path.exists(v):
            os.mkdir(v, mode=0755)

    tpls = ['web/app.py', 'web/wsgi.py']

    for tpl in tpls:
        buf = read_template(tpl)

        buf = buf.replace('Demo', app_name.capitalize()).replace('demo', app_name)
        file_path = os.path.join(current_path, os.path.basename(tpl))

        with open(file_path, 'w') as fh:
            print >> fh, buf

    safe_tpls = ['web/settings.py', 'web/config.py', 'web/handlers.py', 'web/__init__.py', 'web/test.py']
    for tpl in safe_tpls:
        file_path = os.path.join(current_path, os.path.basename(tpl))
        if not os.path.exists(file_path):
            buf = read_template(tpl)

            buf = buf.replace('Demo', app_name.capitalize()).replace('demo', app_name)
            with open(file_path, 'w') as fh:
                print >> fh, buf

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

    cmd = '{} manage.py collectstatic  --noinput'.format(python_path)

    if clean:
        cmd += ' -c'

    os.system(cmd)

    pass


def web_parse_webapp(name):
    """
    convert html to ios html

    css and js file must be use double-quote should prefix with "static/"

    image path in css file should be same as css path

    :param name:
    :return:
    """

    file_path = os.path.join(os.getcwd(), name + '.tt')

    write_path = os.path.join(os.getcwd(), name + '.html')

    if not os.path.exists(file_path):
        raise IOError("File not found.")
    else:
        with open(file_path, 'r') as h:
            buf = h.read()

        buf = buf.replace(' href="static/css/', ' href="').replace(' src="static/js/', ' src="')

        with open(write_path, 'w') as fh:
            print >> fh, buf


pass
