Cabric
==================


Cabric,a deploy tool for CentOS,based on Fabric.


|build-status| |license| |pyimp|


.. note::

    Cabric was stoped development at 2017-12-31.

    We focus on docker but fabric can only works on python2.x.
    we don't plan support python2 anymore.

    We are planing a new project `tara <https://github.com/wangwenpei/tara/>`_
    to play with Docker,K8s and make your development more easier.



Quick Start
--------------------------

#. Installation

    .. code-block:: bash

        pip install cabric


#. Initial

    .. code-block:: bash

        cd /tmp
        cab touch nextoa/cabric-kickstart cabric-demo



#. Edit hosts

     .. code-block:: bash

        cd /tmp/cabric-demo
        sed -i -e "s/example.com/<YOUR SERVER IP>/g" config/fabric/beta.conf

#. Run

    .. code-block:: bash

        cab install --env=beta    # install depends packages
        cab config --env=beta --restart=nginx   # config server and restart nginx services


#. Work With Fabric Task

    .. code-block:: bash

        fab ez:beta hello_world



Features
---------------------------
.. code-block:: bash

    cab check                    # [plan-feature] check current environment
    cab touch                    # touch a project from template repository.
    cab install                  # install depends on target server.
    cab config                   # config target server.
    cab deploy                   # deploy project.
    cab compile                  # compile python project.
    cab clean                    # clean python compiled files.
    cab mini                     # minify python project.
    cab render                   # render project which create by `cab touch`
    cab update                   # [plan-feature] upgrade target server.
    cab package                  # a short way for python package.
    cab hardline                 # batch way to execute fabric & cabric command



.. code end.


FAQ
---------------------------

Q: When I use `cabric`, I got this error:
.. code-bloc:: bash

    rsync: connection unexpectedly closed (0 bytes received so far) [sender]
    rsync error: error in rsync protocol data stream (code 12) at /BuildRoot/Library/Caches/com.apple.xbs/Sources/rsync/rsync-51/rsync/io.c(453) [sender=2.6.9]



.. code end.

A: your remote server may not install `rsync`. please install first. if you still seem this error, please upgrade rsync to newer version.



For more document. please visit `Cabric cookbook <https://www.nextoa.com/cabric/>`_


.. |build-status| image:: https://secure.travis-ci.org/wangwenpei/cabric.png?branch=master
    :alt: Build status
    :target: https://travis-ci.org/wangwenpei/cabric

.. |coverage| image:: https://codecov.io/github/wangwenpei/cabric/coverage.svg?branch=master
    :target: https://codecov.io/github/wangwenpei/cabric?branch=master

.. |license| image:: https://img.shields.io/pypi/l/cabric.svg
    :alt: MIT License
    :target: https://opensource.org/licenses/MIT

.. |wheel| image:: https://img.shields.io/pypi/wheel/cabric.svg
    :alt: Cabric can be installed via wheel
    :target: http://pypi.python.org/pypi/cabric/

.. |pyversion| image:: https://img.shields.io/pypi/pyversions/cabric.svg
    :alt: Supported Python versions.
    :target: http://pypi.python.org/pypi/cabric/

.. |pyimp| image:: https://img.shields.io/pypi/implementation/cabric.svg
    :alt: Support Python implementations.
    :target: http://pypi.python.org/pypi/cabric/

