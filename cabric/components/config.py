# -*- coding: utf-8 -*-

import os
import json
from cliez.component import Component
from cabric.utils import get_roots, mirror_put, run, bind_hosts, execute, get_platform, run_block

try:
    from shlex import quote as shell_quote
except ImportError:
    from pipes import quote as shell_quote


class ConfigComponent(Component):
    def enable_services(self, services):
        """
        :param list services: service list
        :return:
        """

        if get_platform() == 'centos':
            run('systemctl enable %s' % ' '.join(services))
        else:
            self.warn("not support platform.no services enabled.")
        pass

    def reload(self, reloads, all_services):
        if all_services and reloads:
            services = [v for v in reloads if v in all_services]
            run('systemctl reload %s' % ' '.join(services))
        pass

    def restart(self, restarts, all_services):

        if all_services and restarts:
            services = [v for v in restarts if v in all_services]
            if services:
                run('systemctl restart %s' % ' '.join(services))
            else:
                self.warn("restart progress actived,but no restart service found.")
        pass

    def run(self, options):
        """
        plan feature

            use rsync instead fabric put.
            but rsync will may cause permission errors.
            we should fix this.

        :param options:
        :return:
        """

        package_root, config_root, fabric_root = get_roots(options.dir)
        bind_hosts(fabric_root, options.env)

        # try upload repo config if it can recognize
        using_config = os.path.join(package_root, options.env)
        stage_config = os.path.join(config_root, options.env)

        if not options.skip_upload:
            mirror_put(stage_config, '/')

        try:
            env_config = json.load(open(os.path.join(using_config, 'env.json'), 'r'))
        except ValueError:
            self.error("Invalid json syntax:%s" % os.path.join(using_config, 'env.json'))

        services = env_config.get('services', [])

        command_list = []
        if not options.skip_enable_services:
            command_list.append(lambda: self.enable_services(services))

        if options.reload:
            command_list.append(lambda: self.reload(options.reload, services))
            pass

        if options.restart:
            command_list.append(lambda: self.restart(options.restart, services))
            pass

        execute(command_list)
        pass

    @classmethod
    def add_arguments(cls):
        """
        sub parser document
        """
        return [
            (('--skip-enable-services',), dict(action='store_true', help='skip enable system services', )),
            (('--skip-upload',), dict(action='store_true', help='skip upload config files', )),
            (('--reload',), dict(nargs='+', help='set reload service', )),
            (('--restart',), dict(nargs='+', help='set restart service', )),
        ]

    pass
