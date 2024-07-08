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


# set_defor_cat_zero
def set_defor_cat_zero(ldefrate_file,
                       dist_file,
                       dist_thresh,
                       ldefrate_with_zero_file="ldefrate_with_zero.tif",
                       blk_rows=128,
                       verbose=True):
    """Set a value of one (1) to pixels with zero deforestation
    risk. A null risk of deforestation is assumed when distance to
    forest edge is greater than the distance threshold. NoData value
    is set to zero (0).

    :param ldefrate_file: Input raster file of local deforestation
        rates. Deforestation rates are defined by integer values
        between rescale_min_val (e.g. 2) and rescale_max_val
        (e.g. 10000). This file is typically obtained with function
        ``local_defor_rate()``.

    :param dist_file: Path to the distance to forest edge raster file.

    :param dist_thresh: The distance threshold. This distance
        threshold is used to identify pixels with zero deforestation
        risk.

    :param ldefrate_with_zero_file: Output raster file. Default to
        "ldefrate_with_zero.tif" in the current working
        directory. Pixels with zero deforestation risk are assigned a
        value of 1.

    :param blk_rows: If > 0, number of rows for computation by block.

    :param verbose: Logical. Whether to print messages or not. Default
        to ``True``.

    :return: None. A raster file identifying pixels with zero risk of
        deforestation (value 1) will be created (see
        ``ldefrate_with_zero_file``).

    """

    # ==============================================================
    # Input rasters: deforestation rates and distance to forest edge
    # ==============================================================

    # Get local deforestation rate (ldefrate) raster data
    ldefrate_ds = gdal.Open(ldefrate_file)
    ldefrate_band = ldefrate_ds.GetRasterBand(1)
    # Raster size
    xsize = ldefrate_band.XSize
    ysize = ldefrate_band.YSize

    # Get distance to forest edge (dist) raster data
    dist_ds = gdal.Open(dist_file)
    dist_band = dist_ds.GetRasterBand(1)

    # Make blocks
    blockinfo = makeblock(ldefrate_file, blk_rows=blk_rows)
    nblock = blockinfo[0]
    nblock_x = blockinfo[1]
    x = blockinfo[3]
    y = blockinfo[4]
    nx = blockinfo[5]
    ny = blockinfo[6]

    # ==================================
    # Zero category (beyond dist_thresh)
    # ==================================

    # Create cat_zero (catzero) raster
    driver = gdal.GetDriverByName("GTiff")
    if os.path.isfile(ldefrate_with_zero_file):
        os.remove(ldefrate_with_zero_file)
    catzero_ds = driver.Create(
        ldefrate_with_zero_file, xsize, ysize,
        1, gdal.GDT_UInt16, ["COMPRESS=LZW",
                             "PREDICTOR=2", "BIGTIFF=YES"])
    catzero_ds.SetProjection(ldefrate_ds.GetProjection())
    catzero_ds.SetGeoTransform(ldefrate_ds.GetGeoTransform())
    catzero_band = catzero_ds.GetRasterBand(1)
    catzero_band.SetNoDataValue(0)

    # Loop on blocks of data
    for b in range(nblock):
        # Progress bar
        if verbose:
            progress_bar(nblock, b + 1)
        # Position
        px = b % nblock_x
        py = b // nblock_x
        # Data
        catzero_data = ldefrate_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        dist_data = dist_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        # Set 1 for zero risk of deforestation (beyond distance threshold)
        # !: dist to forest edge has positive values outside country border
        # Also ensure NoData outside country borders (second condition)
        catzero_data[(dist_data >= dist_thresh) & (catzero_data != 0)] = 1
        # Ensure NoData when dist_data equals zero (especially for t2)
        catzero_data[dist_data == 0] = 0
        # Write data to band
        catzero_band.WriteArray(catzero_data, x[px], y[py])

    # Compute statistics
    catzero_band.FlushCache()
    cb = gdal.TermProgress_nocb if verbose else 0
    catzero_band.ComputeStatistics(False, cb)

    # Dereference drivers
    catzero_band = None
    del catzero_ds
    del ldefrate_ds, dist_ds

    return None


# # Test
# ldefrate_file = "outputs/ldefrate_ws7.tif"
# dist_file = "outputs/dist_edge.tif"
# dist_thresh = 390
# ldefrate_with_zero_file = "outputs/ldefrate_with_zero.tif"
# blk_rows = 128
# verbose = True

# set_defor_cat_zero(ldefrate_file,
#                    dist_file,
#                    dist_thresh,
#                    ldefrate_with_zero_file,
#                    blk_rows=128,
#                    verbose=True)

# End
