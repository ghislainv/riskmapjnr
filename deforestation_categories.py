#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=3
# license         :GPLv3
# ==============================================================================

# Standard library imports
import os

# Third party imports
import numpy as np
from osgeo import gdal

# Local application imports
from misc import progress_bar, makeblock


# deforestation_categories
def deforestation_categories(input_file,
                             dist_file,
                             dist_thresh,
                             method="Equal Area",
                             blk_rows=128):
    """Computing the deforestation categories from the map of local
    deforestation rates.

    This function computes the deforestation categories from the map
    of local deforestation rates. Three categorization methods can be
    used, either "Equal Area", "Equal Interval", or "Natural
    Breaks". When "Equal Area" is used, the classes with a risk > 0
    have approximately the same surface area. When "Equal Interval" is
    used, some risk classes will predominate in the risk map while
    other classes will be present only in small areas. When "Natural
    Breaks" is used, the data is normalized before running the slicing
    algorithm.

    :param input_file: Input raster file of local deforestation
        rates. Deforestation rates must be in the interval [0,
        10000]. This file is typically obtained with function
        ``local_defor_rate()``.

    :param dist_file: Path to the distance raster file.

    :param dist_thresh: The distance threshold. This distance
        threshold is used to identify pixels with zero deforestation risk
        (category 0).

    :param output_file: Output raster file.

    :param blk_rows: If > 0, number of rows for computation by block.

    :return: None. A raster file with deforestation categories will be
        created (see ``output_file``). Data range from 0 to 30. Raster
        type is Byte ([0, 255]). NoData value is set to 255.

    """

    # ==============================================================
    # Input rasters: deforestation rates and distance to forest edge
    # ==============================================================

    # Get local deforestation rate (ldefrate) raster data
    ldefrate_ds = gdal.Open(input_file)
    ldefrate_band = ldefrate_ds.GetRasterBand(1)
    # Raster size
    xsize = ldefrate_band.XSize
    ysize = ldefrate_band.YSize

    # Get distance to edge (dist) raster data
    dist_ds = gdal.Open(dist_file)
    dist_band = dist_ds.GetRasterBand(1)

    # Make blocks
    blockinfo = makeblock(input_file, blk_rows=blk_rows)
    nblock = blockinfo[0]
    nblock_x = blockinfo[1]
    x = blockinfo[3]
    y = blockinfo[4]
    nx = blockinfo[5]
    ny = blockinfo[6]
    # print("Divide region in {} blocks".format(nblock))

    # ==================================
    # Zero category (beyond dist_thresh)
    # ==================================

    # Create temp directory
    output_dir = os.path.dirname(output_file)

    # Create cat_zero (catzero) raster
    catzero_file = os.path.join(output_dir, "cat_zero.tif")
    driver = gdal.GetDriverByName("GTiff")
    catzero_ds = driver.Create(catzero_file, xsize, ysize, 1,
                               gdal.GDT_UInt16,
                               ["COMPRESS=LZW",
                                "PREDICTOR=2", "BIGTIFF=YES"])
    catzero_ds.SetProjection(ldefrate_ds.GetProjection())
    catzero_ds.SetGeoTransform(ldefrate_ds.GetGeoTransform())
    catzero_band = catzero_ds.GetRasterBand(1)
    catzero_band.SetNoDataValue(65535)

    # Loop on blocks of data
    for b in range(nblock):
        # Progress bar
        progress_bar(nblock, b + 1)
        # Position
        px = b % nblock_x
        py = b // nblock_x
        # Data
        catzero_data = ldefrate_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        dist_data = dist_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        # Replace nodata value in dist_data with 0
        dist_data[dist_data == 65535] = 0
        # Set zero category to value 10001
        catzero_data[dist_data >= dist_thresh] = 10001
        catzero_band.WriteArray(catzero_data, x[px], y[py])

    # Compute statistics
    # print("Compute statistics")
    catzero_band.FlushCache()  # Write cache data to disk
    catzero_band.ComputeStatistics(False)

    # Dereference driver
    catzero_band = None
    del catzero_ds
        
    # ==============================================
    # Categorical raster file for deforestation risk
    # ==============================================

    # Get catzero (catzero) raster data
    catzero_ds = gdal.Open(catzero_file)
    catzero_band = catzero_ds.GetRasterBand(1)
    
    # Create categorical (cat) raster file for deforestation risk
    driver = gdal.GetDriverByName("GTiff")
    cat_ds = driver.Create(output_file, xsize, ysize, 1,
                           gdal.GDT_Byte,
                           ["COMPRESS=LZW", "PREDICTOR=2",
                            "BIGTIFF=YES"])
    cat_ds.SetProjection(ldefrate_ds.GetProjection())
    cat_ds.SetGeoTransform(ldefrate_ds.GetGeoTransform())
    cat_band = cat_ds.GetRasterBand(1)
    cat_band.SetNoDataValue(255)

    # -----------------
    # Compute histogram
    # -----------------

    nvalues = 10000 + 1
    counts = catzero_band.GetHistogram(-0.5, 10000.5, nvalues, 0, 0)

    # Closing
    out_band.FlushCache()
    out_band.ComputeStatistics(False)
    del out_ds, in_ds
    return None


# Test
input_file = "outputs/ldefrate_ws7.tif"
dist_file = "outputs/dist_edge.tif"
output_file = "outputs/defor_cat.tif" 
dist_thresh = 390
method = "Equal Area"
blk_rows = 128

# End
