开始使用Cabric
===================

基于cabric来部署项目，本质上是数个配置文件。
一个有效的cabric部署配置，文件结构是这样的：

.. program-output:: tree ../../cabric-kickstart/


其中：

* config/cabric/<ENV>         存放cabric的配置
* config/fabric/<ENV>.conf    存放远程服务器列表
* config/stage/<ENV>          存放指定环境依赖的配置文件
* config/crontab/*            存放远程服务器使用的crontab文件
* fabfile.py                  fabric文件，存放用户自定义的函数