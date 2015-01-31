# -*- coding: utf-8 -*-


from cabric.cloud.core import cloud_config_guard, NoSectionError, cloud_config_save, NoOptionError
from cabric.lib import print_error


def _format_key(section_key):
    section = None
    key = None

    if section_key.find('.') < 0:
        section = key = section_key
    else:
        section, key = section_key.split('.')

    return section, key


def cc_config_save():
    """
    alias for cloud_config_save
    :return:
    """
    return cloud_config_save()


def cc_config_get(section_key, default=''):
    parser = cloud_config_guard()

    section, key = _format_key(section_key)

    if default is None:
        default = ''

    if not isinstance(default, str) or isinstance(default, int) or isinstance(default, float):
        print_error("`{}' value argument only allow str,int,float".format(cc_config_get.__name__))

    try:
        return parser.get(section, key, default)
    except NoSectionError:
        parser.add_section(section)
        parser.set(section, key, default)
        return default
    except NoOptionError:
        parser.set(section, key, default)
        return default
    except:
        print_error("get {}.{} fail,please check your cloud config file".format(section, key))

    pass


def cc_config_set(section_key, value):
    parser = cloud_config_guard()

    section, key = _format_key(section_key)

    if value is None:
        value = ''

    if not isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
        print_error("`{}' value argument only allow str,int,float,current is {}".format(cc_config_set.__name__, type(value)))

    try:
        return parser.set(section, key, value)
    except NoSectionError:
        parser.add_section(section)
        return parser.set(section, key, value)
    except:
        print_error("set {}.{} fail.".format(section, key))

    pass


def cc_config_lget(section_key, default=[]):
    """
    get config list
    :param section_key:
    :param default:
    :return:
    """

    parser = cloud_config_guard()
    section, key = _format_key(section_key)

    if not isinstance(default, list) or isinstance(default, set):
        print_error("`{}' value argument must be a list".format(cc_config_lget.__name__))

    try:
        buff = parser.get(section, key, default)

        if buff:
            return ','.split(buff)
        else:
            return []
    except NoSectionError:
        parser.add_section(section)
        if default:
            parser.set(section, key, default)
        else:
            parser.set(section, key, '')
        return default
    except NoOptionError:
        if default:
            parser.set(section, key, default)
        else:
            parser.set(section, key, '')
        return default
    except:
        print_error("get list {}.{} fail,please check your cloud config file".format(section, key))

    pass


def cc_config_lset(section_key, value):
    parser = cloud_config_guard()

    section, key = _format_key(section_key)

    # only allow list or set
    if not isinstance(value, list) or isinstance(value, set):
        print_error("`{}' value argument must be a list".format(cc_config_lset.__name__))

    write_value = ','.join(value)

    try:
        parser.set(section, key, write_value)
    except NoSectionError:
        parser.add_section(section)
        parser.set(section, key, write_value)
    except:
        print_error("write list {}.{} fail,please check your cloud config file".format(section, key))

    pass







