# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import re  # Regular expression
sys.path.insert(0, os.path.abspath(".."))


# -- Project information -----------------------------------------------------

project = "riskmapjnr"
copyright = "2024, Ghislain Vieilledent"
author = "Ghislain Vieilledent"

# The full version, including alpha/beta/rc tags
with open("../riskmapjnr/__init__.py", encoding="utf-8") as init_file:
    init_text = init_file.read()
version = re.search('^__version__\\s*=\\s*"(.*)"', init_text, re.M).group(1)
release = version

# -- Sphynx options ----------------------------------------------------------
add_module_names = False
add_function_parentheses = True

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode',
              'sphinx.ext.mathjax']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'  # 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    'description': "Map of deforestation risk following JNR methodology",
    'code_font_family': "'Roboto Mono', 'Consolas', 'Menlo', "
                        "'Deja Vu Sans Mono', "
                        "'Bitstream Vera Sans Mono', monospace",
    'font_family': "'Lato', Arial, sans-serif",
    'head_font_family': "'Lato', Arial, sans-serif",
    'body_text': '#000',
    'sidebar_header': '#4B4032',
    'sidebar_text': '#49443E',
    'github_banner': 'false',
    'github_user': 'ghislainv',
    'github_repo': 'riskmapjnr',
    'github_button': 'true',
    'github_type': 'star',
    'travis_button': 'false',
    'codecov_button': 'false',
    'logo': 'logo-riskmapjnr.svg',
    'logo_name': 'true',
    'page_width': '1300px',
    'body_max_width': 'auto',
    'fixed_sidebar': 'true'
}

html_favicon = '_static/favicon.ico'
html_title = "riskmapjnr — Map of deforestation risk following JNR methodology"
html_short_title = 'riskmapjnr'
html_base_url = 'https://ecology.ghislainv.fr/riskmapjnr/'


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# End of file
