# -*- coding: utf-8 -*-

import argparse
import os

from cliez import conf
from cliez.parser import parse

from cabric import version

conf.COMPONENT_ROOT = os.path.dirname(__file__)
conf.GENERAL_ARGUMENTS = [
    (('--dir',),
     dict(nargs='?', default=os.getcwd(), help='set working directory')),
    (('--debug',), dict(action='store_true', help='open debug mode')),
    (('--verbose', '-v'), dict(action='count')),
    (('--env', '-s'), dict(nargs='?', default='beta', help='set environment')),
    (('--hosts-file',), dict(help='chose another hosts file to load')),
]
conf.EPILOG = 'You can submit issues at: https://www.github.com/nextoa/cabric'


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=conf.EPILOG,
    )

    for v in conf.GENERAL_ARGUMENTS:
        parser.add_argument(*v[0], **v[1])

    parser.add_argument('--version', action='version',
                        version='%(prog)s v{}'.format(version))

    # do nothing when no argument applied
    # parse(parser)

    parse(parser)
    pass


if __name__ == "__main__":
    main()
    pass
