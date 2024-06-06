"""Plot functions."""

import os

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.patches import Rectangle
import numpy as np
from osgeo import gdal, ogr


# Plot vector objects
# (https://github.com/cgarrard/osgeopy-code/blob/master/Chapter13/listing13_3.py)
def plot_polygon(poly, symbol='k-', **kwargs):
    """Plots a polygon using the given symbol."""
    for i in range(poly.GetGeometryCount()):
        subgeom = poly.GetGeometryRef(i)
        x, y = zip(*subgeom.GetPoints())
        plt.plot(x, y, symbol, **kwargs)


# Use this function to fill polygons.
def plot_polygon_fill(poly, symbol='w', **kwargs):
    """Plots a polygon using the given symbol."""
    for i in range(poly.GetGeometryCount()):
        x, y = zip(*poly.GetGeometryRef(i).GetPoints())
        plt.fill(x, y, symbol, **kwargs)


def plot_line(line, symbol='k-', **kwargs):
    """Plots a line using the given symbol."""
    x, y = zip(*line.GetPoints())
    plt.plot(x, y, symbol, **kwargs)


def plot_point(point, symbol='ko', **kwargs):
    """Plots a point using the given symbol."""
    x, y = point.GetX(), point.GetY()
    plt.plot(x, y, symbol, **kwargs)


def plot_layer(filename, symbol, layer_index=0, **kwargs):
    """Plots an OGR layer using the given symbol."""
    ds = ogr.Open(filename)
    for row in ds.GetLayer(layer_index):
        geom = row.geometry()
        geom_type = geom.GetGeometryType()

        # Polygons
        if geom_type == ogr.wkbPolygon:
            plot_polygon(geom, symbol, **kwargs)

        # Multipolygons
        elif geom_type == ogr.wkbMultiPolygon:
            for i in range(geom.GetGeometryCount()):
                subgeom = geom.GetGeometryRef(i)
                plot_polygon(subgeom, symbol, **kwargs)

        # Lines
        elif geom_type == ogr.wkbLineString:
            plot_line(geom, symbol, **kwargs)

        # Multilines
        elif geom_type == ogr.wkbMultiLineString:
            for i in range(geom.GetGeometryCount()):
                subgeom = geom.GetGeometryRef(i)
                plot_line(subgeom, symbol, **kwargs)

        # Points
        elif geom_type == ogr.wkbPoint:
            plot_point(geom, symbol, **kwargs)

        # Multipoints
        elif geom_type == ogr.wkbMultiPoint:
            for i in range(geom.GetGeometryCount()):
                subgeom = geom.GetGeometryRef(i)
                plot_point(subgeom, symbol, **kwargs)


# Saving a matplotlib.pyplot figure as a border-less frame-less image
def figure_as_image(fig, output_file):
    """Remove borders and frames of a Matplotlib figure and save.

    :param fig: Matplotlib figure you want to save as the image.
    :param output_file: Path to the output image file.

    :return: Figure without borders and frame.

    """

    fig.tight_layout()
    a = fig.gca()
    a.set_frame_on(False)
    a.set_xticks([])
    a.set_yticks([])
    plt.axis("off")
    fig.savefig(output_file, dpi="figure", bbox_inches="tight")


