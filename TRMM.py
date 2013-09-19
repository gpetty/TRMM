import sys
import os.path
import time
import datetime
import commands
from pyhdf.SD import SD, SDC
import numpy as np
from StringIO import StringIO

# For Macs:
LOCALMACHINEROOT = "/Volumes" 
#For Linux machines:
# LOCALMACHINEROOT = "" 

MISSINGVAL = -999.9

TRMMroot = LOCALMACHINEROOT + "/data2b/TRMM"
TMIroot =  TRMMroot + "/TMI"
PRroot =  TRMMroot + "/PR"
TMIHDFroot = TMIroot + "/HDF/"
PRHDFroot = PRroot + "/HDF/"
TMIindexpath = TMIroot + "/1B11.index"
PRindexpath = PRroot + "/2A25.index"

class orbitloc:
  pass

# Declare dictionaries for TMI and PR indexes
tmiorb = {}
prorb = {}
  
default = orbitloc()
default.orbitno = -999
default.path = ""
default.localpath = ""
default.startdatetime = ""
default.enddatetime = ""
default.startepochsec = 0.0
default.endepochsec = 0.0
default.slat = MISSINGVAL
default.exists = False

# load edge coordinate file for TMI orbits
TMIedgefile = TMIroot + "/TMIedges.txt"
TMIedges = np.fromfile(TMIedgefile, dtype=float, count=-1, sep=' ')
TMIedges = np.reshape(TMIedges, (len(TMIedges)/4,2,2))

# Load resolution matching coefficients for TMI
#
def readin_weigh(filename, res,alt='PREBOOST'):
  if res == 'LO':
    NPIX = 99 - 6 + 1
  elif res == 'HI':
    NPIX = 203 - 6 + 1
  else:
    print 'res = ',res
    raise IOError('In TRMM.readin_weigh: res must equal HI or LO')
    
#  print filename
  f = open(filename, 'r')

# Skip appropriate number of lines at the beginning  
  if alt == 'PREBOOST':
    for i in range(2):
      f.readline()
  else:
    for i in range(4):
      f.readline()
    
  weigh = []

# Loop over pixels
  for line in range(NPIX):

# Skip over appropriate additional number of lines
    if alt == 'PREBOOST':
      for i in range(5):
        f.readline()
    else:
      for i in range(7):
        f.readline()

    arr = []
    for ii in range(11):
      line = f.readline()
      data = np.genfromtxt(StringIO(line), delimiter = 20)[0:11]
      arr.append(data)
    norm = np.array(arr)/np.sum(arr)
    weigh.append(norm)
    del(arr)
  f.close()
  return weigh
   
CoefDir = '/Volumes/data2b/TRMM/TMI/'

w10vpre = readin_weigh(CoefDir+'BG_COEF_10V_TO_19_TMI_PREBOOST.TXT', 'LO', 'PREBOOST')
w10hpre = readin_weigh(CoefDir+'BG_COEF_10H_TO_19_TMI_PREBOOST.TXT', 'LO', 'PREBOOST')
w21vpre = readin_weigh(CoefDir+'BG_COEF_21_TO_19_TMI_PREBOOST.TXT' , 'LO', 'PREBOOST')
w37vpre = readin_weigh(CoefDir+'BG_COEF_37V_TO_19_TMI_PREBOOST.TXT', 'LO', 'PREBOOST')
w37hpre = readin_weigh(CoefDir+'BG_COEF_37H_TO_19_TMI_PREBOOST.TXT', 'LO', 'PREBOOST')
w85vpre = readin_weigh(CoefDir+'BG_COEF_85V_TO_19_TMI_PREBOOST.TXT', 'HI', 'PREBOOST')
w85hpre = readin_weigh(CoefDir+'BG_COEF_85H_TO_19_TMI_PREBOOST.TXT', 'HI', 'PREBOOST')

