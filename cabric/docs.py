# -*- coding: utf-8 -*-



from fabric.api import *

from cabric.cmd import cmd_git


def docs_server():
    # cmd_git('/tmp','')

    pass


def docs_bootstrap(server=False, init=False):

    with  lcd('~/GDrive/Manuals/framework.ez.co/bootstrap'):
        if init:
            local('git remote add upstream https://github.com/twbs/bootstrap.git')
            pass

        if server:
            local('sudo gem install rouge')
            local('sudo gem install jekyll')

        local('sudo chown -Rfv breezekay .')
        local('git fetch upstream')
        local('git checkout master')
        local('git merge upstream/master')
        local('git push')


pass



# def elasticsearch_doc():
#
# with lcd('~/Codes/ez/servers.ez.co/elasticsearch-doc'):
#         # local('./build_docs.pl --doc README.asciidoc --open')
#         local('./build_docs.pl --doc ../elasticsearch/docs/reference/index.asciidoc  --toc')
#         local('cp -rfv html_docs ~/Manual/server/elasticsearch')
#         local('rm -rf html_docs')
#
#         # local('./build_docs.pl --doc ../elasticsearch/docs/python/index.asciidoc  --toc')
#         # local('cp -rfv html_docs ~/Manual/python/elasticsearch-style')
#         # local('rm -rf html_docs')
#
#
#
#     pass