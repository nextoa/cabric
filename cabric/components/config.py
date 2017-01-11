# -*- coding: utf-8 -*-

import json
import os

from cliez.component import Component

from cabric.dns.dnspod import DNSPod
from cabric.utils import get_roots, mirror_put, run, bind_hosts, execute, get_platform, put, fabric_settings, env

try:
    from shlex import quote as shell_quote
except ImportError:
    from pipes import quote as shell_quote


class ConfigComponent(Component):
    def enable_services(self, services):
        """
        :param list services: service list
        :return:
        """

        if get_platform() == 'centos':
            # run('systemctl disable %s' % ' '.join(services))
            run('systemctl enable %s' % ' '.join(services))
        else:
            self.warn("not support platform.no services enabled.")
        pass

    def reload(self, reloads, all_services):
        if all_services and reloads:
            services = [v for v in reloads if v in all_services]
            run('systemctl reload %s' % ' '.join(services))
        pass

    def restart(self, restarts, all_services):

        if all_services and restarts:
            services = [v for v in restarts if v in all_services]
            if services:
                run('systemctl restart %s' % ' '.join(services))
            else:
                self.warn("restart progress actived,but no restart service found.")
        pass

    def upload_crontab(self, config, env_option, crontab_root):
        user = config.get('user')
        crontab_file = config.get('crontab', env_option + '.conf')

        if not user:
            self.warn("no user found,skip deploy crontab file `%s'" % config.get(crontab_file))
            return

        crontab_path = os.path.join(crontab_root, 'config', 'crontab', crontab_file)

        if os.path.exists(crontab_path):
            put(crontab_path, '/tmp/cabric_crontab')
            run('crontab < /tmp/cabric_crontab', user)
            run('rm -f /tmp/cabric_crontab')
            pass
        else:
            self.warn("crontab file `%s' not found. skip to install it" % crontab_path)

        pass

    def upload_crontabs(self, crons_config, env_option, crontab_root):
        """
        because command list is execute after lambda define.

        if we add upload_crontab directly, the value of crontab_config will always be last item.

        :param crons_config:
        :param env_option:
        :param crontab_root:
        :return:
        """

        for crontab_config in crons_config:
            self.upload_crontab(crontab_config, env_option, crontab_root)

        pass

    def set_hostname(self):
        """
        set machine hostname
        :return:
        """
        try:
            host_index = env.hosts.index(env.host_string)

            if env.host_names[host_index]:
                run("hostnamectl set-hostname %s" % env.host_names[host_index])
                run("hostnamectl set-hostname %s --pretty" % env.host_names[host_index])
                run("hostnamectl set-hostname %s --static" % env.host_names[host_index])
                run("systemctl restart systemd-hostnamed")
                pass
        except IndexError:
            self.warn("can't find current hostname config:%s" % env.host_string)
            pass

        pass

    def set_hosts(self, records):
        """
        ..experiment::

                use env-config to handle hosts file seems a bad idea.

                we already user upload hosts file, it's simple to use,
                user only need to care don't overwrite their hosts

                and if we want to support something like:

                    * delete hosts
                    * update ip

                we need do lot of work to support this.

        :param records:
        :return:
        """

        def set_host(ip, host):
            """
            if you want to use this feature for old file, use 4 space.

            limit:
                only support one2one relation

            :param ip:
            :param host:
            :return:
            """
            with fabric_settings(warn_only=True):
                match = '%s    %s' % (ip, host)
                if run('grep "%s" /etc/hosts' % match).failed:
                    run('echo "%s" >> /etc/hosts' % match)
                    # elif run('grep "%s" /etc/hosts' % host):
                    # sed -i -e "s//g" ???
                    #     pass
            pass

        [set_host(v[0], v[1]) for v in records]
        pass

    def set_dns_list(self, dns_list):

        for dns in dns_list:
            isp = dns.get('isp')

            if isp == '/etc/hosts':
                self.set_hosts(dns.get('records'))
            elif isp == 'dnspod.cn':
                domain = dns.get('domain')
                if domain:
                    dns_client = DNSPod()
                    dns_client.bind_domain(domain)
                    for record in dns.get('records', []):
                        dns_client.bind_record(**record)
                        pass
                    pass
            else:
                self.error("illegal dns config:%s" % dns)
                pass
            pass

        pass

    def set_timezone(self, timezone):
        """
        should limit user input

        ..todo:
            danger if we don't limit timezone.
            something like this  `Asian/Shanghai && rm -rf /`

        timedatectl list-timezones
        timedatectl

        :param timezone:
        :return:
        """
        run('timedatectl set-timezone %s' % timezone)
        pass

    def run(self, options):
        """
        plan feature

            use rsync instead fabric put.
            but rsync will may cause permission errors.
            we should fix this.

        :param options:
        :return:
        """

        package_root, config_root, fabric_root = get_roots(options.dir)
        bind_hosts(fabric_root, options.env)

        # try upload repo config if it can recognize
        using_config = os.path.join(package_root, options.env)
        stage_config = os.path.join(config_root, options.env)

        if not options.skip_upload:
            mirror_put(stage_config, '/')

        try:
            env_config = json.load(open(os.path.join(using_config, 'env.json'), 'r'))
        except ValueError:
            self.error("Invalid json syntax:%s" % os.path.join(using_config, 'env.json'))
            pass

        command_list = []

        if not options.skip_hostname:
            command_list.append(lambda: self.set_hostname())
            pass

        timezone = env_config.get('timezone')

        if not options.skip_timezone and timezone:
            command_list.append(lambda: self.set_timezone(timezone))
            pass

        dns_list = env_config.get('dns-list')

        if not options.skip_dns and dns_list:
            command_list.append(lambda: self.set_dns_list(dns_list))
            pass

        services = env_config.get('services', [])

        if not options.skip_enable_services and services:
            command_list.append(lambda: self.enable_services(services))

        if options.reload:
            command_list.append(lambda: self.reload(options.reload, services))
            pass

        if options.restart:
            command_list.append(lambda: self.restart(options.restart, services))
            pass

        crons_config = env_config.get('crons', [])
        if not options.skip_crontab and crons_config:
            command_list.append(lambda: self.upload_crontabs(crons_config, options.env, options.dir))
            pass

        execute(command_list)
        pass

    @classmethod
    def add_arguments(cls):
        """
        sub parser document
        """
        return [
            (('--skip-enable-services',), dict(action='store_true', help='skip enable system services', )),
            (('--skip-upload',), dict(action='store_true', help='skip upload config files', )),
            (('--skip-crontab',), dict(action='store_true', help='skip upload crontab', )),
            (('--skip-timezone',), dict(action='store_true', help='skip set timezone', )),
            (('--skip-hostname',), dict(action='store_true', help='skip set hostname', )),
            (('--skip-dns',), dict(action='store_true', help='skip config dns', )),
            (('--reload',), dict(nargs='+', help='set reload service', )),
            (('--restart',), dict(nargs='+', help='set restart service', )),
        ]

    pass
