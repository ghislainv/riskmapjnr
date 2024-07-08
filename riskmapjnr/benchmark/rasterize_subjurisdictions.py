"""Resterizing subjurisdictions."""

from osgeo import gdal


def rasterize_subjurisdictions(input_file, fcc_file, output_file,
                               verbose=False):
    """Rasterizing subjurisdictions.

    :param input_file: Input GPKG vector file with subjurisdictions.
    :param fcc_file: Input fcc file for resolution and extent.
    :param output_file: Output raster file with integer id for
        subjurisdictions.
    :param verbose: Logical. Whether to print messages or not. Default
        to ``False``.

    """

    # Callback
    cback = gdal.TermProgress_nocb if verbose else 0

    # Raster info: extent, resolution, proj
    fcc_ds = gdal.Open(fcc_file, gdal.GA_ReadOnly)
    gt = fcc_ds.GetGeoTransform()
    xmin = gt[0]
    xres = gt[1]
    ymax = gt[3]
    yres = -gt[5]
    xmax = xmin + xres * fcc_ds.RasterXSize
    ymin = ymax - yres * fcc_ds.RasterYSize
    extent = (xmin, ymin, xmax, ymax)
    proj = fcc_ds.GetProjectionRef()

    # SQL statement to get id, use "subj" layer
    sql_statement = ("select *, row_number() over () "
                     "as id from subj")

    # Rasterize
    param = gdal.RasterizeOptions(
        outputBounds=extent,
        targetAlignedPixels=True,
        attribute="id",
        outputSRS=proj,
        noData=0,
        xRes=xres,
        yRes=yres,
        SQLStatement=sql_statement,
        SQLDialect="SQLite",
        outputType=gdal.GDT_Byte,
        creationOptions=["COMPRESS=DEFLATE", "BIGTIFF=YES"],
        callback=cback)
    gdal.Rasterize(output_file, input_file, options=param, callback=cback)


# # Test
# import os
# os.chdir("/home/ghislain/deforisk/MTQ_2000_2010_2020_jrc_7221/")
# rasterize_subjurisdictions(
#     input_file="data_raw/gadm41_MTQ_0.gpkg",
#     fcc_file="data/fcc.tif",
#     output_file="outputs/benchmark_model/subj.tif",
#     verbose=True)

# End
