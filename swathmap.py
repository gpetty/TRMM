from mpl_toolkits.basemap import Basemap, cm
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from matplotlib import rcParams

def extrapcorners (x, y):
    '''
    This function accepts 2D NxM arrays of X positions and Y positions
    representing the CENTERS of satellite pixels.  Normally these should
    be in plotter coordinates, not latitudes and longitudes so as to avoid
    problems at the dateline.  The function returns arrays of dimension
    (N+1)x(M+1) containing the CORNER POINTS of tiled quadrilaterals more
    or less centered on the pixels centers.  These arrays can then be
    passed to plt.pcolormesh(xc,yc,data), where data is an MxN array
    containing the pixel values.
    '''
    nx, ny = x.shape
    print nx, ny

    xc = np.zeros((nx+1,ny+1))
    yc = np.zeros((nx+1,ny+1))
    
    for i in range(1,nx):
        for j in range(1,ny):
            xc[i,j] = 0.25*np.sum(x[i-1:i+1,j-1:j+1])
            yc[i,j] = 0.25*np.sum(y[i-1:i+1,j-1:j+1])

    for i in range(1,nx):
        xc[i,0] =  xc[i,1]  - 0.5*((x[i,1]-x[i,0])+ (x[i-1,1]-x[i-1,0]))
        xc[i,-1] = xc[i,-2] + 0.5*((x[i,-1]-x[i,-2]) + (x[i-1,-1]-x[i-1,-2]))
        yc[i,0] =  yc[i,1]  - 0.5*((y[i,1]-y[i,0])+ (y[i-1,1]-y[i-1,0]))
        yc[i,-1] = yc[i,-2] + 0.5*((y[i,-1]-y[i,-2]) + (y[i-1,-1]-y[i-1,-2]))

    for j in range(1,ny):
        xc[0,j]  = xc[1,j]   - 0.5*((x[1,j]-x[0,j]) + (x[1,j-1]-x[0,j-1]) )
        xc[-1,j] = xc[-2,j] + 0.5*((x[-1,j]-x[-2,j]) + (x[-1,j-1]-x[-2,j-1]) )
        yc[0,j]  = yc[1,j]   - 0.5*((y[1,j]-y[0,j]) + (y[1,j-1]-y[0,j-1]) )
        yc[-1,j] = yc[-2,j] + 0.5*((y[-1,j]-y[-2,j]) + (y[-1,j-1]-y[-2,j-1]) )

    xc[0,0] = xc[1,1] - (x[1,1]-x[0,0])
    yc[0,0] = yc[1,1] - (y[1,1]-y[0,0])
    xc[-1,-1] = xc[-2,-2] + (x[-1,-1]-x[-2,-2])
    yc[-1,-1] = yc[-2,-2] + (y[-1,-1]-y[-2,-2])
    xc[-1,0] = xc[-2,1]  - (x[-2,1]-x[-1,0])
    yc[-1,0] = yc[-2,1]  - (y[-2,1]-y[-1,0])
    xc[0,-1] = xc[1,-2]  + (x[-2,1]-x[-1,0])
    yc[0,-1] = yc[1,-2]  + (y[-2,1]-y[-1,0])

    return xc, yc


def makemap(lllat=-90.0,urlat=90.0,lllon=-180.0, urlon=180.0, dellon=10.0):

    m = Basemap(projection='cyl',llcrnrlat=lllat,urcrnrlat=urlat,\
                    llcrnrlon=lllon,urcrnrlon=urlon,resolution='l')

    m.drawcoastlines()
    m.drawstates()
    m.drawcountries()

# draw parallels.
    parallels = np.arange(lllat,urlat+dellon,dellon)
    m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10)

# draw meridians
    meridians = np.arange(lllon,urlon+dellon,dellon)
    m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10)

    return(m)


def plotswath(map, lats, lons, data, MISSING=-999.0, vmin=0.0, vmax=300.0):

    x, y = map(lons, lats) # compute map proj coordinates for pixel centers

    xc, yc = extrapcorners(x,y)  # interpolate/extrapolate corner boundaries of pixels

# plot data as overlayed color mesh
#    datam = ma.masked_where(np.isnan(data),data)

    datam = ma.masked_values(data, MISSING)
    cs = plt.pcolormesh(xc,yc,datam,rasterized=False, vmin=vmin, vmax=vmax)



# # create figure and axes instances
# fig = plt.figure(figsize=(8,8))
# fig.add_subplot(111)
# 
# # ax = fig.add_axes([0.1,0.1,0.8,0.8])
# 
# map = makemap(lllat = 20.0,urlat = 60.0,lllon = -100.0,urlon = -60.0, dellon=10.0)
# 
# lons = np.array([[-90., -88.0, -86.0 ], [-91.0, -89.0, -87.0]]) # pixel center location
# lats = np.array([[ 41. , 40.5, 40.0],  [ 43.0, 42.5, 42.0 ]])  
# data = np.array([[ 0.1, 5.0, 8.0], [ 8.0, 3.0, 6.0]] )
# 
# plotswath(map, lats,lons,data)
# 
# # draw filled contours.
# # clevs = [0,1,2.5,5,7.5,10,15,20,30,40,50,70,100,150,200,250,300,400,500,600,750]
# # cs = m.contourf(x,y,data,clevs,cmap=cm.s3pcpn)
# 
# # add title
# plt.title("Test Plot")
# 
# plt.savefig('satdemo.png')
# 
