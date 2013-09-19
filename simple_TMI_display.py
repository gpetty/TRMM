# -*- coding: utf-8 -*-
# <nbformat>2</nbformat>

# <codecell>

from mpl_toolkits.basemap import Basemap, cm
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from swathmap import *
import TRMM as trmm

# <codecell>

# Read in orbit data

filename = "/Volumes/data2b/TRMM/TMI/HDF/2002/250/1B11.20020907.27436.7.HDF"

myorbit = trmm.TMIorbit(filename)

# Perform channel resolution matching
mt10v, mt10h, mt19v, mt19h, mt21v, mt37v, mt37h, mt85v, mt85h = myorbit.match19()

# <codecell>

# shorthand names for arrays of lat/lons
lats = myorbit.lat_lo
lons = myorbit.lon_lo

# 1D arrays of time tags (one per scan)
iyear = myorbit.Year
iday  = myorbit.DayOfYear
ihour   = myorbit.Hour
iminute  = myorbit.Minute


# create a new figure
fig = plt.figure(figsize=(8,8))
fig.add_subplot(111)

# set map region to plot  (LLLAT is lower-left latitude, URLON is upper-right longitude, etc)
map = makemap(lllat = 18.0,urlat = 33.0,lllon = 115.0,urlon = 130.0, dellon=10.0)

minscan=1000  # starting scan number to plot
maxscan=1400  # ending scan number (max ~3000)
data = mt85v  # channel to plot


deconvolved = True   # plot "native" or deconvolved TBs?

if deconvolved:
    plotname = 'satdemo_deconv.pdf'
    title = 'Deconvolved'
    data = mt85v[minscan:maxscan]
else:
    title = 'Native Resolution'
    plotname = 'satdemo_native.pdf'
    data = myorbit.t85v[minscan:maxscan]

# plot TB data on map previously created
plotswath(map, lats[minscan:maxscan],lons[minscan:maxscan],data[minscan:maxscan],MISSING=trmm.MISSINGVAL, vmin=200.0, vmax=300.0)

# make colorbar
cb = plt.colorbar(shrink=0.75)
cb.set_label("[K]")

# Set plot title
plt.title(title)

# Save plot to PDF file
plt.savefig(plotname)

