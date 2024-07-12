"""Compute deforestation rates per vulnerability class."""

import numpy as np
from osgeo import gdal
import pandas as pd

from ..misc import progress_bar, makeblock


def defrate_per_class(
        fcc_file,
        vulnerability_file,
        time_interval,
        period="calibration",
        deforate_model=None,
        tab_file_defrate="defrate_per_class.csv",
        blk_rows=128,
        verbose=True):
    """Compute deforestation rates per vulnerability class.

    This function computes the historical deforestation rates for each
    vulnerability class.

    A ``.csv`` file with deforestation rates for each vulnerability
    class is created (see ``tab_file_defrate``).

    :param fcc_file: Input raster file of forest cover change at three
        dates (123). 1: first period deforestation, 2: second period
        deforestation, 3: remaining forest at the end of the second
        period. No data value must be 0 (zero).

    :param vulnerability_file: Input file with vulnerability classes.

    :param time_interval: Time interval (in years) for forest cover
        change observations.

    :param period: Either "calibration" (from t1 to t2), "validation"
        (or "confirmation" from t2 to t3), or "historical" (full
        historical period from t1 to t3). Default to "calibration".

    :param deforate_model: Path to the ``.csv`` input file with
        deforestation rates per class from the model's period
        (either "calibration" or "historical" period). Used for
        estimating deforestation for the "validation" or "forecast"
        period after quantity adjustment.

    :param tab_file_defrate: Path to the ``.csv`` output file with
        estimates of deforestation rates for each vulnerability class.

    :param blk_rows: If > 0, number of rows for computation by block.

    :param verbose: Logical. Whether to print messages or not. Default
        to ``True``.

    """

    # ==============================================================
    # Input rasters
    # ==============================================================

    # Get fcc raster data
    fcc_ds = gdal.Open(fcc_file)
    fcc_band = fcc_ds.GetRasterBand(1)

    # Landscape variables
    gt = fcc_ds.GetGeoTransform()
    xres = gt[1]
    yres = -gt[5]

    # Get defor_cat raster data
    defor_cat_ds = gdal.Open(vulnerability_file)
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
    n_cat_max = 30999
    cat = [c + 1 for c in range(n_cat_max)]

    # Create a table to save the results
    data = {"cat": cat, "nfor": 0, "ndefor": 0}
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
        # Defor data on period
        if period == "calibration":
            data_for = defor_cat_data[fcc_data > 0]
            data_defor = defor_cat_data[fcc_data == 1]
        elif period == "validation":
            data_for = defor_cat_data[fcc_data > 1]
            data_defor = defor_cat_data[fcc_data == 2]
        else:  # historical or forecast
            data_for = defor_cat_data[fcc_data > 0]
            data_defor = defor_cat_data[np.isin(fcc_data, [1, 2])]
        # nfor_per_cat
        cat_for = pd.Categorical(data_for.flatten(),
                                 categories=cat)
        df["nfor"] += cat_for.value_counts().values
        # ndefor_per_cat
        cat_defor = pd.Categorical(data_defor.flatten(),
                                   categories=cat)
        df["ndefor"] += cat_defor.value_counts().values

    # Remove classes with no forest
    df = df[df["nfor"] != 0]

    # Annual deforestation rates per category (just for info)
    df["rate_obs"] = (1 - (1 - df["ndefor"] / df["nfor"])
                      ** (1 / time_interval))

    # Relative deforestation rate from model (not annual)
    if period in ["validation", "forecast"]:
        df_mod = pd.read_csv(deforate_model)
        # Some defor class might be missing in the future
        # so we need to join the tables to get rate_mod.
        df = df.merge(right=df_mod, on="cat", how="left", suffixes=(None, "_mod"))
    else:
        df["rate_mod"] = df["ndefor"] / df["nfor"]

    # Correction factor, either ndefor / sum_i p_i
    # or theta * nfor / sum_i p_i
    sum_ndefor = df["ndefor"].sum()
    sum_pi = (df["nfor"] * df["rate_mod"]).sum()
    correction_factor = sum_ndefor / sum_pi

    # Absolute deforestation probability
    # With quantity adjustment
    df["rate_abs"] = df["rate_mod"] * correction_factor

    # Time interval
    df["time_interval"] = time_interval

    # Pixel area
    pixel_area = xres * yres / 10000
    df["pixel_area"] = pixel_area

    # Deforestation density (ha/pixel/yr)
    df["defor_dens"] = df["rate_abs"] * pixel_area / time_interval

    # Export the table of results
    df.to_csv(tab_file_defrate, sep=",", header=True,
              index=False, index_label=False)

    # Dereference drivers
    del fcc_ds, defor_cat_ds


# # Test
# import os
# os.chdir("/home/ghislain/deforisk/MTQ_2000_2010_2020_jrc_7221/")
# defrate_per_class(
#     fcc_file="data/forest/fcc123.tif",
#     vulnerability_file="outputs/benchmark_model/vulnerability_classes.tif",
#     time_interval=10,
#     period="calibration",
#     tab_file_defrate="outputs/benchmark_model/defrate_per_class.csv",
#     blk_rows=128,
#     verbose=True)

# End