# plot.fcc123
def fcc123(input_fcc_raster,
           output_file="fcc123.png",
           maxpixels=500000,
           borders=None,
           zoom=None,
           col=[(255, 165, 0, 255),
                (227, 26, 28, 255),
                (34, 139, 34, 255)],
           figsize=(11.69, 8.27),
           dpi=300, **kwargs):
    """Plot forest-cover change (fcc123) map.

    This function plots the forest-cover change map with 2
    deforestation time-periods (2000 -> 2010 -> 2020 for example) plus
    the remaining forest (3 classes).

    :param input_fcc_raster: Path to fcc123 raster.
    :param output_file: Name of the plot file.
    :param maxpixels: Maximum number of pixels to plot.
    :param borders: Vector file to be plotted.
    :param zoom: Zoom to region (xmin, xmax, ymin, ymax).
    :param col: List of rgba colors for classes 123.
    :param figsize: Figure size in inches.
    :param dpi: Resolution for output image.
    :param \\**kwargs: see below.

    :Keyword Arguments: Additional arguments to plot borders.

    :return: A Matplotlib figure of the forest cover change map.

    """

    # Load raster and band
    rasterR = gdal.Open(input_fcc_raster, gdal.GA_ReadOnly)
    rasterB = rasterR.GetRasterBand(1)
    gt = rasterR.GetGeoTransform()
    ncol = rasterR.RasterXSize
    nrow = rasterR.RasterYSize
    Xmin = gt[0]
    Xmax = gt[0] + gt[1] * ncol
    Ymin = gt[3] + gt[5] * nrow
    Ymax = gt[3]
    extent = [Xmin, Xmax, Ymin, Ymax]

    # Total number of pixels
    npixels_orig = ncol * nrow
    # Check number of pixels is inferior to maxpixels
    if npixels_orig > maxpixels:
        # Remove potential existing external overviews
        if os.path.isfile(input_fcc_raster + ".ovr"):
            os.remove(input_fcc_raster + ".ovr")
        # Find overview level such that npixels <= maxpixels
        i = 0
        npixels_ov = npixels_orig
        while npixels_ov > maxpixels:
            i += 1
            ov_level = pow(2, i)
            npixels_ov = npixels_orig // np.power(ov_level, 2)
        # Build overview
        print("Build overview")
        gdal.SetConfigOption('COMPRESS_OVERVIEW', 'DEFLATE')
        rasterR.BuildOverviews("nearest", [ov_level])
        # Get data from overview
        ov_band = rasterB.GetOverview(0)
        ov_arr = ov_band.ReadAsArray()
    else:
        # Get original data
        ov_arr = rasterB.ReadAsArray()

    # Dereference driver
    rasterB = None
    del rasterR

    # Colormap
    colors = [(1, 1, 1, 0)]  # transparent white for 0
    cmax = 255.0  # float for division
    for i in range(3):
        col_class = tuple(np.array(col[i]) / cmax)
        colors.append(col_class)
    color_map = ListedColormap(colors)

    # Plot raster
    place = 111 if zoom is None else 121
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax1 = plt.subplot(place)
    ax1.set_frame_on(False)
    ax1.set_xticks([])
    ax1.set_yticks([])
    plt.imshow(ov_arr, cmap=color_map, extent=extent,
               resample=False, interpolation="nearest")
    if borders is not None:
        plot_layer(borders, symbol="k-", **kwargs)
    plt.axis("off")
    if zoom is not None:
        z = Rectangle(
            (zoom[0], zoom[2]),
            zoom[1] - zoom[0],
            zoom[3] - zoom[2],
            fill=False
        )
        ax1.add_patch(z)
        ax2 = plt.subplot(222)
        plt.imshow(ov_arr, cmap=color_map, extent=extent,
                   resample=False, interpolation="nearest")
        plt.xlim(zoom[0], zoom[1])
        plt.ylim(zoom[2], zoom[3])
        ax2.set_xticks([])
        ax2.set_yticks([])

    # Save and return figure
    fig.tight_layout()
    fig.savefig(output_file, dpi="figure", bbox_inches="tight")
    return fig


def rescale_zo(x, xmin, xmax):
    """Rescale on interval zero-one."""
    z = (x - xmin) / (xmax - xmin)
    return z


