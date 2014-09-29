# -*- coding: utf-8 -*-



# -*- coding: utf-8 -*-


from tornadoez.web import RequestHandler
from tornado.web import HTTPError


class Deploy(RequestHandler):

    def get(self, *args, **kwargs):
        """
        审核partner
        :param args:
        :param kwargs:
        :return:
        """

        # 查询数据
        projects = None




        self.render('deploy.html',**{
            'projects':projects
        })


    def post(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """





        pass