# -*- coding: utf-8 -*-


from tornado.web import UIModule
from codez.dict import attribute_dict




class Header00(UIModule):
    """
    首页系页头,主工作间头
    """

    def render(self,*args, **kwargs):
        return self.render_string('ui00/header.html')
        pass



class Header01(UIModule):
    """
    产品简介的页头,适用于非首页,人才招聘啊等等适用于本站公告的
    """

    def render(self,*args, **kwargs):
        return self.render_string('ui00/header.html')
        pass





