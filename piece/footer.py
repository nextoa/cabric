# -*- coding: utf-8 -*-


from tornado.web import UIModule


class Footer(UIModule):
    def render(self, *args, **kwargs):
        return self.render_string('_ui_/footer.html')
