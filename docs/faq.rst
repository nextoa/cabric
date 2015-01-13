FAQ [Chinese Version]
==============================


鉴于目前的小伙伴提问的零碎问题太多，整理至此，供查询。



目标与限制
--------------------------
* 只针对centos系统做优化
* 使用cabric安装的包会覆盖原有的配置，建议在新机器上安装




快速指南
---------------------------------


安装
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::
    pip install fabez

会同时安装底层的依赖



自动初始化一个新项目
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::
    mkdir project
    cd project
    fabez init  # 如果已经有机器，可以使用  fabez init  root@example.com
    git init . #[可选]


项目会在 project 下创建config/fabez 和 config/cabric 目录

config/fabez/*.conf  存放 机器的配置，语法兼容 pssh
config/cabric/*  存放 cabric 配置文件，比如cloud配置



配置需要部署的机器
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    vi ./config/fabez/beta.conf

添加你有权限的机器: 比如 root@example.com


测试执行
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

在项目根目录执行，请

::

    fab ez:beta upgrade



如果存在警告 找不到 ~/.ssh/config 文件， 建议创建该文件




接下来可以做的
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

使用方法与fabric一致，我们打包了很多针对Cento工具的安装

请编辑你的fabfile.py 加入想要的功能

定义函数时，请不要使用 init_  update_ 作为函数前缀，后期我们可能会开发相应的功能









安装篇
--------------------------



安装web套件
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


目前我们的安装套件，为 Tengine+tornado，快速安装::

    server_websuite()  #安装pypy版本

    server_websuite(only_pypy=False,complicate=False)  #安装python3版本

    server_websuite(only_pypy=False,complicate=True)  #安装python3+pypy版本


技术细节：

    * 部署webuser用户
    * 构造web目录 /webdata
    * 构造log目录 /logs/tornado
    * 安装tengine tornado python|pypy monit






安装redis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

demo::

    utils_remi()
    server_redis(card='eth0')       #绑定eth0网卡



安装mongodb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
demo::

    service_mongo(card='eth0')




安装php
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
demo::

    server_phpd(user)





更多
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
文档撰写中…… 写文档很辛苦有木有






配置篇
--------------------------


如何用monit启动tornado
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


配置::

    check process pupils_9001
        matching "port 9001"
        # 需求日志
        start program = "/bin/bash -c '/usr/local/pypy/bin/pypy -u -OO /usr/local/pypy/bin/ez /webdata/pupils.baixing.com  product --port 9001 &>> /logs/tornado/pupils_9001.log'"
            as uid webuser and gid webuser
        stop program  = "/bin/grep 'product --port 9001' | /bin/grep -v grep | /bin/awk '{print $2}' | /usr/bin/xargs kill -9"
            as uid webuser and gid webuser

        if failed port 9001 protocol http
           with timeout 3 seconds
           then restart
        group server



如果需求日志，就用如上所示/bin/bash启动，如果不需要，就直接用命令启动




如何上传配置
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* Nginx（Tengine）和 monit配置，建议使用config_*()上传，比如：config_monit('project')，具体参考 etc.py

    注意事项：
        * 除online环境之外，其他需要加后缀，如果上传名称为project
            * ol环境  实际上传为project
            * test环境 实际上传为project_test
            * dev环境 实际上传为project_test


        * 文件后缀必须为*.conf
        * 文件需要放置在 [fabfile root]/config/nginx|monit/ 目录下


* 其他的自行使用run命令上传




如何动态配置mongodb
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
首先，config目录中需要存在 config/mongo/mongod.conf
配置文件中，bind_ip={}

demo::

    from fabez.cmd import cmd_ip
    ....


    config_mongo('mongod', *[cmd_ip('eth0')])








如何自动挂载云服务商分配到的新硬盘
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

目前使用xfs文件格式，其他模式，有时间再开发

demo::

    def init_large_disk():
        utils_disktools()

        io_big_disk('/dev/sdb')
        io_format_disk('/dev/sdb1')
        io_mount_disk('/dev/sdb1', '/mnt/storage')

    pass







如何为硬盘扩容
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*resize脚本待验证，考虑到成本问题等真实扩容时在做，因为硬盘一旦扩容不能再缩小*

按照目前主流厂商的操作，目前大多数不支持不卸载扩容。
针对这一场景，你需要做如下操作


* 卸载硬盘::

    def umount_large_disk():
        io_umount_disk('/mnt/storage')
        pass


* 在云平台中调整硬盘的大小


* 执行remount操作::

    def resize_large_disk():
        print("请先确认硬盘已经被扩容")
        #io_mount_disk('/dev/sdb1', '/mnt/storage')  #可以尝试不使用此行来扩容试试看
        io_resize_disk('/mnt/storage')
    pass




通知篇
--------------------------



如何发起release通知
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

cabric集成了自动发送上线通知的功能，要使用本功能，需要满足如下条件:

* 需要使用git管理本地安装库
* 安装msmtp
* fabfile目录配置 ./config/cabric/release-note.conf::
    [mail]
        title:邮件标题
        to:mail@example.com
        hello:Dear All
        current:Current Release
        plan:Planing Feature
        sign:Thanks




执行 fab release_note:[发送邮箱]


