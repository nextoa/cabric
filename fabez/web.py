# -*- coding: utf-8 -*-


# -*- coding: utf-8 -*-

from cliez.loader import ArgLoader
import os, sys
import traceback

from tornadoez.embed import embed

try:
    import pkg_resources
except:
    pass


def main():
    importer = __import__

    a = ArgLoader((
        ('Useage: cabric project1,project2,projectN'),
        '',
        'Arguments',
        '    project1...N a project depends on fabez style file ',
        '',
        'Options:',
        ('--host:', 'tornado bind host default is None'),
        ('--port:', 'bind port to work,default is 6001'),
        ('--help:', 'print help document'),
    ))

    if a.options.get('--help'):
        print a
        return

    try:
        project_list = a.argv[1].split(',')
    except:
        print(traceback.format_exc())
        raise Exception("Please set your project list or use `--help` to see help manual.")
        pass

    port = int(a.options.get('port', '6001'))

    # projects = [v for v in project_list: if v]

    projects=[]

    for v in project_list:
        projects.append(os.path.expanduser(v))


    print(projects)

    a.argv[1]='pro'
    embed(a)

    pass


if __name__ == '__main__':
    main()
    pass


