..
   # ==============================================================================
   # author          :Ghislain Vieilledent
   # email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
   # web             :https://ecology.ghislainv.fr
   # license         :GPLv3
   # ==============================================================================

.. image:: https://ecology.ghislainv.fr/riskmapjnr/_static/logo-riskmapjnr.svg
   :align: right
   :target: https://ecology.ghislainv.fr/riskmapjnr
   :alt: Logo riskmapjnr
   :width: 140px

``riskmapjnr`` Python package
*****************************

|Python version| |PyPI version| |GitHub Actions| |License| |Zenodo|


Overview
========

The ``riskmapjnr`` Python package can be used to obtain **maps of the
spatial risk of deforestation and forest degradation** following the
methodology developed in the context of the Jurisdictional and Nested
REDD+ (`JNR`_) and using only a forest cover change map as input.

.. _JNR:
   https://verra.org/project/jurisdictional-and-nested-redd-framework/

.. image:: https://ecology.ghislainv.fr/riskmapjnr/_static/riskmapjnr-example.png
   :align: center
   :target: https://ecology.ghislainv.fr/riskmapjnr
   :alt: riskmapjnr-example
   :width: 1300px


Statement of Need
=================

The `VCS`_ (Verified Carbon Standard) program allows certified
projects to turn their greenhouse gas (GHG) emission reductions and
removals into tradable carbon credits. Since its launch in 2006, the
VCS program has grown into the world's largest voluntary GHG program.

In the forest sector, programs to mitigate GHG emissions across entire
national or subnational jurisdictions (called `REDD+`_ programs,
i.e. programs aiming at Reducing Emissions from Deforestation and
Forest Degradation) can be accounted for and credited using a
jurisdictional-scale framework, the Jurisdictional and Nested REDD+
(`JNR`_) framework. JNR integrates government-led and project-level
REDD+ activities and establishes a clear pathway for subnational- and
project-level activities to be incorporated within broader REDD+
programs. The JNR framework ensures all projects and other reducing
emissions from deforestation and degradation activities in a given
jurisdiction are developed using consistent baselines and crediting
approaches. They mitigate the risk of "leakage", i.e. the displacement
of emission-causing activities to areas outside the project boundary,
by monitoring emissions across an entire jurisdictional area.

The `JNR Risk Mapping Tool`_ is a "benchmark" methodology that
provides a standardized approach for developing deforestation and
forest degradation risk maps for users of the `JNR Allocation Tool`_
in the context of Jurisdictional and Nested REDD+ (JNR)
requirements. The methodology allows deriving a map of the
deforestation (or degradation) risk based on a minimal spatial
information provided by the past deforestation (or degradation) map at
the jurisdictional scale.

The `JNR Risk Mapping Tool`_ allows the creation of categorical and
spatially static maps whose categories represent different levels of
risk of deforestation or forest degradation in the validity period of
the Forest Reference Emissions Level (FREL) and throughout the
jurisdictional geographical boundaries. In the `JNR Allocation Tool`_,
the level of risk determines how the jurisdictional FREL is spatially
distributed to nested lower-level jurisdictional programs and
projects.

While the `JNR Risk Mapping Tool`_ methodology favors simplicity,
obtaining the risk map is not straightforward. The approach requires
several geoprocessing steps on raster data that can be large,
i.e. covering large spatial extent (eg. national scale) at high
spatial resolution (eg. 30 m). The ``riskmapjnr`` Python package
includes functions to perform these geoprocessing steps and derive a
risk map on any jurisdiction and at any spatial resolution following
the `JNR Risk Mapping Tool`_ methodology.

.. _VCS:
   https://verra.org/project/vcs-program/

.. _REDD+:
   https://redd.unfccc.int/

.. _JNR:
   https://verra.org/project/jurisdictional-and-nested-redd-framework/
   
.. _JNR Risk Mapping Tool:
   https://verra.org/wp-content/uploads/2021/04/DRAFT_JNR_Risk_Mapping_Tool_15APR2021.pdf

.. _JNR Allocation Tool:
   https://verra.org/wp-content/uploads/2021/04/JNR_Allocation_Tool_Guidance_v4.0.pdf

Installation
============

You will need several dependencies to run the ``riskmapjnr`` Python
package. The best way to install the package is to create a Python
virtual environment, either through ``conda`` (recommended) or
``virtualenv``.

Using ``conda`` (recommended)
+++++++++++++++++++++++++++++

You first need to have ``miniconda3`` installed (see `here
<https://docs.conda.io/en/latest/miniconda.html>`__).

Then, create a conda environment (details `here
<https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html>`__)
and install the ``riskmapjnr`` package with the following commands:

