# -*- coding: utf-8 -*-

import os
import unittest
import argparse
from cliez import parser


class ConfigComponentTests(unittest.TestCase):
    def setUp(self):
        from cabric import main
        pass

    def test_invalid_env(self):
        with self.assertRaises(OSError):
            parser.parse(argparse.ArgumentParser(), argv=['command', 'config',
                                                          '--debug',
                                                          '--env', 'invalid-env',
                                                          '--dir', __file__.rsplit('/', 2)[0]])
        pass

    def test_on_centos(self):
        parser.parse(argparse.ArgumentParser(), argv=['command', 'config',
                                                      '--debug',
                                                      '--env', 'beta',
                                                      '--dir', __file__.rsplit('/', 2)[0]])
        pass

    def test_only_enable(self):
        parser.parse(argparse.ArgumentParser(), argv=['command', 'config',
                                                      '--debug',
                                                      '--env', 'beta',
                                                      '--skip-upload',
                                                      '--dir', __file__.rsplit('/', 2)[0]])
        pass

    def test_only_restart(self):
        parser.parse(argparse.ArgumentParser(), argv=['command', 'config',
                                                      '--debug',
                                                      '--env', 'beta',
                                                      '--skip-enable-services',
                                                      '--skip-upload',
                                                      '--restart', 'nginx','redis',
                                                      '--dir', __file__.rsplit('/', 2)[0]])
        pass

    pass
