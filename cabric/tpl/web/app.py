# -*- coding: utf-8 -*-

##################
# Note:
# This file was auto create by cabric, don't edit this file
# It will be always overwrite.
#########


from cliez.loader import ArgLoader
import bree
import bree.web
import tornado.ioloop
import tornado.web


from demo import settings
from demo.handlers import handlers


if __name__ == "__main__":
    from datetime import datetime

    a = ArgLoader((
        ('Usage app.py port',),
        '',
        '',
        'Options:',
        ('--debug', 'debug flag'),
        ('--help', 'print help document', '-h'),
    ))

    try:
        port = int(a.argv[1])
    except:
        port = 9001

    debug = a.options.get('--debug') or False

    print("[tornado]:demo start, bind port {}, begin at: {}.".format(port, datetime.now()))

    settings_debug = None
    if debug:
        print("[tornado]:demo debug mode enabled.")
        settings_debug = settings.dev
        pass

    default_settings = bree.web.build_settings(settings.pro, __file__, debug=settings_debug)
    bree.settings = default_settings

    application = tornado.web.Application(handlers, **default_settings)
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
