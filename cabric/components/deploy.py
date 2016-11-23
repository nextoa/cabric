# -*- coding: utf-8 -*-

import os
import sys
import requests
import json
from getpass import getpass
from cliez.component import Component
from cabric.utils import get_roots, mirror_put, run, bind_hosts, execute, get_platform, get_repo
from Crypto.PublicKey import RSA

print(sys.path)
from git import config as pygit

try:
    input = raw_input
except NameError:
    pass


class DeployComponent(Component):
    def upload_deploy_key(self, private_key, remote_user, github=None, force_upload=False, key_length=8192):
        """
        upload deploy key

        :param string private_key: private key local path
            default is ~/.ssh/.deploies/`github`.rsa
        :param string remote_user: remote user name to deploy
        :param string github: github repo name
        :param bool force_upload: try replace exist key if key exists,default is False
        :param int key_length: must a legal ssh key length value. default is 8192


        ..note::
            if private_key path is not exists,but github is set. cabric will try auto create private-key.

            if you use github and want to use auto generate private-key feature.
            there is two ways can do this:

                - you must set access token in your ~/.gitconfig file
                - you must disable github two-factor authentication.


            currently, we use `<remote_user>@cabric` as our deploy key name.
            so if you upload your key use to other purpose, don't use `@cabric` as key suffix.

        :return:
        """

        if not os.path.exists(private_key) and github:
            self.warn("deploy key `%s' is not exists,we will try generate it." % private_key)

            authorized_methods = []

            # login
            def use_personal_token():
                """
                ..note::
                    token was limited when user use strict permission
                :return:
                """
                git_config_path = os.path.expanduser('~/.gitconfig')
                if os.path.exists(git_config_path):
                    git_config = pygit.GitConfigParser(git_config_path)
                    git_config.read()
                    access_token = git_config.get_value('github', 'token', default='')
                    username = git_config.get_value('github', 'user', default='')
                    pass

                    if access_token and username:
                        return (username, access_token)
                pass

            def use_github_password():
                username = input('Github Account:')
                password = getpass('Github Password:')
                auth_config = (username, password)
                return auth_config

            authorized_methods = [
                use_personal_token,
                use_github_password
            ]

            auth_config = None

            for v in authorized_methods:
                temp_config = v()
                response = requests.get('https://api.github.com/repos/{}/keys'.format(github), auth=temp_config)
                if response.status_code != 200:
                    self.warn("use `%s' method login to github is failed,try next way." % v.__name__.replace('use_', '').replace('_', '-'))
                    continue

                auth_config = temp_config
                keys = response.json
                key_title = remote_user + '@cabric'
                break

            if not auth_config:
                self.error("login github failed.")

            try:
                uploaded_keys = [v for v in keys if v.get('title') == key_title]
            except TypeError:
                uploaded_keys = []

            if uploaded_keys:
                if force_upload:
                    self.warn("deploy key exits,but your set `--force-new-key',it will re-generate new key")
                else:
                    self.warn("deploy key exists,if you want to re-generate key,please set `--force-new-key' option")
                    return  # return and don't create key

            # clean old key if exists
            for v in uploaded_keys:
                response = requests.delete('https://api.github.com/repos/{}/keys/{}'.format(github, v.get('id')), auth=auth_config)
                if response.status_code != 204:
                    self.error("delete old deploy key failed,please try it later.")
                    pass

            # generate new key
            self.print_message("Generating deploy key... this will cost about 1 minute...")
            key = RSA.generate(key_length)

            private_key_dir = os.path.dirname(private_key)
            if not os.path.exists(private_key_dir):
                os.makedirs(private_key_dir, 0700)
                pass

            with open(private_key, mode='w') as fp:
                fp.write(key.exportKey('PEM'))
                pass

            pubkey = key.publickey()
            pubkey_path = os.path.splitext(private_key)[0] + '.pub'

            with open(pubkey_path, mode='w') as fp:
                fp.write(key.exportKey('OpenSSH'))
                pass

            response = requests.post('https://api.github.com/repos/{}/keys'.format(github), data=json.dumps({
                'title': key_title,
                'key': pubkey.exportKey('OpenSSH'),
                'read_only': True,
            }), auth=auth_config)

            if response.status_code != 201:
                self.error("create key failed. server return\n:%s" % response.text)
                pass

            pass

        pass

    def enable_services(self):

        pass

    def install_requirements(self):

        pass

    def compile_templates(self):

        pass

    def upload_resources(self):

        pass

    def reload(self):

        pass

    def restart(self):

        pass

    def upgrade(self, config):
        """
        config and default value

        * check values
            - user, if not set user,it will cause an error
            - repo, if not set use project root,repo

                ..note::
                    - currently,this only support git+ssh mode
                    - if you use pull-request develop mode,and downstream has remote machine permission.
                        you must set this value


            - branch, default is master
            - root, if not set,default is user-home + project-name

                ..note::
                    user must be set home

        :param config:
        :return:
        """

        user = config.get('user')
        branch = config.get('branch', 'master')

        pass

    def run(self, options):
        """
        workflow
            * basic check

                - user value must be set
                - currently, repo only support git
                - for safety reason,we don't allow private_key path occur in project path

            * upload deploy-key when not exist.
            * git clone with project-deploy-key.
            * install requirements.txt package if exist
            * install nodejs local-package if exist
            * parse template file
            * git pull or checkout commit
            * add crontab if user set
            * finish

        :param options:
        :return:
        """

        package_root, _, fabric_root = get_roots(options.dir)
        bind_hosts(fabric_root, options.env)

        using_config = os.path.join(package_root, options.env)
        project_root = os.path.dirname(package_root)

        try:
            packages_config = json.load(open(os.path.join(using_config, 'env.json'), 'r'))
        except ValueError:
            self.error("Invalid json syntax:%s" % os.path.join(using_config, 'env.json'))

        config = packages_config.get('deploy', {})

        # basic check
        if not config.get('user'):
            self.error("user must be set")

        user = config['user']
        repo = config.get('repo', get_repo())

        if repo.find('git') != 0:
            self.error("sorry,currently we only support git+ssh mode")

        github = config.get('github')

        project_name = github if github else os.path.basename(repo).replace('.git', '')
        private_key = config.get('private_key', '~/.ssh/.deploies/%s.rsa' % project_name)

        if project_root in private_key:
            self.error("for safety reason,we don't allow private_key path in project's path")

        command_list = []

        if not options.skip_deploy_key:
            command_list.append(lambda: self.upload_deploy_key(os.path.expanduser(private_key), user, github=github))

        if not options.skip_enable_services:
            command_list.append(lambda: self.enable_services())

        if not options.skip_requirements:
            command_list.append(lambda: self.install_requirements())

        if not options.skip_compile_templates:
            command_list.append(lambda: self.compile_templates())

        if not options.skip_upload_resources:
            command_list.append(lambda: self.upload_resources())

        command_list.append(lambda: self.reload())
        command_list.append(lambda: self.restart())
        execute(command_list)
        pass

    @classmethod
    def add_arguments(cls):
        """
        python web project deploy tool
        """
        return [
            # ('commit', dict(nargs='?', help='set which commit to deploy,default is latest version', )),
            (('--skip-deploy-key',), dict(action='store_true', help='skip upload deploy key', )),
            (('--skip-enable-services',), dict(action='store_true', help='skip enable system services', )),
            (('--skip-requirements',), dict(action='store_true', help='skip install requirements', )),
            (('--skip-compile-templates',), dict(action='store_true', help='skip compile templates', )),
            (('--skip-upload-resources',), dict(action='store_true', help='skip upload resources', )),
            (('--reload',), dict(nargs='*', help='set reload service', )),
            (('--restart',), dict(nargs='*', help='set restart service', )),
        ]
        pass

    pass
