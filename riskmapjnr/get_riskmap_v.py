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

    # ================================
    # Create ldefrate_with_zero_v_file
    # ================================

    # Get fcc
    fcc_ds = gdal.Open(fcc_file)
    fcc_band = fcc_ds.GetRasterBand(1)

    # Get ldefrate_file
    ldef_ds = gdal.Open(ldefrate_file)
    ldef_band = ldef_ds.GetRasterBand(1)

    # Get dist_v_file
    distv_ds = gdal.Open(dist_v_file)
    distv_band = distv_ds.GetRasterBand(1)

    # Raster size
    xsize = ldef_band.XSize
    ysize = ldef_band.YSize

    # Create ldefrate_with_zero_v raster file
    driver = gdal.GetDriverByName("GTiff")
    ldefzv_ds = driver.Create(ldefrate_with_zero_v_file, xsize, ysize, 1,
                              gdal.GDT_UInt16,
                              ["COMPRESS=LZW", "PREDICTOR=2",
                               "BIGTIFF=YES"])
    ldefzv_ds.SetProjection(ldef_ds.GetProjection())
    ldefzv_ds.SetGeoTransform(ldef_ds.GetGeoTransform())
    ldefzv_band = ldefzv_ds.GetRasterBand(1)
    ldefzv_band.SetNoDataValue(65535)

    # Create riskmap_v raster file
    driver = gdal.GetDriverByName("GTiff")
    riskv_ds = driver.Create(riskmap_v_file, xsize, ysize, 1,
                             gdal.GDT_Byte,
                             ["COMPRESS=LZW", "PREDICTOR=2",
                              "BIGTIFF=YES"])
    riskv_ds.SetProjection(ldef_ds.GetProjection())
    riskv_ds.SetGeoTransform(ldef_ds.GetGeoTransform())
    riskv_band = riskv_ds.GetRasterBand(1)
    riskv_band.SetNoDataValue(255)

    # Make blocks
    blockinfo = makeblock(ldefrate_file, blk_rows=blk_rows)
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
        fcc_data = fcc_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        ldef_data = ldef_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        distv_data = distv_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        # Remove defor rate for fcc == 1
        ldefzv_data = ldef_data
        ldefzv_data[fcc_data == 1] = 65535
        # Replace nodata value (65535) in distv_data with 0
        distv_data[distv_data == 65535] = 0
        # Set 0 risk beyond distance threshold
        ldefzv_data[distv_data >= dist_thresh] = 0
        # Categorize
        riskv_data = pd.cut(ldefzv_data.flatten(), bins=bins,
                            labels=False, include_lowest=True,
                            right=False)
        riskv_data[np.isnan(riskv_data)] = 255
        riskv_data = riskv_data.reshape(ldefzv_data.shape)
        # Write to files
        ldefzv_band.WriteArray(ldefzv_data, x[px], y[py])
        riskv_band.WriteArray(riskv_data, x[px], y[py])

    # Compute statistics
    ldefzv_band.FlushCache()
    riskv_band.FlushCache()
    cb = gdal.TermProgress if verbose else 0
    ldefzv_band.ComputeStatistics(False, cb)
    riskv_band.ComputeStatistics(False, cb)

    # Dereference drivers
    ldefzv_band, riskv_band = None, None
    del fcc_ds, ldef_ds, distv_ds, ldefzv_ds, riskv_ds

    return None


# # Test
# ldefrate_file = "outputs_steps/ldefrate.tif"
# fcc_file = "data/fcc123_GLP.tif"
# dist_thresh = 120
# bins = [0, 1, 334, 668, 1001, 1334, 1668, 2001, 2334, 2667,
#         3001, 3334, 3667, 4001, 4334, 4667, 5000, 5334, 5667,
#         6000, 6334, 6667, 7000, 7334, 7667, 8000, 8334, 8667,
#         9000, 9333, 9667, 10001]
# dist_v_file = "outputs_steps/dist_edge_v.tif"
# ldefrate_with_zero_v_file = "outputs_steps/ldefrate_with_zero_v.tif"
# riskmap_v_file = "outputs_steps/riskmap_v.tif"
# blk_rows = 128
# verbose = True

# End
