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
        ('--env:', 'explicit define settings'),
        ('--debug', 'debug flag'),
        ('--help', 'print help document', '-h'),
    ))

    try:
        port = int(a.argv[1])
    except:
        port = 9001

    debug = a.options.get('--debug') or False

    print("[tornado]:demo start, bind port {}, begin at: {}.".format(port, datetime.now()))

    current_env = a.options.get('--env') or 'pro'

    if hasattr(settings, current_env):
        base_settings = getattr(settings, current_env)
    else:
        raise Exception("Missing settings:`{}' in settings.py".format(current_env))

    settings_debug = None
    if debug:
        print("[tornado]:demo use settings:{}.".format(current_env))
        print("[tornado]:demo debug mode enabled.")
        settings_debug = settings.dev
        pass

    default_settings = bree.web.build_settings(base_settings, __file__, debug=settings_debug)
    bree.settings = default_settings

    application = tornado.web.Application(handlers, **default_settings)
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
