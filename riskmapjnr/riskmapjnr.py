#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=3.6
# license         :GPLv3
# ==============================================================================

import riskmapjnr as rmj


def main():
    """riskmapjnr.riskmapjnr: provides entry point main().

    Running ``riskmapjnr`` in the terminal prints riskmapjnr
    description and version. Can be used to check that the
    ``riskmapjnr`` Python package has been correctly imported.

    """

    print(rmj.__doc__)
    print(f"version {rmj.__version__}.")

# End
