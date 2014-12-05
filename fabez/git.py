# -*- coding: utf-8 -*-

from fabric.api import *

import os


try:
    import ConfigParser as configparser
except:
    import configparser

    pass


def git_ensure_status():
    """
    :return: raise exception when has untracked files
    """

    result = local('git status', capture=True)

    if result.find('Untracked files') > -1:
        raise Exception("Your have Untracked files")

    pass


def git_ensure_master():
    result = local('git branch', capture=True)

    begin = result.find('*')
    end = result.find("master") + 6
    current = result[begin:end]
    if current != '* master':
        raise Exception("This operate only allow on master branch")

    pass


def git_pick_release_log(limit=1000):
    # refer
    # git log --format="%h %ad %d %an: %s" --tags --date=short

    result = local('git log --format="%d %s" -n {}'.format(limit), capture=True)
    end = result.find('(tag: ')

    buffer = result[0:end]

    filter_words = [
        '调试',
        '测试',
        # '更新',
        'debug',
        'test',
        'daily',
        'update',  # keep upgrade but filter update

        # git system
        'Update Release Files...',
        'Create Release Files...',
        'Merge branch',
        'Merge pull',
        '(origin/dev',
        '(origin/beta',

    ]

    rtn = []

    for b in buffer.split("\n"):
        match_filter = False

        for s in filter_words:
            if b.find(s) > -1:
                match_filter = True
                break

        if match_filter:
            continue

        f = b.strip()
        if f:
            f = f.replace('(HEAD, origin/master, master)', '').replace('(HEAD, master)', '').replace('(origin/master)', '').strip()
            rtn.append('* ' + f)

        pass

    return rtn


def git_release_mail(conf, curr_buff, next_buff, to=None):
    title = conf.get('mail', 'title', 'Project Upgrade Notice')
    if not to:
        to = conf.get('mail', 'to')

    hello = conf.get('mail', 'hello', 'Dear All')

    title_curr = conf.get('mail', 'current', '')
    title_plan = conf.get('mail', 'plan', '')
    msg_sign = conf.get('mail', 'sign', '')

    buff = "Subject:{}\nTO:{}\r\nContent-Type: text/plain; charset=UTF-8\n{}\n\n\n{}\n\n{}\n\n\n{}\n\n{}\n\n\n-------\n\n{}\n\n\n".format(title, to, hello, title_curr, curr_buff, title_plan, next_buff,
                                                                                                                                msg_sign)

    return buff, to


def release_note(send_to=None, limit=1000):
    """
    depends on msmtp
    :param limit:
    :return:
    """

    git_ensure_status()
    git_ensure_master()

    note = git_pick_release_log()

    buff = "Current Release\n======================================================\n\n"
    buff += "\n".join(note) + "\n\n"

    with open('./docs/releases/current.rst', 'w') as fh:
        fh.write("\n".join(note))

    with settings(warn_only=True):
        local('git add . && git commit -a -m "Update Release Files..."')

    if not os.path.exists('./config/cabric/release-note.conf'):
        print("No release-note config found. skip notice.")
        print("if you want use send mail feature, please see http://plan  ")
        return

    conf = configparser.ConfigParser()
    conf.read('./config/cabric/release-note.conf')

    msmtp = local('which msmtp', capture=True)

    if not msmtp:
        print("msmtp not found. skip notice.")
        print("if you want use send mail feature, please install it.")
        return

    buff_current = ''
    buff_next = ''

    with open('./docs/releases/current.rst', 'r') as fh:
        buff_current = fh.read()
        pass

    with open('./docs/releases/next.rst', 'r') as fh:
        buff_next = fh.read()
        pass




    text, to = git_release_mail(conf, buff_current, buff_next,to=send_to)


    local("echo '{}' | msmtp {}".format(text,to))

    pass


def tag(tag_name=None):

    git_ensure_status()
    git_ensure_master()

    local('git tag -l')

    try:
        input = raw_input
    except:
        #python3
        pass


    choice=input("Are you sure you want to named version {} or reset it:[y/n/version]".format(tag_name))


    if choice == 'n':
        return

    if choice != 'y':
        tag_name = choice

    local('git tag {}'.format(tag_name))

    pass