#  IGNORE THE POST-BOOST FILES FOR NOW
# w10vpost = readin_weigh(CoefDir+'BG_COEF_1065V_TO_1935H_TMI_POSTB.TXT', 'LO', 'POSTBOOST')
# w10hpost = readin_weigh(CoefDir+'BG_COEF_1065H_TO_1935H_TMI_POSTB.TXT', 'LO', 'POSTBOOST')
# w21vpost = readin_weigh(CoefDir+'BG_COEF_213V_TO_1935H_TMI_POSTB.TXT', 'LO', 'POSTBOOST')
# w37vpost = readin_weigh(CoefDir+'BG_COEF_370V_TO_1935H_TMI_POSTB.TXT', 'LO', 'POSTBOOST')
# w37hpost = readin_weigh(CoefDir+'BG_COEF_370H_TO_1935H_TMI_POSTB.TXT', 'LO', 'POSTBOOST')
# w85vpost = readin_weigh(CoefDir+'BG_COEF_855V_TO_1935H_TMI_POSTB.TXT', 'HI', 'POSTBOOST')
# w85hpost = readin_weigh(CoefDir+'BG_COEF_855H_TO_1935H_TMI_POSTB.TXT', 'HI', 'POSTBOOST')

def initindex(indexpath, orb):
  findex = open(indexpath)
  try:
    for line in findex:
      line = line.rstrip('\n')

      HDFpath = line[0:line.index(".HDF")+4]
      basename = HDFpath[-25:]
      iorbit = int(basename[14:19])

      slat = float(line[-10:-2])

      startdatetime = line[line.index(".HDF")+5:line.index(".HDF")+28]
      startfracsec = 0.001*int(startdatetime[-3:])
      startepochsec = time.mktime(time.strptime(startdatetime[0:19],"%Y-%m-%d %H:%M:%S"))+startfracsec

      enddatetime = line[line.index(".HDF")+29:line.index(".HDF")+52]
      endfracsec = 0.001*int(enddatetime[-3:])
      endepochsec = time.mktime(time.strptime(enddatetime[0:19],"%Y-%m-%d %H:%M:%S"))+endfracsec

      tmporbit = orbitloc()
      tmporbit.orbitno = iorbit
      tmporbit.localpath = HDFpath
      tmporbit.path = HDFpath
      tmporbit.startdatetime = datetime.datetime.fromtimestamp(startepochsec)
      tmporbit.enddatetime = datetime.datetime.fromtimestamp(endepochsec)
      tmporbit.startepochsec = startepochsec
      tmporbit.endepochsec = endepochsec
      tmporbit.slat = slat
      tmporbit.exists = True
    


#       print tmporbit.orbitno
#       print tmporbit.localpath
#       print tmporbit.path
#       print tmporbit.startdatetime
#       print tmporbit.enddatetime
#       print tmporbit.startepochsec
#       print tmporbit.endepochsec
#       print tmporbit.slat
#       print tmporbit.exists


      orb[iorbit] = tmporbit
  except:
    print 'Error in initindex: ',indexpath,orb
  finally:
    findex.close
  return

initindex(TMIindexpath, tmiorb)  
initindex(PRindexpath, prorb)  

def orbitquery(orbitno,orb):
  iorbitno = int(orbitno)
  result = orb.get(iorbitno,default)
  return result

def TMIquery(orbitno):
# retrieve basic parameters from index file
  result = orbitquery(orbitno,tmiorb)

# construct associated swath boundaries
  edges = []
  for i in range(len(TMIedges)):
    alat0, alon0 = TMIedges[i][0]
    alat1, alon1 = TMIedges[i][1]
    alon0 += result.slat
    alon1 += result.slat
    if alon0 <= -180.0:
      alon0 += 360.0
    if alon0 > 180.0:
      alon0 -= 360.0
    if alon1 <= -180.0:
      alon1 += 360.0
    if alon1 > 180.0:
      alon1 -= 360.0
    edges.append(((alat0,alon0), (alat1,alon1)))
  result.edges = edges
  return result

def PRquery(orbitno):
  return orbitquery(orbitno,prorb)


