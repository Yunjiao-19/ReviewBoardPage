# -*- coding: utf-8 -*-
#
# Review Board Manual build configuration file, created by
# sphinx-quickstart on Thu Feb 12 02:10:34 2009.
#
# This file is execfile()d with the current directory set to its containing
# dir.
#
# The contents of this file are pickled, so don't put values in the namespace
# that aren't pickleable (module imports are okay, they're removed
# automatically).
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.
import logging
import os
import sys
from datetime import datetime
sys.path.append(os.path.abspath('_ext'))

# Set this up to parse Django-driven code.
sys.path.insert(0, os.path.abspath(os.path.join(__file__, '..', '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(__file__, '..', '..', '..',
                                                '..', 'djblets')))
sys.path.insert(0, os.path.dirname(__file__))

# The nightly docs system needs to inject certain builds of Djblets and Django.
# PYTHONPATH will only append, meaning that the system-installed ones will
# be looked up first, so allow us to append instead.
sys.path = os.getenv('PYTHONPATH_PREPEND', '').split(':') + sys.path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reviewboard.settings')

import reviewboard
from reviewboard.dependencies import (django_doc_major_version,
                                      djblets_doc_major_version)

from beanbag_docutils.sphinx.ext.github import github_linkcode_resolve


# Set up logging. Sphinx won't set up a root logger for us, and we want to
# avoid errors about not having handlers there.
logging.basicConfig()


# If your extensions are in another directory, add it here. If the directory
# is relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
#sys.path.append(os.path.abspath('.'))


# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.linkcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'beanbag_docutils.sphinx.ext.autodoc_utils',
    'beanbag_docutils.sphinx.ext.django_utils',
    'beanbag_docutils.sphinx.ext.extlinks',
    'beanbag_docutils.sphinx.ext.http_role',
    'beanbag_docutils.sphinx.ext.ref_utils',
    'beanbag_docutils.sphinx.ext.retina_images',
    'webapidocs',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8'

# The master toctree document.
master_doc = 'contents'

# General information about the project.
project = 'Review Board Manual'
copyright = '2009-%s, Beanbag, Inc.' % datetime.now().year

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '.'.join([str(i) for i in reviewboard.__version_info__[:2]])
# The full version, including alpha/beta/rc tags.
release = reviewboard.get_version_string()

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of documents that shouldn't be included in the build.
#unused_docs = []

# List of directories, relative to source directory, that shouldn't be searched
# for source files.
exclude_trees = ['_build', '_templates']

# The reST default role (used for this markup: `text`) to use for all
# documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = False

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# Disable warning of unknown referenced options.
suppress_warnings = ['ref.option']


# Options for HTML output
# -----------------------

html_theme = 'classic'

# The style sheet to use for HTML and HTML Help pages. A file of that name
# must exist either in Sphinx' static/ path, or in one of the custom paths
# given in html_static_path.
html_style = 'classic.css'

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = "Review Board Manual"

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "classic.css" will overwrite the builtin "classic.css".
#html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_use_modindex = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, the reST sources are included in the HTML build as _sources/<name>.
html_copy_source = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# If nonempty, this is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = ''

# Output file base name for HTML help builder.
htmlhelp_basename = 'ReviewBoardManual'


# Options for LaTeX output
# ------------------------

# The paper size ('letter' or 'a4').
#latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
#latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class
# [howto/manual]).
latex_documents = [
  ('users/index', 'UserManual.tex', 'Review Board User Manual',
   'Beanbag, Inc.', 'manual', False),
  ('admin/index', 'AdminGuide.tex', 'Review Board Administration Guide',
   'Beanbag, Inc.', 'manual', False),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# Additional stuff for the LaTeX preamble.
#latex_preamble = ''

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_use_modindex = True

latex_show_urls = 'inline'
latex_show_pagerefs = True


# Determine the branch or tag used for code references.
rb_version = reviewboard.VERSION

if rb_version[3] == 'final' or rb_version[5] > 0:
    git_branch = 'release-%s.%s' % (rb_version[0], rb_version[1])

    if reviewboard.is_release():
        if rb_version[2]:
            git_branch += '.%s' % rb_version[2]

            if rb_version[3]:
                git_branch += '.%s' % rb_version[3]

        if version[4] != 'final':
            git_branch += rb_version[4]

            if rb_version[5]:
                git_branch += '%d' % rb_version[5]
    else:
        git_branch += '.x'
else:
    git_branch = 'master'


# Check whether reviewboard.org intersphinx lookups should use the local
# server.
if os.getenv('DOCS_USE_LOCAL_RBWEBSITE') == '1':
    rbwebsite_url = 'http://localhost:8081'
else:
    rbwebsite_url = 'https://www.reviewboard.org'


django_doc_base_url = ('http://django.readthedocs.io/en/%s.x/'
                       % django_doc_major_version)


intersphinx_mapping = {
    'django': (django_doc_base_url, None),
    'djblets': ('%s/docs/djblets/%s/'
                % (rbwebsite_url, djblets_doc_major_version),
                None),
    'python': ('https://docs.python.org/3', None),
    'rbtools': ('%s/docs/rbtools/latest/' % rbwebsite_url, None),
    'rbcontributing': ('%s/docs/codebase/dev/' % rbwebsite_url, None),
}


extlinks = {
    'djangodoc': ('%s%%s.html' % django_doc_base_url, None),
    'backbonejs': ('http://backbonejs.org/#%s', 'Backbone.'),
    'rbintegration': ('https://www.reviewboard.org/integrations/%s', ''),
    'rbsource': ('https://github.com/reviewboard/reviewboard/blob/%s/%%s'
                 % git_branch,
                 ''),
    'rbtree': ('https://github.com/reviewboard/reviewboard/tree/%s/%%s'
               % git_branch,
               ''),
}

todo_include_todos = True

autodoc_member_order = 'bysource'
autoclass_content = 'class'
autodoc_default_flags = [
    'members',
    'special-members',
    'undoc-members',
    'show-inheritance',
]


autodoc_excludes = {
    '*': [
        '__dict__',
        '__doc__',
        '__module__',
        '__weakref__',
    ],
    'class': [
        # Common to models.
        'DoesNotExist',
        'MultipleObjectsReturned',

        # Common to forms.
        'base_fields',
        'media',
    ],
}

autosummary_generate = True

napoleon_beanbag_docstring = True
napoleon_google_docstring = False
napoleon_numpy_docstring = False

webapi_docname_map = {
    'o-auth-application': 'oauth-application',
    'o-auth-token': 'oauth-token',
}


def linkcode_resolve(domain, info):
    return github_linkcode_resolve(domain=domain,
                                   info=info,
                                   allowed_module_names=['reviewboard'],
                                   github_org_id='reviewboard',
                                   github_repo_id='reviewboard',
                                   branch=git_branch)