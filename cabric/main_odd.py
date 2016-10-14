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
    :param fabric_dir:
    :return:
    """

    fabric_dir = os.path.join(root,'fabric')
    cabric_dir = os.path.join(root,'cabric')

    dirs = [fabric_dir, cabric_dir]            

    for v in dirs:
        if os.path.exists(v) is False:
            os.makedirs(v, 0755)  # can cause OSError.
        else:
            print("Directory `%s' existed.skip init." % v.replace(os.getcwd(), '.'))

    # create config files

    files = {
        # 'dev': os.path.join(fabric_dir, 'dev.conf'),
        'beta': os.path.join(fabric_dir, 'beta.conf'),
        'online': os.path.join(fabric_dir, 'online.conf'),
        'fabfile': fabfile_name + '.py',
        'cloud_file': os.path.join(cabric_dir, 'cloud.conf'),
    }

    for k, f in files.items():
        if os.path.exists(f) is False:
            if k == 'beta':
                with open(f, 'w') as fh:
                    for item in hosts:
                        print>> fh, item

            elif k == 'fabfile':

                try:
                    template = pkg_resources.resource_string('cabric', 'tpl/fabfile.py')
                except:
                    template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'fabfile.py')).read()
                    pass

                with open(f, 'w') as fh:
                    print>> fh, template.replace('{0}', fabric_dir.replace(os.getcwd(), ''))

                pass
            elif k == 'cloud_file':
                try:
                    template = pkg_resources.resource_string('cabric', 'tpl/cloud.conf')
                except:
                    template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'cloud.conf')).read()
                    pass

                with open(f, 'w') as fh:
                    print>> fh, template.replace('{0}', fabric_dir.replace(os.getcwd(), ''))

                pass
            else:
                with open(f, 'w') as fh:
                    os.utime(f, None)

    pass


def main():
    importer = __import__

    a = ArgLoader((
        ('Useage: cabric init [host]'),
        '',
        'Arguments',
        '    host         pre-release environment host group.',
        '                     e.g:root@example.com,root1@example.com',

        'Actions',
        ('@init', 'init fabric file'),
        '',
        'Options:',
        # ('--dir-name:', 'set config directory name,default is `./config/cabric`'),
        # ('--fabfile:', 'set fabfile name,default is `fabfile`'),
        ('--debug', 'debug flag'),
        ('--help', 'print help document', '-h'),
    ))

    if a.options.get('--help'):
        print(a)
        return

    try:

        if a.argv[1].find('@') == -1:
            print("host format is invalid. e.g: root@example.com")
            return -1
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


