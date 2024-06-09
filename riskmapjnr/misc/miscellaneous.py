#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=3
# license         :GPLv3
# ==============================================================================

# Standard library imports
from itertools import islice
import os
from pathlib import Path

# Third party imports
import numpy as np
from osgeo import gdal


# Invlogit
def invlogit(x):
    """Compute the inverse-logit of a numpy array.

    We differenciate the positive and negative values to avoid
    under/overflow with the use of exp().

    :param x: Numpy array.

    :return: Return the inverse-logit of the array.

    """

    r = x
    r[x > 0] = 1.0 / (1.0 + np.exp(-x[x > 0]))
    r[x <= 0] = np.exp(x[x <= 0]) / (1 + np.exp(x[x <= 0]))
    return r


# Function to make a directory
def make_dir(newdir):
    """Make new directory

        * Already exists, silently complete
        * Regular file in the way, raise an exception
        * Parent directory(ies) does not exist, make them as well

    :param newdir: Directory path to create.

    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired \
                      dir, '{}', already exists.".format(newdir))
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            make_dir(head)
        # print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)


# Makeblock
def makeblock(rasterfile, blk_rows=128):
    """Compute block information.

    This function computes block information from the caracteristics
    of a raster file and an indication on the number of rows to
    consider.

    :param rasterfile: Path to a raster file.
    :param blk_rows: If > 0, number of rows for block. If <=0, the
        block size will be 256 x 256.

    :return: A tuple of length 6 including block number, block number
        on x axis, block number on y axis, block offsets on x axis,
        block offsets on y axis, block sizes on x axis, block sizes on
        y axis.

    """

    r = gdal.Open(rasterfile)
    # b = r.GetRasterBand(1)
    # Landscape variables
    ncol = r.RasterXSize
    nrow = r.RasterYSize
    # Block size
    # block_xsize, block_ysize = b.GetBlockSize()
    # Adapt number of blocks
    if blk_rows > 0:
        block_xsize = ncol
        block_ysize = blk_rows
    else:
        block_xsize = 256
        block_ysize = 256
    # Number of blocks
    nblock_x = int(np.ceil(ncol / block_xsize))
    nblock_y = int(np.ceil(nrow / block_ysize))
    nblock = nblock_x * nblock_y
    # Upper-left coordinates of each block
    x = np.arange(0, ncol, block_xsize, dtype=np.int32).tolist()
    y = np.arange(0, nrow, block_ysize, dtype=np.int32).tolist()
    # Size (number of col and row) of each block
    nx = [block_xsize] * nblock_x
    ny = [block_ysize] * nblock_y
    # Modify last values of nx and ny
    if (ncol % block_xsize) > 0:
        nx[-1] = ncol % block_xsize
    if (nrow % block_ysize) > 0:
        ny[-1] = nrow % block_ysize
    # b = None
    del r
    return (nblock, nblock_x, nblock_y, x, y, nx, ny)


# Make_square
def make_square(rasterfile, square_size=33):
    """Compute square information.

    This function computes block information from the caracteristics
    of a raster file and an indication on the number of rows to
    consider.

    :param rasterfile: Path to a raster file.
    :param square_size: Pixel number to define square side size.

    :return: A tuple of length 6 including square number, square
        number on x axis, square number on y axis, square offsets on x
        axis, square offsets on y axis, square sizes on x axis, square
        sizes on y axis.

    """

    r = gdal.Open(rasterfile)
    # Landscape variables
    ncol = r.RasterXSize
    nrow = r.RasterYSize
    # Number of squares
    nsquare_x = int(np.ceil(ncol / square_size))
    nsquare_y = int(np.ceil(nrow / square_size))
    nsquare = nsquare_x * nsquare_y
    # Upper-left coordinates of each square
    x = np.arange(0, ncol, square_size, dtype=int).tolist()
    y = np.arange(0, nrow, square_size, dtype=int).tolist()
    # Size (number of col and row) of each square
    nx = [square_size] * nsquare_x
    ny = [square_size] * nsquare_y
    # Modify last values of nx and ny
    if (ncol % square_size) > 0:
        nx[-1] = ncol % square_size
    if (nrow % square_size) > 0:
        ny[-1] = nrow % square_size
    # b = None
    del r
    return (nsquare, nsquare_x, nsquare_y, x, y, nx, ny)


def progress_bar(niter, i):
    """Draw progress_bar

     See results of ``[(100 * i / niter) // 10 * 10 for i in
     range(niter + 1)]`` to understand how it works.

    :param niter: Total number of iterations.
    :param i: Current number of iteration (starts at 1).

    """

    pkg_name = "riskmapjnr"

    if niter >= 40:
        perc_10 = 100 * i / niter // 10 * 10
        perc_previous_10 = 100 * (i - 1) / niter // 10 * 10
        perc_2_5 = 100 * i / niter // 2.5 * 2.5
        perc_previous_2_5 = 100 * (i - 1) / niter // 2.5 * 2.5
        if i == 1:
            print(f"{pkg_name}: 0", end="", flush=True)
        elif perc_10 != perc_previous_10:
            if i == niter:
                print("100 - done", end="\n", flush=True)
            else:
                print(f"{int(perc_10)}", end="", flush=True)
        elif perc_2_5 != perc_previous_2_5:
            print(".", end="", flush=True)
    else:
        perc_10 = 100 * i / niter // 10 * 10
        perc_previous_10 = 100 * (i - 1) / niter // 10 * 10
        if i == 0:
            print(f"{pkg_name}: 0...", end="", flush=True)
        elif perc_10 != perc_previous_10:
            if i == niter:
                print("100 - done", end="\n", flush=True)
            else:
                print(f"{int(perc_10)}...", end="", flush=True)


# Rescale
def rescale(value, min_val=1, max_val=10000):
    """Rescale probability values to.

    This function rescales probability values (float in [0, 1]) to
    integer values in [min_val, max_val]. Raster data can then be of type
    UInt16 with 0 as nodata value.

    :param value: Numpy array of float values in [0, 1].

    :param min_val: Integer. Minimal value for
        rescaling. Down to 1. Default to 1.

    :param max_val: Integer. Maximal value for
        rescaling. Up to 65535. Default to 10000.

    :return: Rescaled numpy array of integer values in [min_val, max_val].

    """

    # Transform to float (otherwise 1e-06 is set to 0)
    value = value.astype(float)
    # Avoid nodata value (0) for low proba
    value[value < 1e-06] = 1e-06
    # Rescale and round to nearest integer
    r = ((value * 1e6 - 1) * (max_val - min_val) / 999999.0) + min_val
    r = np.rint(r).astype(int)
    return r


# Tree
# from https://stackoverflow.com/questions/9727673/
# list-directory-tree-structure-in-python

space = '    '
branch = '│   '
tee = '├── '
last = '└── '


def tree(dir_path: Path, level: int = -1, limit_to_directories: bool = False,
         length_limit: int = 1000):
    """Given a directory Path object print a visual tree structure.

    :param dir_path: Directory path.
    :param level: Option to limit recursion to a given level.
    :param limit_to_directories: Option to limit to just directories.
    :param length_limit: Length limit of the output in number of lines.
    :return: Visual tree stucture.

    """
    dir_path = Path(dir_path)  # accept string coerceable to Path
    files = 0
    directories = 0

    def inner(dir_path: Path, prefix: str = '', level=-1):
        nonlocal files, directories
        if not level:
            return  # 0, stop iterating
        if limit_to_directories:
            contents = [d for d in dir_path.iterdir() if d.is_dir()]
        else:
            contents = list(dir_path.iterdir())
        pointers = [tee] * (len(contents) - 1) + [last]
        for pointer, path in zip(pointers, contents):
            if path.is_dir():
                yield prefix + pointer + path.name
                directories += 1
                extension = branch if pointer == tee else space
                yield from inner(path, prefix=prefix+extension, level=level-1)
            elif not limit_to_directories:
                yield prefix + pointer + path.name
                files += 1
    print(dir_path.name)
    iterator = inner(dir_path, level=level)
    for line in islice(iterator, length_limit):
        print(line)
    if next(iterator, None):
        print(f'... length_limit, {length_limit}, reached, counted:')
    print(f'\n{directories} directories' +
          (f', {files} files' if files else ''))


# End
