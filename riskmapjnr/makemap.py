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
import multiprocessing as mp

# Third party imports
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

# Local application imports
from .misc import make_dir
from . import dist_edge_threshold, local_defor_rate, set_defor_cat_zero
from . import defor_cat, defrate_per_cat, validation
from . import dist_values, get_ldefz_v, get_riskmap_v


# Function for computing by window size
def makemap_ws(i, win_size, fcc_file, time_interval, dist_file, dist_v_file,
               dist_edge_thresh, calval_dir, ncat, methods, meth, n_m,
               csize, nqe, figsize, dpi, blk_rows, verbose):
    """Internal function for parallel computing."""

    # Window size
    s = win_size

    # Output files depending only on window size
    ldefrate_file = os.path.join(calval_dir, f"ldefrate_ws{s}.tif")
    ldefrate_with_zero_file = os.path.join(calval_dir,
                                           f"ldefrate_with_zero_ws{s}.tif")
    ldefzv_file = os.path.join(calval_dir, f"ldefrate_with_zero_ws{s}_v.tif")

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
        dist_thresh=dist_edge_thresh["dist_thresh"],
        ldefrate_with_zero_file=ldefrate_with_zero_file,
        blk_rows=blk_rows,
        verbose=False)

    # ldefz_v
    get_ldefz_v(
        ldefrate_file=ldefrate_file,
        dist_v_file=dist_v_file,
        dist_thresh=dist_edge_thresh["dist_thresh"],
        ldefrate_with_zero_v_file=ldefzv_file,
        blk_rows=blk_rows,
        verbose=False)

    # wRMSE list
    wRMSE_list = []

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
        riskmap_v_file = os.path.join(calval_dir, f"riskmap_ws{s}_{m}_v.tif")
        tab_file_defrate = os.path.join(calval_dir,
                                        f"defrate_per_cat_ws{s}_{m}.csv")
        tab_file_pred = os.path.join(calval_dir, f"pred_obs_ws{s}_{m}.csv")
        fig_file_pred = os.path.join(calval_dir, f"pred_obs_ws{s}_{m}.png")
        # Categories of deforestation risk
        bins = defor_cat(
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
        # Risk map for validation period
        get_riskmap_v(
            ldefrate_with_zero_v_file=ldefzv_file,
            bins=bins,
            riskmap_v_file=riskmap_v_file,
            blk_rows=blk_rows,
            verbose=False)
        # Validation
        val = validation(
            fcc_file=fcc_file,
            time_interval=time_interval[1],
            riskmap_file=riskmap_v_file,
            tab_file_defrate=tab_file_defrate,
            csize=csize,
            no_quantity_error=nqe,
            tab_file_pred=tab_file_pred,
            fig_file_pred=fig_file_pred,
            figsize=figsize,
            dpi=dpi,
            verbose=False)
        wRMSE_list.append(val["wRMSE"])

    # Return iteration and wRMSE
    return (i, wRMSE_list, val["ncell"], val["csize_km"])


# makemap
def makemap(fcc_file, time_interval,
            output_dir="outputs",
            clean=False,
            dist_bins=np.arange(0, 1080, step=30),
            win_sizes=[5, 11],
            ncat=30,
            methods=["Equal Interval", "Equal Area"],
            csize=300,
            no_quantity_error=False,
            parallel=False,
            ncpu=None,
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
        period. No data value must be 0 (zero). The raster must be
        projected to compute Euclidean distances with the
        ``gdal_proximity()`` function.

    :param time_interval: A list of two numbers. Time interval (in
        years) for forest cover change observations for the two periods
        of time.

    :param output_dir: Output directory for files (rasters, tables, and
        figures) produced by calling the ``makemap()`` function:

        * ``calval``: A directory for files produced during the
          calibration and validation steps:

            + ``dist_edge_cal.tif``: Raster of distance to forest edge
              at the start of the calibration period (same as
              ``dist_edge.tif``).

            + ``perc_dist_cal.csv``: Table of cumulative deforestation
              with distance to forest edge for the calibration period.

            + ``perc_dist_cal.png``: Figure of cumulative deforestation
              with distance to forest edge for the calibration period.

            + ``ldefrate_ws{s}.tif``: Rasters of local deforestation
              rates for each window size ``s`` for the calibration
              period.

            + ``ldefrate_with_zero_ws{s}.tif``: Rasters of local
              deforestation rates with zero category for each window
              size ``s`` for the calibration period.

            + ``riskmap_ws{s}_{m}.tif``: Riskmaps with categories of
              deforestation risk for each window size ``s`` and
              slicing method ``m`` for the calibration period.

            + ``defrate_per_cat_ws{s}_{m}.csv``: Tables of
              deforestation rate per category of deforestation risk
              for each window size ``s`` and slicing method ``m`` for
              the calibration period.

            + ``dist_edge_v.tif``: Raster of distance to forest edge
              at the start of the validation period.

            + ``ldefrate_with_zero_ws{s}_v.tif``: Rasters of local
              deforestation rates with zero category for each window
              size ``s`` at the start of the validation period.

            + ``riskmap_ws{s}_{m}_v.tif``: Riskmaps with categories of
              deforestation risk for each window size ``s`` and
              slicing method ``m`` at the start of the validation
              period.

            + ``pred_obs_ws{s}_{m}.csv``: Tables of predictions
              vs. observations for each window size ``s`` and slicing
              method ``m`` for the validation period.

            + ``pred_obs_ws{s}_{m}.png``: Figures of predictions
              vs. observations for each window size ``s`` and slicing
              method ``m`` for the validation period.

        * ``modcomp``: A directory containing files for model comparison:

            + ``pred_obs_ws{s}_{m}.csv``: Table of predictions
              vs. observations for the validation period for the best
              model with window size ``s`` and slicing method ``m``.

            + ``pred_obs_ws{s}_{m}.png``: Figure of predictions
              vs. observations for the validation period for the best
              model with window size ``s`` and slicing method ``m``.

            + ``mod_comp.csv``: Table for relationship between
              wRMSE and window size by slicing method.

            + ``mod_comp.png``: Figure for relationship between
              wRMSE and window size by slicing method.

        * ``fullhist``: A directory containing files for the full
          historical period (historical period = calibration period +
          validation period):

            + ``dist_edge.tif``: Raster file of distance to forest
              edge at the start of the historical period
              (corresponding to start of calibration period).

            + ``perc_dist.csv``: Table of cumulative deforestation with
              distance to forest edge for the historical period.

            + ``perc_dist.png``: Figure of cumulative deforestation with
              distance to forest edge for the historical period.

            + ``ldefrate_ws{s}.tif``: Raster of local deforestation
              rates for the best model with window size ``s`` for the
              historical period.

            + ``ldefrate_with_zero_ws{s}.tif``: Raster of local
              deforestation rates with zero category for the best model
              with window size ``s`` for the historical period.

            + ``riskmap_ws{s}_{m}.tif``: Riskmap with categories of
              deforestation risk using the best model with window size
              ``s`` and slicing method ``m`` at the start of the
              historical period.

            + ``defrate_per_cat_ws{s}_{m}.csv``: Table of
              deforestation rate per category of deforestation risk
              for the best model with window size ``s`` and slicing
              method ``m`` for the historical period.

        * ``endval``: A directory containing files at the end of the
          validation period that can be used for future projections:

            + ``dist_edge_ev.tif``: Raster of distance to forest edge
              at the end of the validation period.

            + ``ldefrate_with_zero_ws{s}_ev.tif``: Raster of local
              deforestation probability with zero category for the
              best model with window size ``s`` at the end of the
              validation period.

            + ``riskmap_ws{s}_{m}_ev.tif``: Riskmap with categories of
              deforestation risk for the best model with window size
              ``s`` and slicing method ``m`` at the end of the
              validation period.

    :param clean: Logical. Delete the ``calval`` directory at the
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

    :param no_quantity_error: Correct the deforestation rates to avoid
        a "quantity" error on deforestation due to differences in
        total deforestation between first and second periods. This
        point is being discussed to improve the JNR methodology.

    :param parallel: Logical. Parallel (if ``True``) or sequential (if
        ``False``) computing. Default to ``False``.

    :param ncpu: Number of CPUs for parallel computing.

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
        * ``no_quantity_error``: no_quantity_error argument.
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

    # Create output directories
    make_dir(os.path.join(output_dir, "calval"))
    make_dir(os.path.join(output_dir, "modcomp"))
    make_dir(os.path.join(output_dir, "fullhist"))
    make_dir(os.path.join(output_dir, "endval"))

    # Output files for calibration and validation
    calval_dir = os.path.join(output_dir, "calval")
    dist_file = os.path.join(calval_dir, "dist_edge_cal.tif")
    dist_v_file = os.path.join(calval_dir, "dist_edge_val.tif")
    tab_file_dist = os.path.join(calval_dir, "perc_dist_cal.csv")
    fig_file_dist = os.path.join(calval_dir, "perc_dist_cal.png")

    # Output files for model comparison
    modcomp_dir = os.path.join(output_dir, "modcomp")
    tab_file_map_comp = os.path.join(modcomp_dir, "mod_comp.csv")
    fig_file_map_comp = os.path.join(modcomp_dir, "mod_comp.png")

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
    dist_edge_thresh = dist_edge_threshold(
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

    # Distance to forest edge for validation
    dist_values(
        input_file=fcc_file,
        dist_file=dist_v_file,
        values="0,1",
        verbose=False)

    # Sequential computing
    if parallel is False:
        # Loop on window sizes
        for i in range(n_ws):
            s = win_sizes[i]
            ii, wRMSE_list, ncell, csize_km = makemap_ws(
                i, s, fcc_file, time_interval,
                dist_file, dist_v_file,
                dist_edge_thresh, calval_dir, ncat, methods,
                meth, n_m, csize, no_quantity_error,
                figsize, dpi, blk_rows, verbose)
            df.loc[df["ws"] == s, "wRMSE"] = wRMSE_list

    # Parallel computing
    if parallel is True:
        pool = mp.Pool(processes=ncpu)
        args = [(i, s, fcc_file, time_interval,
                 dist_file, dist_v_file,
                 dist_edge_thresh, calval_dir, ncat, methods,
                 meth, n_m, csize, no_quantity_error,
                 figsize, dpi, blk_rows,
                 verbose) for i, s in enumerate(win_sizes)]
        res = pool.starmap_async(makemap_ws, args).get()
        ncell = res[0][2]
        csize_km = res[0][3]
        wRMSE_obj = [r[1] for r in res]
        df.loc[:, "wRMSE"] = np.array(wRMSE_obj).flatten()
        pool.close()
        pool.join()

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

    # ============================================
    # Deriving risk map for full historical period
    # ============================================

    # Message
    if verbose:
        print("Deriving risk map for full historical period")

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
    tab_file_pred = os.path.join(modcomp_dir, f"pred_obs_ws{s}_{m}.csv")
    fig_file_pred = os.path.join(modcomp_dir, f"pred_obs_ws{s}_{m}.png")
    shutil.copy2(tab_file_pred_cal, tab_file_pred)
    shutil.copy2(fig_file_pred_cal, fig_file_pred)

    # Output files for full historical period
    fullhist_dir = os.path.join(output_dir, "fullhist")
    dist_file = os.path.join(fullhist_dir, "dist_edge.tif")
    tab_file_dist = os.path.join(fullhist_dir, "perc_dist.csv")
    fig_file_dist = os.path.join(fullhist_dir, "perc_dist.png")
    ldefrate_file = os.path.join(fullhist_dir, f"ldefrate_ws{s}.tif")
    ldefrate_with_zero_file = os.path.join(fullhist_dir,
                                           f"ldefrate_with_zero_ws{s}.tif")
    riskmap_file = os.path.join(fullhist_dir,
                                f"riskmap_ws{s}_{m}.tif")
    tab_file_defrate = os.path.join(fullhist_dir,
                                    f"defrate_per_cat_ws{s}_{m}.csv")

    # Deforestation risk and distance to forest edge
    dist_edge_thresh = dist_edge_threshold(
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
        dist_thresh=dist_edge_thresh["dist_thresh"],
        ldefrate_with_zero_file=ldefrate_with_zero_file,
        blk_rows=blk_rows,
        verbose=False)

    # Categories of deforestation risk
    bins = defor_cat(
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
        time_interval=np.array(time_interval).sum(),
        tab_file_defrate=tab_file_defrate,
        blk_rows=blk_rows,
        verbose=False)

    # ==============================
    # End of validation period (_ev)
    # ==============================

    # Output files for end of validation period
    endval_dir = os.path.join(output_dir, "endval")
    dist_ev_file = os.path.join(endval_dir, "dist_edge_ev.tif")
    ldefz_ev_file = os.path.join(endval_dir,
                                 f"ldefrate_with_zero_ws{s}_ev.tif")
    riskmap_ev_file = os.path.join(endval_dir,
                                   f"riskmap_ws{s}_{m}_ev.tif")

    # Distance to forest edge for validation
    dist_values(
        input_file=fcc_file,
        dist_file=dist_ev_file,
        values="0,1,2",  # Two periods
        verbose=False)

    # ldefz_v
    get_ldefz_v(
        ldefrate_file=ldefrate_file,
        dist_v_file=dist_v_file,
        dist_thresh=dist_edge_thresh["dist_thresh"],
        ldefrate_with_zero_v_file=ldefz_ev_file,
        blk_rows=blk_rows,
        verbose=False)

    # Risk map for validation period
    get_riskmap_v(
        ldefrate_with_zero_v_file=ldefz_ev_file,
        bins=bins,
        riskmap_v_file=riskmap_ev_file,
        blk_rows=blk_rows,
        verbose=False)

    # Cleaning
    if clean:
        if verbose:
            # Message
            print("Cleaning files")
        shutil.rmtree("calval")

    # Return
    return {'tot_def': dist_edge_thresh["tot_def"],
            'dist_thresh': dist_edge_thresh["dist_thresh"],
            'perc_thresh': dist_edge_thresh["perc_thresh"],
            'ncell': ncell, 'csize': csize,
            'csize_km': csize_km,
            'no_quantity_error': no_quantity_error,
            'ws_hat': ws_hat, 'm_hat': m_hat,
            'wRMSE_hat': wRMSE_hat}


# Test
# r_makemap = makemap(
#     fcc_file="data/fcc123_GLP.tif",
#     time_interval=[10, 10],
#     output_dir="outputs_get_started",
#     clean=False,
#     dist_bins=np.arange(0, 1080, step=30),
#     win_sizes=np.arange(5, 50, 6),
#     ncat=30,
#     parallel = False
#     methods=["Equal Interval", "Equal Area"],
#     csize=40,
#     no_quantity_error = True
#     figsize=(6.4, 4.8),
#     dpi=100,
#     blk_rows=128,
#     verbose=True)

# fcc_file = "data/fcc123_GLP.tif"
# time_interval = [10, 10]
# output_dir = "outputs_get_started"
# clean = False
# dist_bins = np.arange(0, 1080, step=30)
# win_sizes = np.arange(5, 50, 6)
# ncat = 30
# parallel = False
# methods = ["Equal Interval", "Equal Area"]
# csize = 40
# no_quantity_error = True
# figsize = (6.4, 4.8)
# dpi = 100
# blk_rows = 128
# verbose = True

# End
