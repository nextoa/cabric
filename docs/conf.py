# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, __file__.rsplit('/', 2)[0])

from cabric import version

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinxcontrib.programoutput',
]

templates_path = ['_templates']

source_parsers = {
    '.md': 'recommonmark.parser.CommonMarkParser',
}
source_suffix = ['.rst', '.md']
source_encoding = 'utf-8-sig'
master_doc = 'index'

project = 'Dream'
copyright = u'2017, WANG WENPEI'
author = 'WANG WENPEI'
show_authors = True

release = version

language = None

today_fmt = '%Y-%m-%d'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

pygments_style = 'sphinx'
todo_include_todos = False

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'https://docs.python.org/': None}

html_static_path = ['_static']
html_search_options = {'type': 'default'}

user_theme = os.environ.get('SPHINX_THEME', 'guzzle')

if user_theme == 'guzzle':
    import guzzle_sphinx_theme

    html_theme_path = guzzle_sphinx_theme.html_theme_path()
    html_theme = 'guzzle_sphinx_theme'

    # Register the theme as an extension to generate a sitemap.xml
    extensions.append("guzzle_sphinx_theme")

    # Guzzle theme options (see theme.conf for more information)
    html_theme_options = {
        # Set the name of the project to appear in the sidebar
        "project_nav_name": "Cabric",
        "google_analytics_account": "e6fb1684262fb4a16e67cbce449314d4"
    }
