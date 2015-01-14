# -*- coding: utf-8 -*-


from fabez.env import *

from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def cloud_run(func, hold_func=None, strict=True, return_key=None, func_args=[], func_kwargs={}):
    """
    execute cloud operation
    :return:
    """

    result = func(*func_args, **func_kwargs)

    print("[Execute]:{}".format(func.__name__))

    if not result:
        raise Exception("Network error")

    if result['ret_code']:
        if strict:
            raise Exception(result['message'])
        else:
            print("[Warning]:{}".format(result['message']))

    data = None
    if return_key:
        data = result[return_key]

    if not strict and result['ret_code']:
        return data

    if hold_func is False:
        current_hold_func = False
    else:
        current_hold_func = hold_func if hold_func else ez_env.cloud_processor

    if not current_hold_func:
        return data

    job_id = result['job_id']
    stop = False
    counter = 0
    print("[Holding]: {} ...".format(job_id))

    while True:
        result = current_hold_func([job_id])

        for v in result['job_set']:
            if v['status'] in ['successful']:
                stop = True
            elif v['status'] in ['pending', 'working']:

                time.sleep(1)
            else:
                raise Exception(v)
            pass

            counter += 1
            print("." * counter)
        if stop:
            break
        pass

    return data


def cloud_update(buff, file='./config/cabric/cloud.yaml'):
    return dump(buff, open(file, 'w'), Dumper=Dumper)


def cloud_read(file='./config/cabric/cloud.yaml'):
    return load(open(file, 'r'), Loader=Loader)


def cloud_connect(handler=None):
    handler = handler if handler else ez_env.cloud_handler

    h = handler.connect_to_zone(*ez_env.cloud)
    ez_env.cloud_processor = h.describe_jobs

    return h


def cc_instance_list():
    """
    :return: [instance_id, eip_id, eip_addr, vxnet, status_time, instance_type]
    """

    h = cloud_connect()

    result = h.describe_instances()

    data = []

    d = result.get('instance_set')

    for v in d:

        if v.get('status') == 'running':

            eip = v.get('eip')

            if eip:
                eip_id = eip.get('eip_id')
                eip_addr = eip.get('eip_addr')
            else:
                eip_id = None
                eip_addr = None
            try:
                vxnet = v.get('vxnets', [])[0].get('vxnet_id')
            except:
                vxnet = None

            instance_id = v.get('instance_id')
            instance_type = v.get('instance_type')

            status_time = v.get('status_time')

            cell = (instance_id, eip_id, eip_addr, vxnet, status_time, instance_type)

            data.append(cell)

            pass

    return data


def cc_instance_info(match_id):
    data = cc_instance_list()

    key = match_id in zip(*data)[0]
    if key:
        return data[key]

    pass


def cc_free_eips(wait=1, tries=100, *args, **kwargs):
    """
    get free ip list
    :param wait:
    :param tries:
    :param args:
    :param kwargs:
    :return:
    """
    h = cloud_connect()

    addrs = set()
    process = 0

    while True:
        data = h.describe_eips()

        if not data.get('eip_set'):
            print("get new ip fail,try 1s later.")
            time.sleep(1)
            continue

        for eip in data['eip_set']:
            if eip['status'] == 'available':
                addrs.add(eip['eip_id'])
                pass
            pass

        if len(addrs) >= wait:
            break

        process += 1
        if process == tries:
            break

        time.sleep(1)
        pass

    return list(addrs)



