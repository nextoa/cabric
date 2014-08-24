# -*- coding: utf-8 -*-


from fabez.utils import utils_baselib
from fabez.cmd import cmd_git



# def python(pip_index_url=None, user='webuser'):
def lang_python(branch='master'):
    '''
    install python. include python,setuptools,pip and supervisord
    :param pip_index_url:proxy url
    '''

    utils_baselib()
    cmd_git('/tmp/python', 'https://github.com/kbonez/python.git',branch)
    # cmd_git('/tmp/pip', 'https://github.com/kbonez/pip.git')
    # cmd_git('/tmp/setuptools', 'https://github.com/kbonez/setuptools.git')

    with cd('/tmp/python'):
        run('./configure')
        run('make && make install')


    pass

    # setup_py('/tmp/setuptools', '/usr/local/bin/python')
    # setup_py('/tmp/pip', '/usr/local/bin/python')
    #
    # if pip_index_url:
    #     with settings(warn_only=True):
    #         if run('test -d ~/.pip').failed:
    #             run('mkdir ~/.pip')
    #         run(
    #             "grep 'index_url' ~/.pip/pip.conf || echo '[global]\nindex_url = %s' >> ~/.pip/pip.conf" % pip_index_url)
    #
    # supervisor(user)