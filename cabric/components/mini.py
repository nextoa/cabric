# -*- coding: utf-8 -*-

import os

from cliez.component import Component


class MiniComponent(Component):
    def check(self):
        rtn = os.system("pyminifier --version > /dev/null")
        return True if rtn == 0 else False

    def minifier(self, infile):

        outfile = self.options.outdir + infile.replace(self.options.indir, '')
        outdir = os.path.dirname(outfile)
        _, infile_extension = os.path.splitext(infile)

        if self.options.dry_run:
            self.warn(outfile, prefix="[dry-run]: ", suffix="")
            return

        # currently,if outdir is file, an error caused and we don't handle it.

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        if infile_extension in self.options.extension:
            cmd = "pyminifier {} > {}".format(infile, outfile)

            if self.options.prepend:
                cmd = cmd.replace('pyminifier',
                                  'pyminifier --prepend=%s' %
                                  self.options.prepend)
                pass

            if self.options.debug:
                self.logger.debug(cmd)

            os.system(cmd)
        else:
            with open(outfile, 'wb') as fw, open(infile, 'rb') as fr:
                fw.write(fr.read())
                pass
            pass
        pass

    def run(self, options):
        """
        :param options:
        :return:
        """
        if not self.check():
            self.error("please make sure you have installed pyminifier.")

        for path, subdirs, files in os.walk(options.indir):
            for name in files:
                self.minifier(os.path.join(path, name))

        if self.options.with_release:
            os.chdir(self.options.outdir)
            if os.path.exists("setup.py"):
                cmd = "python setup.py sdist upload -r %s" % \
                      self.options.with_release
                os.system(cmd)
                pass
            else:
                self.warn("no setup.py found,skip release")
            pass
        pass

    @classmethod
    def add_arguments(cls):
        """
        python web project deploy tool
        """
        return [
            (('indir',), dict(
                help='minifier root,default is current directory',
            )),
            (('outdir',), dict(
                help='minifier root,default is current directory',
            )),
            (('--with-release',),
             dict(help='release package to pypi server', )),
            (('--extension',),
             dict(nargs='+', default='.py',
                  help='file extension', )),
            (('--prepend',),
             dict(help='file extension', )),
            (('--dry-run',),
             dict(action='store_true',
                  help='show file list instead filter it', )),
        ]

    pass
