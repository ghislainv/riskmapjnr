#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=2.7
# license         :GPLv3
# ==============================================================================

# Import
import io
import re
from setuptools import setup, find_packages


# find_version
def find_version(pkg_name):
    """Finding package version."""
    with open(f"{pkg_name}/__init__.py", encoding="utf-8") as init_file:
        init_text = init_file.read()
    _version = (re.search('^__version__\\s*=\\s*"(.*)"',
                          init_text, re.M)
                .group(1))
    return _version


version = find_version("riskmapjnr")

# reStructuredText README file
with io.open("README.rst", encoding="utf-8") as f:
    long_description = f.read()

# Project URLs
project_urls = {
    'Documentation': 'https://ecology.ghislainv.fr/riskmapjnr',
    'Source': 'https://github.com/ghislainv/riskmapjnr',
    'Traker': 'https://github.com/ghislainv/riskmapjnr/issues',
}

# Setup
setup(name="riskmapjnr",
      version=version,
      author="Ghislain Vieilledent",
      author_email="ghislain.vieilledent@cirad.fr",
      url="https://github.com/ghislainv/riskmapjnr",
      license="GPLv3",
      description="Mapping deforestation risk following JNR methodology",
      long_description=long_description,
      long_description_content_type="text/x-rst",
      classifiers=["Development Status :: 4 - Beta",
                   "License :: OSI Approved :: GNU General Public License v3 "
                   "(GPLv3)",
                   "Programming Language :: Python :: 3",
                   "Operating System :: OS Independent",
                   "Topic :: Scientific/Engineering :: Bio-Informatics"],
      keywords="carbon deforestation emissions forests jnr map probability"
               "redd risk tropics vcs",
      python_requires=">=3.6",
      packages=find_packages(),
      package_dir={"riskmapjnr": "riskmapjnr"},
      package_data={
          "riskmapjnr": ["data/fcc123_GLP.tif",
                         "data/ctry_border_GLP.gpkg"]
      },
      include_package_data=True,
      entry_points={
          "console_scripts": ["riskmapjnr = riskmapjnr.riskmapjnr:main"]
      },
      install_requires=[
          "gdal",
          "numpy",
          "matplotlib",
          "pandas",
          "scipy",
      ],
      extras_require={
          "interactive": ["jupyter", "geopandas", "descartes", "folium",
                          "tabulate"]
      },
      zip_safe=False)

# End
