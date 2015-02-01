快速入门指南
=================================

关于Cabirc
--------------------------

Cabric 是基于 `Fabric <https://www.fabfile.org>`_ 的特定版本。 所以在语法上全兼容 Fabric

Cabric 主要针对CentOS做优化，同时内部集成对云平台的操作，使部署工作变得极其简单快速。

当前版本，我们集成 `青云 <https://www.qingcloud.com>`_



安装
--------------------------

因为fabric只支持python2.x版本，所以请确认自己的python版本是否能正常工作。

目前我们的测试环境为pypy2.4

::
    pip install cabric
    pip install qingcloud-sdk  #可选，如果不使用青云可无视




创建项目
--------------------------

在需要创建项目的位置，执行

::

    cabric init [root@host]


该操作会在当前项目初始化
::
    fabfile.py
    config/cabric/cloud.conf
    config/fabric/*.conf

如果指定了host，会将host配置写入到 `config/fabric/beta.conf` 中

接下来的操作，将和fabric完全一致。 如果你是高级用户，你可以通过源码直接了解我们现在已经配置好的模块来使用。也可以直接跳至 `服务的安装` 环节了解




新的数据中心
--------------------------

如果你是青云用户，可以编辑 fabfile.py 加入自己的Appkey 和 AppSecret。
加入完成后执行

::

    fab init_datacenter


该操作会帮你自动搭建一个数据中心。

*Note* 因为青云北京1机房与其他机房配置方式略有不同，
且北京1区资源并不是对所有用户开放的。所以北京1机房不支持使用自动化部署

数据中心目前还不支持对负载均衡器的自动加载，正在开发中


添加机器
--------------------------

当数据中心搭建完成后，可以创建机器

::

    fab init_instance:机器类型,数量


该操作会自动对机器名称做自增，方便机器的管理，比如

::

    fab init_instance:web


将会生成  web01 的机器


添加非全时机器
--------------------------

作为一个web网站，每一家的业务特色会出现全天服务器使用的高峰期和低谷，在高峰期和低谷动态调整备用的机器，可以帮我们节省成本。

使用如下方式，则可以自动创建并登记需要在闲时 关闭的机器

::

    fab init_instance_parttime:机器类型




关闭非全时机器
--------------------------

通过以下操作可以关闭已经登记的可休眠机器。
建议将任务放置在定时器中，比如 crontab

::

    fab cc_instance_parttime_stop:机器类型



启动全时机器
--------------------------

::

    fab cc_instance_parttime_start:机器类型




更新机器配置
--------------------------

在对服务器扩容后，我们总是需要将机器添加到配置表中,这个操作很麻烦且容易出错。

使用cabric，可以通过如下方式来解决

::

    fab cc_dump:机器类型编号#机器类型编号-编号#机器类型*,写入的配置文件名


比如

::

    fab cc_dump:web01,beta  # 将一台机器写入到beta配置中
    fab cc_dump:web01-05,beta    # 将web01-05 所有有效的机器写入到beta配置中
    fab cc_dump:web01-05#web12-15,beta    # 将web01-05,web12-15 所有有效的机器写入到beta配置中
    fab cc_dump:web*,beta    # 将所有web机器写入到beta配置中


服务的安装
--------------------------

接下来你可以使用cabric打包好的命令来安装服务，也可以继续使用fabric。

服务的安装因为涉及到机器，所以所有的服务均需要追加 `ez:环境` 来绑定host

::

    fab ez:beta ...


*Note* 考虑到online是我们最常用的环境，所以 online 做了次简化，文件名为online， 请求指令为  `ez:ol`

模块说明:

::

    cabric.cmd     #常用指令
    cabric.server  #包含常用的服务器安装
    cabric.env     #环境变量，类似于fabric.env
    cabric.etc     #常用配置的更新
    cabric.io      #常用的io操作，如：自动挂载硬盘
    cabric.git     #本地git操作，如：根据commit，自动生成release_note并发送
    cabric.perm    #权限设置相关
    cabric.pythonic   #python 相关安装
    cabric.user    #user设定
    cabric.utils   #常用工具设定



基础Lib说明:

::

    cabric.escape  #包含了字符转码解决python2的unicode问题
    cabric.lib     #基础库函数



比如安装redis服务至beta环境，则只需要执行
::

    fab ez:beta server_redis


*Note* 在cabric中，所有的服务安装完毕后，都是不会自动启动的，因为我们建议用户至少做一次重启来验证服务的有效性，同时也考虑到用户的自定义配置的需求



更新服务配置
------------------------------

常用的server，我们会对应一份配置的指令。以redis为例

::

    fab ez:beta config_redis:配置名


*Note* 不同的服务会根据自己的服务需求动态生成配置名，以 redis 和 nginx 配置为例。

如果 nginx 的配置名称是 project1.conf  那么
   * 上传至 online 服务集群，则只需要 project1.conf 文件。
   * 上传至 其他服务集群，则需要加后缀，比如beta：project1_beta.conf 文件。


如果 redis 的配置名称是 redis.conf  那么 上传至任意服务器，都是:
    * 上传至 online 服务集群，则只需要 redis.conf 文件。


相关文档后期会整理，一个简单的规则是：如果服务器涉及后端存储，则使用通用配置，其他使用动态配置



