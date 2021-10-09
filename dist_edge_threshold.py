#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=3
# license         :GPLv3
# ==============================================================================


# Python virtual environment
# conda create --name jnr-vcs -c conda-forge python gdal numpy
# matplotlib pip scipy pandas --yes

# Third party imports
import numpy as np
from osgeo import gdal
import pandas as pd

# Local application imports
from misc import progress_bar, makeblock


# dist_value
def dist_value(input_file,
               dist_file,
               value=0):
    """Computing the shortest distance to a pixel with a specific value in
    a raster file.

    :param input_file: Input raster file.

    :param dist_file: Path to the distance raster file that will be
        created.

    :param value: Value of the raster to compute the distance
        to. Default to 0.

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
    val = "VALUES=" + str(value)
    gdal.ComputeProximity(srcband, dstband,
                          [val, "DISTUNITS=GEO"],
                          callback=gdal.TermProgress)

    # Set nodata value
    dstband.SetNoDataValue(0)

    # Delete objects
    srcband = None
    dstband = None
    del src_ds, dst_ds
    return None


# dist_edge_threshold
def dist_edge_threshold(input_file,
                        dist_file,
                        bins,
                        blk_rows=128):
    """Computing the percentage of total deforestation as a function of
    the distance to forest edge.

    This function computes the percentage of total deforestation as a
    function of the distance to forest edge. It returns a table with
    the cumulative percentage of deforestation as distance to forest
    edge increases. It also identifies the distance threshold for the
    distance to forest edge so that the deforestation under that
    threshold is >= 99 % of the total deforestation in the
    landscape. The function also plots the relationship between the
    percentage of deforestation and the distance to forest edge. A
    raster of distance to forest edge will be created. The distance
    unit will be the one of the input file.

    :param input_file: Input raster file of forest cover change at
        three dates(123). 1: first period deforestation, 2: second
        period deforestation, 3: remaining forest at the end of the
        second period. No data value must be 0 (zero).

    :param dist_file: Path to the distance raster file that will be
        created.

    :param bins: Distance bins (in m). See parameter `bins` of the
        `pandas.cut()` function
        `here<https://pandas.pydata.org/docs/reference/api/pandas.cut.html>`_\\
        . Default to np.arange(0, 1080, step=30).

    :param blk_rows: Number of rows for block. Must be greater or
        equal to ``win_size``. This is used to break lage raster files
        in several blocks of data that can be hold in memory.

    :return: A dictionary. With dist_thresh: the distance threshold,
        perc: the percentage of deforestation for pixels with distance
        <= dist_thresh.

    """

    # Compute the distance to the forest edge
    print("Compute the distance to forest edge")
    dist_value(input_file, dist_file, value=0)

    # Make blocks
    blockinfo = makeblock(dist_file, blk_rows=blk_rows)
    nblock = blockinfo[0]
    nblock_x = blockinfo[1]
    x = blockinfo[3]
    y = blockinfo[4]
    nx = blockinfo[5]
    ny = blockinfo[6]
    print("Divide region in {} blocks".format(nblock))

    # Read rasters
    dist_ds = gdal.Open(dist_file)
    dist_band = dist_ds.GetRasterBand(1)
    fcc_ds = gdal.Open(input_file)
    fcc_band = fcc_ds.GetRasterBand(1)

    # Total deforested pixels
    npix_def = 0

    # Loop on blocks of data
    for b in range(nblock):
        # Progress bar
        progress_bar(nblock, b + 1)
        # Position in 1D-arrays
        px = b % nblock_x
        py = b // nblock_x
        # Data for one block of the stack (shape = (nband,nrow,ncol))
        dist_data = dist_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        fcc_data = fcc_band.ReadAsArray(x[px], y[py], nx[px], ny[py])
        # Deforested pixels
        npix_def += (fcc_data == 1).sum()
        # Categorize distance
        dist_cat = pd.cut(dist_data, bins, right=True, retbins=True)

    # Compute deforested area
    print("Compute the deforested area in ha")
    gt = fcc_ds.GetGeoTransform()
    pix_area = gt[1] * (-gt[5])
    area_def = pix_area * npix_def / 10000

    # Results
    return {'npix_def': npix_def, 'area_def': area_def}


# Test
dist_value(input_file="data/fcc123.tif",
           dist_file="outputs/dist_edge.tif",
           value=0)

# End