.. code-block:: shell
		
   conda create --name conda-rmj -c conda-forge python=3 gdal numpy matplotlib pandas pip scipy --yes
   conda activate conda-rmj
   pip install riskmapjnr # For PyPI version
   # pip install https://github.com/ghislainv/riskmapjnr/archive/master.zip # For GitHub dev version
   # conda install -c conda-forge sphinx flake8 jedi jupyter geopandas descartes folium --yes  # Optional additional packages

To deactivate and delete the conda environment:

.. code-block:: shell
		
   conda deactivate
   conda env remove --name conda-rmj

Using ``virtualenv``
++++++++++++++++++++

You first need to have the ``virtualenv`` package installed (see `here <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/>`__).

Then, create a virtual environment and install the ``riskmapjnr``
package with the following commands:

.. code-block:: shell

   cd ~
   mkdir venvs # Directory for virtual environments
   cd venvs
   virtualenv --python=/usr/bin/python3 venv-rmj
   source ~/venvs/venv-rmj/bin/activate
   # Install numpy first
   pip install numpy
   # Install gdal (the correct version) 
   pip install --global-option=build_ext --global-option="-I/usr/include/gdal" gdal==$(gdal-config --version)
   pip install riskmapjnr # For PyPI version, this will install all other dependencies
   # pip install https://github.com/ghislainv/riskmapjnr/archive/master.zip # For GitHub dev version
   # pip install sphinx flake8 jedi jupyter geopandas descartes folium # Optional additional packages

To deactivate and delete the virtual environment:

.. code-block:: shell
		
   deactivate
   rm -R ~/venvs/venv-rmj # Just remove the repository

Installation testing
++++++++++++++++++++

You can test that the package has been correctly installed using the
command ``riskmapjnr`` in a terminal:

.. code-block:: shell

  riskmapjnr

This should return a short description of the ``riskmapjnr`` package
and the version number:

.. code-block:: shell

  # riskmapjnr: Map of deforestation risk following JNR methodology.
  # https://ecology.ghislainv.fr/riskmapjnr/
  # riskmapjnr version x.x.

You can also test the package executing the commands in the `Get
started
<https://ecology.ghislainv.fr/riskmapjnr/notebooks/get_started.html>`__
tutorial.
   
Main functionalities
====================

The ``riskmapjnr`` package includes functions to:

1. Estimate the distance to forest edge beyond which the deforestation
   risk is negligible: ``dist_edge_threshold()``.
2. Compute local deforestation rates using a moving window whose size
   can vary: ``local_defor_rate()``.
3. Transform local deforestation rates into categories of
   deforestation risks using several slicing algorithms:
   ``set_defor_cat_zero()`` and ``defor_cat()``
4. Validate maps of deforestation risk and select the map with the
   higher accuracy: ``defrate_per_cat()`` and ``validation()``.

The ``riskmapjnr`` package uses several known Python scientific
packages such as ``NumPy``, ``SciPy``, and ``Pandas`` for fast matrix
and vector operations and ``gdal`` for processing georeferenced raster
data. Raster data are divided into blocks of data for in-memory
processing. Such an approach allow processing large raster files with
large geographical extents (e.g. country scale) and high spatial
resolutions (eg. 30 m).

Contributing
============

The ``riskmapjnr`` Python package is Open Source and released under
the `GNU GPL version 3 license
<https://ecology.ghislainv.fr/riskmapjnr/license.html>`__. Anybody
who is interested can contribute to the package development following
our `Community guidelines
<https://ecology.ghislainv.fr/riskmapjnr/contributing.html>`__. Every
contributor must agree to follow the project's `Code of conduct
<https://ecology.ghislainv.fr/riskmapjnr/code_of_conduct.html>`__.


.. |Python version| image:: https://img.shields.io/pypi/pyversions/riskmapjnr?logo=python&logoColor=ffd43b&color=306998
   :target: https://pypi.org/project/riskmapjnr
   :alt: Python version

.. |PyPI version| image:: https://img.shields.io/pypi/v/riskmapjnr
   :target: https://pypi.org/project/riskmapjnr
   :alt: PyPI version

.. |GitHub Actions| image:: https://github.com/ghislainv/riskmapjnr/actions/workflows/python-package.yml/badge.svg
   :target: https://github.com/ghislainv/riskmapjnr/actions/workflows/python-package.yml
   :alt: GitHub Actions
	 
.. |License| image:: https://img.shields.io/badge/licence-GPLv3-8f10cb.svg
   :target: https://www.gnu.org/licenses/gpl-3.0.html
   :alt: License GPLv3	 

.. |Zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.6670011.svg
   :target: https://doi.org/10.5281/zenodo.6670011
   :alt: Zenodo

