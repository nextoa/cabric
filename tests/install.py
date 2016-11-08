# -*- coding: utf-8 -*-

import os
import unittest
import argparse
from cliez import parser


class InstallComponentTests(unittest.TestCase):
    def setUp(self):
        from cabric import main
        pass

    def test_invalid_env(self):
        with self.assertRaises(OSError):
            parser.parse(argparse.ArgumentParser(), argv=['command', 'install',
                                                          '--debug',
                                                          '--env', 'invalid-env',
                                                          '--dir', __file__.rsplit('/', 2)[0]])
        pass

    def test_ok(self):
        parser.parse(argparse.ArgumentParser(), argv=['command', 'install',
                                                      '--debug',
                                                      '--env', 'beta',
                                                      '--dir', __file__.rsplit('/', 2)[0]])
        pass

    def test_dev(self):
        parser.parse(argparse.ArgumentParser(), argv=['command', 'install',
                                                      '--debug',
                                                      '--env', 'dev',
                                                      '--dir', __file__.rsplit('/', 2)[0]])
        pass

    pass
