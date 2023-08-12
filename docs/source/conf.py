# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath('../../dunderlab/django/timescaledbapp'))
# sys.path.insert(0, os.path.abspath('../../dunderlab/django'))
# sys.path.insert(0, os.path.abspath('../../dunderlab'))
# sys.path.insert(0, os.path.abspath('../../example'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Django App: RealTimeDB'
copyright = '2023, Yeison Cardona'
author = 'Yeison Cardona'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'nbsphinx',
    'dunderlab.docs',
]

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_logo = '_static/logo.svg'
html_favicon = '_static/favicon.ico'

html_theme = 'alabaster'
html_static_path = ['_static']

html_theme_options = {
    'caption_font_family': 'Noto Sans',
    'font_family': 'Noto Sans',
    'head_font_family': 'Noto Sans',
    'page_width': '1280px',
    'sidebar_width': '300px',
}

autodoc_mock_imports = [
    'timescale',
    'django',
    'django.db',
    'rest_framework',
    'django_filters',
]

dunderlab_maxdepth = 3
dunderlab_color_links = '#12c5a5'
dunderlab_code_reference = True
dunderlab_github_repository = 'https://github.com/dunderlab/python-django-timescaledbapp'

