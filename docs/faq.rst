FAQ [Chinese Version]
==============================


鉴于目前的小伙伴提问的零碎问题太多，整理至此，供查询。


如何用monit启动tornado
---------------------------------------------

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
---------------------------------------------


* Nginx（Tengine）和 monit配置，建议使用config_*()上传，参考etc.py

* 其他的自行使用run命令上传




