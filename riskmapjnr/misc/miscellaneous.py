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
import sys

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
    return (r)


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
    x = np.arange(0, ncol, block_xsize, dtype=np.int).tolist()
    y = np.arange(0, nrow, block_ysize, dtype=np.int).tolist()
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
    x = np.arange(0, ncol, square_size, dtype=np.int).tolist()
    y = np.arange(0, nrow, square_size, dtype=np.int).tolist()
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


# Progress_bar
def progress_bar(niter, i):
    """ Draw progress_bar

    :param niter: Total number of iterations.
    :param i: Current number of iteration (starts at 1).

    :return: This function does not return any value.

    """

    step = 1 if niter <= 100 else niter // 100
    if i == 1:
        sys.stdout.write("0%")
        sys.stdout.flush()
    elif i % step == 0:
        sys.stdout.write("\r{}%".format((100 * i) // niter))
        sys.stdout.flush()
    if (i == niter):
        sys.stdout.write("\r100%\n")
        sys.stdout.flush()
    return None


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
