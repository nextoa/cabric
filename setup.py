# -*- coding: utf-8 -*-

from distutils.core import setup
from setuptools import find_packages


import fabez

setup(
    name='fabez',
    version=fabez.version,
    packages=['fabez'],
    url='https://github.com/kbonez/fabez',
    download_url='https://github.com/kbonez/fabez/tarball/master',
    license='http://opensource.org/licenses/MIT',
    install_requires=[
        'fabric',
        'cliez',
        'qingcloud-sdk'
    ],
    author='Breeze.Kay',
    author_email='wangwenpei@kbonez.com',
    description='fabric helper tools',
    keywords='fabric,fabez,ez',
    package_data={
        'fabez': ['tpl/*.*']
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'fabez = fabez.main:main'
        ]
    },

)

