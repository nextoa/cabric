# -*- coding: utf-8 -*-



import os,sys
import importlib

import json


from github3 import login,GitHub



class Projects(object):
    """
    项目列表的构造
    """

    def __init__(self,path):

        self.projects_root = path

        self.ptree={}

        self.project_list = os.listdir(path)

        for v in self.project_list:

            #隐藏文件跳过
            if v[0] == '.':
                continue


            sub_path = os.path.join(path,v)

            #是文件跳过
            if os.path.isfile(sub_path):
                continue

            self.ptree[v]=self.parse_project(v)

        pass


    def parse_project(self,project):

        data={
            'code':project
        }

        project_path = os.path.join(self.projects_root,project)

        icon_root_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'wwwroot','static','icons')
        icon_strip_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'wwwroot')
        icon_path = os.path.join(icon_root_path,project+'.png')
        icon_default_path = os.path.join(icon_root_path,'default.png')

        readme_path = os.path.join(project_path,'Readme.rst')

        #匹配图标文件
        if os.path.exists(icon_path):
            data['icon']=icon_path.replace(icon_strip_path,"")
        else:
            data['icon']=icon_default_path.replace(icon_strip_path,"")


        #匹配项目标题
        if os.path.exists(readme_path):
            with open(readme_path, 'r') as f:
                data['name'] = f.readline()
        else:
            data['name']=project

        return data


pass


class Project(object):

    def __init__(self,path,init_name=True,init_env=True,init_tags=False):
        """
        单个项目的初始化
        :param path:
        :return:
        """

        sys.path.insert(0,path)

        self.root = path
        self.fabfile = importlib.import_module("fabfile")
        self.github = GitHub(token=self.fabfile._token())

        self.code = os.path.basename(path)

        self.name=self.code
        self.tags=[]
        self.environment=[]

        if init_name:
            self.name = self.upgrade_name()

        if init_tags:
            self.tags=self.upgrade_tags()

        if init_env:
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


    def upgrade_name(self):

        readme_path = os.path.join(self.root,'Readme.rst')

        #匹配项目标题
        if os.path.exists(readme_path):
            with open(readme_path, 'r') as f:
                return f.readline()
        else:
            return self.code

        pass



# demo code
if __name__ == "__main__":

    project_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'projects','fabez-bx')
    a = Project(project_path,with_init=True)

    pass

