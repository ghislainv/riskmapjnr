#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=3
# license         :GPLv3
# ==============================================================================

"""
Compute the distance to forest edge threshold.
"""

# Third party imports
from matplotlib import pyplot as plt
import numpy as np
from osgeo import gdal
import pandas as pd

# Local application imports
from .misc import progress_bar, makeblock


# check_fcc_file
def check_fcc_file(fcc_file, blk_rows=128, verbose=True):
    """Perform some checks on the fcc file.

    Check that the fcc file:

    * Is not in latlon coordinates and is projected in order to be
      able to compute euclidean distances.

    * Includes values 0, 1, 2, and 3.

    * Has 0 as NoData value.

    :param input_file: Input raster file.

    :param blk_rows: Number of rows for block. This is used to break
        lage raster files in several blocks of data that can be hold
        in memory.

    :param verbose: Logical. Whether to print messages or not. Default
        to ``True``.

    :return: None.

    """

    # Read fcc file
    fcc_ds = gdal.Open(fcc_file)
    fcc_band = fcc_ds.GetRasterBand(1)

    # ================
    # Check projection
    # ================
    crs = fcc_ds.GetSpatialRef()
    if not crs.IsProjected():
        msg = ("'fcc_file' cannot be in latlon coordinates "
               "and must be projected to compute euclidean "
               "distances.")
        raise ValueError(msg)

    # ==================
    # Check nodata value
    # ==================
    nodata = fcc_band.GetNoDataValue()
    if nodata != 0:
        msg = "'fcc_file' must have 0 (zero) as NoData value."
        raise ValueError(msg)

    # ============
    # Check values
    # ============

    # Necessary values
    nece_val = np.array([0, 1, 2, 3])

    # Unique values
    uniq_val = []

    # Make blocks
    blockinfo = makeblock(fcc_file, blk_rows=blk_rows)
    nblock = blockinfo[0]
    nblock_x = blockinfo[1]
    x = blockinfo[3]
    y = blockinfo[4]
    nx = blockinfo[5]
    ny = blockinfo[6]

    # Loop on blocks of data
    for b in range(nblock):
        # Progress bar
        if verbose:
            progress_bar(nblock, b + 1)
        # Position in 1D-arrays
        px = b % nblock_x
        py = b // nblock_x
        # Data for one block of the stack (shape = (nband,nrow,ncol))
        fcc_data = fcc_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        # Unique values
        uniq_val_b = np.unique(fcc_data)
        # Check values are in [0, 1, 2, 3]
        if not all(np.isin(uniq_val_b, nece_val)):
            msg = ("'fcc_file' must only include values 0, 1, 2, and 3 "
                   "with 0 (zero) as NoData.")
            raise ValueError(msg)
        # Actualize unique values
        uniq_val.extend(list(uniq_val_b))
        uniq_val = list(np.unique(uniq_val))

    # Check whole values are equal to [0, 1, 2, 3]
    if not np.array_equal(np.unique(uniq_val), nece_val):
        msg = ("'fcc_file' must include values 0, 1, 2, and 3 "
               "with 0 (zero) as NoData.")
        raise ValueError(msg)


# dist_values
def dist_values(input_file,
                dist_file,
                values=0,
                verbose=True):
    """Computing the shortest distance to pixels with given values in
    a raster file.

    This function computes the shortest distance to pixels with given
    values in a raster file. Distances generated are in georeferenced
    coordinates.

    :param input_file: Input raster file.

    :param dist_file: Path to the distance raster file that is
        created.

    :param values: Values of the raster to compute the distance
        to. Use list (e.g. [1, 2]) to specify several values. Default
        to 0.

    :param verbose: Logical. Whether to print messages or not. Default
        to ``True``.

    :return: None. A distance raster file is created (see
        ``dist_file``). Raster data type is UInt32 ([0,
        4294967295]). NoData is set to zero.

    """

    # Read input file
    src_ds = gdal.Open(input_file)
    srcband = src_ds.GetRasterBand(1)

    # Create raster of distance
    drv = gdal.GetDriverByName("GTiff")
    dst_ds = drv.Create(dist_file,
                        src_ds.RasterXSize, src_ds.RasterYSize, 1,
                        gdal.GDT_UInt32,
                        ["COMPRESS=LZW", "PREDICTOR=2", "BIGTIFF=YES"])
    dst_ds.SetGeoTransform(src_ds.GetGeoTransform())
    dst_ds.SetProjection(src_ds.GetProjectionRef())
    dstband = dst_ds.GetRasterBand(1)

    # Compute distance
    val_as_string = ",".join([str(i) for i in values])
    val = "VALUES=" + val_as_string
    cb = gdal.TermProgress_nocb if verbose else 0
    gdal.ComputeProximity(srcband, dstband,
                          [val, "DISTUNITS=GEO"],
                          callback=cb)

    # Set nodata value
    dstband.SetNoDataValue(0)

    # Delete objects
    srcband = None
    dstband = None
    del src_ds, dst_ds


