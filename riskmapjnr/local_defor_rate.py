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
import scipy.ndimage

from .misc import progress_bar, rescale


# local_defor_rate
def local_defor_rate(fcc_file, defor_values, ldefrate_file, win_size,
                     time_interval, rescale_min_val=2,
                     rescale_max_val=10000, blk_rows=128,
                     verbose=True):
    """Computing the local deforestation rate using a moving window.

    This function computes the local deforestation rate using a moving
    window. SciPy is used for the focal analysis. The
    ``uniform_filter`` is used over the ``generic_filter``. The
    ``generic_filter`` is 40 times slower than the strides implemented
    in the ``uniform_filter``. For cells on the edge of the raster,
    the local deforestation rate is computed from a lower number of
    existing cells in the moving window using ``mode='constant'`` and
    ``cval=0``.

    :param fcc_file: Input raster file of forest cover change at
        three dates (123). 1: first period deforestation, 2: second
        period deforestation, 3: remaining forest at the end of the
        second period. NoData value must be 0 (zero).

    :param defor_values: Raster values to consider for
       deforestation. Must correspond to either scalar 1 if first
       period, or list [1, 2] if both first and second period are
       considered.

    :param ldefrate_file: Output raster file.

    :param win_size: Size of the moving window in number of
        cells. Must be an odd number lower or equal to ``blk_rows``.

    :param time_interval: Time interval (in years) for forest cover
        change observations.

    :param rescale_min_val: Integer. Minimal value for rescaling. Down
        to 1. Default to 1.

    :param rescale_max_val: Integer. Maximal value for rescaling. Up
        to 65535. Default to 10000.

    :param blk_rows: Number of rows for block. Must be greater or
        equal to ``win_size``. This is used to break lage raster files
        in several blocks of data that can be hold in memory.

    :param verbose: Logical. Whether to print messages or not. Default
        to ``True``.

    :return: None. A raster with the local deforestation rate will be
        created (see ``ldefrate_file``). Data range from 1 to
        10000. Raster type is UInt16 ([0, 65535]). NoData value is set
        to 65535.

    """

    # Check win_size
    win_size = int(win_size)  # Must be int for uniform_filter
    if (win_size % 2) == 0:
        msg = "'win_size' must be an odd number."
        raise ValueError(msg)
    if win_size > blk_rows:
        msg = "'win_size' must be lower or equal to 'blk_rows'."
        raise ValueError(msg)

    # Get raster data
    in_ds = gdal.Open(fcc_file)
    in_band = in_ds.GetRasterBand(1)
    # Raster size
    xsize = in_band.XSize
    ysize = in_band.YSize

    # Create output raster file
    driver = gdal.GetDriverByName("GTiff")
    if os.path.isfile(ldefrate_file):
        os.remove(ldefrate_file)
    out_ds = driver.Create(ldefrate_file, xsize, ysize, 1,
                           gdal.GDT_UInt16,
                           ["COMPRESS=LZW", "PREDICTOR=2",
                            "BIGTIFF=YES"])
    out_ds.SetProjection(in_ds.GetProjection())
    out_ds.SetGeoTransform(in_ds.GetGeoTransform())
    out_band = out_ds.GetRasterBand(1)
    out_band.SetNoDataValue(0)

    # Iteration
    iter_block = 0

    # Loop on blocks of data
    for i in range(0, ysize, blk_rows):

        # Progress bar
        nblock = (ysize // blk_rows) + 1
        iter_block = iter_block + 1
        if verbose:
            progress_bar(nblock, iter_block)

        # Extra lines at the bottom and top
        extra_lines = win_size // 2

        # Compute y offset and line numbers
        # For the condition, think in terms of cell index (starting from 0),
        # not cell number (starting from 1).
        if (i + blk_rows + 2 * extra_lines - 1) < ysize:
            rows = blk_rows + 2 * extra_lines
        else:
            rows = ysize - i + extra_lines
        yoff = max(0, i - extra_lines)

        # Read block data
        in_data = in_band.ReadAsArray(0, yoff, xsize, rows)
        # defor (during period)
        defor_data = np.zeros(in_data.shape, int)
        defor_data[np.isin(in_data, defor_values)] = 1
        # Use uniform filter to get the mean then multiply to obtain the sum
        win_defor = scipy.ndimage.uniform_filter(
            defor_data, size=win_size, mode="constant", cval=0,
            output=float) * (win_size ** 2)
        # Round to nearest int to remove approximation due to float precision
        win_defor = np.rint(win_defor).astype(int)
        # for (start of first period)
        for_data = np.zeros(in_data.shape, int)
        w = np.where(in_data > 0)
        for_data[w] = 1
        # Use uniform filter to get the mean then multiply to obtain the sum
        win_for = scipy.ndimage.uniform_filter(
            for_data, size=win_size, mode="constant", cval=0,
            output=float) * (win_size ** 2)
        # Round to nearest inter to remove approximation due to float precision
        win_for = np.rint(win_for).astype(int)
        # Annual deforestation rate
        out_data = np.zeros(in_data.shape, int)
        theta = 1 - (1 - win_defor[w] / win_for[w]) ** (1 / time_interval)
        # Rescale
        out_data[w] = rescale(theta, rescale_min_val, rescale_max_val)
        if yoff == 0:
            out_band.WriteArray(out_data)
        else:
            out_band.WriteArray(out_data[(extra_lines):], 0,
                                yoff + extra_lines)

    # Closing
    out_band.FlushCache()
    cb = gdal.TermProgress_nocb if verbose else 0
    out_band.ComputeStatistics(False, cb)
    del out_ds, in_ds


# # Test
# ws = 7
# local_defor_rate(fcc_file="data/fcc123_GLP.tif",
#                  ldefrate_file="outputs/ldefrate_ws{}.tif".format(ws),
#                  win_size=ws,
#                  time_interval=10,
#                  blk_rows=100)

# End
