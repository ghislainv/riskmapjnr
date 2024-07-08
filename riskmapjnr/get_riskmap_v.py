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


# get_riskmap_v
def get_riskmap_v(ldefrate_with_zero_v_file,
                  bins,
                  riskmap_v_file="riskmap_v.tif",
                  blk_rows=128,
                  verbose=True):
    """Get the risk map at the beginning of the validation period.

    We categorize the deforestation rates using the previous bins
    identified for the historical period.

    :param ldefrate_with_zero_v_file: Input raster file of local
        deforestation rate with zero risk class at the beginning of
        the validation period. This file is typically obtained with
        function ``get_ldefz_v()``.

    :param bins: Bins used to categorize the deforestation risk. Bins
        are typically obtained with function ``defor_cat()``.

    :param riskmap_v_file: Path to the output raster file for the risk
        map at the beginning of the validation period. Default to
        "riskmap_v.tif" in the current working directory.

    :param blk_rows: If > 0, number of rows for computation by block.

    :param verbose: Logical. Whether to print messages or not. Default
        to ``True``.

    :return: None. A raster file with deforestation categories is
        created (see ``riskmap_v_file``). Data range from 0 to
        30. Raster type is Byte ([0, 255]). NoData value is set to
        255.

    """

    # ================================
    # Create ldefrate_with_zero_v_file
    # ================================

    # Get ldefrate_file
    ldefzv_ds = gdal.Open(ldefrate_with_zero_v_file)
    ldefzv_band = ldefzv_ds.GetRasterBand(1)

    # Raster size
    xsize = ldefzv_band.XSize
    ysize = ldefzv_band.YSize

    # Create riskmap_v raster file
    driver = gdal.GetDriverByName("GTiff")
    if os.path.isfile(riskmap_v_file):
        os.remove(riskmap_v_file)
    riskv_ds = driver.Create(riskmap_v_file, xsize, ysize, 1,
                             gdal.GDT_Byte,
                             ["COMPRESS=LZW", "PREDICTOR=2",
                              "BIGTIFF=YES"])
    riskv_ds.SetProjection(ldefzv_ds.GetProjection())
    riskv_ds.SetGeoTransform(ldefzv_ds.GetGeoTransform())
    riskv_band = riskv_ds.GetRasterBand(1)
    riskv_band.SetNoDataValue(255)

    # Make blocks
    blockinfo = makeblock(ldefrate_with_zero_v_file, blk_rows=blk_rows)
    nblock = blockinfo[0]
    nblock_x = blockinfo[1]
    x = blockinfo[3]
    y = blockinfo[4]
    nx = blockinfo[5]
    ny = blockinfo[6]

    # Loop on blocks of data
    for b in range(nblock):
        # Progress bar
        if verbose:
            progress_bar(nblock, b + 1)
        # Position
        px = b % nblock_x
        py = b // nblock_x
        # Data
        ldefzv_data = ldefzv_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        # Categorize
        riskv_data = pd.cut(ldefzv_data.flatten(), bins=bins,
                            labels=False, include_lowest=True,
                            right=False)
        riskv_data[np.isnan(riskv_data)] = 255
        riskv_data = riskv_data.reshape(ldefzv_data.shape)
        # Write to files
        riskv_band.WriteArray(riskv_data, x[px], y[py])

    # Compute statistics
    riskv_band.FlushCache()
    cb = gdal.TermProgress_nocb if verbose else 0
    riskv_band.ComputeStatistics(False, cb)

    # Dereference drivers
    riskv_band = None
    del ldefzv_ds, riskv_ds

    return None


# # Test
# ldefrate_with_zero_v_file = "outputs_steps/ldefrate_with_zero_v.tif"
# bins = [0, 1, 334, 668, 1001, 1334, 1668, 2001, 2334, 2667,
#         3001, 3334, 3667, 4001, 4334, 4667, 5000, 5334, 5667,
#         6000, 6334, 6667, 7000, 7334, 7667, 8000, 8334, 8667,
#         9000, 9333, 9667, 10001]
# riskmap_v_file = "outputs_steps/riskmap_v.tif"
# blk_rows = 128
# verbose = True

# End