def orbitfetch(orbitno,sensor):
  # get orbit info

  if sensor=="TMI":
    orbitinfo = TMIquery(orbitno)
    HDFroot = TMIHDFroot
    remotesubdir = "TRMM_L1/TRMM_1B11/"
    filesuffix = ""
  elif sensor=="PR":
    orbitinfo = PRquery(orbitno)
    HDFroot = PRHDFroot
    remotesubdir = "TRMM_L2/TRMM_2A25/"
    filesuffix = ".Z"
  else:
    return default

  # check whether orbit exists
  if not orbitinfo.exists:
    return orbitinfo

  # check whether file already exists on local server, including
  # possible compressed forms

  localcopy = os.path.exists(orbitinfo.localpath)
  if localcopy:
    return orbitinfo

  localcopy = os.path.exists(orbitinfo.localpath+".Z")
  if localcopy:
    orbitinfo.localpath = orbitinfo.localpath+".Z"
    return orbitinfo

  localcopy = os.path.exists(orbitinfo.localpath+".gz")
  if localcopy:
    orbitinfo.localpath = orbitinfo.localpath+".gz"
    return orbitinfo

  
  # if it does not, fetch it from NASA server

  # FUTURE: First check for sufficient space; delete oldest files if
  # needed to make space
  # /FUtURE

  #get filename and relative path
  orbitpath = orbitinfo.localpath
#  print 'orbitpath ',orbitpath
  relpath = orbitpath[len(HDFroot):]
#  print 'relpath ',relpath
  subdir = relpath[0:9]
#  print 'subdir ',subdir
  subdir1 = relpath[0:4]
#  print 'subdir1 ',subdir1
  fname = relpath[len(subdir):]
#  print 'fname ',fname

  # create target subdirectories, if needed
  targetdir1 = HDFroot + subdir1
#  print "targetdir1 ",targetdir1 
  if not os.path.exists(targetdir1):
    comstring = 'mkdir ' + targetdir1
#    print comstring
    commands.getoutput(comstring)
    comstring = 'chmod a+rwx ' + targetdir1
#    print comstring
    commands.getoutput(comstring)

  targetdir2 = HDFroot + subdir
#  print 'targetdir2 ',targetdir2
  if not os.path.exists(targetdir2):
    comstring = 'mkdir ' + targetdir2
#    print comstring
    commands.getoutput(comstring)
    comstring = 'chmod a+rwx ' + targetdir2
#    print comstring
    commands.getoutput(comstring)
#  relpath = relpath[8:] + filesuffix
  relpath = relpath + filesuffix
#  print 'relpath ',relpath
  comstring = '/sw/bin/lftp -c "user anonymous gwpetty@wisc.edu ; get ftp://disc2.nascom.nasa.gov/ftp/data/s4pa/'+ remotesubdir + relpath + ' -o ' + HDFroot + relpath +'"'
#  print comstring
  commands.getoutput(comstring)


  # check for all possible variations on local filename
  localcopy = os.path.exists(orbitinfo.localpath)
  if localcopy:
    return orbitinfo

  localcopy = os.path.exists(orbitinfo.localpath+".Z")
  if localcopy:
    orbitinfo.localpath = orbitinfo.localpath+".Z"
    return orbitinfo

  localcopy = os.path.exists(orbitinfo.localpath+".gz")
  if localcopy:
    orbitinfo.localpath = orbitinfo.localpath+".gz"
    return orbitinfo

  return default


def TMIfetch(orbitno):
  return orbitfetch(orbitno,"TMI")

def PRfetch(orbitno):
  return orbitfetch(orbitno,"PR")

class TMIorbit:
  def __init__(self,filename):

#  "/Volumes/data2b/TRMM/TMI/HDF/2001/237/1B11.20010825.21545.7.HDF"
    words1 = filename.split('/')
#    print words1
    words2 = words1[-1].split('.')
#    print words2
    self.orbitno = int(words2[2])
#    print 'self.orbitno =',self.orbitno

    TMI_SDS = SD(filename, SDC.READ)   
