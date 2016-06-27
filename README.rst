Cabric
==================


A deploy tool for Centos, based on Fabric.

Important Note
---------------------

this project was designed for Centos6,it's a little old.

I am planning a more elegant solution for Centos In my spare time.


CentOS released 7.x

Fabric added task feature

I believe we can do more with a better way.




Quick Start
----------------------------
`Chinese Version <https://github.com/nextoa/cabric/blob/master/docs/quick-start.rst>`_


FAQ
----------------------------
`Chinese Version <https://github.com/nextoa/cabric/blob/master/docs/faq.rst>`_


Install
---------------------------
.. code-block::

    sudo pip install cabric




Create New Project
---------------------------
.. code-block::

    cabric init






Release Note
----------------------------

* 0.2.x
    * support mongodb 3.x repo
    * support cloud feature
        * currently,we only support `qingcloud <https://www.qingcloud.com>`_
        * support create router
        * support create pubkey
        * support create lan
        * support create internet
        * support create instance
        * support create part-time instance


* 0.1.x

    * support create tornado app easily,depends on `bree <https://github.com/nextoa/bree>`_
    * support mongo shard feature
    * support local web operation,like django's  manage.py collectstatic
    * support supervisor
    * support statsd
    * support send release-note use mail
    * support smtp server
    * support php
    * support more config type
    * improve install python lxml
    * support tengine
    * support nginx
    * support python3,pypy
    * support python complex package.e.g:pillow
    * support redis
    * support mongodb
    * support mysql
    * core feature
        * add user
        * git clone/git pull code
        * upload private | public key
        * ...



