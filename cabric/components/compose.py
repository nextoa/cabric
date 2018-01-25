# -*- coding: utf-8 -*-

from cliez.component import Component
from fabric.context_managers import shell_env
from fabric.operations import local
from fabric.state import env

from cabric.utils import (get_roots, bind_hosts, execute, run)

try:
    from shlex import quote as shell_quote
except ImportError:
    from pipes import quote as shell_quote


class ComposeComponent(Component):

    def run(self, options):
        """
        ..note::
            unstable feature.

            current we use rsync instead fabric put.
            but rsync may cause permission errors.

        :param options:
        :return:
        """

        package_root, config_root, fabric_root = get_roots(options.dir)

        bind_hosts(fabric_root, options.env, options.parallel,
                   options.hosts_file)

        self.warn("Please confirm you set envrionment")

        def deploy():
            docker_host = 'tcp://%s:%d' % (env['host'], options.port)
            with shell_env(DOCKER_TLS_VERIFY="1",
                           DOCKER_HOST=docker_host):
                local('docker-compose %s' % options.extra)
                pass
            pass

        execute([deploy])
        pass

    @classmethod
    def add_arguments(cls):
        """
        sub parser document
        """
        return [
            (('extra',), dict(help='docker compose arguments')),

            (('--parallel', '-P'), dict(action='store_true',
                                        help='default to parallel execution'
                                             ' method', )),
            (('--port',),
             dict(type=int, default='2376',
                  help='default TLS port is 2376', )),
        ]

    pass