# plot.vulnerability_map
def vulnerability_map(
        input_map,
        output_file="prob.png",
        maxpixels=500000,
        borders=None,
        legend=False,
        figsize=(11.69, 8.27),
        dpi=300, **kwargs):
    """Plot deforestation vulnerability map.

    :param input_map: Path to vulnerability map.
    :param output_file: Name of the plot file.
    :param maxpixels: Maximum number of pixels to plot.
    :param borders: Vector file to be plotted.
    :param legend: Add colorbar if True.
    :param figsize: Figure size in inches.
    :param dpi: Resolution for output image.
    :param \\**kwargs: see below.

    :Keyword Arguments: Additional arguments to plot borders.

    :return: A Matplotlib figure of the map of spatial probability of
        deforestation.

    """

    # Load raster and band
    rasterR = gdal.Open(input_map, gdal.GA_ReadOnly)
    rasterB = rasterR.GetRasterBand(1)
    gt = rasterR.GetGeoTransform()
    ncol = rasterR.RasterXSize
    nrow = rasterR.RasterYSize
    Xmin = gt[0]
    Xmax = gt[0] + gt[1] * ncol
    Ymin = gt[3] + gt[5] * nrow
    Ymax = gt[3]
    extent = [Xmin, Xmax, Ymin, Ymax]

    # Total number of pixels
    npixels_orig = ncol * nrow
    # Check number of pixels is inferior to maxpixels
    if npixels_orig > maxpixels:
        # Remove potential existing external overviews
        if os.path.isfile(input_map + ".ovr"):
            os.remove(input_map + ".ovr")
        # Find overview level such that npixels <= maxpixels
        i = 0
        npixels_ov = npixels_orig
        while npixels_ov > maxpixels:
            i += 1
            ov_level = pow(2, i)
            npixels_ov = npixels_orig // np.power(ov_level, 2)
        # Build overview
        gdal.SetConfigOption('COMPRESS_OVERVIEW', 'DEFLATE')
        rasterR.BuildOverviews("nearest", [ov_level])
        # Get data from overview
        ov_band = rasterB.GetOverview(0)
        ov_arr = ov_band.ReadAsArray()
    else:
        # Get original data
        ov_arr = rasterB.ReadAsArray()

    # Dereference driver
    rasterB = None
    del rasterR

    # Colormap
    colors = []
    cmax = 255.0  # float for division
    vmin = 1001.0
    vmax = 30999.0  # float for division
    # dark green for no deforestation above dist threshold
    colors.append((rescale_zo(1001, vmin, vmax),
                   (25 / cmax, 110 / cmax, 25 / cmax, 1)))
    # green
    colors.append((rescale_zo(2000, vmin, vmax),
                   (34 / cmax, 139 / cmax, 34 / cmax, 1)))
    # orange
    colors.append((rescale_zo(10000, vmin, vmax),
                   (1, 165 / cmax, 0, 1)))
    # red
    colors.append((rescale_zo(20000, vmin, vmax),
                   (227 / cmax, 26 / cmax, 28 / cmax, 1)))
    # black
    colors.append((rescale_zo(30999, vmin, vmax),
                   (0, 0, 0, 1)))
    color_map = LinearSegmentedColormap.from_list(
        name="mycm", colors=colors, N=30999-1000, gamma=1.0
    )
    # Set transparent color for lower out-of-range values.
    color_map.set_under(color=(1, 1, 1, 0))

    # Plot raster
    fig = plt.figure(figsize=figsize, dpi=dpi)
    plt.subplot(111)
    plt.imshow(ov_arr, cmap=color_map, extent=extent,
               vmin=0.01, vmax=30999,
               resample=False, interpolation="nearest")
    if borders is not None:
        plot_layer(borders, symbol="k-", **kwargs)

    # Legend
    if legend is True:
        t = np.linspace(0, 30999, 6, endpoint=True)
        cbar = plt.colorbar(ticks=t, orientation="vertical",
                            shrink=0.5, aspect=20)
        vl = np.linspace(0, 1, 6, endpoint=True).astype(int)
        cbar.ax.set_yticklabels(vl)

    # Save image
    figure_as_image(fig, output_file)

    # Return figure
    return fig

# EOF
