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

    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd

    import riskmapjnr as rmj

We create some directories to hold the data and the ouputs with the
function ``rmj.make_dir()``.

.. code:: python

    rmj.make_dir("outputs")

We increase the cache for GDAL to increase computational speed.

.. code:: python

    # GDAL
    os.environ["GDAL_CACHEMAX"] = "1024"
