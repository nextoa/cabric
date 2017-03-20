# -*- coding: utf-8 -*-

import argparse
import os
import unittest

import mock
from cliez import parser

try:
    input = raw_input
    mock_input = '__builtin__.raw_input'
except NameError:
    mock_input = 'builtins.input'
    pass


class DeployComponentTests(unittest.TestCase):
    def clean_keys(self):
        keys = {
            'beta_private': os.path.expanduser(
                '~/.ssh/.deploies/nextoa/cabric.rsa'),
            'beta_pub': os.path.expanduser(
                '~/.ssh/.deploies/nextoa/cabric.rsa'),
            'beta2_private': os.path.expanduser('~/.ssh/.deploies/cabric.rsa'),
            'beta2_pub': os.path.expanduser('~/.ssh/.deploies/cabric.rsa'),
        }

        for k in keys:
            if os.path.exists(k):
                os.unlink(k)
            pass

        self.test_keys = keys
        pass

    def setUp(self):
        self.clean_keys()
        pass

    def tearDown(self):
        self.clean_keys()
        pass

    def test_invalid_env(self):
        with self.assertRaises(OSError):
            parser.parse(argparse.ArgumentParser(), argv=['command', 'deploy',
                                                          '--debug',
                                                          '--env',
                                                          'invalid-env',
                                                          '--dir',
                                                          __file__.rsplit('/',
                                                                          2)[
                                                              0]])
        pass

    def test_only_upload_key(self):
        """
        ..note::
            for safety reason, we only use github token
             test github work progress.
            so make sure your token is valid.

        ..todo::
            this feature doesn't test yet.

        :return:
        """

        with mock.patch(mock_input, side_effect=["\n", "\n"]):
            parser.parse(argparse.ArgumentParser(),
                         argv=['command', 'deploy',
                               '--debug',
                               '--env', 'beta',
                               '--with-deploy-key',
                               '--fresh-new',
                               '--skip-requirements',
                               '--skip-compile-templates',
                               '--skip-upload-resources',
                               '--dir',
                               __file__.rsplit('/',
                                               2)[
                                   0]])
            pass

        pass

    def test_only_static(self):
        """
        ..note::
            for safety reason, we only use github token
             test github work progress.
            so make sure your token is valid.

        ..todo::
            this feature doesn't test yet.

        :return:
        """

        # os.chdir(os.path.join(__file__.rsplit('/', 3)[0], 'dream'))

        parser.parse(argparse.ArgumentParser(),
                     argv=['command', 'deploy',
                           '--debug',
                           '--env', 'beta',
                           '--skip-source-code',
                           '--skip-requirements',
                           '--skip-compile-templates',
                           '--dir',
                           __file__.rsplit('/', 2)[
                               0]])

        pass

    pass
