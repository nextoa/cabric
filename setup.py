# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='fabez',
    version='0.2.0',
    packages=['fabez'],
    url='https://github.com/kbonez/fabez',
    download_url='https://github.com/kbonez/fabez/tarball/master',
    license='http://opensource.org/licenses/MIT',
    install_requires=[
        'fabric',
        'tornadoez',
        'requests',
        'github3.py',
    ],
    author='Breeze.Kay',
    author_email='wangwenpei@kbonez.com',
    description='fabric helper tools',
    keywords='fabric,fabez,ez',
    include_package_data=True,
    package_data={
        'fabez': ['tpl/*.*']
    },
    entry_points={
        'console_scripts': [
            'fabez = fabez.main:main'
        ]
    },

)

