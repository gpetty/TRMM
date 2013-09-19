
from mpl_toolkits.basemap import Basemap, cm
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from swathmap import *
import TRMM as trmm

# create figure and axes instances
fig = plt.figure(figsize=(8,8), bbox='tight')
fig.add_subplot(111)

map = makemap(lllat = 0.0,urlat = 30.0,lllon = 70.0,urlon = 100.0, dellon=10.0)
# map = makemap(lllat = 15.0,urlat = 17.0,lllon = 80.0,urlon = 82.0, dellon=10.0)

filename = "/Volumes/data2b/TRMM/TMI/HDF/2002/061/1B11.20020302.24491.7.HDF"

minscan = 800
maxscan = 1500
myorbit = trmm.TMIorbit(filename)

lats = myorbit.lat_lo[minscan:maxscan]
lons = myorbit.lon_lo[minscan:maxscan]

mt10v, mt10h, mt19v, mt19h, mt21v, mt37v, mt37h, mt85v, mt85h = myorbit.match19()

# data = mt19h[minscan:maxscan] - myorbit.t19h[minscan:maxscan] 

deconvolved = True

if deconvolved:
    plotname = 'satdemo_deconv.pdf'
    title = 'Deconvolved'
    data = mt85v[minscan:maxscan]
else:
    title = 'Native Resolution'
    plotname = 'satdemo_native.pdf'
    data = myorbit.t85v[minscan:maxscan]

plotswath(map, lats,lons,data,MISSING=trmm.MISSINGVAL, vmin=200.0, vmax=300.0)

# make colorbar
cb = plt.colorbar(shrink=0.75)
cb.set_label("K")


# draw filled contours.
# clevs = [0,1,2.5,5,7.5,10,15,20,30,40,50,70,100,150,200,250,300,400,500,600,750]
# cs = m.contourf(x,y,data,clevs,cmap=cm.s3pcpn)

plt.title(title)
plt.savefig(plotname)

