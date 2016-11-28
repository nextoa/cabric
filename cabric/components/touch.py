# -*- coding: utf-8 -*-

import os
from cliez.components.create import CreateComponent


class TouchComponent(CreateComponent):
    """
    alias for cliez create component
    """
    exclude_global_option = True

    @classmethod
    def add_arguments(cls):
        """
        create project form repo.support github,bitbucket and local repo.

        By default,cabric search repo orders is:

            - github
            - bitbucket
            - local


        if user define `--local` option. search local path first.

        if user define `--bitbucket`, search bitbucket first,then search github.


        ..note::

            * currently,we only support ssh mode when use bitbucket *

        """
        return [
            (('repo',), dict(help='repo path.')),
            (('name',), dict(nargs='?', default='', help='project name.')),
            (('--local',), dict(action='store_true', help='try load repo local path.')),
            (('--bitbucket',), dict(action='store_true', help='search bitbucket first.')),

            (('--dir',), dict(nargs='?', default=os.getcwd(), help='set working directory')),
            (('--debug',), dict(action='store_true', help='open debug mode')),
            (('--dry-run',), dict(action='store_true', help='print command instead execute it')),
            (('--verbose', '-v'), dict(action='count')),
        ]

    pass
