# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import numpy as np

# This path points to the top-level ERA-interim directory

ROOTDIR = '/Volumes/data2b/ERA-interim/'

lats = np.array(np.loadtxt(ROOTDIR+"latlist.txt"))
lons = np.array(np.loadtxt(ROOTDIR+"lonlist.txt"))

if len(lats) != 256:
    print "No. of lat values = ",len(lats)," : quitting!"
    exit(-1) 

if len(lons) != 512:
    print "No. of lon values = ",len(lons)," : quitting!"
    exit(-1) 

cursktfile1 = ""
cursktfile2 = ""
curtcwvfile1 = ""
curtcwvfile2 = ""
skint1 = []
skint2 = []
tcwv1 = []
tcwv2 = []

# <codecell>


def getera(iyear,iday,ihr,imin,alat,alon):
    global cursktfile1,cursktfile2
    global curtcwvfile1,curtcwvfile2
    global skint1,skint2
    global tcwv1,tcwv2
    
#    print cursktfile1, cursktfile2

# compute nominal slice number (floating point)
    fslice = (iday-1 + (ihr+imin/60.0)/24.)*4.0 + 1.0  
    
    
# compute first slice going back 3 hrs
    iyear1 = iyear
    fslice1 = fslice - 0.5
    islice1 = int(np.floor(fslice1+0.5))
    wt2 = fslice-islice1

#    print "wt2: ",wt2

#    print islice1

# number of slices in previous year
    if np.mod(iyear-1,4) == 0:
        imax = 1464
    else:
        imax = 1460


    if islice1 < 1:
        islice1 += imax
        iyear1 -= 1


# compute second slice going forward 3 hrs

    iyear2 = iyear
    fslice2 = fslice + 0.5
    islice2 = int(np.floor(fslice2+0.5))

#    print islice2

    wt1 = islice2-fslice

#    print "wt1: ",wt1

# number of slices in present year
    if np.mod(iyear,4) == 0:
        imax = 1464
    else:
        imax = 1460

    if islice2 > imax: 
        islice2 -= imax
        iyear2 += 1

    
# load SkinT files

    skintfile1 = ROOTDIR+str(iyear1)+"/"+"skt_235."+str(iyear1)+"."+str(islice1)+".txt"
    skintfile2 = ROOTDIR+str(iyear2)+"/"+"skt_235."+str(iyear2)+"."+str(islice2)+".txt"

    if cursktfile1 != skintfile1:
        cursktfile1 = skintfile1
        skint1 = np.array(np.loadtxt(cursktfile1, skiprows=16))
        if len(skint1) != 131072:
            print "No. of grid values = ",len(skint1)," : quitting!"
            exit(-1) 

        skint1 = np.reshape(skint1,(256,512))

    
    if cursktfile2 != skintfile2:
        cursktfile2 = skintfile2

        skint2 = np.array(np.loadtxt(cursktfile2, skiprows=16))

        if len(skint2) != 131072:
            print "No. of grid values = ",len(skint2)," : quitting!"
            exit(-1) 

        skint2 = np.reshape(skint2,(256,512))

# load water vapor files

    tcwvfile1 = ROOTDIR+str(iyear1)+"/"+"tcwv_137."+str(iyear1)+"."+str(islice1)+".txt"
    tcwvfile2 = ROOTDIR+str(iyear2)+"/"+"tcwv_137."+str(iyear2)+"."+str(islice2)+".txt"

    if curtcwvfile1 != tcwvfile1:
        curtcwvfile1 = tcwvfile1
        tcwv1 = np.array(np.loadtxt(curtcwvfile1, skiprows=16))
        if len(tcwv1) != 131072:
            print "No. of grid values = ",len(tcwv1)," : quitting!"
            exit(-1) 

        tcwv1 = np.reshape(tcwv1,(256,512))

    if curtcwvfile2 != tcwvfile2:
        curtcwvfile2 = tcwvfile2
        tcwv2 = np.array(np.loadtxt(curtcwvfile2, skiprows=16))
        if len(tcwv2) != 131072:
            print "No. of grid values = ",len(tcwv2)," : quitting!"
            exit(-1) 

        tcwv2 = np.reshape(tcwv2,(256,512))

# compute indices into grids

    if alon < 0.0: alon += 360.0
    idxlat=(np.abs(lats-alat)).argmin()
    idxlon=(np.abs(lons-alon)).argmin()

    skt1 = skint1[idxlat][idxlon]
    skt2 = skint2[idxlat][idxlon]
    
    wv1 = tcwv1[idxlat][idxlon]
    wv2 = tcwv2[idxlat][idxlon]


#    print fslice1,fslice,fslice2

#    print skt1,skt2

#    print wv1,wv2

    if (wt1+wt2) > 0:
        skt = (wt2*skt2 + wt1*skt1)/(wt1+wt2)
        wv = (wt2*wv2 + wt1*wv1)/(wt1+wt2)
    else:
        skt = skt1
        wv = wv1

    return(skt,wv)


# <codecell>


