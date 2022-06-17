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
import shutil

# Third party imports
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

# Local application imports
from .misc import make_dir
from . import dist_edge_threshold, local_defor_rate, set_defor_cat_zero
from . import defor_cat, defrate_per_cat, validation


# makemap
def makemap(fcc_file, time_interval,
            output_dir="outputs",
            clean=False,
            dist_bins=np.arange(0, 1080, step=30),
            win_sizes=[5, 11],
            ncat=30,
            methods=["Equal Interval", "Equal Area"],
            csize=300,
            figsize=(6.4, 4.8),
            dpi=100,
            blk_rows=128,
            verbose=True):
    """Make maps of deforestation risk and select the best.

    This function peforms all the necessary steps to obtain a map of
    the deforestation risk following the JNR methodology.

    :param fcc_file: Input raster file of forest cover change at three
        dates (123). 1: first period deforestation, 2: second period
        deforestation, 3: remaining forest at the end of the second
        period. No data value must be 0 (zero).

    :param time_interval: A list of two numbers. Time interval (in
        years) for forest cover change observations for the two period
        of time.

    :param output_dir: Output directory for files (rasters, tables, and
        figures) produced by calling the ``makemap()`` function:

        * ``dist_edge.tif``: Raster file of distance to forest edge at
          the beginning of the historical period.

        * ``map_comp.csv``: Table for relationship between
          wRMSE and window size by slicing method.

        * ``map_comp.png``: Figure for relationship between
          wRMSE and window size by slicing method.

        * ``perc_dist.csv``: Table of cumulative deforestation with
          distance to forest edge for the entire historical period.

        * ``perc_dist.png``: Figure of cumulative deforestation with
          distance to forest edge for the entire historical period.

        * ``pred_obs_ws{s}_{m}.csv``: Table for predictions
          vs. observations on the validation period for the best model
          with window size ``s`` and slicing method ``m``.

        * ``pred_obs_ws{s}_{m}.png``: Figure for predictions
          vs. observations on the validation period for the best model
          with window size ``s`` and slicing method ``m``.

        * ``ldefrate_ws{s}.tif``: Raster of local deforestation rates
          for the best model with window size ``s``.

        * ``ldefrate_ws{s}_with_zero.tif``: Raster of local
          deforestation rates with zero category for the best model
          with window size ``s``.

        * ``riskmap_ws{s}_{m}.tif``: Riskmap with categories of
          deforestation risk using the best model with window size
          ``s`` and slicing method ``m``.

        * ``defrate_per_cat_ws{s}_{m}.csv``: Table of deforestation
          rate per category of deforestation risk for the best model
          with window size ``s`` and slicing method ``m``.

        * ``calval``: A directory for files produced during the
          calibration and validation steps:

            + ``dist_edge_cal.tif``: Raster of distance to forest edge
              for the calibration period.

            + ``perc_dist_cal.csv``: Table of cumulative deforestation
              with distance to forest edge for the calibration period.

            + ``perc_dist_cal.png``: Figure of cumulative deforestation
              with distance to forest edge for the calibration period.

            + ``ldefrate_ws{s}.tif``: Rasters of local deforestation
              rates for each window size ``s``.

            + ``ldefrate_ws{s}_with_zero.tif``: Rasters of local
              deforestation rates with zero category for each window
              size ``s``.

            + ``riskmap_ws{s}_{m}.tif``: Riskmaps with categories of
              deforestation risk for each window size ``s`` and
              slicing method ``m``.

            + ``defrate_per_cat_ws{s}_{m}.csv``: Tables of
              deforestation rate per category of deforestation risk
              for each window size ``s`` and slicing method ``m``.

            + ``pred_obs_ws{s}_{m}.csv``: Tables of predictions
              vs. observations for each window size ``s`` and slicing
              method ``m``.

            + ``pred_obs_ws{s}_{m}.png``: Figures of predictions
              vs. observations for each window size ``s`` and slicing
              method ``m``.

   :param clean: Logical. Delete the ``calval_dir`` directory at the
        end of the computation. Default to False.

   :param dist_bins: Array of bins for distances. It has to be
        1-dimensional and monotonic. The array must also include zero
        as the first value. Default to ``np.arange(0, 1080,
        step=30)``.

    :param win_sizes: A list of numbers representing the different
        sizes of the moving window in number of cells. Must be odd
        numbers lower or equal to ``blk_rows``. Default to [5, 11].

    :param ncat: Number of deforestation risk categories (zero
        risk class excluded). Default to 30.

    :param methods: Methods used for categorizing. Either "Equal
        Interval" (abbreviated "ei"), "Equal Area" ("ea"), or "Natural
        Breaks" ("nb").

    :param csize: Spatial cell size in number of pixels. Must
        correspond to a distance < 10 km. Default to 300 corresponding
        to 9 km for a 30 m resolution raster.

    :param figsize: Figure sizes.

    :param dpi: Resolution for output images.

    :param blk_rows: If > 0, number of rows for computation by block.

    :param verbose: Logical. Whether to print messages or not. Default
        to ``True``.

    :return: A dictionary. With:

        * ``tot_def``: total deforestation (in ha) during the entire historical
          period.
        * ``dist_thresh``: the distance threshold.
        * ``perc``: the percentage of deforestation for pixels with
          distance <= dist_thresh.
        * ``ncell``: the number of grid cells with forest cover > 0 at
          the beginning of the validation period.
        * ``csize``: the cell size in number of pixels.
        * ``csize_km``: the cell size in kilometers.
        * ``ws_hat``: window size of the best risk map.
        * ``m_hat``: slicing method of the best risk map.
        * ``wRMSE_hat``: weighted Root Mean Squared Error (in hectares)
          of the best risk map.

    """

    # ==========================
    # Calibration and validation
    # ==========================

    # Message
    if verbose:
        print("Model calibration and validation")

    # Create output directory
    make_dir(os.path.join(output_dir, "calval"))

    # Output files for calibration and validation
    calval_dir = os.path.join(output_dir, "calval")
    dist_file = os.path.join(calval_dir, "dist_edge_cal.tif")
    tab_file_dist = os.path.join(calval_dir, "perc_dist_cal.csv")
    fig_file_dist = os.path.join(calval_dir, "perc_dist_cal.png")

    # Output files for final map
    tab_file_map_comp = os.path.join(output_dir, "map_comp.csv")
    fig_file_map_comp = os.path.join(output_dir, "map_comp.png")

    # Abbreviations for methods
    meth = pd.Series(methods)
    meth.loc[meth == "Equal Interval"] = "ei"
    meth.loc[meth == "Equal Area"] = "ea"
    meth.loc[meth == "Natural Breaks"] = "nb"
    meth = meth.tolist()

    # Dataframe to save validation results
    n_ws = len(win_sizes)
    n_m = len(methods)
    n_mod = n_ws*n_m
    data = {"mod_id": list(range(n_mod)),
            "ws": np.repeat(win_sizes, n_m),
            "m": meth * n_ws,
            "wRMSE": 0}
    df = pd.DataFrame(data)

    # Deforestation risk and distance to forest edge
    dist_edge_thres = dist_edge_threshold(
        fcc_file=fcc_file,
        defor_values=1,  # First period
        dist_file=dist_file,
        dist_bins=dist_bins,
        tab_file_dist=tab_file_dist,
        fig_file_dist=fig_file_dist,
        figsize=figsize,
        dpi=dpi,
        blk_rows=blk_rows,
        verbose=False)

    # Loop on window sizes
    for i in range(n_ws):
        # Window size
        s = win_sizes[i]
        # Output files
        ldefrate_file = os.path.join(output_dir, "calval",
                                     f"ldefrate_ws{s}.tif")
        ldefrate_with_zero_file = os.path.join(output_dir, "calval",
                                               f"ldefrate_ws{s}_with_zero.tif")
        # Local deforestation rates
        local_defor_rate(
            fcc_file=fcc_file,
            defor_values=1,  # First period
            ldefrate_file=ldefrate_file,
            win_size=s,
            time_interval=time_interval[0],
            blk_rows=blk_rows,
            verbose=False)
        # Pixels with zero risk of deforestation
        set_defor_cat_zero(
            ldefrate_file=ldefrate_file,
            dist_file=dist_file,
            dist_thresh=dist_edge_thres["dist_thresh"],
            ldefrate_with_zero_file=ldefrate_with_zero_file,
            blk_rows=blk_rows,
            verbose=False)
        # Loop on slicing methods
        for j in range(n_m):
            # Method
            m = meth[j]
            mm = methods[j]
            # Message
            if verbose:
                imod = i * n_m + j
                print(f".. Model {imod}: window size = {s}, "
                      f"slicing method = {m}.")
            # Output files
            riskmap_file = os.path.join(calval_dir,
                                        f"riskmap_ws{s}_{m}.tif")
            tab_file_defrate = os.path.join(calval_dir,
                                            f"defrate_per_cat_ws{s}_{m}.csv")
            tab_file_pred = os.path.join(calval_dir, f"pred_obs_ws{s}_{m}.csv")
            fig_file_pred = os.path.join(calval_dir, f"pred_obs_ws{s}_{m}.png")
            # Categories of deforestation risk
            defor_cat(
                ldefrate_with_zero_file=ldefrate_with_zero_file,
                riskmap_file=riskmap_file,
                ncat=ncat,
                method=mm,
                blk_rows=blk_rows,
                verbose=False)
            # Compute deforestation rates per cat
            defrate_per_cat(
                fcc_file,
                defor_values=1,
                riskmap_file=riskmap_file,
                time_interval=time_interval[0],
                tab_file_defrate=tab_file_defrate,
                blk_rows=blk_rows,
                verbose=False)
            # Validation
            val = validation(
                fcc_file=fcc_file,
                time_interval=time_interval[1],
                riskmap_file=riskmap_file,
                tab_file_defrate=tab_file_defrate,
                csize=csize,
                tab_file_pred=tab_file_pred,
                fig_file_pred=fig_file_pred,
                figsize=figsize,
                dpi=dpi,
                verbose=False)
            # wRMSE
            df.loc[(df["ws"] == s) &
                   (df["m"] == m),
                   "wRMSE"] = val["wRMSE"]

    # Export the table of results
    df.to_csv(tab_file_map_comp, sep=",", header=True,
              index=False, index_label=False)

    # Plot of wRMSE
    fig = plt.figure(figsize=figsize, dpi=dpi)
    df.set_index("ws", inplace=True)
    df.groupby("m")["wRMSE"].plot(legend=True)
    plt.xlabel("Window size (pixels)")
    plt.ylabel("wRMSE (ha)")
    fig.savefig(fig_file_map_comp)
    plt.close(fig)

    # Identifying the best model
    wRMSE_hat = df["wRMSE"].min()
    df_hat = df[df["wRMSE"] == wRMSE_hat]
    ws_hat = df_hat.index[0]
    m_hat = df_hat["m"].iloc[0]

    # ==============================================
    # Deriving risk map for entire historical period
    # ==============================================

    # Message
    if verbose:
        print("Deriving risk map for entire historical period")

    # Set s and m optimal values
    s = ws_hat
    m = m_hat
    if m == "ei":
        mm = "Equal Interval"
    elif m == "ea":
        mm = "Equal Area"
    else:
        mm = "Natural Breaks"

    # Copy pred_obs
    tab_file_pred_cal = os.path.join(calval_dir, f"pred_obs_ws{s}_{m}.csv")
    fig_file_pred_cal = os.path.join(calval_dir, f"pred_obs_ws{s}_{m}.png")
    tab_file_pred = os.path.join(output_dir, f"pred_obs_ws{s}_{m}.csv")
    fig_file_pred = os.path.join(output_dir, f"pred_obs_ws{s}_{m}.png")
    shutil.copy2(tab_file_pred_cal, tab_file_pred)
    shutil.copy2(fig_file_pred_cal, fig_file_pred)

    # Output files for final map
    dist_file = os.path.join(output_dir, "dist_edge.tif")
    tab_file_dist = os.path.join(output_dir, "perc_dist.csv")
    fig_file_dist = os.path.join(output_dir, "perc_dist.png")
    ldefrate_file = os.path.join(output_dir, f"ldefrate_ws{s}.tif")
    ldefrate_with_zero_file = os.path.join(output_dir,
                                           f"ldefrate_ws{s}_with_zero.tif")
    riskmap_file = os.path.join(output_dir,
                                f"riskmap_ws{s}_{m}.tif")
    tab_file_defrate = os.path.join(output_dir,
                                    f"defrate_per_cat_ws{s}_{m}.csv")

    # Deforestation risk and distance to forest edge
    dist_edge_thres = dist_edge_threshold(
        fcc_file=fcc_file,
        defor_values=[1, 2],  # Two periods
        dist_file=dist_file,
        dist_bins=dist_bins,
        tab_file_dist=tab_file_dist,
        fig_file_dist=fig_file_dist,
        figsize=figsize,
        dpi=dpi,
        blk_rows=blk_rows,
        verbose=False)

    # Local deforestation rates
    local_defor_rate(
        fcc_file=fcc_file,
        defor_values=[1, 2],  # Two periods
        ldefrate_file=ldefrate_file,
        win_size=s,
        time_interval=np.array(time_interval).sum(),
        blk_rows=blk_rows,
        verbose=False)

    # Pixels with zero risk of deforestation
    set_defor_cat_zero(
        ldefrate_file=ldefrate_file,
        dist_file=dist_file,
        dist_thresh=dist_edge_thres["dist_thresh"],
        ldefrate_with_zero_file=ldefrate_with_zero_file,
        blk_rows=blk_rows,
        verbose=False)

    # Categories of deforestation risk
    defor_cat(
        ldefrate_with_zero_file=ldefrate_with_zero_file,
        riskmap_file=riskmap_file,
        ncat=ncat,
        method=mm,
        blk_rows=blk_rows,
        verbose=False)

    # Compute deforestation rates per cat
    defrate_per_cat(
        fcc_file,
        defor_values=[1, 2],
        riskmap_file=riskmap_file,
        time_interval=time_interval[0],
        tab_file_defrate=tab_file_defrate,
        blk_rows=blk_rows,
        verbose=False)

    # Cleaning
    if clean:
        if verbose:
            # Message
            print("Cleaning files")
        shutil.rmtree("calval")

    # Return
    return {'tot_def': dist_edge_thres["tot_def"],
            'dist_thresh': dist_edge_thres["dist_thresh"],
            'perc_thresh': dist_edge_thres["perc_thresh"],
            'ncell': val["ncell"], 'csize': csize,
            'csize_km': val["csize_km"],
            'ws_hat': ws_hat, 'm_hat': m_hat,
            'wRMSE_hat': wRMSE_hat}


# Test
# r_makemap = makemap(
#     fcc_file="data/fcc123_GLP.tif",
#     time_interval=[10, 10],
#     output_dir="outputs_makemap",
#     clean=False,
#     dist_bins=np.arange(0, 1080, step=30),
#     win_sizes=np.arange(5, 50, 6),
#     ncat=30,
#     methods=["Equal Interval", "Equal Area"],
#     csize=40,
#     figsize=(6.4, 4.8),
#     dpi=100,
#     blk_rows=128,
#     verbose=True)

# End
