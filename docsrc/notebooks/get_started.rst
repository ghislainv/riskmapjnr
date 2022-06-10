===========
Get Started
===========




1 Introduction
--------------

1.1 Importing Python modules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We import the Python modules needed for running the analysis.

.. code:: python

    # Imports
    import os
    import pkg_resources

    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd
    from tabulate import tabulate

    import riskmapjnr as rmj

We create some directories to hold the data and the ouputs with the
function ``rmj.make_dir()``.

.. code:: python

    rmj.make_dir("outputs")

We increase the cache for GDAL to increase computational speed.

.. code:: python

    # GDAL
    os.environ["GDAL_CACHEMAX"] = "1024"

.. code:: python

    os.environ["PROJ_LIB"] = "/home/ghislain/.pyenv/versions/miniconda3-latest/envs/conda-rmj/share/proj"

1.2 Forest cover change data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We use the Guadeloupe archipelago as a case study. Recent forest cover
change data for Guadeloupe is included in the \`\`riskmapjnr\`\`
package. The raster file (\`\`fcc123\_GLP.tif\`\`) includes the following
values: **1** for deforestation on the period 2000--2010, **2** for
deforestation on the period 2010--2020, and **3** for the remaining
forest in 2020. NoData value is set to **0**. This is the only data we
need to derive a map of deforestation risk following the JNR
methodology.

.. code:: python

    fcc_file = pkg_resources.resource_filename("riskmapjnr", "data/fcc123_GLP.tif")
    print(fcc_file)

::

    /home/ghislain/Code/riskmapjnr/riskmapjnr/data/fcc123_GLP.tif

2 Deforestation risk and distance to forest edge
------------------------------------------------

The first step is to compute the distance to the forest edge after
which the risk of deforestation becomes negligible. Indeed, it is
known from previous studies on tropical deforestation that the
deforestation risk decreases rapidly with the distance to the forest
edge and that most of the deforestation occurs close to the forest
edge (Vieilledent et al., 2013, Grinand et al., 2020, Vieilledent,
2021, Dezécache et al., 2017). The VCS-JNR suggests identifying the
distance to the forest edge :math:`d`, so that at least 99% of the
deforestation occurs within a distance :math:`\leq d`. Forest areas located at
a distance from the forest edge :math:`\gt d` can be considered as having no
risk of being deforested. As a consequence, forest pixels with a
distance from the forest edge :math:`\gt d` are assigned category 0 (zero) for
the deforestation risk.

.. code:: python

    ofile = "outputs/plot_dist.png"
    rmj.dist_edge_threshold(input_file=fcc_file,
                            dist_file="outputs/dist_edge.tif",
                            tab_file="outputs/tab_dist.csv",
                            fig_file=ofile,
                            bins=np.arange(0, 1080, step=30),
                            blk_rows=128)
    ofile

.. image:: outputs/plot_dist.png
    :width: 600

A table indicating the cumulative percentage of deforestation as a function of the distance is also produced:

.. table::

    +----------+---------+---------+------------+------------+
    | Distance | Npixels |    Area | Cumulation | Percentage |
    +==========+=========+=========+============+============+
    |       30 |   25325 | 2279.25 |    2279.25 |    85.2263 |
    +----------+---------+---------+------------+------------+
    |       60 |    3134 |  282.06 |    2561.31 |    95.7732 |
    +----------+---------+---------+------------+------------+
    |       90 |     869 |   78.21 |    2639.52 |    98.6976 |
    +----------+---------+---------+------------+------------+
    |      120 |     235 |   21.15 |    2660.67 |    99.4885 |
    +----------+---------+---------+------------+------------+
    |      150 |      91 |    8.19 |    2668.86 |    99.7947 |
    +----------+---------+---------+------------+------------+
    |      180 |      30 |     2.7 |    2671.56 |    99.8957 |
    +----------+---------+---------+------------+------------+
    |      210 |      15 |    1.35 |    2672.91 |    99.9462 |
    +----------+---------+---------+------------+------------+
    |      240 |       5 |    0.45 |    2673.36 |     99.963 |
    +----------+---------+---------+------------+------------+
    |      270 |       2 |    0.18 |    2673.54 |    99.9697 |
    +----------+---------+---------+------------+------------+
    |      300 |       2 |    0.18 |    2673.72 |    99.9764 |
    +----------+---------+---------+------------+------------+