# dist_edge_threshold
def dist_edge_threshold(fcc_file,
                        defor_values,
                        defor_threshold=99.5,
                        dist_file="dist_edge.tif",
                        dist_bins=np.arange(0, 1080, step=30),
                        tab_file_dist="perc_dist.csv",
                        fig_file_dist="perc_dist.png",
                        figsize=(6.4, 4.8),
                        dpi=100,
                        blk_rows=128,
                        dist_file_available=False,
                        check_fcc=True,
                        verbose=True):
    """Computing the percentage of total deforestation as a function of
    the distance to forest edge.

    This function computes the percentage of total deforestation as a
    function of the distance to forest edge. It returns a table with
    the cumulative percentage of deforestation as distance to forest
    edge increases. It also identifies the distance threshold for the
    distance to forest edge so that the deforestation under that
    threshold is >= 99.5 % of the total deforestation in the
    landscape. The function also plots the relationship between the
    percentage of deforestation and the distance to forest edge. A
    raster of distance to forest edge will be created. The distance
    unit will be the one of the input file.

    :param fcc_file: Input raster file of forest cover change at three
        dates (123). 1: first period deforestation, 2: second period
        deforestation, 3: remaining forest at the end of the second
        period. No data value must be 0 (zero). The raster must be
        projected to compute Euclidean distances with the
        ``gdal_proximity()`` function.

    :param defor_values: Raster values to consider for
        deforestation. Must correspond to either scalar 1 if first
        period, or list [1, 2] if both first and second period are
        considered.

    :param defor_threshold: Deforestation threshold (in
        percent). Default to 99.5.

    :param dist_file: Path to either (i) the output raster file of
        distance to forest edge or (ii) the input raster file of
        distance to forest edge if ``dist_file_available`` is
        ``True``. Raster of distance to forest edge is computed in the
        first case only. Default to ``dist_edge.tif``.

    :param dist_bins: Array of bins for distances. It has to be
        1-dimensional and monotonic. The array must also include zero
        as the first value. Default to ``np.arange(0, 1080,
        step=30)``.

    :param tab_file_dist: Path to the table ``.csv`` file that will be
        created. This table includes the following variables:

        * ``distance``: bins of distance to forest edge (in m).
        * ``npix``: the number of deforested pixels in each bin.
        * ``area``: the corresponding area (in ha).
        * ``cum``: the cumulative sum of the deforested area (in ha).
        * ``perc``: the corresponding percentage of total deforestation.

    :param fig_file_dist: Path to the plot file that will be
        created. This plot represents the cumulative deforestation
        percentage as the distance to forest edge increases.

    :param figsize: Figure size.

    :param dpi: Resolution for output image.

    :param blk_rows: Number of rows for block. This is used to break
        lage raster files in several blocks of data that can be hold
        in memory.

    :param dist_file_available: Boolean. If ``True``, parameter
        ``dist_file`` indicates the input raster file of distance to
        forest edge which is not computed. Default to ``False``.

    :param check_fcc: Boolean. If ``True``, performs some checks on
        the fcc input file. Default to ``True``.

    :param verbose: Logical. Whether to print messages or not. Default
        to ``True``.

    :return: A dictionary. With ``tot_def``: total deforestation (in
        ha), ``dist_thresh``: the distance threshold, ``perc``: the
        percentage of deforestation for pixels with distance <=
        dist_thresh.

    """

    # Check fcc_file
    if check_fcc:
        check_fcc_file(fcc_file, blk_rows=blk_rows, verbose=verbose)

    # Compute the distance to the forest edge
    if dist_file_available is not True:
        dist_values(fcc_file, dist_file, values=0, verbose=verbose)

    # Create a table to save the results
    data = {"distance": dist_bins[1:], "npix": 0, "area": 0.0,
            "cum": 0.0, "perc": 0.0}
    res_df = pd.DataFrame(data)

    # Total deforested pixels
    npix_def = 0

    # Make blocks
    blockinfo = makeblock(dist_file, blk_rows=blk_rows)
    nblock = blockinfo[0]
    nblock_x = blockinfo[1]
    x = blockinfo[3]
    y = blockinfo[4]
    nx = blockinfo[5]
    ny = blockinfo[6]

    # Read rasters
    dist_ds = gdal.Open(dist_file)
    dist_band = dist_ds.GetRasterBand(1)
    fcc_ds = gdal.Open(fcc_file)
    fcc_band = fcc_ds.GetRasterBand(1)

    # Loop on blocks of data
    for b in range(nblock):
        # Progress bar
        if verbose:
            progress_bar(nblock, b + 1)
        # Position in 1D-arrays
        px = b % nblock_x
        py = b // nblock_x
        # Data for one block of the stack (shape = (nband,nrow,ncol))
        dist_data = dist_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        fcc_data = fcc_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        # Number of deforested pixels
        npix_def += np.isin(fcc_data, defor_values).sum()
        # Consider only deforested pixels for distances
        dist_def = dist_data * np.isin(fcc_data, defor_values)
        dist_def = dist_def[dist_def > 0]
        # Categorize distance
        dist_cat = pd.cut(dist_def.flatten(), dist_bins, right=True)
        # Sum by category
        df = pd.DataFrame({"dist": dist_cat})
        counts = df.groupby(df.dist, observed=False).size()
        # Update data-frame
        res_df.loc[:, "npix"] += counts.values

    # Compute deforested areas
    gt = dist_ds.GetGeoTransform()
    pix_area = gt[1] * (-gt[5])
    area = res_df["npix"].values * pix_area / 10000
    res_df.loc[:, "area"] = area
    tot_area_def = npix_def * pix_area / 10000
    # Cumulated deforestation
    res_df.loc[:, "cum"] = res_df["area"].cumsum().values
    # Percentage of total deforestation
    res_df.loc[:, "perc"] = 100 * res_df["cum"].values / tot_area_def

    # Export the table of results
    res_df.to_csv(tab_file_dist, sep=",", header=True,
                  index=False, index_label=False)

    # Distance and percentage for deforestation threshold
    try:
        index_thresh = np.nonzero(res_df["perc"].values > defor_threshold)[0][0]
    except IndexError:
        raise ValueError("Increase maximal distance "
                         "defined in argument 'dist_bins'.")

    dist_thresh = res_df.loc[index_thresh, "distance"]
    perc_thresh = np.around(res_df.loc[index_thresh, "perc"], 2)

    # Plot
    fig = plt.figure(figsize=figsize, dpi=dpi)
    plt.subplot(111)
    plt.plot(res_df["distance"], res_df["perc"], "b-")
    plt.vlines(dist_thresh,
               ymin=np.min(res_df["perc"]),
               ymax=perc_thresh,
               colors="k", linestyles="dashed")
    plt.hlines(perc_thresh,
               xmin=0,
               xmax=dist_thresh,
               colors="k", linestyles="dashed")
    plt.xlabel("Distance to forest edge (m)")
    plt.ylabel("Percentage of total deforestation (%)")
    # Text distance
    t1 = str(dist_thresh) + " m"
    x1_text = dist_thresh - 0.01 * np.max(dist_bins)
    y1_text = np.min(res_df["perc"])
    plt.text(x1_text, y1_text, t1, ha="right", va="bottom")
    # Text percentage
    t2 = str(perc_thresh) + " %"
    x2_text = 0
    y2_text = perc_thresh - 0.01 * (100 - np.min(res_df["perc"]))
    plt.text(x2_text, y2_text, t2, ha="left", va="top")
    fig.savefig(fig_file_dist)
    plt.close(fig)

    # Results
    return {'tot_def': tot_area_def, 'dist_thresh': dist_thresh,
            'perc_thresh': perc_thresh}


# # Test
# dist_edge_threshold(fcc_file="data/fcc_GLP.tif",
#                     defor_values=1,
#                     dist_file="outputs_steps/dist_edge_cal.tif",
#                     dist_bins=np.arange(0, 1080, step=30),
#                     tab_file_dist="outputs_steps/perc_dist.csv",
#                     fig_file_dist="outputs_steps/perc_dist.png",
#                     figsize=(6.4, 4.8),
#                     dpi=100,
#                     blk_rows=128,
#                     verbose=True)

# fcc_file = "data/fcc123_GLP.tif"
# defor_values = 1
# dist_file = "outputs_steps/dist_edge_cal.tif"
# dist_bins = np.arange(0, 1080, step = 30)
# tab_file_dist = "outputs_steps/perc_dist_cal.csv"
# fig_file_dist = "outputs_steps/perc_dist_cal.png"
# figsize = (6.4, 4.8)
# dpi = 100
# blk_rows = 128
# verbose = True

# End
