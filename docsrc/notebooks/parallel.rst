==================
Parallel computing
==================




.. contents::
  :local:
  :depth: 2

1 Preamble
----------

Import the Python modules needed to run the analysis.

.. code:: python

    # Imports
    import os
    import multiprocessing as mp
    import pkg_resources
    import time

    import numpy as np
    import pandas as pd
    from tabulate import tabulate

    import riskmapjnr as rmj

Increase the cache for GDAL to increase computational speed.

.. code:: python

    # GDAL
    os.environ["GDAL_CACHEMAX"] = "1024"

Set the ``PROJ_LIB`` environmental variable.

.. code:: python

    os.environ["PROJ_LIB"] = "/home/ghislain/.pyenv/versions/miniconda3-latest/envs/conda-rmj/share/proj"

Create a directory to save results.

.. code:: python

    out_dir = "outputs_parallel"
    rmj.make_dir(out_dir)

Load forest data.

.. code:: python

    fcc_file = pkg_resources.resource_filename("riskmapjnr", "data/fcc123_GLP.tif")
    print(fcc_file)
    border_file = pkg_resources.resource_filename("riskmapjnr", "data/ctry_border_GLP.gpkg")
    print(border_file)

::

    /home/ghislain/Code/riskmapjnr/riskmapjnr/data/fcc123_GLP.tif
    /home/ghislain/Code/riskmapjnr/riskmapjnr/data/ctry_border_GLP.gpkg

2 Sequential computing
----------------------

We set ``parallel`` argument to ``False`` in the call to ``makemap()`` function.

.. code:: python

    start_time = time.time()
    results_makemap = rmj.makemap(
        fcc_file=fcc_file,
        time_interval=[10, 10],
        output_dir=out_dir,
        clean=False,
        dist_bins=np.arange(0, 1080, step=30),
        win_sizes=np.arange(5, 48, 6),
        ncat=30,
        parallel=False,
        ncpu=None,
        methods=["Equal Interval", "Equal Area"],
        csize=40,
        no_quantity_error=True,
        figsize=(6.4, 4.8),
        dpi=100,
        blk_rows=128,
        verbose=True)
    sec_seq = time.time() - start_time
    print('Time Taken:', time.strftime("%H:%M:%S",time.gmtime(sec_seq)))

::

    Model calibration and validation
    .. Model 0: window size = 5, slicing method = ei.
    .. Model 1: window size = 5, slicing method = ea.
    .. Model 2: window size = 11, slicing method = ei.
    .. Model 3: window size = 11, slicing method = ea.
    .. Model 4: window size = 17, slicing method = ei.
    .. Model 5: window size = 17, slicing method = ea.
    .. Model 6: window size = 23, slicing method = ei.
    .. Model 7: window size = 23, slicing method = ea.
    .. Model 8: window size = 29, slicing method = ei.
    .. Model 9: window size = 29, slicing method = ea.
    .. Model 10: window size = 35, slicing method = ei.
    .. Model 11: window size = 35, slicing method = ea.
    .. Model 12: window size = 41, slicing method = ei.
    .. Model 13: window size = 41, slicing method = ea.
    .. Model 14: window size = 47, slicing method = ei.
    .. Model 15: window size = 47, slicing method = ea.
    Deriving risk map for full historical period
    Time Taken: 00:02:06

3 Parallel computing
--------------------

We use parallel computing using several CPUs. We set ``parallel`` argument to ``True`` in the call to ``makemap()`` function and set ``ncpu`` to ``mp.cpu_count()`` to use the maximum number of available CPUs (here 8). When using parallel computing, one CPU is used for each window size.

.. code:: python

    ncpu = mp.cpu_count()
    print(f"Number of CPUs to use: {ncpu}.") 

::

    Number of CPUs to use: 8.


.. code:: python

    start_time = time.time()
    results_makemap = rmj.makemap(
        fcc_file=fcc_file,
        time_interval=[10, 10],
        output_dir=out_dir,
        clean=False,
        dist_bins=np.arange(0, 1080, step=30),
        win_sizes=np.arange(5, 48, 6),
        ncat=30,
        parallel=True,
        ncpu=ncpu,
        methods=["Equal Interval", "Equal Area"],
        csize=40,
        no_quantity_error=True,
        figsize=(6.4, 4.8),
        dpi=100,
        blk_rows=128,
        verbose=True)
    sec_par = time.time() - start_time
    print('Time Taken:', time.strftime("%H:%M:%S",time.gmtime(sec_par)))

::

    Model calibration and validation
    .. Model 0: window size = 5, slicing method = ei.
    .. Model 2: window size = 11, slicing method = ei.
    .. Model 6: window size = 23, slicing method = ei.
    .. Model 4: window size = 17, slicing method = ei.
    .. Model 12: window size = 41, slicing method = ei.
    .. Model 8: window size = 29, slicing method = ei.
    .. Model 14: window size = 47, slicing method = ei.
    .. Model 10: window size = 35, slicing method = ei.
    .. Model 1: window size = 5, slicing method = ea.
    .. Model 3: window size = 11, slicing method = ea.
    .. Model 7: window size = 23, slicing method = ea.
    .. Model 15: window size = 47, slicing method = ea.
    .. Model 5: window size = 17, slicing method = ea.
    .. Model 13: window size = 41, slicing method = ea.
    .. Model 9: window size = 29, slicing method = ea.
    .. Model 11: window size = 35, slicing method = ea.
    Deriving risk map for full historical period
    Time Taken: 00:00:45

4 Results
---------

Sequential computing took 02m 06s against 45s for parallel computing with 8 CPUs when considering 8 window sizes.
