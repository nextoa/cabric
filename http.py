# -*- coding: utf-8 -*-

import os
import web.deploy as Deploy

from bx.helloworld import HelloWorld


def _handlers():
    '''
    Handlers 下划线用于隐藏
    :return:
    '''
    return [
        # (r"/", Dashboard.Dashboard),

        # locale 语言切换,应该是ajax方式,请求之后,然后js控制刷新页面
        (r"/deploy/?", Deploy.Deploy),

    ]
    pass



def production(**ez_settings):
    '''
    开发机
    :param ez_settings:
    :return:
    '''
    config = {}

    config.update({
        'cookie_secret': '8888',
        'debug': False,
        'static_path': os.path.join(os.path.dirname(__file__), 'wwwroot', 'static'),
        'locale_callback': None,
        'auth_callback': None,
    })

    return config, _handlers()




# for quick test
if __name__ == '__main__':
    __requires__ = 'tornadoez'
    import sys
    from pkg_resources import load_entry_point

    sys.argv.append(os.path.dirname(__file__))
    # sys.argv.append('--debug')
    sys.argv.append('production')
    sys.argv.append("--port")
    sys.argv.append("9801")

    sys.exit(
        load_entry_point('tornadoez', 'console_scripts', 'ez')()
    )

