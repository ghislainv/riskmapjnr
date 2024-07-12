"""
riskmapjnr: mapping deforestation risk using the moving window approach.
https://ecology.ghislainv.fr/riskmapknr/
"""

# Define double undescore variables
# https://peps.python.org/pep-0008/#module-level-dunder-names
__author__ = "Ghislain Vieilledent"
__email__ = "ghislain.vieilledent@cirad.fr"
__version__ = "1.3.2"

# GDAL exceptions
from osgeo import gdal

# Standard library imports
import os

# Local imports
from .defrate_per_cat import defrate_per_cat
from .defor_cat import defor_cat
from .deforest import deforest
from .dist_edge_threshold import dist_values, dist_edge_threshold
from .get_ldefz_v import get_ldefz_v
from .get_riskmap_v import get_riskmap_v
from .local_defor_rate import local_defor_rate
from .misc import countpix, invlogit, make_dir, tree, rescale
from .set_defor_cat_zero import set_defor_cat_zero
from .validation import validation
from .validation_fcc import validation_fcc
from .plot import fcc123, riskmap
from . import benchmark
# Import makemap in last as it uses from . import
from .makemap import makemap

# GDAL exceptions
gdal.UseExceptions()

# EOF
