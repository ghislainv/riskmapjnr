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
import time

# Local application imports
from .misc import progress_bar, makeblock, make_square


# validation
def validation(fcc_file, time_interval,
               defor_cat_file, defrate_per_cat_file,
               csize=300,
               tab_file="validation_data.csv",
               fig_file="pred_obs.png"):
    """Validation of the deforestation risk map.

    This function computes the observed and predicted deforestion (in
    ha) for the validation time period. Deforestion is computed for
    spatial grid cells of a maximum size of 10km. Deforestation rate
    estimates obtained with the ``defrate_per_cat`` function are used
    to compute the predicted deforestation in each grid cell. The
    function creates both a `.csv` file with the validation data and a
    plot comparing predictions vs. observations. The function returns
    the weighted Root Mean Squared Error (wRMSE, in hectares)
    associated with the deforestation predictions.

    :param fcc_file: Input raster file of forest cover change at three
        dates (123). 1: first period deforestation, 2: second period
        deforestation, 3: remaining forest at the end of the second
        period. No data value must be 0 (zero).

    :param time_interval: Time interval (in years) for forest cover
        change observations.

    :param defor_cat_file: Input raster file with categories of
        spatial deforestation risk. This file is typically obtained
        with function ``defor_cat()``.

    :param defrate_per_cat_file: Path to the `.csv` input file with
        estimates of deforestation rates per category of deforestation
        risk. This file is typically obtained with function
        ``defrate_per_cat()``.

    :param csize: Spatial cell size in number of pixels. Must
        correspond to a distance < 10 km. Default to 300 corresponding
        to 9 km for a 30 m resolution raster.

    :param tab_file: Path to the `.csv` output file with validation
        data.

    :param fig_file: Path to the `.png` output file for the
        predictions vs. observations plot.

    :return: the weighted Root Mean Squared Error (in hectares) of the
        deforestation predictions.

    """

    # ==============================================================
    # Input raster
    # ==============================================================

    # Get fcc raster data
    fcc_ds = gdal.Open(fcc_file)
    fcc_band = fcc_ds.GetRasterBand(1)

    # Get defor_cat raster data
    defor_cat_ds = gdal.Open(defor_cat_file)
    defor_cat_band = defor_cat_ds.GetRasterBand(1)

    # Get defrate per cat
    defrate_per_cat = pd.read_csv(defrate_per_cat_file)
    cat_csv = defrate_per_cat["cat"].values

    # Number of deforestation categories
    print("Compute statistics")
    stats = defor_cat_band.ComputeStatistics(False)
    n_cat = int(stats[1])  # Get the maximum
    cat_raster = np.array([c + 1 for c in range(n_cat)])

    # Check categories
    if not np.array_equal(cat_csv, cat_raster):
        msg = ("Categories in the 'defrate_per_cat_file' csv file do not"
               "correspond to categories in the 'defor_cat_file' raster"
               "file.")
        raise ValueError(msg)
    else:
        cat = cat_csv

    # Pixel area (in unit square, eg. meter square)
    gt = fcc_ds.GetGeoTransform()
    pix_area = gt[1] * (-gt[5])

    # Make spatial cell
    cellinfo = make_square(fcc_file, csize)
    ncell = cellinfo[0]
    ncell_x = cellinfo[1]
    x_cell = cellinfo[3]
    nx_cell = cellinfo[5]

    # Some info on cells
    x_cell_min = x_cell
    x_cell_max = np.array(x_cell) + np.array(nx_cell) - 1

    # Create a table to save the results
    data = {"cell": list(range(ncell)), "nfor_obs": 0,
            "ndefor_obs": 0, "ndefor_pred": 0}
    df = pd.DataFrame(data)

    # # Loop on squares
    # for s in range(nsquare):
    #     # Progress bar
    #     progress_bar(nsquare, s + 1)
    #     # Position in 1D-arrays
    #     px = s % nsquare_x
    #     py = s // nsquare_x
    #     # Observed forest cover and deforestation for validation period
    #     fcc_data = fcc_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
    #     df.loc[s, "nfor_obs"] = np.sum(fcc_data > 1)
    #     df.loc[s, "ndefor_obs"] = np.sum(fcc_data == 2)
    #     # Predicted deforestation for validation period
    #     defor_cat_data = defor_cat_band.ReadAsArray(
    #         x[px], y[py], nx[px], ny[py])
    #     defor_cat = pd.Categorical(defor_cat_data.flatten(), categories=cat)
    #     defor_cat_count = defor_cat.value_counts().values
    #     df.loc[s, "ndefor_pred"] = np.sum(defor_cat_count *
    #                                       defrate_per_cat["rate"].values)

    # Make blocks
    blockinfo = makeblock(fcc_file, blk_rows=csize)
    nblock = blockinfo[0]
    nblock_x = blockinfo[1]
    x = blockinfo[3]
    y = blockinfo[4]
    nx = blockinfo[5]
    ny = blockinfo[6]
    print("Divide region in {} blocks".format(nblock))

    # # Some info on blocks
    # nelement = nx[0] * ny[0]
    # blk_shape = (ny[0], nx[0])

    # # Array with cell id
    # cell_id = list(range(ncell_x))
    # cell_data = np.repeat(cell_id, repeats=csize*csize)[:nelement]
    # cell_data = cell_data.reshape(blk_shape, order="F")

    # Loop on squares
    for s in range(nblock):
        # Progress bar
        progress_bar(nblock, s + 1)
        # Position in 1D-arrays
        px = s % nblock_x
        py = s // nblock_x
        # Data
        fcc_data = fcc_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        defor_cat_data = defor_cat_band.ReadAsArray(
            x[px], y[py], nx[px], ny[py])
        # Loop on cells
        for c in range(ncell_x):
            # Get cell id
            c_id = s * ncell_x + c
            # Extract data for cell
            fcc_cell = fcc_data[:, x_cell_min[c]:x_cell_max[c]]
            defor_cat_cell = defor_cat_data[:, x_cell_min[c]:x_cell_max[c]]
            # Observed forest cover and deforestation for validation period
            df.loc[c_id, "nfor_obs"] = np.sum(fcc_cell > 1)
            df.loc[c_id, "ndefor_obs"] = np.sum(fcc_cell == 2)
            # Predicted deforestation for validation period
            defor_cat = pd.Categorical(
                defor_cat_cell.flatten(), categories=cat)
            defor_cat_count = defor_cat.value_counts().values
            df.loc[c_id, "ndefor_pred"] = np.sum(
                defor_cat_count *
                defrate_per_cat["rate"].values
            )

    # Dereference drivers
    del fcc_ds, defor_cat_ds

    # Select cells with forest cover > 0
    df = df[df["nfor_obs"] > 0]
    if df.shape[0] < 1000:
        msg = ("Number of cells with forest cover > 0 ha is < 1000. "
               "Please decrease the spatial cell size 'csize' to get"
               "more cells.")
        raise ValueError(msg)

    # Compute areas in ha
    df.loc["nfor_obs_ha"] = df["nfor_obs"] * pix_area / 10000
    df.loc["ndefor_obs_ha"] = df["ndefor_obs"] * pix_area / 10000
    df.loc["ndefor_pred_ha"] = df["ndefor_pred"] * pix_area / 10000

    # Export the table of results
    df.to_csv(tab_file, sep=",", header=True,
              index=False, index_label=False)

    return None


# Test
fcc_file = "data/fcc123.tif"
time_interval = 10
defor_cat_file = "outputs/defor_cat.tif"
defrate_per_cat_file = "outputs/defrate_per_cat.csv"
csize = 300
tab_file = "outputs/validation_data_block.csv"
fig_file = "outputs/pred_obs.png"

tic = time.perf_counter()
validation(fcc_file, time_interval, defor_cat_file, defrate_per_cat_file,
           csize, tab_file, fig_file)
toc = time.perf_counter()
print(f"Computation in {toc - tic:0.4f} seconds")

# End
