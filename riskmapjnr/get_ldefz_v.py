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

from osgeo import gdal

from .misc import progress_bar, makeblock


# get_ldefz_v
def get_ldefz_v(ldefrate_file,
                dist_v_file,
                dist_thresh,
                ldefrate_with_zero_v_file="ldefrate_with_zero_v.tif",
                blk_rows=128,
                verbose=True):
    """Get the raster map of the local deforestation rate with zero at the
    beginning of the validation period.

    To derive the risk map at the beginning of the validation period,
    we consider (i) the map of local deforestation rates on the
    historical period, (ii) the map of distance to forest edge at the
    beginning of the validation period, and (ii) the distance
    threshold estimated on the historical period.

    :param ldefrate_file: Input raster file of local deforestation
        rates. Deforestation rates are defined by integer values
        between rescale_min_val (e.g. 2) and rescale_max_val
        (e.g. 10000). This file is typically obtained with function
        ``local_defor_rate()``.

    :param dist_v_file: Input raster file of distance to forest edge
        at the beginning of the validation period. This file is
        typically obtained with function ``dist_values()`` setting
        ``values="0,1"``.

    :param dist_thresh: The distance threshold. This distance
        threshold is used to identify pixels with zero deforestation
        risk. The distance threshold is typically obtained with
        function ``dist_edge_threshold()`` for the historical period.

    :param ldefrate_with_zero_v_file: Path to the output raster file
        of local deforestation rate with zero risk class. Default to
        "ldefrate_with_zero_v.tif" in the current working
        directory. Pixels with zero deforestation risk are assigned a
        value of 0.

    :param blk_rows: If > 0, number of rows for computation by block.

    :param verbose: Logical. Whether to print messages or not. Default
        to ``True``.

    :return: None. A raster files of local deforestation risk at the
        beginning of the validation period is created (see
        ``ldefrate_with_zero_v_file``). Data range from 1 to 65535. Raster
        type is UInt16 ([0, 65535]). NoData value is set to 0.

    """

    # ================================
    # Create ldefrate_with_zero_v_file
    # ================================

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
    if os.path.isfile(ldefrate_with_zero_v_file):
        os.remove(ldefrate_with_zero_v_file)
    ldefzv_ds = driver.Create(ldefrate_with_zero_v_file, xsize, ysize, 1,
                              gdal.GDT_UInt16,
                              ["COMPRESS=LZW", "PREDICTOR=2",
                               "BIGTIFF=YES"])
    ldefzv_ds.SetProjection(ldef_ds.GetProjection())
    ldefzv_ds.SetGeoTransform(ldef_ds.GetGeoTransform())
    ldefzv_band = ldefzv_ds.GetRasterBand(1)
    ldefzv_band.SetNoDataValue(0)

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
        ldef_data = ldef_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        distv_data = distv_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        # Remove defor rate for fcc == 1 (corresponding to distv == 0)
        ldefzv_data = ldef_data
        ldefzv_data[distv_data == 0] = 0
        # Set 1 for null risk beyond distance threshold
        ldefzv_data[distv_data >= dist_thresh] = 1
        # Write to files
        ldefzv_band.WriteArray(ldefzv_data, x[px], y[py])

    # Compute statistics
    ldefzv_band.FlushCache()
    cb = gdal.TermProgress_nocb if verbose else 0
    ldefzv_band.ComputeStatistics(False, cb)

    # Dereference drivers
    ldefzv_band = None
    del ldef_ds, distv_ds, ldefzv_ds


# # Test
# ldefrate_file = "outputs_steps/ldefrate.tif"
# dist_v_file = "outputs_steps/dist_edge_v.tif"
# dist_thresh = 120
# ldefrate_with_zero_v_file = "outputs_steps/ldefrate_with_zero_v.tif"
# blk_rows = 128
# verbose = True

# End
