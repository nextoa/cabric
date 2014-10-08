# -*- coding: utf-8 -*-


from tornado.web import UIModule



class Header(UIModule):
    """
    首页系页头,主工作间头
    """

    def render(self,*args, **kwargs):
        return self.render_string('_ui_/header.html')
        pass





