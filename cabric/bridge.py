# -*- coding: utf-8 -*-

"""
Most of them copy form `cabric.main` directly.

`import cabric.main` will make script work not right.

some error like:

..code-block::

    Usage: fab [options] <command>
    [:arg1,arg2=val2,host=foo,hosts='h1;h2',...] ...

    main.py: error: no such option: --skip-enable-services

"""

import os
from optparse import OptionParser

from fabric import state
from fabric.state import env_options


def parse_options(args=[]):
    """
    Handle command-line options with optparse.OptionParser.

    Return list of arguments, largely for use in `parse_arguments`.
    """
    #
    # Initialize
    #

    parser = OptionParser(
        usage=("cabric bridge [options] <command>"
               "[:arg1,arg2=val2,host=foo,hosts='h1;h2',...] ..."))

    #
    # Define options that don't become `env` vars (typically ones which cause
    # Fabric to do something other than its normal execution, such as
    # --version)
    #

    # Display info about a specific command
    parser.add_option('-d', '--display',
                      metavar='NAME',
                      help="print detailed info about command NAME"
                      )

    # Control behavior of --list
    LIST_FORMAT_OPTIONS = ('short', 'normal', 'nested')
    parser.add_option('-F', '--list-format',
                      choices=LIST_FORMAT_OPTIONS,
                      default='normal',
                      metavar='FORMAT',
                      help="formats --list, choices: %s" % ", ".join(
                          LIST_FORMAT_OPTIONS)
                      )

    parser.add_option('-I', '--initial-password-prompt',
                      action='store_true',
                      default=False,
                      help="Force password prompt up-front"
                      )

    parser.add_option('--initial-sudo-password-prompt',
                      action='store_true',
                      default=False,
                      help="Force sudo password prompt up-front"
                      )

    # List Fab commands found in loaded fabfiles/source files
    parser.add_option('-l', '--list',
                      action='store_true',
                      dest='list_commands',
                      default=False,
                      help="print list of possible commands and exit"
                      )

    # Allow setting of arbitrary env vars at runtime.
    parser.add_option('--set',
                      metavar="KEY=VALUE,...",
                      dest='env_settings',
                      default="",
                      help="comma separated KEY=VALUE pairs"
                           " to set Fab env vars"
                      )

    # Like --list, but text processing friendly
    parser.add_option('--shortlist',
                      action='store_true',
                      dest='shortlist',
                      default=False,
                      help="alias for -F short --list"
                      )

    # Version number (optparse gives you --version but we have to do it
    # ourselves to get -V too. sigh)
    parser.add_option('-V', '--version',
                      action='store_true',
                      dest='show_version',
                      default=False,
                      help="show program's version number and exit"
                      )

    #
    # Add in options which are also destined to show up as `env` vars.
    #

    for option in env_options:
        parser.add_option(option)

    #
    # Finalize
    #

    # Return three-tuple of parser + the output from parse_args (opt obj, args)
    # Hack:make fab not accept any argument.
    opts, args = parser.parse_args(args=args)
    return parser, opts, args


def update_output_levels(show, hide):
    """
    Update state.output values as per given comma-separated list of key names.

    For example, ``update_output_levels(show='debug,warnings')`` is
    functionally equivalent to ``state.output['debug'] = True ;
    state.output['warnings'] = True``. Conversely, anything given to ``hide``
    sets the values to ``False``.
    """
    if show:
        for key in show.split(','):
            state.output[key] = True
    if hide:
        for key in hide.split(','):
            state.output[key] = False


def load_settings(path):
    """
    Take given file path and return dictionary of any key=value pairs found.

    Usage docs are in sites/docs/usage/fab.rst, in "Settings files."
    """
    if os.path.exists(path):
        comments = (lambda s: s) and not s.startswith("#")
        settings = filter(comments, open(path, 'r'))
        return dict((k.strip(), v.strip()) for k, _, v in
                    [s.partition('=') for s in settings])
    # Handle nonexistent or empty settings file
    return {}
