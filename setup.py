# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

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
        'cliez'
    ],
    author='Breeze.Kay',
    author_email='wangwenpei@kbonez.com',
    description='fabric helper tools',
    keywords='fabric,fabez,ez',
    include_package_data=True,
    package_data={
        'fabez': ['tpl/*.conf','tpl/*.py','tpl/*.repo']
    },
    entry_points={
        'console_scripts': [
            'fabez = fabez.main:main'
        ]
    },

)

