# -*- coding: utf-8 -*-


# -*- coding: utf-8 -*-

from cliez.loader import ArgLoader
import os, sys, pickle
# import pkg_resources


def init_fabric(hosts, dir, fabfile_name):
    """
    init fabfile system
    :param hosts:
    :param dir:
    :return:
    """

    if os.path.exists(dir) is False:
        os.makedirs(dir, 0755)  # can cause OSError.
    else:
        print "Directory `%s' existed.skip init." % dir.replace(os.getcwd(), '.')


    # create config files

    files = {
        'dev': os.path.join(dir, 'dev.conf'),
        'test': os.path.join(dir, 'test.conf'),
        'online': os.path.join(dir, 'online.conf'),
        'fabfile': fabfile_name + '.py'
    }

    for k, f in files.items():
        if os.path.exists(f) is False:
            if k == 'dev':
                with open(f, 'w') as fh:
                    for item in hosts:
                        print>> fh, item

            if k == 'fabfile':

                template = open(os.path.join(os.path.dirname(__file__), 'tpl', 'fabfile.py')).read()
                # template = pkg_resources.resource_string('fabez', 'tpl\fabfile.py')

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
        ('Useage: fabez init [options] host'),
        '',
        'Arguments',
        '    host         develop environment host group.',
        '                     e.g:root@example.com,root1@example.com',

        'Actions',
        ('@init', 'init fabric file'),
        '',
        'Options:',
        ('--dir-name:', 'set config directory name,default is `./config/fabez`'),
        ('--fabfile:', 'set fabfile name,default is `fabfile`'),
        ('--debug', 'debug flag'),
        ('--help', 'print help document', '-h'),
    ))

    if a.options.get('--help'):
        print a
        return

    try:
        hosts = a.argv[1].split(',')
    except:
        print "Please set your host group or use `--help` to see help manual."
        sys.exit(-1)
        pass

    config_name = a.options.get('--dir-name') or 'config'
    fabfile_name = a.option.get('--fabfile') or 'fabfile'

    config_path = os.path.join(os.getcwd(), config_name, 'fabez')

    if a.actions.get('init'):
        init_fabric(hosts, config_path, fabfile_name)
        return

    pass


if __name__ == '__main__':
    main()
    pass


