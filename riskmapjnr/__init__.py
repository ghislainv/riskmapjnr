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
import os

# Third party imports
import matplotlib
# Use Agg if no display found
if os.environ.get("DISPLAY", "") == "":
    print("no display found. Using non-interactive Agg backend")
    matplotlib.use("Agg")

# Local imports
from .defrate_per_cat import defrate_per_cat
from .defor_cat import defor_cat
from .deforest import deforest
from .dist_edge_threshold import dist_values, dist_edge_threshold
from .get_ldefz_v import get_ldefz_v
from .get_riskmap_v import get_riskmap_v
from .local_defor_rate import local_defor_rate
from .misc import countpix, invlogit, make_dir, tree
from .set_defor_cat_zero import set_defor_cat_zero
from .validation import validation
from .validation_fcc import validation_fcc
from .plot import fcc123, riskmap
# Import makemap in last as it uses from . import
from .makemap import makemap

# # Welcome message
# print("# riskmapjnr: Map of deforestation risk following JNR methodology.")
# print("# https://ecology.ghislainv.fr/riskmapjnr/")

# EOF
