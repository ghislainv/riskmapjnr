#!/usr/bin/env python

# Standard system library
import os
import sys

# Setup GRASS
gisbase = "/usr/lib/grass82"
os.environ['GISBASE'] = gisbase
gisdb = os.path.expanduser("~/Code/riskmapjnr/docsrc/notebooks/grassdata")
os.environ['GISDBASE'] = gisdb
location = "kenya"
mapset = "PERMANENT"
sys.path.append(os.path.join(gisbase, "etc/python"))

# Import GRASS Python bindings
from grass.pygrass.modules import Module
from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules.shortcuts import raster as r
from grass.pygrass.modules.shortcuts import vector as v
import grass.script.setup as gsetup
import grass.script as gs

# Launch session
rcfile = gsetup.init(gisdb, location, mapset)

# Region
g.list(type="raster")
g.region(raster="lc_2010", flags="p")

# Constant
OVR = True

# Forest cover at each date
year = [2010, 2014, 2018]
for i in year:
    expr = (f"for_{i} = if(lc_{i} == 0, null(), "
            f"if((lc_{i} >= 1) & (lc_{i} <= 3), 1, 0))")
    r.mapcalc(expression=expr, overwrite=OVR)

# Forest cover change
expr = ("fcc123 = if(for_2018 == 1, 3, "
        "if(for_2014 == 1, 2, "
        "if(for_2010 == 1, 1, null())))")
r.mapcalc(expression=expr, overwrite=OVR)

# Color
expr = (
    "nv 255:255:255\n"
    "1 255:165:0\n"
    "2 227:26:28\n"
    "3 34:139:34"
)
r.colors(map="fcc123", rules="-", stdin_=expr)

# Export
ofile = os.path.join("data", "fcc123_KEN_101418.tif")
r.out_gdal(input="fcc123",
           output=ofile,
           format="GTiff", type="Byte", nodata=0,
           createopt="COMPRESS=LZW,PREDICTOR=2")

# EOF
