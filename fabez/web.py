# -*- coding: utf-8 -*-


# used for python web world


from fabric.api import *
import shutil

def web_fetch_app():
    """
    get current apps, exclude web,docs,resources,config,template,static dirs
    :return:
    """
    current_path = local('pwd', capture=True)
    files = os.listdir(current_path)

    filters = ['web', 'config', 'docs', 'resources', 'templates', 'static']

    apps = [v for v in files if v not in filters and os.path.isdir(v) and not v.startswith('_') and not v.startswith('.')]

    return apps, current_path

def web_sync_config():
    apps, root = web_fetch_app()
    for v in apps:
        shutil.copy('config.py', os.path.join(root, v, 'config.py'))

    pass


def web_sync_static():
    """
    @todo
    this feature like django's  manage.py collectstatic
    but works for all packages
    :return:
    """

    pass

