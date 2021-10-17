#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=3
# license         :GPLv3
# ==============================================================================


# Third party imports
import numpy as np
from osgeo import gdal

# Local application imports
from misc import progress_bar

# deforestation_categories
deforestation_categories(input_file,
                         blk_rows=128)

    """Computing the deforestation categories from the map of local
    deforestation rates.

    This function computes the deforestation categories from the map
    of local deforestation rates. Three categorization methods can be
    used, either "Equal Area", "Equal Interval" and "Natural
    Breaks". When "Equal Area" is used, the classes with a risk > 0
    have approximately the same surface area. When "Equal Interval" is
    used, some risk classes will predominate in the risk map while
    other classes will be present only in small areas. When "Natural
    Breaks" is used, the data is normalized before running the slicing
    algorithm.

    :param input_file: Input raster file of local deforestation rates.
