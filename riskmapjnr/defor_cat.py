#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=3
# license         :GPLv3
# ==============================================================================

import os

import numpy as np
from osgeo import gdal
import pandas as pd

from .misc import progress_bar, makeblock


# defor_cat
def defor_cat(ldefrate_with_zero_file,
              riskmap_file="riskmap.tif",
              ncat=30,
              method="Equal Area",
              blk_rows=128,
              verbose=True):
    """Categorizing local deforestation rates.

    This function categorizes the deforestation risk from the map of
    local deforestation rates. This function assumes that pixels with
    zero deforestation risk have been previously identified (see
    function ``set_defor_cat_zero()``). Three categorization methods
    can be used, either "Equal Area", "Equal Interval", or "Natural
    Breaks". When "Equal Area" is used, the classes with a risk > 0
    have approximately the same surface area. When "Equal Interval" is
    used, some risk classes will predominate in the risk map while
    other classes will be present only in small areas. When "Natural
    Breaks" is used, the data is normalized before running the slicing
    algorithm.

    :param ldefrate_with_zero_file: Input raster file of local
        deforestation rates. Deforestation rates are defined by
        integer values between 1 and 10000 (ten thousand)). Pixels
        with zero deforestation risk (beyond a given distance from the
        forest edge) have value 0. This file is typically obtained
        with function ``set_defor_cat_zero()``.

    :param riskmap_file: Output raster file with categories of
        deforestation risk.

    :param ncat: Number of deforestation risk categories (zero
        risk class excluded). Default to 30.

    :param method: Method used for categorizing. Either "Equal
        Interval", "Equal Area", or "Natural Breaks".

    :param blk_rows: If > 0, number of rows for computation by block.

    :param verbose: Logical. Whether to print messages or not. Default
        to ``True``.

    :return: Bins used to categorize the deforestation risk. A raster
        file with deforestation categories is created (see
        ``riskmap_file``). Data range from 0 to 30. Raster type is
        Byte ([0, 255]). NoData value is set to 255.

    """

    # ==============================================================
    # Input raster
    # ==============================================================

    # Get catzero (catzero) raster data
    catzero_ds = gdal.Open(ldefrate_with_zero_file)
    catzero_band = catzero_ds.GetRasterBand(1)
    # Raster size
    xsize = catzero_band.XSize
    ysize = catzero_band.YSize

    # Make blocks
    blockinfo = makeblock(ldefrate_with_zero_file, blk_rows=blk_rows)
    nblock = blockinfo[0]
    nblock_x = blockinfo[1]
    x = blockinfo[3]
    y = blockinfo[4]
    nx = blockinfo[5]
    ny = blockinfo[6]

    # ==============================================
    # Categorical raster file for deforestation risk
    # ==============================================

    # Create categorical (cat) raster file for deforestation risk
    driver = gdal.GetDriverByName("GTiff")
    if os.path.isfile(riskmap_file):
        os.remove(riskmap_file)
    cat_ds = driver.Create(riskmap_file, xsize, ysize, 1,
                           gdal.GDT_Byte,
                           ["COMPRESS=LZW", "PREDICTOR=2",
                            "BIGTIFF=YES"])
    cat_ds.SetProjection(catzero_ds.GetProjection())
    cat_ds.SetGeoTransform(catzero_ds.GetGeoTransform())
    cat_band = cat_ds.GetRasterBand(1)
    cat_band.SetNoDataValue(255)

    # =================
    # Compute bins
    # =================

    # Equal Interval
    if method == "Equal Interval":
        bin_size = (10000 - 1) / ncat
        bins = [1 + i * bin_size for i in range(ncat)]
        bins = np.rint([0] + bins + [10000]).astype(int)

    # Equal Area
    if method == "Equal Area":
        # Compute histogram
        nvalues = 10000
        counts = catzero_band.GetHistogram(0.5, 10000.5, nvalues, 0, 0)
        npix = sum(counts)
        # Percentage
        perc = np.array(counts) / npix
        # Cumulative percentage
        cum_perc = np.cumsum(perc)
        # Correction of the approximation for last value
        cum_perc[-1] = 1.0
        # Quantiles
        q = [i * 1 / ncat for i in range(1, ncat + 1)]  # len(q)=30
        # Bins
        bins = [0, 1]
        # Loop on quantiles
        for qi in q:
            comp = (cum_perc <= qi)
            sum_comp = np.sum(comp)
            if sum_comp > 1:
                bins.append(sum_comp)
        # Remove duplicate
        bins = list(np.unique(bins))

    # Replace last bin value 10000 by 10001 to include 10000 in
    # last category with pd.cut(right=False).
    bins[-1] = 10001

    # =================
    # Categorizing
    # =================

    # Loop on blocks of data
    for b in range(nblock):
        # Progress bar
        if verbose:
            progress_bar(nblock, b + 1)
        # Position
        px = b % nblock_x
        py = b // nblock_x
        # Data
        catzero_data = catzero_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        # Categorize
        cat_data = pd.cut(catzero_data.flatten(), bins=bins,
                          labels=False, include_lowest=True,
                          right=False)
        cat_data[np.isnan(cat_data)] = 255
        cat_data = cat_data.reshape(catzero_data.shape)
        # Write to file
        cat_band.WriteArray(cat_data, x[px], y[py])

    # Compute statistics
    cat_band.FlushCache()
    cb = gdal.TermProgress_nocb if verbose else 0
    cat_band.ComputeStatistics(False, cb)

    # Dereference drivers
    cat_band = None
    del cat_ds, catzero_ds

    return bins


# # Test
# ldefrate_with_zero_file = "outputs_steps/ldefrate_with_zero.tif"
# riskmap_file = "outputs_steps/riskmap.tif"
# ncat = 30
# method = "Equal Area"
# blk_rows = 128

# defor_cat(ldefrate_with_zero_file,
#           riskmap_file="outputs/riskmap_equal_interval.tif",
#           ncat=30,
#           method="Equal Interval",
#           blk_rows=128)

# defor_cat(ldefrate_with_zero_file,
#           riskmap_file="outputs/riskmap_equal_area.tif",
#           ncat=30,
#           method="Equal Area",
#           blk_rows=128)

# End
