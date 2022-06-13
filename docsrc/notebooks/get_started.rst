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

2 Deforestation risk and distance to forest edge
------------------------------------------------

The first step is to compute the distance to the forest edge after which the risk of deforestation becomes negligible. Indeed, it is known from previous studies on tropical deforestation that the deforestation risk decreases rapidly with the distance to the forest edge and that most of the deforestation occurs close to the forest edge (Vieilledent et al., 2013, Grinand et al., 2020, Vieilledent, 2021, Dezécache et al., 2017). The JNR methodology suggests identifying the distance to the forest edge :math:`d`, so that at least 99% of the deforestation occurs within a distance :math:`\leq d`. Forest areas located at a distance from the forest edge :math:`\gt d` can be considered as having no risk of being deforested. As a consequence, forest pixels with a distance from the forest edge :math:`\gt d` are assigned category 0 (zero) for the deforestation risk.

.. code:: python

    ofile = "outputs/plot_dist.png"
    dist_edge_thres = rmj.dist_edge_threshold(
        input_file=fcc_file,
        dist_file="outputs/dist_edge.tif",
        tab_file="outputs/tab_dist.csv",
        fig_file=ofile,
        bins=np.arange(0, 1080, step=30),
        blk_rows=128)
    ofile

.. _fig:dist_edge:

.. figure:: outputs/plot_dist.png
    :width: 600


    **Identifying areas for which the risk of deforestation is negligible.** Figure shows that more than 99% of the deforestation occurs within a distance from the forest edge ≤ 120 m. Forest areas located at a distance > 120 m from the forest edge can be considered as having no risk of being deforested.

The function returns a dictionnary including the distance threshold.

.. code:: python

    dist_thresh = dist_edge_thres["dist_thresh"]
    print(f"The distance threshold is {dist_thresh} m")

::

    The distance threshold is 120 m


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

3 Local deforestation rate
--------------------------

The second step is to compute a local risk of deforestation at the pixel level using a moving window made of several pixels. The deforestation risk is estimated from the deforestation rate inside the moving window. The deforestation rate :math:`\theta` (in %/yr) is computed from the formula :math:`\theta=(\alpha_2/\alpha_1)^{1/\tau}-1`, with :math:`\alpha` the forest areas (in ha) at time :math:`t_1` and :math:`t_2`, and :math:`\tau`, the time interval (in yr) between time :math:`t_1` and :math:`t_2`. Using the deforestation rate formula, the moving window and the past forest cover change map, we can derive a raster map describing the local risk of deforestation at the same resolution as the input map.

To save space on disk, deforestation rates are converted to integer values between 0 and 10000 (ten thousand) and the raster type is set to UInt16. This ensures a precision of 10\ :sup:`-4`\ for the deforestation rate which is sufficient to determine the 30 categories of deforestation risk, as imposed by the JNR methodology.

.. code:: python

    # Set window size
    ws = 31
    # Compute local deforestation rate
    rmj.local_defor_rate(input_file=fcc_file,
                         output_file="outputs/ldefrate_ws{}.tif".format(ws),
                         win_size=ws,
                         time_interval=10,
                         blk_rows=100)

4 Pixels with zero risk of deforestation
----------------------------------------

This third step sets a value of 10001 to pixels with zero deforestation risk. As explained previously, a risk of deforestation of zero is assumed when distance to forest edge is greater than the distance below which more than 99% of the deforestation occurs.

.. code:: python

    rmj.set_defor_cat_zero(
        input_file="outputs/ldefrate_ws31.tif",
        dist_file="outputs/dist_edge.tif",
        dist_thresh=dist_thresh,
        output_file="outputs/defor_cat_zero.tif",
        blk_rows=128,
        verbose=True)

5 Categories of deforestation risk
----------------------------------

The fourth step implies converting the continuous values of the raster map of deforestation risk to categorical values. The JNR methodology suggests to use 31 classes of risk from “0” to “30” including the “0” class for the forest pixels with no risk of being deforested (located at a distance to the forest edge :math:`> d`, see first step). Following the JNR methodology, at least three slicing algorithms must be compared to derive the categorical map of deforestation risk, such as “equal area”, “equal interval”, and “natural breaks”. With the “equal area” algorithm, each class from “1” to “30” must cover approximately the same area. With the “equal interval” algorithm, classes from “1” to “30” correspond to bins of deforestation risk of the same range. In this case, some risk classes will be in majority in the landscape compared to other classes of lower frequency. With the “natural breaks” algorithm, the continuous deforestation risk is normalized before running an “equal interval” algorithm.

.. code:: python

    rmj.defor_cat(input_file="outputs/defor_cat_zero.tif",
                  output_file="outputs/defor_cat.tif",
                  nbins=30,
                  method="Equal Area",
                  blk_rows=128)

6 Deforestation rates per category of risk
------------------------------------------

Before the validation step, we need to compute the historical deforestation rates (in %/yr) for each category of spatial deforestation risk. The historical deforestation rates are computed for the calibration period (here 2000--2010). Deforestation rates provide estimates of the percentage of forest (which is then converted to an area of forest) that should be deforested inside each forest pixel which belongs to a given category of deforestation risk.

.. code:: python

    rmj.defrate_per_cat(
        fcc_file = fcc_file,
        defor_cat_file = "outputs/defor_cat.tif",
        time_interval = 10,
        tab_file = "outputs/defrate_per_cat.csv",
        blk_rows = 128)

A table indicating the deforestation rate per category of deforestation is produced:

