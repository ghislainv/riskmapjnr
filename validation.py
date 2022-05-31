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
from misc import progress_bar, make_square


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

    # Make square
    squareinfo = make_square(fcc_file, csize)
    nsquare = squareinfo[0]
    nsquare_x = squareinfo[1]
    x = squareinfo[3]
    y = squareinfo[4]
    nx = squareinfo[5]
    ny = squareinfo[6]
    print("Divide region in {} square cells".format(nsquare))

    # Create a table to save the results
    data = {"cell": list(range(nsquare)), "nfor_obs": 0,
            "ndefor_obs": 0, "ndefor_pred": 0}
    df = pd.DataFrame(data)

    # Loop on squares
    for s in range(nsquare):
        # Progress bar
        progress_bar(nsquare, s + 1)
        # Position in 1D-arrays
        px = s % nsquare_x
        py = s // nsquare_x
        # Observed forest cover and deforestation for validation period
        fcc_data = fcc_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        df.loc[s, "nfor_obs"] = np.sum(fcc_data > 1)
        df.loc[s, "ndefor_obs"] = np.sum(fcc_data == 2)
        # Predicted deforestation for validation period
        defor_cat_data = defor_cat_band.ReadAsArray(
            x[px], y[py], nx[px], ny[py])
        defor_cat = pd.Categorical(defor_cat_data.flatten(), categories=cat)
        defor_cat_count = defor_cat.value_counts().values
        df.loc[s, "ndefor_pred"] = np.sum(defor_cat_count *
                                          defrate_per_cat["rate"].values)
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
    df["nfor_obs_ha"] = df["nfor_obs"] * pix_area / 10000
    df["ndefor_obs_ha"] = df["ndefor_obs"] * pix_area / 10000
    df["ndefor_pred_ha"] = df["ndefor_pred"] * pix_area / 10000

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
tab_file = "outputs/validation_data.csv"
fig_file = "outputs/pred_obs.png"

# End
