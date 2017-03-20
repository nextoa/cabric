Cabric
==================

Cabric,a deploy tool for CentOS,based on Fabric.

|build-status| |license| |pyimp|


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



.. code end.


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

