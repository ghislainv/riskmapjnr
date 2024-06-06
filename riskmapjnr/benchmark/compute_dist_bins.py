"""Compute distance bins."""

import math

from osgeo import gdal


def compute_dist_bins(dist_file, dist_thresh):
    """Compute distance bins.

    A geometric classification is used to convert distance to
    forest edge into vulnerability classes.

    :param dist_file: Distance to forest edge file.
    :param dist_thresh: Distance threshold.

    """

    with gdal.Open(dist_file) as dist_ds:
        gt = dist_ds.GetGeoTransform()
    xres = gt[1]
    yres = -gt[5]
    dist_min = min(xres, yres)
    n_classes = 29
    ratio = math.pow(dist_min / dist_thresh, 1/n_classes)
    bins = [dist_thresh * math.pow(ratio, n_classes - i)
            for i in range(n_classes + 1)]
    # Correction for dist_min
    bins[0] = dist_min

    return bins

# End
