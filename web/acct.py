# -*- coding: utf-8 -*-


import os
from tornadoez.web import RequestHandler
from tornado.web import HTTPError

from lib.project import Projects, Project

import subprocess

import traceback

from github3 import login

from hashlib import sha1


import urllib


def verify_acct(handle):
    """
    验证签名
    :param handle:
    :return:
    """

    uid = handle.get_cookie('uid')
    origin = uid

    try:
        user_path = os.path.join(handle.application.settings['resource_path'], origin + '.user')

        if os.path.isfile(user_path):
            with open(user_path, 'r') as f:
                origin += f.readline()
        else:
            return False

        sign=sha1(origin).hexdigest()

        if sign == handle.get_cookie('sign'):
            return uid

    except Exception as e:
        print traceback.format_exc()
        pass

    return False


class Login(RequestHandler):
    def get(self, *args, **kwargs):
        """
        登录界面
        """
        if self.get_current_user():
            self.redirect('/')
            return

        self.render('login.html')

        pass


    def post(self, *args, **kwargs):
        user = self.get_argument('u')
        passwd = self.get_argument('p')

        github = login(user, passwd)

        try:
            u = github.user()
            user_path = os.path.join(self.application.settings['resource_path'], u.login + '.user')

            origin = u.login
            if os.path.isfile(user_path):
                with open(user_path, 'r') as f:
                    origin += f.readline()

                self.set_cookie('uid', u.login, expires_days=365)
                self.set_cookie('user', urllib.quote_plus(u.name.encode('utf-8')), expires_days=365)
                self.set_cookie('sign', sha1(origin).hexdigest(), expires_days=365)

                self.redirect("/")

            else:
                raise HTTPError(403)

        except Exception as e:
            self.write(e.__str__())
            print traceback.format_exc()
            pass

        pass


    pass


class Logout(RequestHandler):
    """
    登出
    """

    def get(self):
        # 清理cookie,只清理登录状态，这样还可以继续使用用户的身份信息
        self.clear_cookie('uid')
        self.clear_cookie('user')
        self.clear_cookie('sign')
        return self.redirect('/')

