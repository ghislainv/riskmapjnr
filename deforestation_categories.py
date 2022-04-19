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

    :param input_file: Input raster file of local deforestation rates.

    :param dist_file: Path to the distance raster file.

    :param dist_thresh: The distance threshold.

    :param output_file: Output raster file.

    :param blk_rows: If > 0, number of rows for computation by block.

    :return: None. A raster files with deforestation categories will
        be created (see ``output_file``). Data range from 0 to
        30. Raster type is Byte ([0, 255]), NoData value is set to
        255.

    """

    # Get raster data
    in_ds = gdal.Open(input_file)
    in_band = in_ds.GetRasterBand(1)
    # Raster size
    xsize = in_band.XSize
    ysize = in_band.YSize

    # Create output raster file
    driver = gdal.GetDriverByName("GTiff")
    out_ds = driver.Create(output_file, xsize, ysize, 1,
                           gdal.GDT_Byte,
                           ["COMPRESS=LZW", "PREDICTOR=2", "BIGTIFF=YES"])
    out_ds.SetProjection(in_ds.GetProjection())
    out_ds.SetGeoTransform(in_ds.GetGeoTransform())
    out_band = out_ds.GetRasterBand(1)
    out_band.SetNoDataValue(255)

    # Make blocks
    blockinfo = makeblock(input_file, blk_rows=blk_rows)
    nblock = blockinfo[0]
    nblock_x = blockinfo[1]
    x = blockinfo[3]
    y = blockinfo[4]
    nx = blockinfo[5]
    ny = blockinfo[6]
    print("Divide region in {} blocks".format(nblock))

    # Zero category (beyond dist_thresh)

    # Compute histogram

    # Closing
    out_band.FlushCache()
    out_band.ComputeStatistics(False)
    del out_ds, in_ds
    return None


# # Test
# ws = 7
# local_defor_rate(input_file="data/fcc123.tif",
#                  output_file="outputs/ldefrate_ws{}.tif".format(ws),
#                  win_size=ws,
#                  time_interval=5,
#                  blk_rows=100)

# End
