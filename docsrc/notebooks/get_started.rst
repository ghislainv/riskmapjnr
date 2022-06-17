===========
Get Started
===========




1 Preamble
----------

1.1 Importing Python modules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We import the Python modules needed for running the analysis.

.. code:: python

    # Imports
    import os
    import pkg_resources

    import numpy as np
    import pandas as pd
    from tabulate import tabulate

    import riskmapjnr as rmj

We increase the cache for GDAL to increase computational speed.

.. code:: python

    # GDAL
    os.environ["GDAL_CACHEMAX"] = "1024"

Set ``PROJ_LIB`` environmental variable.

.. code:: python

    os.environ["PROJ_LIB"] = "/home/ghislain/.pyenv/versions/miniconda3-latest/envs/conda-rmj/share/proj"

1.2 Forest cover change data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We use the Guadeloupe archipelago as a case study. Recent forest cover change data for Guadeloupe is included in the ``riskmapjnr`` package. The raster file (``fcc123_GLP.tif``) includes the following values: **1** for deforestation on the period 2000--2010, **2** for deforestation on the period 2010--2020, and **3** for the remaining forest in 2020. NoData value is set to **0**. The first period (2000--2010) will be used for calibration and the second period (2010--2020) will be used for validation. This is the only data we need to derive a map of deforestation risk following the JNR methodology.

.. code:: python

    fcc_file = pkg_resources.resource_filename("riskmapjnr", "data/fcc123_GLP.tif")
    print(fcc_file)

::

    /home/ghislain/Code/riskmapjnr/riskmapjnr/data/fcc123_GLP.tif

2 Derive the deforestation risk map
-----------------------------------

.. code:: python

    results_makemap = rmj.makemap(
        fcc_file="data/fcc123_GLP.tif",
        time_interval=[10, 10],
        output_dir="outputs_makemap",
        clean=False,
        dist_bins=np.arange(0, 1080, step=30),
        win_sizes=np.arange(5, 48, 16),
        ncat=30,
        methods=["Equal Interval", "Equal Area"],
        csize=40,
        figsize=(6.4, 4.8),
        dpi=100,
        blk_rows=128,
        verbose=True)

3 Results
---------

3.1 Deforestation risk and distance to forest edge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Distance threshold.

.. code:: python

    dist_thresh = results_makemap["dist_thresh"]
    print(f"The distance theshold is {dist_thresh} m")

::

    The distance theshold is 180 m


We can have access to a table indicating the cumulative percentage of deforestation as a function of the distance.

.. table::

    +----------+---------+---------+------------+------------+
    | Distance | Npixels |    Area | Cumulation | Percentage |
    +==========+=========+=========+============+============+
    |       30 |   53389 | 4805.01 |    4805.01 |     75.253 |
    +----------+---------+---------+------------+------------+
    |       60 |   10235 |  921.15 |    5726.16 |    89.6795 |
    +----------+---------+---------+------------+------------+
    |       90 |    3848 |  346.32 |    6072.48 |    95.1033 |
    +----------+---------+---------+------------+------------+
    |      120 |    1474 |  132.66 |    6205.14 |     97.181 |
    +----------+---------+---------+------------+------------+
    |      150 |     914 |   82.26 |     6287.4 |    98.4693 |
    +----------+---------+---------+------------+------------+
    |      180 |     428 |   38.52 |    6325.92 |    99.0725 |
    +----------+---------+---------+------------+------------+
    |      210 |     230 |    20.7 |    6346.62 |    99.3967 |
    +----------+---------+---------+------------+------------+
    |      240 |     178 |   16.02 |    6362.64 |    99.6476 |
    +----------+---------+---------+------------+------------+
    |      270 |      90 |     8.1 |    6370.74 |    99.7745 |
    +----------+---------+---------+------------+------------+
    |      300 |      39 |    3.51 |    6374.25 |    99.8294 |
    +----------+---------+---------+------------+------------+

3.2 Validation
~~~~~~~~~~~~~~

.. code:: python

    ofile = "outputs_makemap/pred_obs_ws5_ei.png"
    ofile

.. _fig:pred_obs:

.. figure:: outputs_makemap/pred_obs_ws5_ei.png
    :width: 600


    **Relationship between observed and predicted deforestation in 1 x 1 km grid cells**. The red line is the identity line. Values of the weighted root mean squared error (wRMSE, in ha) and of the number of observations (:math:`n`, the number of spatial cells) are reported on the graph.

3.3 Riskmap
~~~~~~~~~~~

To be done.
