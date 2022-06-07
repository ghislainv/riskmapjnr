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
from misc import progress_bar, makeblock


# defor_cat
def defor_cat(input_file,
              output_file="defor_cat.tif",
              nbins=30,
              method="Equal Area",
              blk_rows=128):
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

    :param input_file: Input raster file of local deforestation
        rates. Deforestation rates are defined by integer values
        between 0 and 10000 (ten thousand)). Pixels with zero
        deforestation risk (beyond a certain distance from the forest
        edge) have value 10001. This file is typically obtained with
        function ``set_defor_cat_zero()``.

    :param output_file: Output raster file with categories of
        deforestation risk.

    :param nbins: Number of deforestation risk categories (zero
        risk class excluded). Default to 30.

    :param method: Method used for categorizing. Either "Equal
        Interval", "Equal Area", or "Natural Breaks".

    :param blk_rows: If > 0, number of rows for computation by block.

    :return: None. A raster file with deforestation categories will be
        created (see ``output_file``). Data range from 0 to 30. Raster
        type is Byte ([0, 255]). NoData value is set to 255.

    """

    # ==============================================================
    # Input raster
    # ==============================================================

    # Get catzero (catzero) raster data
    catzero_ds = gdal.Open(input_file)
    catzero_band = catzero_ds.GetRasterBand(1)
    # Raster size
    xsize = catzero_band.XSize
    ysize = catzero_band.YSize

    # Make blocks
    blockinfo = makeblock(input_file, blk_rows=blk_rows)
    nblock = blockinfo[0]
    nblock_x = blockinfo[1]
    x = blockinfo[3]
    y = blockinfo[4]
    nx = blockinfo[5]
    ny = blockinfo[6]
    print("Divide region in {} blocks".format(nblock))

    # ==============================================
    # Categorical raster file for deforestation risk
    # ==============================================

    # Create categorical (cat) raster file for deforestation risk
    driver = gdal.GetDriverByName("GTiff")
    cat_ds = driver.Create(output_file, xsize, ysize, 1,
                           gdal.GDT_Byte,
                           ["COMPRESS=LZW", "PREDICTOR=2",
                            "BIGTIFF=YES"])
    cat_ds.SetProjection(catzero_ds.GetProjection())
    cat_ds.SetGeoTransform(catzero_ds.GetGeoTransform())
    cat_band = cat_ds.GetRasterBand(1)
    cat_band.SetNoDataValue(255)

    # -----------------
    # Categorize
    # -----------------

    # Equal Interval
    if method == "Equal Interval":
        bin_size = round(10000 / nbins)
        bins = [i * bin_size for i in range(nbins)]
        bins = bins + [10000, 10001]

    # Equal Area
    if method == "Equal Area":
        # Compute histogram
        print("Compute histogram")
        nvalues = 10000 + 1
        counts = catzero_band.GetHistogram(-0.5, 10000.5, nvalues, 0, 0)
        npix = sum(counts)
        # Percentage
        perc = np.array(counts) / npix
        # Cumulative percentage
        cum_perc = np.cumsum(perc)
        # Correction of the approximation
        cum_perc[-1] = 1.0
        # Quantiles
        q = [i * 1 / nbins for i in range(1, nbins + 1)]
        # Bins
        bins = [0]
        # Loop on quantiles
        for qi in q:
            comp = (cum_perc <= qi)
            sum_comp = np.sum(comp)
            if sum_comp != 0:
                bins.append(sum_comp - 1)
        # Remove duplicate
        bins = list(np.unique(bins))
        # Add category 10001
        bins.append(10001)

    # Loop on blocks of data
    for b in range(nblock):
        # Progress bar
        progress_bar(nblock, b + 1)
        # Position
        px = b % nblock_x
        py = b // nblock_x
        # Data
        catzero_data = catzero_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        # Categorize
        cat_data = pd.cut(catzero_data.flatten(), bins=bins,
                          labels=False, include_lowest=True)
        cat_data = cat_data + 1
        cat_data[np.isnan(cat_data)] = 255
        cat_data[cat_data == (len(bins) - 1)] = 0
        cat_data = cat_data.reshape(catzero_data.shape)
        # Write to file
        cat_band.WriteArray(cat_data, x[px], y[py])

    # Compute statistics
    print("Compute statistics")
    cat_band.FlushCache()
    cat_band.ComputeStatistics(False)

    # Dereference drivers
    cat_band = None
    del cat_ds, catzero_ds

    return None


# # Test
# input_file = "outputs/defor_cat_zero.tif"
# output_file = "outputs/defor_cat.tif"
# nbins = 30
# method = "Equal Area"
# blk_rows = 128

# defor_cat(input_file,
#           output_file="outputs/defor_cat_equal_interval.tif",
#           nbins=30,
#           method="Equal Interval",
#           blk_rows=128)

# defor_cat(input_file,
#           output_file="outputs/defor_cat_equal_area.tif",
#           nbins=30,
#           method="Equal Area",
#           blk_rows=128)

# End
