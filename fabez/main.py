# -*- coding: utf-8 -*-


# -*- coding: utf-8 -*-

from cliez.loader import ArgLoader
import os, sys, pickle

try:
    import pkg_resources
except:
    pass


def init_fabric(hosts, root, fabfile_name):
    """
    init fabfile system
    :param hosts:
    :param dir:
    :return:
    """

    dir =  os.path.join(root,'fabez')
    cabric_dir = os.path.join(root,'cabric')

    dirs = [dir,cabric_dir]

    for v in dirs:
        if os.path.exists(v) is False:
            os.makedirs(v, 0755)  # can cause OSError.
        else:
            print("Directory `%s' existed.skip init." % dir.replace(os.getcwd(), '.'))

    # create config files

    files = {
        # 'dev': os.path.join(dir, 'dev.conf'),
        'beta': os.path.join(dir, 'beta.conf'),
        'online': os.path.join(dir, 'online.conf'),
        'fabfile': fabfile_name + '.py',
        'cloud_file': os.path.join(cabric_dir, 'cloud.yaml'),
    }

    for k, f in files.items():
        if os.path.exists(f) is False:
            if k == 'beta':
                with open(f, 'w') as fh:
                    for item in hosts:
                        print>> fh, item

            elif k == 'fabfile':

                try:
                    template = pkg_resources.resource_string('fabez', 'tpl/fabfile.py')
                except:
                    template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'fabfile.py')).read()
                    pass

                with open(f, 'w') as fh:
                    print>> fh, template.replace('{0}', dir.replace(os.getcwd(), ''))

                pass
            elif k == 'cloud_file':
                try:
                    template = pkg_resources.resource_string('fabez', 'tpl/cloud.yaml')
                except:
                    template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'cloud.yaml')).read()
                    pass

                with open(f, 'w') as fh:
                    print>> fh, template.replace('{0}', dir.replace(os.getcwd(), ''))

                pass
            else:
                with open(f, 'w') as fh:
                    os.utime(f, None)

    pass


def main():
    importer = __import__

    a = ArgLoader((
        ('Useage: fabez init [host]'),
        '',
        'Arguments',
        '    host         pre-release environment host group.',
        '                     e.g:root@example.com,root1@example.com',

        'Actions',
        ('@init', 'init fabric file'),
        '',
        'Options:',
        # ('--dir-name:', 'set config directory name,default is `./config/fabez`'),
        # ('--fabfile:', 'set fabfile name,default is `fabfile`'),
        ('--debug', 'debug flag'),
        ('--help', 'print help document', '-h'),
    ))

    if a.options.get('--help'):
        print(a)
        return

    try:
        hosts = a.argv[1].split(',')
    except:
        hosts = ''

    # config_name = a.options.get('--dir-name') or 'config'
    config_name = 'config'
    # fabfile_name = a.options.get('--fabfile') or 'fabfile'
    fabfile_name = 'fabfile'


    root = os.path.join(os.getcwd(), config_name)

    if a.actions.get('init'):
        init_fabric(hosts, root, fabfile_name)
        return
    else:
        print(a)

    pass


if __name__ == '__main__':
    main()
    pass


