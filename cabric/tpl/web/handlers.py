# -*- coding: utf-8 -*-

import bree
import bree.web

class DemoHandler(bree.web.RequestHandler):
    def get(self):
        self.write("Hello world")


handlers = [(r"/", DemoHandler)]