#        print dir(TMI_SDS)
#        print TMI_SDS.datasets()

    tempb = TMI_SDS.select('lowResCh')  # get all low-res channels
    tempb = np.array(tempb[:])              # convert to arrays
    tempb = (tempb/100.0) + 100.0           # convert to physical units
    self.t10v = tempb[:, :, 0] 
    self.t10h = tempb[:, :, 1]
    self.t19v = tempb[:, :, 2]
    self.t19h = tempb[:, :, 3]
    self.t21v = tempb[:, :, 4]
    self.t37v = tempb[:, :, 5]
    self.t37h = tempb[:, :, 6]

    tempb = TMI_SDS.select('highResCh')  # get all hi-res channels
    tempb = np.array(tempb[:])                # convert to arrays
    tempb = (tempb/100.0) + 100.0             # convert to physical units
    self.t85v = tempb[:, :, 0]
    self.t85h = tempb[:, :, 1]

    lat_hi = TMI_SDS.select('Latitude')
    lon_hi = TMI_SDS.select('Longitude')
    self.lat_hi = np.array(lat_hi[:])
    self.lon_hi = np.array(lon_hi[:])
    ihi, jhi = self.lat_hi.shape    
    lat_lo = lat_hi[:, 0:jhi:2]
    lon_lo = lon_hi[:, 0:jhi:2]
    self.lat_lo = np.array(lat_lo[:])
    self.lon_lo = np.array(lon_lo[:])

    Year = TMI_SDS.select('Year')
    self.Year = np.array(Year[:])
    Month = TMI_SDS.select('Month')
    self.Month = np.array(Month[:])
    DayOfMonth = TMI_SDS.select('DayOfMonth')
    self.DayOfMonth = np.array(DayOfMonth[:])
    DayOfYear = TMI_SDS.select('DayOfYear')
    self.DayOfYear = np.array(DayOfYear[:])
    Hour = TMI_SDS.select('Hour')
    self.Hour = np.array(Hour[:])
    Minute = TMI_SDS.select('Minute')
    self.Minute = np.array(Minute[:])
    Second = TMI_SDS.select('Second')
    self.Second = np.array(Second[:])
    MilliSecond = TMI_SDS.select('MilliSecond')
    self.MilliSecond = np.array(MilliSecond[:])
    
    validity = TMI_SDS.select('validity')
    self.validity = np.array(validity[:])

    geoqual = TMI_SDS.select('geoQuality')
    self.geoqual = np.array(geoqual[:])

    missing = TMI_SDS.select('missing')
    self.missing = np.array(missing[:])

    dataqual = TMI_SDS.select('dataQuality')
    self.dataqual = np.array(dataqual[:])
#    self.flag =  (self.missing == 0.0) & (self.validity == 0.0) & (self.geoqual == 0.0) & (self.dataqual == 0.0)
    self.flag =  (self.missing == 0.0) 

    scori = TMI_SDS.select('SCorientation')
    self.scori = np.array(scori[:])
    TMI_SDS.end()

  def match19(self):
    PREBOOST = self.orbitno < (21260+21541)/2
    if PREBOOST == True:
      w10v = w10vpre
      w10h = w10hpre
      w21v = w21vpre
      w37v = w37vpre
      w37h = w37hpre
      w85v = w85vpre
      w85h = w85hpre
    else:
