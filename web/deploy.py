# -*- coding: utf-8 -*-

import os
from tornadoez.web import RequestHandler
from tornado.web import HTTPError

from lib.project import Projects, Project

import subprocess

from tornado.web import authenticated



class Dashboard(RequestHandler):
    @authenticated
    def get(self, *args, **kwargs):
        """
        init
        :param args:
        :param kwargs:
        :return:
        """

        projects_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'projects')

        projects = Projects(projects_path)

        self.render('index.html', **{
            'projects': projects.ptree
        })

        pass


    pass


class Deploy(RequestHandler):
    @authenticated
    def get(self, project, *args, **kwargs):
        """
        进行发布
        :param args:
        :param kwargs:
        :return:
        """

        project_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'projects', os.path.basename(project))

        project = Project(project_path)

        self.render('deploy.html', **{
            'project': project
        })

        pass


class Tags(RequestHandler):
    @authenticated
    def get(self, project, *args, **kwargs):
        """
        设置tags
        :param args:
        :param kwargs:
        :return:
        """

        project_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'projects', os.path.basename(project))

        project = Project(project_path, init_tags=True, init_env=False, init_name=False)

        self.api_write(200, tags=project.tags)

        pass


class Process(RequestHandler):
    @authenticated
    def get(self, *args, **kwargs):
        """
        处理位置
        :param args:
        :param kwargs:
        :return:
        """

        prepare = self.get_argument("prepare", 0)

        if prepare:
            self.render("process.html")
            return

        project = self.get_argument("project")
        config_file = self.get_argument("env")
        tag = self.get_argument("version", 0)

        workspace = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'projects', os.path.basename(project))

        # 项目如果异常,会导致整个app崩溃
        # os.chdir(workspace)

        # 兼容命令行的语法
        if config_file == "online.conf":
            env = "ol"
        else:
            # @TODO 暂时不考虑没有.情况
            pos = config_file.find(".")
            env = config_file[0:pos]



        # @note 关于fabez的挂起问题.
        # 首先,问题的原因:
        # 因为tornado使用了单队列,不用异步就会导致整个tornado堵塞.
        #
        # 第一种
        # 如果我们能保证client中途不会出现交互式,那么整个流程是没问题,这个锁也会给我们带来好处,
        # 所以我们只要能保证client是正常的,那就可以了
        # 第二种
        # 干掉当前用户的fabez进程,因为tornado是单队列堵塞机制,所以我们需要先干掉锁死掉的进程,这个对于小团队来说不会是太大的问题
        # 第三种
        # 做异步,异步带来的问题是,进程可以无限开启,所以会导致垃圾进程.

        # 目前我们坚持第一种
        cmd = "cd {} && fab ez:{} upgrade".format(workspace,env)

        if tag != "0":
            cmd += ":tag=" + tag

        out_stream = subprocess.PIPE
        err_stream = subprocess.PIPE



        # 可以开始异步的地方,建议直接使用feature来完成
        p = subprocess.Popen(cmd, shell=True, stdout=out_stream, stderr=err_stream)

        self.write("<html>"
                   "<style>"
                   "* {color:white;background-color:black;}"
                   "html,body {margin:0;padding:0;}"
                   "</style>"
                   "<body>")

        self.write("<p>Call:{}</p><hr />".format(cmd))

        while p.poll() is None:
            line = p.stdout.readline()
            # print line,
            self.write("<p>" + line + "</p>")
            self.flush()
        pass

        self.write("</body></html>")

    pass


