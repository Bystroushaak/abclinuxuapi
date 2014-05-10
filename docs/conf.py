# -*- coding: utf-8 -*-
#
import os
import sys
import urllib
import os.path

sys.path.insert(0, os.path.normpath(os.path.abspath('.') + '/..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinxcontrib.napoleon',
    'sphinx.ext.intersphinx'
]

intersphinx_mapping = {
    'python': ('http://docs.python.org/2.7', None),
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True

# Document all methods in classes
autoclass_content = 'both'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'API for http://abclinuxu.cz'
copyright = u'2014 Bystroushaak'

# The full version, including alpha/beta/rc tags.
try:
    # read data from CHANGES.rst
    from __init__ import getVersion
    release = getVersion(open("../CHANGELOG.rst").read())
except:
    # this is here specially for readthedocs, which downloads only docs, not
    # other files
    fh = urllib.urlopen("https://pypi.python.org/pypi/" + project + "/")
    release = filter(lambda x: "<title>" in x, fh.read().splitlines())
    release = release[0].split(":")[0].split()[1]

# The short X.Y version.
version = ".".join(release.split(".")[:2])

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'default'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = True

# Output file base name for HTML help builder.
htmlhelp_basename = 'abclinuxu'
