# -*- coding: utf-8 -*-

import os
import web.deploy as Deploy
import web.acct as Acct

from piece import *



def _handlers():
    '''
    Handlers 下划线用于隐藏
    :return:
    '''
    return [
        # (r"/", Dashboard.Dashboard),

        # locale 语言切换,应该是ajax方式,请求之后,然后js控制刷新页面
        (r"/", Deploy.Dashboard),
        (r"/deploy/(.+)", Deploy.Deploy),
        (r"/process/?", Deploy.Process),
        (r"/tags/(.+)", Deploy.Tags),

        (r"/login/?", Acct.Login),
        (r"/logout/?", Acct.Logout),


    ]
    pass


def dev(**ez_settings):
    '''
    开发机
    :param ez_settings:
    :return:
    '''
    config = {}

    config.update({
        'cookie_secret': '8888',
        'debug': True,
        'static_path': os.path.join(os.path.dirname(__file__), 'wwwroot', 'static'),
        'locale_callback': None,
        'auth_callback': Acct.verify_acct,
        'ui_modules': [header, footer],
        'resource_path':os.path.join(os.path.dirname(__file__),'resources')
    })

    return config, _handlers()


# for quick test
if __name__ == '__main__':
    __requires__ = 'bree'
    import sys
    from pkg_resources import load_entry_point

    sys.argv.append(os.path.dirname(__file__))
    sys.argv.append('.')
    sys.argv.append('dev')
    sys.argv.append("--port")
    sys.argv.append("9801")

    sys.exit(
        load_entry_point('bree', 'console_scripts', 'ez')()
    )

