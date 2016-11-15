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

    def test_only_pkg_centos(self):
        parser.parse(argparse.ArgumentParser(), argv=['command', 'install',
                                                      '--debug',
                                                      '--skip-pyenv',
                                                      '--skip-node',
                                                      '--env', 'beta',
                                                      '--dir', __file__.rsplit('/', 2)[0]])
        pass

    def test_only_pkg_remote_mac(self):
        parser.parse(argparse.ArgumentParser(), argv=['command', 'install',
                                                      '--debug',
                                                      '--skip-pyenv',
                                                      '--skip-node',
                                                      '--env', 'beta2',
                                                      '--dir', __file__.rsplit('/', 2)[0]])
        pass

    def test_only_pkg_local_mac(self):
        parser.parse(argparse.ArgumentParser(), argv=['command', 'install',
                                                      '--debug',
                                                      '--skip-pyenv',
                                                      '--skip-node',
                                                      '--env', 'dev',
                                                      '--dir', __file__.rsplit('/', 2)[0]])

    def test_only_pyenv_centos(self):
        parser.parse(argparse.ArgumentParser(), argv=['command', 'install',
                                                      '--debug',
                                                      '--skip-pkg',
                                                      '--skip-node',
                                                      '--env', 'beta',
                                                      '--dir', __file__.rsplit('/', 2)[0]])
        pass

    def test_only_pyenv_remote_mac(self):
        parser.parse(argparse.ArgumentParser(), argv=['command', 'install',
                                                      '--debug',
                                                      '--skip-pkg',
                                                      '--skip-node',
                                                      '--env', 'beta2',
                                                      '--dir', __file__.rsplit('/', 2)[0]])
        pass

    def test_only_pyenv_local_mac(self):
        parser.parse(argparse.ArgumentParser(), argv=['command', 'install',
                                                      '--debug',
                                                      '--skip-pkg',
                                                      '--skip-node',
                                                      '--env', 'dev',
                                                      '--dir', __file__.rsplit('/', 2)[0]])

    def test_only_node_centos(self):
        parser.parse(argparse.ArgumentParser(), argv=['command', 'install',
                                                      '--debug',
                                                      '--skip-pkg',
                                                      '--skip-pyenv',
                                                      '--env', 'beta',
                                                      '--dir', __file__.rsplit('/', 2)[0]])
        pass

    def test_only_node_remote_mac(self):
        parser.parse(argparse.ArgumentParser(), argv=['command', 'install',
                                                      '--debug',
                                                      '--skip-pkg',
                                                      '--skip-pyenv',
                                                      '--env', 'beta2',
                                                      '--dir', __file__.rsplit('/', 2)[0]])
        pass

    def test_only_node_local_mac(self):
        parser.parse(argparse.ArgumentParser(), argv=['command', 'install',
                                                      '--debug',
                                                      '--skip-pkg',
                                                      '--skip-pyenv',
                                                      '--env', 'dev',
                                                      '--dir', __file__.rsplit('/', 2)[0]])

        pass

    pass
