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
from .misc import progress_bar, makeblock


# defrate_per_cat
def defrate_per_cat(fcc_file, defor_values, riskmap_file, time_interval,
                    tab_file_defrate="defrate_per_cat.csv",
                    blk_rows=128, verbose=True):
    """Compute deforestation rates per category of deforestation risk.

    This function computes the historical deforestation rates for each
    category of spatial deforestation risk.

    :param fcc_file: Input raster file of forest cover change at three
        dates (123). 1: first period deforestation, 2: second period
        deforestation, 3: remaining forest at the end of the second
        period. No data value must be 0 (zero).

    :param defor_values: Raster values to consider for
       deforestation. Must correspond to either scalar 1 if first
       period, or list [1, 2] if both first and second period are
       considered.

    :param riskmap_file: Input raster file with categories of
        spatial deforestation risk. This file is typically obtained
        with function ``defor_cat()``.

    :param time_interval: Time interval (in years) for forest cover
        change observations.

    :param tab_file_defrate: Path to the ``.csv`` output file with
        estimates of deforestation rates per category of deforestation
        risk.

    :param blk_rows: If > 0, number of rows for computation by block.

    :param verbose: Logical. Whether to print messages or not. Default
        to ``True``.

    :return: None. A ``.csv`` file with deforestation rates per
        category of deforestation risk will be created (see
        ``tab_file_defrate``).

    """

    # ==============================================================
    # Input rasters
    # ==============================================================

    # Get fcc raster data
    fcc_ds = gdal.Open(fcc_file)
    fcc_band = fcc_ds.GetRasterBand(1)

    # Get defor_cat raster data
    defor_cat_ds = gdal.Open(riskmap_file)
    defor_cat_band = defor_cat_ds.GetRasterBand(1)

    # Make blocks
    blockinfo = makeblock(fcc_file, blk_rows=blk_rows)
    nblock = blockinfo[0]
    nblock_x = blockinfo[1]
    x = blockinfo[3]
    y = blockinfo[4]
    nx = blockinfo[5]
    ny = blockinfo[6]

    # ==============================================
    # Compute deforestation rates per cat
    # ==============================================

    # Number of deforestation categories
    cb = gdal.TermProgress if verbose else 0
    stats = defor_cat_band.ComputeStatistics(False, cb)
    n_cat = int(stats[1])  # Get the maximum
    cat = [c + 1 for c in range(n_cat)]

    # Create a table to save the results
    data = {"cat": cat, "nfor": 0, "ndefor": 0,
            "rate": 0}
    df = pd.DataFrame(data)

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
        defor_cat_data = defor_cat_band.ReadAsArray(
            x[px], y[py], nx[px], ny[py])
        # nfor_per_cat
        data_for = defor_cat_data[fcc_data > 0]
        cat_for = pd.Categorical(data_for.flatten(), categories=cat)
        df["nfor"] += cat_for.value_counts().values
        # ndefor_per_cat
        data_defor = defor_cat_data[np.isin(fcc_data, defor_values)]
        cat_defor = pd.Categorical(data_defor.flatten(), categories=cat)
        df["ndefor"] += cat_defor.value_counts().values

    # Annual deforestation rates per category
    df["rate"] = 1 - (1 - df["ndefor"] / df["nfor"]) ** (1 / time_interval)

    # Export the table of results
    df.to_csv(tab_file_defrate, sep=",", header=True,
              index=False, index_label=False)

    # Dereference drivers
    del fcc_ds, defor_cat_ds

    return None


# # Test
# fcc_file = "data/fcc123.tif"
# riskmap_file = "outputs/defor_cat.tif"
# time_interval = 10
# tab_file_defrate = "outputs/defrate_per_cat.csv"
# blk_rows = 128

# defrate_per_cat(fcc_file,
#                 riskmap_file,
#                 time_interval,
#                 tab_file_defrate,
#                 blk_rows=128,
#                 verbose=True)

# End