.. table::

    +-----+-------+--------+------------+
    | cat |  nfor | ndefor |       rate |
    +=====+=======+========+============+
    |   1 | 39841 |      8 | 0.00200617 |
    +-----+-------+--------+------------+
    |   2 | 13367 |     29 |  0.0214846 |
    +-----+-------+--------+------------+
    |   3 | 13238 |     46 |  0.0342101 |
    +-----+-------+--------+------------+
    |   4 | 13348 |     72 |    0.05265 |
    +-----+-------+--------+------------+
    |   5 | 13290 |    105 |  0.0762562 |
    +-----+-------+--------+------------+
    |   6 | 13309 |    150 |   0.107158 |
    +-----+-------+--------+------------+
    |   7 | 13328 |    168 |   0.119136 |
    +-----+-------+--------+------------+
    |   8 | 13175 |    184 |     0.1312 |
    +-----+-------+--------+------------+
    |   9 | 13435 |    232 |   0.159864 |
    +-----+-------+--------+------------+
    |  10 | 13272 |    268 |   0.184534 |
    +-----+-------+--------+------------+
    |  11 | 13336 |    348 |   0.232344 |
    +-----+-------+--------+------------+
    |  12 | 13291 |    386 |   0.255262 |
    +-----+-------+--------+------------+
    |  13 | 13308 |    410 |     0.2687 |
    +-----+-------+--------+------------+
    |  14 | 13296 |    491 |   0.313587 |
    +-----+-------+--------+------------+
    |  15 | 13304 |    628 |   0.383405 |
    +-----+-------+--------+------------+
    |  16 | 13315 |    649 |   0.393287 |
    +-----+-------+--------+------------+
    |  17 | 13285 |    611 |   0.375516 |
    +-----+-------+--------+------------+
    |  18 | 13333 |    763 |    0.44528 |
    +-----+-------+--------+------------+
    |  19 | 13308 |    955 |   0.525106 |
    +-----+-------+--------+------------+
    |  20 | 13301 |   1041 |   0.557349 |
    +-----+-------+--------+------------+
    |  21 | 13304 |   1270 |   0.633328 |
    +-----+-------+--------+------------+
    |  22 | 13288 |   1509 |   0.700437 |
    +-----+-------+--------+------------+
    |  23 | 13321 |   1623 |   0.727261 |
    +-----+-------+--------+------------+
    |  24 | 13300 |   1790 |   0.764367 |
    +-----+-------+--------+------------+
    |  25 | 13302 |   2280 |   0.847442 |
    +-----+-------+--------+------------+
    |  26 | 13314 |   2751 |   0.901193 |
    +-----+-------+--------+------------+
    |  27 | 13295 |   3834 |   0.966697 |
    +-----+-------+--------+------------+
    |  28 | 13314 |   6932 |    0.99936 |
    +-----+-------+--------+------------+

From this table, we see that except for category 1, categories have approximately the same surface area (corresponding to about 13300 pixels). Note that the number of categories might be slightly inferior to 30. Note also that the deforestation rate increases with the deforestation risk category and that deforestation rates are spread on the interval [0, 1], suggesting that category 1 represents well a category with very low deforestation risk (close to 0), and category 28 represents well a category with very high deforestation risk (close to 1).

7 Validation
------------

The fifth step focuses on comparing the map of deforestation risk with a deforestation map corresponding to the validation period. The validation period follows the calibration period and provides independent observations of deforestation.

To do so, we consider a square grid of at least 1000 spatial cells containing at least one forest pixel at the beginning of the validation period. Following JNR specification, the cell size should be :math:`\leq` 10 km. Note that with the map of deforestation risk, each forest pixel at the beginning of the validation period falls into a category of deforestation risk. For each cell of the grid, we compute the predicted area of deforestation (in ha) given the map of deforestation risk and the historical deforestation rates for each category of deforestation risk computed on the calibration period (see previous step).

We can then compare the predicted deforestation with the observed deforestation in that spatial cell for the validation period. Because all cells don’t have the same forest cover at the beginning of the validation period, a weight :math:`w_j` is computed for each grid cell :math:`j` such that :math:`w_j=\beta_j / B`, with :math:`\beta_j` the forest cover (in ha) in the cell :math:`j` at the beginning of the validation period and :math:`B` the total forest cover in the jurisdiction (in ha) at the same date. We then calculate the weighted root mean squared error (wRMSE) from the observed and predicted deforestation for each cell and the cell weights.

.. code:: python

    ofile = "outputs/pred_obs.png"
    rmj.validation(
        fcc_file = fcc_file,
        time_interval = 10,
        defor_cat_file = "outputs/defor_cat.tif",
        defrate_per_cat_file = "outputs/defrate_per_cat.csv",
        csize = 40,
        tab_file = "outputs/validation_data.csv",
        fig_file = ofile,
        figsize = (6.4, 4.8),
        dpi = 100)
    ofile

.. _fig:pred_obs:

.. figure:: outputs/pred_obs.png
    :width: 600


    **Relationship between observed and predicted deforestation in 1 x 1 km grid cells**. The red line is the identity line. Values of the weighted root mean squared error (wRMSE, in ha) and of the number of observations (:math:`n`, the number of spatial cells) are reported on the graph.

8 Final risk map
----------------

The user must repeat the procedure and obtain risk maps for various window size and slicing algorithms. Following the JNR methodology, at least 25 different sizes for the moving window must be tested together with two slicing algorithms (“Equal Interval” and “Equal Area”), thus leading to a minimum of 50 different maps of deforestation risk. The map with the smallest wRMSE value is considered the best risk map. Once the best risk map is identified, with the corresponding window size and slicing algorithm, a final risk map is derived considering both the calibration and validation period.
