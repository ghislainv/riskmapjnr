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
import pandas as pd

# Local application imports
from .dist_edge_threshold import dist_values
from .misc import progress_bar, makeblock


# get_riskmap_v
def get_riskmap_v(fcc_file,
                  ldefrate_file,
                  dist_thresh,
                  bins,
                  dist_v_file="dist_edge_v.tif",
                  ldefrate_with_zero_v_file="ldefrate_with_zero_v.tif",
                  riskmap_v_file="riskmap_v.tif",
                  blk_rows=128,
                  verbose=True):
    """Get the risk map at the beginning of the validation period.

    To derive the risk map at the beginning of the validation period,
    we consider (i) the forest cover at this date, (ii) the map of
    local deforestation rates, (ii) the threshold distance, and (iii)
    the bins used to categorize the deforestation rates. All these
    data are obtained from previous steps and based on the
    deforestation for the historical period. The approch is the
    following: first, we identify the forest pixels at the beginning of
    the validation period. Second, we assign category zero to pixels at
    a distance from the forest edge which is greater than the distance
    threshold. Third, we categorize the deforestation rates using the
    previous bins identified for the historical period. In addition to
    the risk map, two additional raster files are produced: the raster
    file of the distance to forest edge at the beginning of the
    validation period, and the raster file of local deforestation
    rates including the zero deforestation risk.

   :param fcc_file: Input raster file of forest cover change at
        three dates (123). 1: first period deforestation, 2: second
        period deforestation, 3: remaining forest at the end of the
        second period. NoData value must be 0 (zero).

    :param ldefrate_file: Input raster file of local deforestation
        rates. Deforestation rates are defined by integer values
        between 0 and 10000 (ten thousand). This file is typically
        obtained with function ``local_defor_rate()``.

    :param dist_thresh: The distance threshold. This distance
        threshold is used to identify pixels with zero deforestation
        risk. The distance threshold is typically obtained with
        function ``dist_edge_threshold()``.

    :param bins: Bins used to categorize the deforestation risk. Bins
        are typically obtained with function ``defor_cat()``.

    :param dist_v_file: Path to the output raster file of distance to
        forest edge at the beginning of the validation period. Default
        to "dist_v.tif" in the current working directory.

    :param ldefrate_with_zero_v_file: Path to the output raster file
        of local deforestation rate with zero risk class. Default to
        "ldefrate_with_zero_v.tif" in the current working
        directory. Pixels with zero deforestation risk are assigned a
        value of 10001.

    :param riskmap_v_file: Path to the output raster file for the risk
        map at the beginning of the validation period. Default to
        "riskmap_v.tif" in the current working directory.

    :param blk_rows: If > 0, number of rows for computation by block.

    :param verbose: Logical. Whether to print messages or not. Default
        to ``True``.

    :return: None. Three raster files are created (see
        ``riskmap_v_file``, ``dist_v_file``, and
        ``ldefrate_with_zero_v_file``).

    """

    # ===================================
    # Compute the distance to forest edge at the
    # beginning of the validation period
    # ===================================

    dist_values(input_file=fcc_file,
                dist_file=dist_v_file,
                values="0,1",
                verbose=False)

    
