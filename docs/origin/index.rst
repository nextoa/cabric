Fabez
==================

`fabez <http://fabez.leadyi.com>`_ , A easy deploy system for centos, based on fabric



Upgrade notes
-------------
* Version 0.9.1
    - support python3


* Version 0.9.0
    - Add ``--once`` option. execute once and exit instead of wait.

* Version 0.8.99
    - As of Comb 0.8.99, we change  ``--sleep_max`` option to ``--sleep-max``.
    - change comb script install path,use python library path instead /usr/local/bin


Quick links
-----------

* `Documentation <http://comb.kbonez.com/>`_
* `Source (github) <https://github.com/kbonez/comb>`_




Installation
------------

**Automatic installation**::

    pip install comb

comb is listed in `PyPI <http://pypi.python.org/pypi/comb/>`_ and
can be installed with ``pip`` or ``easy_install``.
it includes demo applications.


**Manual installation**: Download the latest source from `Github
<http://www.github.com/kbonez/comb/>`_.

.. parsed-literal::

    git clone  https://github.com/kbonez/comb.git
    cd comb
    python setup.py build
    sudo python setup.py install

The comb source code is `hosted on GitHub
<https://github.com/kbonez/comb/>`_.

**Prerequisites**: comb was only test on Python 2.7.  It may be runs on
all Python versions.




How to use
---------------

To use comb, you should create a python module file. we named *slot*.

A legal slot must be named 'Slot' in your module file and it must be at least contain four method:

* `initialize`

    initial resource, e.g: database handle

* `__enter__ `

    get next data to do,you can fetch one or more data.

* `slot`

    user custom code


* `__exit__`

    when slot finished, call this method


Slot Demo
---------------

* `Deal List Data <https://github.com/kbonez/comb/blob/master/comb/demo/list.py>`_


* `Deal Mongo MQ <https://github.com/kbonez/comb/blob/master/comb/demo/mongo.py>`_


* `Recycle Mongo MQ <https://github.com/kbonez/comb/blob/master/comb/demo/garbage.py>`_


* `Custom Slot options <https://github.com/kbonez/comb/blob/master/comb/demo/redis.py>`_



Start
---------------

* Execute a comb is very simple. just execute::

    comb --root SLOT_ROOT_PATH  slot-package.slot-module

  if you set `SLOTPATH` environment, you can use::

    comb slot-package.slot-module

* Quick View. call::

	comb   comb.demo.list

this will execute the `Deal List Demo <https://github.com/kbonez/comb/blob/master/comb/demo/list.py>`_


Note for production deployment
---------------------------------------------

* You'd better make comb process number equals your cpu core number.

* We strongly recommend you use comb with `supervisor <http://supervisord.org/>`_







