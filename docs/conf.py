import sys
import pathlib
import tomllib

from datetime import datetime


# -- Path setup --------------------------------------------------------------

THIS_DIR = pathlib.Path(__file__).parent.resolve()
PROJECT_ROOT = THIS_DIR.parent.resolve()

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
for path in (THIS_DIR, PROJECT_ROOT, PROJECT_ROOT / 'src'):
    sys.path.insert(0, str(path.resolve()))

import fca_api
from fca_api.__version__ import __version__

with open(PROJECT_ROOT / 'pyproject.toml', 'rb') as f:
    pyproject_data = tomllib.load(f)

# import pprint
# pprint.pprint(pyproject_data)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

author = pyproject_data['project']['authors'][0]['name']
copyright = f'{author}, {datetime.now().year}'
description = pyproject_data['project']['description']
github_url = 'https://github.com'
github_repo = pyproject_data['project']['urls']['Repository']
github_version = 'main'

pypi_project = 'https://pypi.org/project/fca-api/'
project = fca_api.__name__
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Define master TOC
master_doc = 'index'

# Native docs language
language = 'en'

# Minimum required version of Sphinx
#needs_sphinx >= '7.2.5'

# Set primary domain to null
primary_domain = None

# Global substitutions
rst_epilog = f"""
.. |author|                 replace:: **{author}**
.. |copyright|              replace:: **{copyright}**
.. |docs_url|               replace:: { pyproject_data['project']['urls']['Documentation'] }
.. |project|                replace:: **{project}**
.. |project_description|    replace:: {description}
.. |release|                replace:: **{release}**
.. |github_release_target|  replace:: https://github.com/release-art/fca-api/releases/tag/{release}
.. |pypi_release_target|    replace:: https://pypi.org/project/fca-api/{release}
"""

# Publish author(s)
show_authors = True

# Sphinx extensions: not all of these are used or required, but they are still
# listed here if requirements change.
extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.duration',
    'sphinx.ext.extlinks',
    'sphinx.ext.graphviz',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx_copybutton',
    'sphinx_design',
]

# Autodoc settings -
#     For more on all available autodoc defaults see
#         https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_default_options
autodoc_default_options = {
    'exclude-members': '',
    'member-order': 'bysource',
    'private-members': False,
    'special-members': '__init__,__new__'
}

# Sphinx autodoc autosummary settings
autosummary_generate = False

# Intersphinx mappings to reference external documentation domains - none required.
intersphinx_mapping = {}

# Static template paths
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
source_encoding = 'utf-8'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build',
                    'Thumbs.db',
                    '.DS_Store',]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of prefixes that are ignored when creating the module index. (new in Sphinx 0.6)
modindex_common_prefix = ["fca_api."]

doctest_global_setup = "import fca_api"

# If this is True, the ``todo`` and ``todolist`` extension directives
# produce output, else they produce nothing. The default is ``False``.
todo_include_todos = True

# -- Project file data variables ---------------------------------------------

# HTML global context for templates
html_context = {
    'authors': author,
    'copyright': copyright,
    'default_mode': 'auto',
    'doc_path': 'doc',
    'conf_path': 'doc/conf.py',
    'project': project,
    'project_description': description,
    'release': release,
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# General (non-theme) HTML output options
html_baseurl = 'https://docs.release.art/fca-api/'

# HTML theme options
html_theme = 'pydata_sphinx_theme'
html_theme_options = {
    "icon_links": [
        {
            # Label for this link
            "name": "GitHub",
            # URL where the link will redirect
            "url": github_repo,  # required
            # Icon class (if "type": "fontawesome"), or path to local image (if "type": "local")
            "icon": "fa-brands fa-github",
            # The type of image to be used (see below for details)
            "type": "fontawesome",
        },
        {
            "name": "PyPI",
            "url": pypi_project,
            "icon": "fa-brands fa-python",
            "type": "fontawesome",
        }
   ]
}

#html_logo = '_static/logo.png'

# Relative path (from the ``docs`` folder) to the static files folder - so
# ``_static`` should be one level below ``docs``.
html_static_path = ['_static']

# Custom CSS file(s) - currently source the Font Awesome CSS classes to support
# Font Awesome icons. for more information see:
#
#     https://sphinx-design.readthedocs.io/en/latest/badges_buttons.html#fontawesome-icons
#
html_css_files = [
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/7.0.1/css/all.min.css',
]

# Timestamp format for the last page updated time
html_last_updated_fmt = '%b %d, %Y'

# Show link to ReST source on HTML pages
html_show_sourcelink = True

# If true, the reST sources are included in the HTML build as _sources/<name>.
html_copy_source = True

# Output file base name for HTML help builder - use the project name
htmlhelp_basename = 'fca-api'
