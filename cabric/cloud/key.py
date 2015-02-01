# -*- coding: utf-8 -*-


from cabric.cloud.core import *
from cabric.cloud.config import *
import cabric.cloud.instance

from cabric.lib import *
from cabric.lib import _detected_ssh_public_key_type


# only use in develop for cabric
try:
    import qingcloud.iaas.connection.APIConnection as H
except:

    pass


def cc_key_find_all(search_word=None):
    """
    find key data on cloud

    :param search_word:
    :return: tuple list on success, null list on fail, tuple contain: key_name , key_id
    """
    h = cloud_init()

    result = h.describe_key_pairs(search_word=search_word)
    key_data = []

    if result['total_count']:
        key_data = [(v['keypair_name'], v['keypair_id']) for v in result['keypair_set']]

    return key_data


def cc_key_find_one(name):
    """
    find key by name
    :param name:
    :return: tuple (name,cloud-id)
    """
    key_pairs = cc_key_find_all(name)

    try:
        compare = zip(*key_pairs)[0]
        pos = cloud_name_match(name, compare)
    except:
        pos = -1
        pass

    if pos > -1:
        return key_pairs[pos]

    return None, None


def cc_key_create(pub_key='~/.ssh/id_rsa.pub', name=None, strict=False):
    """
    upload a new key to cloud
    :param name: key name
    :param pub_key: public key path
    :param strict: if strict is True, exist when key already exists.
    :return:
    """
    h = cloud_init()
    buff = None

    name = cc_config_get('global.author')

    if not name:
        print_error("system can't find your username")

    _, key_id = cc_key_find_one(name)

    if key_id:
        print_debug("key {} exist on cloud".format(name))
        if strict:
            print_error("{} key already on cloud.please check it. or use disable strict mode".format(name))
        else:
            return True

    print_debug("upload key,username:{}".format(name))

    with open(os.path.expanduser(pub_key)) as fh:
        buff = fh.read()
        pass

    result = h.create_keypair(name, mode='user', public_key=buff, encrypt_method=_detected_ssh_public_key_type(pub_key))

    return True if result['ret_code'] == 0 else False


def cc_key_delete(name):
    """
    delete key.
    *note* if you have multiple keys, will delete first match
    :param name:key name
    :return:True on success,None when not found
    """
    h = cloud_init()
    key_data = cc_key_find_one(name)
    key_name, key_id = key_data

    if not key_id:
        return

    instances_data = cabric.cloud.instance.cc_instance_find_all(tag='all')


    def rebuild(instance):
        return instance.get('instance_id')


    instances = filter(None, map(rebuild, instances_data))

    print_debug("instances used `{}' key:{}".format(name, instances))

    if instances:
        cloud_run(h.detach_keypairs, ([key_id], instances))

    h.delete_keypairs([key_id])
    pass
