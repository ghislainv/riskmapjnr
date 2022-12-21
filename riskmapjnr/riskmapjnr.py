#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
# author          :Ghislain Vieilledent
# email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
# web             :https://ecology.ghislainv.fr
# python_version  :>=3.6
# license         :GPLv3
# ==============================================================================

__version__ = "1.0"


def main():
    """riskmapjnr.riskmapjnr: provides entry point main().

    Running ``riskmapjnr`` in the terminal prints riskmapjnr
    description and version. Can be used to check that the
    ``riskmapjnr`` Python package has been correctly imported.

    """
    print("# riskmapjnr: Map of deforestation risk following JNR methodology.")
    print("# https://ecology.ghislainv.fr/riskmapjnr")
    print("# riskmapjnr version {}.".format(__version__))
    return None

# End
