#!/usr/bin/env python

# Standard system library
import os
import sys

# External libraries
import riskmapjnr as rmj

# PROJ_LIB
os.environ["PROJ_LIB"] = ("/home/ghislain/.pyenv/versions/miniconda3-latest"
                          "/envs/conda-rmj/share/proj")

# Setup GRASS
gisbase = "/usr/lib/grass82"
os.environ['GISBASE'] = gisbase
gisdb = os.path.expanduser("~/Code/riskmapjnr/docsrc/notebooks/grassdata")
os.environ['GISDBASE'] = gisdb
location = "kenya"
mapset = "PERMANENT"
sys.path.append(os.path.join(gisbase, "etc/python"))

# Import GRASS Python bindings
noqa = True
if noqa:  # noqa
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

# Working directory
wd = os.path.expanduser("~/Code/riskmapjnr/docsrc/notebooks")
os.chdir(wd)

# =========================
# Forest cover at each date
# =========================

year = [2010, 2014, 2018]
for i in year:
    expr = (f"for_{i} = if(lc_{i} == 0, null(), "
            f"if((lc_{i} >= 1) & (lc_{i} <= 3), 1, 0))")
    r.mapcalc(expression=expr, overwrite=OVR)

# =======================
# Forest cover change 123
# =======================

expr = ("fcc123 = if(for_2018 == 1, 3, "
        "if(for_2014 == 1, 2, "
        "if(for_2010 == 1, 1, null())))")
r.mapcalc(expression=expr, overwrite=OVR)

# Color 123
expr = (
    "nv 255:255:255\n"
    "1 255:165:0\n"
    "2 227:26:28\n"
    "3 34:139:34"
)
r.colors(map="fcc123", rules="-", stdin_=expr)

# Export fcc123
ofile = os.path.join("data", "fcc123_KEN_101418.tif")
r.out_gdal(input="fcc123",
           output=ofile,
           format="GTiff", type="Byte", nodata=0,
           createopt="COMPRESS=LZW,PREDICTOR=2",
           overwrite=OVR)

# =======================
# Forest cover change 12
# =======================

# Forest cover change 12 from fcc123
expr = ("fcc12 = if(fcc123 == 3 || fcc123 == 2, 1, "
        "if(fcc123 == 1, 0, null()))")
r.mapcalc(expression=expr, overwrite=OVR)

# Color 12
expr = (
    "nv 255:255:255\n"
    "0 227:26:28\n"
    "1 34:139:34"
)
r.colors(map="fcc12", rules="-", stdin_=expr)

# Export fcc12
ofile = os.path.join("data/far-kenya", "fcc12_KEN_1014.tif")
r.out_gdal(input="fcc12",
           output=ofile,
           format="GTiff", type="Byte", nodata=255,
           createopt="COMPRESS=LZW,PREDICTOR=2",
           overwrite=OVR)

# =======================
# Forest cover change 23
# =======================

# Forest cover change 23 from fcc123
expr = ("fcc23 = if(fcc123 == 3, 1, "
        "if(fcc123 == 2, 0, null()))")
r.mapcalc(expression=expr, overwrite=OVR)

# Color 23
expr = (
    "nv 255:255:255\n"
    "0 227:26:28\n"
    "1 34:139:34"
)
r.colors(map="fcc23", rules="-", stdin_=expr)

# Export fcc23
ofile = os.path.join("data/far-kenya/forest", "fcc23_KEN_1418.tif")
r.out_gdal(input="fcc23",
           output=ofile,
           format="GTiff", type="Byte", nodata=255,
           createopt="COMPRESS=LZW,PREDICTOR=2",
           overwrite=OVR)

# ===============================
# Distance to forest edge in 2010
# ===============================

# Recompute forest_KEN_2014 to have only 1 and 0 values
expr = ("forest_KEN_2010 = if(fcc12 == 1 || fcc12 == 0, 1, null())")
r.mapcalc(expression=expr, overwrite=OVR)

# Export forest_KEN_2014
ofile = os.path.join("data/far-kenya/forest", "forest_KEN_2010.tif")
r.out_gdal(input="forest_KEN_2010",
           output=ofile,
           format="GTiff", type="Byte", nodata=0,
           createopt="COMPRESS=LZW,PREDICTOR=2",
           overwrite=OVR)

ifile = os.path.join("data/far-kenya/forest", "forest_KEN_2010.tif")
ofile = os.path.join("data/far-kenya", "dist_edge_2010.tif")
rmj.dist_value(ifile, ofile, value=0, verbose=True)

# ===============================
# Distance to forest edge in 2014
# ===============================

# Recompute forest_KEN_2014 to have only 1 and 0 values
expr = ("forest_KEN_2014 = if(fcc12 == 1, 1, null())")
r.mapcalc(expression=expr, overwrite=OVR)

# Export forest_KEN_2014
ofile = os.path.join("data/far-kenya/forest", "forest_KEN_2014.tif")
r.out_gdal(input="forest_KEN_2014",
           output=ofile,
           format="GTiff", type="Byte", nodata=0,
           createopt="COMPRESS=LZW,PREDICTOR=2",
           overwrite=OVR)

ifile = os.path.join("data/far-kenya/forest", "forest_KEN_2014.tif")
ofile = os.path.join("data/far-kenya/forecast", "dist_edge_2014.tif")
rmj.dist_value(ifile, ofile, value=0, verbose=True)

# ===============================
# forest_KEN_2018
# ===============================

# Recompute forest_KEN_2018 to have only 1 and 0 values
expr = ("forest_KEN_2018 = if(fcc123 == 3, 1, null())")
r.mapcalc(expression=expr, overwrite=OVR)

# Export forest_KEN_2018
ofile = os.path.join("data/far-kenya/forest", "forest_KEN_2018.tif")
r.out_gdal(input="forest_KEN_2018",
           output=ofile,
           format="GTiff", type="Byte", nodata=0,
           createopt="COMPRESS=LZW,PREDICTOR=2",
           overwrite=OVR)

# EOF
