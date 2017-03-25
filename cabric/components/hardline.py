# -*- coding: utf-8 -*-

import json
import os
import subprocess

from cliez.component import Component

from cabric.utils import get_roots

try:
    from shlex import quote as shell_quote
except ImportError:
    from pipes import quote as shell_quote


class HardlineComponent(Component):
    def run(self, options):
        """
        :param options:
        :return:
        """

        package_root, _, _ = get_roots(options.dir)
        config_file = os.path.join(package_root, 'hardlines.json')

        if not os.path.exists(config_file):
            raise OSError("%s not exists" % config_file)

        try:
            hardlines = json.load(open(config_file, 'r'))
        except ValueError:
            self.error("Invalid json syntax:%s" % config_file)
            return False

        # show keys and exit
        if not options.node:
            docs = [(v, hardlines[v].get('title', '')) for v in
                    hardlines.keys()]

            self.print_message("All Hardline:\n")
            self.print_message(
                "\n".join([v[0] + "\t" + v[1] for v in docs]))

            return

        node = hardlines.get(options.node, {})

        if not node:
            self.error("Invalid node :%s" % options.node)
            return False

        workflow = [
            v for v in node.get('workflow', [])
            if v[0:3] in ('cab', 'fab') and '&' not in v and '|' not in v
            and '>' not in v and '<' not in v
            ]

        if not workflow:
            self.error("No workflow set.")
            return False

        commands = "\n".join(workflow)

        if options.preview:
            self.print_message("WorkFlow:\n")
            self.print_message(commands)
            return

        commands = "shopt -s expand_aliases\n" \
                   "source ~/.bash_profile\n" + commands

        if options.debug:
            self.print_message("commands will be execute:\n" + commands)
            pass

        subprocess.call(commands, shell=True, executable='/bin/bash')
        pass

    @classmethod
    def add_arguments(cls):
        """
        sub parser document
        """
        return [
            (('--preview',),
             dict(action='store_true', help='show task', )),
            (('node',),
             dict(nargs='?', help='which node to active', )),
        ]
        pass

    pass
