# -*- coding: utf-8 -*-
import sys

from distutils.core import setup

from setuptools import find_packages

import cabric

setup(
    name='cabric',
    version=cabric.version,
    packages=find_packages(exclude=["tests"]),
    url='https://github.com/nextoa/cabric',
    download_url='https://github.com/nextoa/cabric/tarball/master',
    license='http://opensource.org/licenses/MIT',
    install_requires=[
        'requests',
        'gitpython',
        'pycrypto',
        'fabric' if sys.version_info[0] < 3 else 'fabric3',
        'cliez==2.0.12',
    ],
    author='WANG WENPEI',
    author_email='wangwenpei@nextoa.com',
    description='Cabric,a deploy tool for CentOS,based on Fabric.',
    keywords='fabric,cabric',
    entry_points={
        'console_scripts': [
            'cab = cabric.main:main',
        ]
    },

)