#       w10v = w10vpost
#       w10h = w10hpost
#       w21v = w21vpost
#       w37v = w37vpost
#       w37h = w37hpost
#       w85v = w85vpost
#       w85h = w85hpost
      w10v = w10vpre
      w10h = w10hpre
      w21v = w21vpre
      w37v = w37vpre
      w37h = w37hpre
      w85v = w85vpre
      w85h = w85hpre

    [M, N] = self.t10v.shape

    if np.abs(self.scori[0]-self.scori[M-1]) > 2 :
      raise IOError('orbit changes directions!')
    elif np.abs(self.scori[0] - 180) < 5 :
      co10v = np.flipud(w10v)
      co10h = np.flipud(w10h)
      co21v = np.flipud(w21v)
      co37v = np.flipud(w37v)
      co37h = np.flipud(w37h)
      co85v = np.flipud(w85v)
      co85h = np.flipud(w85h)
    elif np.abs(self.scori[0]) < 5 :
      co10v = w10v
      co10h = w10h
      co21v = w21v
      co37v = w37v
      co37h = w37h
      co85v = w85v
      co85h = w85h
    else:
      print "SCORI = ",self.scori[0], self.scori[M-1]
      raise IOError('orbit has non-standard orientation!')

    mt10v = np.zeros((M, N))
    mt10h = np.zeros((M, N))
    mt19v = np.zeros((M, N))
    mt19h = np.zeros((M, N))
    mt21v = np.zeros((M, N))
    mt37v = np.zeros((M, N))
    mt37h = np.zeros((M, N))
    mt85v = np.zeros((M, N))
    mt85h = np.zeros((M, N))
    for scan in range(M):
      for pixel in range(N):
        if (not self.flag[scan]): # calculate it at least when the center data is valid
          mt10v[scan, pixel] = MISSINGVAL
          mt10h[scan, pixel] = MISSINGVAL
          mt19v[scan, pixel] = MISSINGVAL
          mt19h[scan, pixel] = MISSINGVAL
          mt21v[scan, pixel] = MISSINGVAL
          mt37v[scan, pixel] = MISSINGVAL
          mt37h[scan, pixel] = MISSINGVAL
          mt85v[scan, pixel] = MISSINGVAL
          mt85h[scan, pixel] = MISSINGVAL
        elif (scan<5)|(scan>M-6)|(pixel<5)|(pixel>N-6): # no edges
          mt10v[scan, pixel] = MISSINGVAL
          mt10h[scan, pixel] = MISSINGVAL
          mt19v[scan, pixel] = MISSINGVAL
          mt19h[scan, pixel] = MISSINGVAL                    
          mt21v[scan, pixel] = MISSINGVAL
          mt37v[scan, pixel] = MISSINGVAL
          mt37h[scan, pixel] = MISSINGVAL
          mt85v[scan, pixel] = MISSINGVAL
          mt85h[scan, pixel] = MISSINGVAL
        elif (sum(self.flag[scan-5: scan+6]) < 11): # every single data in the pool should be valid
          mt10v[scan, pixel] = MISSINGVAL
          mt10h[scan, pixel] = MISSINGVAL
          mt19v[scan, pixel] = MISSINGVAL
          mt19h[scan, pixel] = MISSINGVAL
          mt21v[scan, pixel] = MISSINGVAL
          mt37v[scan, pixel] = MISSINGVAL
          mt37h[scan, pixel] = MISSINGVAL
          mt85v[scan, pixel] = MISSINGVAL
          mt85h[scan, pixel] = MISSINGVAL
        else:
          mt10v[scan,pixel] = np.sum(self.t10v[scan-5: scan+6, pixel-5:pixel+6]*co10v[pixel - 5])
          mt10h[scan,pixel] = np.sum(self.t10h[scan-5: scan+6, pixel-5:pixel+6]*co10h[pixel - 5])
          mt19v[scan,pixel] = self.t19v[scan, pixel]
          mt19h[scan,pixel] = self.t19h[scan, pixel]
          mt21v[scan,pixel] = np.sum(self.t21v[scan-5: scan+6, pixel-5:pixel+6]*co21v[pixel - 5])
          mt37v[scan,pixel] = np.sum(self.t37v[scan-5: scan+6, pixel-5:pixel+6]*co37v[pixel - 5])
          mt37h[scan,pixel] = np.sum(self.t37h[scan-5: scan+6, pixel-5:pixel+6]*co37h[pixel - 5])
          mt85v[scan,pixel] = np.sum(self.t85v[scan-5: scan+6, 2*pixel-5:2*pixel+6]*co85v[2*pixel - 5])
          mt85h[scan,pixel] = np.sum(self.t85h[scan-5: scan+6, 2*pixel-5:2*pixel+6]*co85h[2*pixel - 5])

    return mt10v, mt10h, mt19v, mt19h, mt21v, mt37v, mt37h, mt85v, mt85h

