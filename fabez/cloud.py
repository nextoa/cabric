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

def cloud_processor(func=None):
    ez_env.cloud_processor = func
    pass



