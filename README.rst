Cabric
==================

.. image:: https://pypip.in/v/cabric/badge.svg
:target: https://pypi.python.org/pypi/cabric/
.. image:: https://pypip.in/d/cabric/badge.svg
:target: https://pypi.python.org/pypi/cabric/
.. image:: https://pypip.in/license/cabric/badge.svg
:target: https://pypi.python.org/pypi/cabric/

A deploy tool for Centos, based on Fabric.


新候选词:
-----------------------
deploy tool for centos 已经不能满足我们的概念了.

经过这段时间的积累,我们融入了很多不错的想法,并且已经试验验证了可行性.但是这些概念远远超过了deploy的概念.

但是我又很喜欢cabric这个命名.
所有我们只能升级这个概念了.


一些备选词:

- chart n. 图表；航海图
- chess n. 棋
- coat n. 外套；涂层；表皮；皮毛 vt. 给……穿外套；涂上
- collar n. 衣领； 硬领
- comb n. 梳子 v. 梳
- companion n. 同伴；同事
- calm a. 镇静的； 沉着的 v. 镇静； 沉着



Feature
---------------------------
.. code-block::

    cab check                    #检查当前环境是否支持cabric的运行
    cab prepare                  #安装缺失的依赖,并检测python的环境
    cab init                     #根据配置,初始化云资源
    cab init-project             #根据配置,初始化项目配置
    cab ez:<ENV> install         #根据环境,安装依赖包
    cab ez:<ENV> config          #根据环境,更新配置
    cab ez:<ENV> deploy          #根据环境,部署代码
    cab compile                  #针对python的编译策略
    cab ez:<ENV> release         #根据环境,发布包(只针对python,发布公网包,发布私有包,发布spider)
    cab clean                    #清理编译文件等





