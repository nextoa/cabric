# -*- coding: utf-8 -*-

from __future__ import absolute_import

import argparse
import os
import unittest

from cliez import parser


class MiniComponentTests(unittest.TestCase):
    def setUp(self):
        from cabric import main
        pass

    def test_mini(self):
        parser.parse(argparse.ArgumentParser(),
                     argv=['command', 'mini',
                           os.path.join(os.path.dirname(__file__),
                                        'resources', 'mini_input'),
                           os.path.join(os.path.dirname(__file__),
                                        'resources', 'mini_output')
                           ])
        pass

    def test_mini_extension_dry_run(self):
        parser.parse(argparse.ArgumentParser(),
                     argv=['command', 'mini',
                           os.path.join(os.path.dirname(__file__),
                                        'resources', 'mini_input'),
                           os.path.join(os.path.dirname(__file__),
                                        'resources', 'mini_output'),
                           '--dry-run',
                           '--extension',
                           '.py', '.txt'
                           ])
        pass

    def test_mini_extension(self):
        parser.parse(argparse.ArgumentParser(),
                     argv=['command', 'mini',
                           os.path.join(os.path.dirname(__file__),
                                        'resources', 'mini_input'),
                           os.path.join(os.path.dirname(__file__),
                                        'resources', 'mini_output'),
                           '--extension',
                           '.py', '.txt'
                           ])
        pass

    def test_mini_extension_prepend(self):
        parser.parse(argparse.ArgumentParser(),
                     argv=['command', 'mini',
                           os.path.join(os.path.dirname(__file__),
                                        'resources', 'mini_input'),
                           os.path.join(os.path.dirname(__file__),
                                        'resources', 'mini_output'),
                           '--extension',
                           '.py', '.txt',
                           '--debug',
                           '--prepend',
                           os.path.join(os.path.dirname(__file__),
                                        'resources', 'mini_input',
                                        'COPYRIGHT'),
                           ])
        pass

    def test_mini_extension_prepend_deploy(self):
        parser.parse(argparse.ArgumentParser(),
                     argv=['command', 'mini',
                           os.path.join(os.path.dirname(__file__),
                                        'resources', 'mini_input'),
                           os.path.join(os.path.dirname(__file__),
                                        'resources', 'mini_output'),
                           '--extension',
                           '.py', '.txt',
                           '--debug',
                           '--prepend',
                           os.path.join(os.path.dirname(__file__),
                                        'resources', 'mini_input',
                                        'COPYRIGHT'),
                           '--with-release',
                           'dream'
                           ])

    pass
