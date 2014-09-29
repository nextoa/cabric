# -*- coding: utf-8 -*-



import os,sys
import importlib

import json


from github3 import login,GitHub



class Projects(object):
    """
    项目树的构造
    """

    def __init__(self,path):

        self.projects_root = path

        self.ptree={}

        self.project_list = os.listdir(path)

        for v in self.project_list:
            self.ptree[v]=self.parse_project(v)


        pass


    def parse_project(self,project):


        pass


pass


class Project(object):

    def __init__(self,path,with_init=True):
        """
        单个项目的初始化
        :param path:
        :return:
        """

        sys.path.insert(0,path)
        self.root = path
        self.fabfile = importlib.import_module("fabfile")
        self.github = GitHub(token=self.fabfile._token())

        self.tags=[]
        self.environment=[]

        if with_init:
            self.tags=self.upgrade_tags()
            self.environment=self.upgrade_environment()

        pass



    def upgrade_tags(self):
        """
        获取最新的tags
        :return:
        """
        h = self.github._get(self.fabfile._github()+"/tags")

        buffer = h.content
        json_code = json.loads(buffer)

        #@todo 我感觉应该有更简洁的写法
        tags=[]
        for d in json_code:
            tags.append(d['name'])

        return tags



    def upgrade_environment(self):
        config_root = os.path.join(self.root,'config','fabez')
        return os.listdir(config_root)
        pass




if __name__ == "__main__":

    project_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'projects','fabez-bx')
    a = Project(project_path)

    pass

