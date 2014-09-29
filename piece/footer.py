# -*- coding: utf-8 -*-


from tornado.web import UIModule



class Footer00(UIModule):
    def render(self, *args, **kwargs):
        return self.render_string('ui_modules/footer.html')
        pass