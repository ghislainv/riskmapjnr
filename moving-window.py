#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=3
# license         :GPLv3
# ==============================================================================

# Import
import os

# Third party imports
import numpy as np
from osgeo import gdal
import scipy

# Local application imports
from ..misc import progress_bar


# perc_defor
def perc_defor(input, output, win_size, blk_rows=128):
    """Compute the percentage of deforestation using a moving window.

    Compute the percentage of deforestation using a moving
    window. SciPy is used for the focal analysis. The uniform_filter
    is used over the generic_filter. The generic_filter is 40 times
    slower than the strides implemented in the uniform_filter.

    :param input_file: Input raster file of forest cover change at three
        dates (123). No data value must be 0 (zero).
    :param output_file: Output raster file.
    :param win_size: Window size in number of cells. Must be an odd number.
    :param blk_rows: Number of rows for block.

    :return: A raster with the percentage of deforestation locally.

    """

    in_ds = gdal.Open(input_file)
    in_band = in_ds.GetRasterBand(1)

    xsize = in_band.XSize
    ysize = in_band.YSize

    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(output_file, xsize, ysize, 1,
                           gdal.GDT_Int32,
                           ["COMPRESS=LZW", "PREDICTOR=2", "BIGTIFF=YES"])
    out_ds.SetProjection(in_ds.GetProjection())
    out_ds.SetGeoTransform(in_ds.GetGeoTransform())
    out_band = out_ds.GetRasterBand(1)
    out_band.SetNoDataValue(-9999)

    for i in range(0, ysize, blk_rows):
        if i + blk_rows + 1 < ysize:
            rows = blk_rows + 2
        else:
            rows = ysize - i
        yoff = max(0, i - 1)

        in_data = in_band.ReadAsArray(0, yoff, xsize, rows)
        # defor
        defor_data = np.zeros(in_data.shape, np.int8)
        defor_data[np.where(in_data == 1)] = 1
        win_defor = scipy.ndimage.uniform_filter(
            defor_data, size=win_size, mode="constant", cval=0)
        # for
        for_data = np.zeros(in_data.shape, np.int8)
        for_data[np.where(in_data != 0)] = 1
        win_for = scipy.ndimage.uniform_filter(
            for_data, size=win_size, mode="constant", cval=0)
        # percentage
        out_data = np.rint(10000 * win_defor / win_for)

        if yoff == 0:
            out_band.WriteArray(out_data)
        else:
            out_band.WriteArray(out_data[1:], 0, yoff + 1)

    out_band.FlushCache()
    out_band.ComputeStatistics(False)
    del out_ds, in_ds

# End
