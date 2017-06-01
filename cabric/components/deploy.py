# -*- coding: utf-8 -*-

import json
import os
from getpass import getpass

import requests
from Crypto.PublicKey import RSA
from cliez.component import Component
from fabric.context_managers import settings
from fabric.operations import put as fabric_put
from git import config as pygit

from cabric.utils import get_roots, bind_hosts, \
    execute, get_repo, put, run, \
    get_home, get_git_host, known_host, cd

try:
    input = raw_input
except NameError:
    pass


class DeployComponent(Component):
    def create_github_key(self, private_key, github, remote_user,
                          key_length=8192):

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
                access_token = git_config.get_value('github', 'token',
                                                    default='')
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
            response = requests.get(
                'https://api.github.com/repos/{}/keys'.format(github),
                auth=temp_config)
            if response.status_code != 200:
                self.warn("use `%s' method login to github is failed,"
                          "try next way." % v.__name__.replace('use_',
                                                               '').replace('_',
                                                                           '-')
                          )
                if self.options.debug:
                    self.warn("github-api"
                              " request: %s" % 'https://api.github.com'
                                               '/repos/{}/keys'.format(github))
                    self.warn(
                        "github-api status-code: %d" % response.status_code)
                    self.warn("github-api auth: %s" % ' '.join(temp_config))
                    self.warn("github-api return: %s" % response.text)
                    pass
                continue

            auth_config = temp_config
            keys = response.json
            key_title = remote_user + '@cabric'
            break

        if not auth_config:
            self.error("login github failed or project not exists.")

        try:
            uploaded_keys = [v for v in keys if v.get('title') == key_title]
        except TypeError:
            uploaded_keys = []

        # clean old key if exists
        for v in uploaded_keys:
            response = requests.delete('https://api.github.com'
                                       '/repos/{}/keys/{}'.format(github,
                                                                  v.get('id')),
                                       auth=auth_config)
            if response.status_code != 204:
                self.error("delete old deploy key failed,"
                           "please try it later."
                           "server response:\n%s" % response.text)
                pass

        # generate new key
        self.print_message(
            "Generating deploy key... this will cost about 1 minute...")
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

        response = requests.post(
            'https://api.github.com/repos/{}/keys'.format(github),
            data=json.dumps({
                'title': key_title,
                'key': pubkey.exportKey('OpenSSH'),
                'read_only': True,
            }), auth=auth_config)

        if response.status_code != 201:
            self.error(
                "create key failed.server response:\n%s" % response.text)
            pass

        pass

    def upload_deploy_key(self, private_key, remote_user, project_name):
        """
        upload deploy key

        :param string private_key: private key local path
            default is ~/.ssh/.deploies/`github`.rsa
        :param string remote_user: remote user name to deploy
        :param string project_name: a project name
        :param string github: github repo name
        :param bool force_renew: try to replace deploy
                    key when use auto-generate
        :param int key_length: must a legal ssh key length value.
                    default is 8192


        ..note::

            if you use github and want to
             use auto generate private-key feature.

            there is two ways can do this:

                - you must set access token in your ~/.gitconfig file
                - you must disable github two-factor authentication,
                    input your username and password.

            currently, we use `<remote_user>@cabric` as our deploy key name.
            so if you upload your key use to other purpose,
             don't use `@cabric` as key suffix.


            if github deploy key already exist and
            you want to replace deploy key. you must set `--fresh-new' option.


            cabric allow each machine deploy multiple github project,
            but disallow deploy same name project in one user.

            if you still want do this.
                - you can set github value if you use it.
                - deploy them in different remote user.


        ..note::

            currently, this only works on linux.

        :return:
        """

        if not os.path.exists(private_key):
            self.error(
                "deploy key `%s' is not exists,please set it." % private_key)

        if os.path.exists(private_key):
            self.print_message("upload deploy key...")
            remote_key = self.get_remote_key(remote_user, project_name)
            remote_key_root = os.path.dirname(remote_key)

            run('test -e {0} || mkdir -p {0}'.format(remote_key_root),
                remote_user)
            with settings(warn_only=True):
                run('chmod 700 -Rf {}'.format(remote_key_root), remote_user)

            fabric_put(private_key, remote_key)
            run('chmod 600 -f {}'.format(remote_key))
            run('chown {1} -f {0}'.format(remote_key, remote_user))
            pass

        pass

    def get_project_python(self, user, project_name):
        project_path = self.get_remote_project_path(user, project_name)
        with settings(warn_only=True):
            version = run("test -f {0}/.python-version &&"
                          " cat {0}/.python-version".format(project_path))
            version = version.strip("\n")
            return version
        pass

    def install_project_python(self, user, project_name):
        remote_version = self.get_project_python(user, project_name)
        if remote_version:
            run('pyenv install -s %s' % remote_version)
        pass

    def install_requirements(self, user, project_name, pip='pip'):
        """
        when requirements file exits. install it.

        :param user: remote user to deploy
        :param project_name: project name
        :return:
        """

        project_path = self.get_remote_project_path(user, project_name)
        python_version = self.get_project_python(user, project_name)

        requirement_files = [
            os.path.join(project_path, 'requirements.txt'),
            os.path.join(project_path, 'requirements', 'test.txt'),
            os.path.join(project_path, 'requirements', 'private.txt'),
        ]

        for f in requirement_files:
            # 有版本bug
            # " install -U  --upgrade-strategy only-if-needed -r {0} || "

            run("test -f {0} && /usr/local/var/pyenv/versions/{1}/bin/pip"
                " install -U  -r {0} || "
                "echo '{0} not exist,skip install...'".format(f,
                                                              python_version))
            pass

        requirement_files = [
            os.path.join(project_path, 'requirements-static.txt'),
            os.path.join(project_path, 'requirements', 'zip.txt'),
            os.path.join(project_path, 'requirements', 'private-static.txt'),
            os.path.join(project_path, 'requirements', 'test-static.txt'),
        ]

        for f in requirement_files:
            run("test -f {0} && /usr/local/var/pyenv/versions/{1}/bin/pip"
                " install -r {0} || "
                "echo '{0} not exist,skip install...'".format(f,
                                                              python_version))
            pass

        pass

    def migrate_db(self, user, project_name):
        """
        try migrate database

        :param user: remote user
        :param project_name: project name
        :return:
        """
        project_path = self.get_remote_project_path(user, project_name)

        with cd(project_path):
            run('test -f ./manage.py && python manage.py migrate'
                ' || echo "skip migrate database"')
            pass

        pass

    def compile_templates(self, user, project_name):
        """
        try compile pug template files

        ..note::

            cabric use project root as pug basedir root.
            if you don't use this path,
            use `--skip-compile-templates` to skip this progress.


        :param user: remote user
        :param project_name: project name
        :return:
        """
        project_path = self.get_remote_project_path(user, project_name)
        run('which pug && pug -E html -b {0} {0} '
            '|| echo "skip parser jade file"'.format(project_path))
        pass

    def upload_resources(self, user, project_name, working_root=None,
                         static_prefix=None):
        """
        upload static resoures file is exists.

        only works for django+nginx(start with nginx user) project.

        cabric will upload:

            - static    django resource directory
            - assets    webpack resource directory

        ..todo::
            use remote path to validate install

        :return:
        """

        remote_root = self.get_remote_project_path(user, project_name)

        working_root = working_root or os.getcwd()
        django_manage = os.path.join(working_root, 'manage.py')

        if not os.path.exists(django_manage):
            self.warn("not django project,skip upload resources")
            return

        with settings(warn_only=True):
            if run("test -f %s/manage.py" % remote_root).failed:
                self.warn("deploy project is not django project,"
                          "skip upload resources")
                return
            pass

        try:
            nginx_home = get_home('nginx')
        except ValueError:
            self.warn("remote server only support nginx "
                      "and must use nginx user start,"
                      "skip deploy static resources...")
            return

        static_prefix = static_prefix or ''
        nginx_static_root = os.path.join(nginx_home, static_prefix, 'static')

        # collect static files by user
        # fabric_local('python manage.py collectstatic --noinput')

        with settings(warn_only=True):
            run('test -e {0} || mkdir -p {0}'.format(nginx_static_root))

        static_root_list = [
            os.path.join(working_root, 'static'),
            os.path.join(working_root, 'assets')
        ]

        for v in static_root_list:
            if os.path.exists(v):
                put(v, nginx_static_root)
                pass
            pass

        pass

    def upload_javascripts(self, remote_user, project_name,
                           working_root=None):

        remote_path = self.get_remote_project_path(remote_user, project_name)
        working_root = working_root or os.getcwd()

        webpack_stats_file = os.path.join(working_root, 'javascripts',
                                          'webpack-stats.json')
        remote_javascripts_dir = os.path.join(remote_path, 'javascripts')

        with settings(warn_only=True):
            if os.path.exists(webpack_stats_file):
                if not run("test -d %s" % remote_javascripts_dir).failed:
                    put(webpack_stats_file, remote_javascripts_dir)
                pass

        pass

    def upgrade(self, remote_user, project_name,
                repo, branch, commit=None):
        """
        upgrade source code

        :param remote_user:deploy username
        :param project_name: project name
        :param repo:git repo address
        :param branch:which branch to deploy

        ..note::
            currently,if remote machine already cloned from repo,
            branch can't be change.

            if you really need to change branch.
            you have to remove remote project directory,
            do upgrade again.

        :param commit:which commit to deploy,default use latest commit,
            support tags

        ..note::
            commit or tag must be valid in branch


        :return:
        """

        host = get_git_host(repo)
        known_host(host, remote_user)

        remote_path = self.get_remote_project_path(remote_user, project_name)
        deploy_key = self.get_remote_key(remote_user, project_name)

        with settings(warn_only=True):
            if run("test -d %s/.git" % remote_path).failed:
                parent_path = os.path.dirname(remote_path)
                run('test -d {0} || mkdir {0}'.format(parent_path),
                    remote_user)
                with cd(parent_path):
                    run('git clone {} -b {} {}'.format(repo, branch,
                                                       remote_path),
                        remote_user)
                    run("cd {} && git config core.fileMode false".format(
                        remote_path), remote_user)

        run("cd {} && git pull origin {}".format(remote_path, branch),
            remote_user)
        run("cd {} && git pull origin {} --tags".format(remote_path, branch),
            remote_user)

        if commit:
            # make sure there is no merge commit on remote server
            # run("cd {} && git checkout -- .".format(remote_path),
            #     remote_user)
            run("cd {} && git checkout {}".format(remote_path, commit),
                remote_user)

        pass

    def get_remote_key(self, user, project_name):
        """
        ..note::
            currently,we force use ~/.ssh/id_rsa
            if you saved more than on project deploy in same remote_user.
            use `--with-deploy-key' to replace remote key.


        ..todo::
            make sure only one project is deploying


        :param user:
        :param project_name:
        :return:
        """

        # return '{}/.cabric/{}.rsa'.format(get_home(user), project_name)
        return '%s/.ssh/id_rsa' % get_home(user)

    def get_remote_project_path(self, user, project_name):
        """
        ..note::
            it must be called in lambda

        :param user:
        :param project_name:
        :return:
        """

        return os.path.join(get_home(user), project_name)

    def run(self, options):
        """ workflow
        * basic check

            - user value must be set
            - currently, repo only support git
            - for safety reason,we don't allow private_key path
              occur in project path

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

        if options.verbose == 3:
            options.debug = True

        package_root, _, fabric_root = get_roots(options.dir)
        bind_hosts(fabric_root, options.env, options.parallel)

        using_config = os.path.join(package_root, options.env)
        project_root = os.path.dirname(package_root)

        try:
            packages_config = json.load(
                open(os.path.join(using_config, 'env.json'), 'r'))
        except ValueError:
            self.error("Invalid json syntax:%s" % os.path.join(using_config,
                                                               'env.json'))

        config = packages_config.get('deploy', {})

        # basic check
        if not config.get('user'):
            self.error("user must be set")

        user = config['user']
        repo = config.get('repo', get_repo())
        branch = config.get('branch', 'master')

        if repo.find('git') != 0:
            self.error("sorry,currently we only support git+ssh mode")

        github = config.get('github')

        project_name = github if github else os.path.basename(repo).replace(
            '.git', '')
        private_key = os.path.expanduser(config.get('private_key',
                                                    '~/.ssh/.deploies/'
                                                    '%s.rsa' % project_name))

        if project_root in private_key:
            self.error("for safety reason,"
                       "we don't allow private_key path in project's path")

        command_list = []

        if options.with_deploy_key:
            if options.force_renew or (
                    not os.path.exists(private_key) and github):
                self.create_github_key(private_key, github, user)

            command_list.append(
                lambda: self.upload_deploy_key(private_key, user,
                                               project_name))

        if not options.skip_source_code:
            command_list.append(
                lambda: self.upgrade(user, project_name, repo, branch,
                                     commit=options.commit))

        if not options.skip_requirements:
            command_list.append(
                lambda: self.install_project_python(user, project_name))
            command_list.append(
                lambda: self.install_requirements(user, project_name))

        if not options.skip_compile_templates:
            command_list.append(
                lambda: self.compile_templates(user, project_name))

        if not options.skip_migrate:
            command_list.append(
                lambda: self.migrate_db(user, project_name))

        if not options.skip_upload_resources:
            command_list.append(
                lambda: self.upload_resources(user, project_name,
                                              static_prefix=config.get(
                                                  'static-prefix')))
            command_list.append(
                lambda: self.upload_javascripts(user, project_name))

        execute(command_list)
        pass

    @classmethod
    def add_arguments(cls):
        """
        python web project deploy tool
        """
        return [
            (('commit',), dict(nargs='?',
                               help='set which commit to deploy,'
                                    'default is latest version', )),
            (('--parallel', '-P'), dict(action='store_true',
                                        help='default to parallel '
                                             'execution method', )),
            (('--with-deploy-key',),
             dict(action='store_true', help='upload deploy key', )),
            (('--force-renew',), dict(action='store_true',
                                      help='only works when user '
                                           'set github value', )),
            (('--skip-source-code',),
             dict(action='store_true', help='skip upgrade source code', )),
            (('--skip-requirements',),
             dict(action='store_true', help='skip install requirements', )),
            (('--skip-compile-templates',),
             dict(action='store_true', help='skip compile templates', )),
            (('--skip-migrate',),
             dict(action='store_true', help='skip migrate', )),
            (('--skip-upload-resources',),
             dict(action='store_true', help='skip upload resources', )),
        ]
        pass

    pass
