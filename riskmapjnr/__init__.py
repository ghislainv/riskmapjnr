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
from .misc import invlogit, make_dir, tree
from .dist_edge_threshold import dist_edge_threshold
from .local_defor_rate import local_defor_rate
from .set_defor_cat_zero import set_defor_cat_zero
from .defrate_per_cat import defrate_per_cat
from .defor_cat import defor_cat
from .validation import validation
from .makemap import makemap
from .plot import fcc123, riskmap

# # Welcome message
# print("# riskmapjnr: Map of deforestation risk following JNR methodology.")
# print("# https://ecology.ghislainv.fr/riskmapjnr/")

# EOF
