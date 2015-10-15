# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import numpy as np

sfcclasses = ['0w', '1w', '1c', '2w', '2c', '3w', '3c', '4w', '4c', '5w', '5c', '6w', '6c']
dbdims = ['db0', 'db1', 'db2', 'db3']

dbbasename = '_class'
coeffbasename = 'pc_coeffs'
xmeanbasename = 'xmeans'

warmthresh = 275.0

dbaselocal = True
if dbaselocal:
    datapath = '/Users/gpetty/Dropbox/Public/UWALGO/DBASE/'
    print 'Loading databases locally... this will take a minute.'
    def customopen(fname):
        return(open(fname,'r'))

else:
    from urllib import URLopener
    datapath = 'https://dl.dropboxusercontent.com/u/1653737/UWALGO/DBASE/'
    print 'Loading databases from remote server ... this may take several minutes.'
    def customopen(fname):
        return(URLopener().open(fname))


# Initialize database


dbase_dict = {}
coeff_dict = {}
xmean_dict = {}

for cls in sfcclasses:   # Loop over classes
    print cls

    fname1 = datapath + coeffbasename +cls+'.dat'
    fname2 = datapath + xmeanbasename +cls+'.dat'

    f1 = customopen(fname1)
    f2 = customopen(fname2)

        
#    print 'Loading data from ',fname1
#    print 'Loading data from ',fname2

# load linear coefficients  and means needed for pseudochannel transformations
    tmpa = []
    for line in f1:
        columns = line.split()
        tmpa.append([float(c) for c in columns])    
            
    f1.close()        
    coeff_dict.update({cls : np.array(tmpa).T})

    tmpa = []
    for line in f2:
        columns = line.split()
        tmpa.append([float(c) for c in columns])    
            
    f2.close()        
    xmean_dict.update({cls : np.array(tmpa)[0]})
    

# load database entries
    dbase_dict.update({cls : {}})    
    for idim in range(4):
        dbd = 'db'+str(idim)
        dbase_dict[cls].update({dbd : {}})
        
        if dbaselocal:
            fname = datapath + dbbasename +cls+'.'+dbd
            f = open(fname, 'r')
        else:
            fname = datapath + dbbasename +cls+'.'+dbd
            f = URLopener().open(fname)
                
#        print 'Loading data from ',fname
        
        
        for line in f:
            columns = line.split()
            
            ic = int(columns[0])
            ikey = tuple([int(c) for c in columns[1:3+idim]])
            rr = float(columns[-17])
            fracs = [float(x) for x in columns[-16:]]
            dictentry = {'NCOUNT': ic, 'RR' : rr, 'FR' : fracs}
            dbase_dict[cls][dbd].update({ikey : dictentry}) 
            
        f.close()        

print 'Done loading databases.'
print

class landclassmap:
    def __init__(self):
        global dbaselocal
        global datapath
        
        fname = datapath + 'TRMM_classmap.dat'
        print 'Loading class map ',fname


        if dbaselocal:
            landclassmap.data = np.loadtxt(fname, dtype='int')[:,1]
        else:
            f = URLopener().open(fname)
            tmp = []
            for line in f:
                columns = line.split()
                tmp.append(int(columns[1]))

            f.close()        
            landclassmap.data = np.array(tmp)

        landclassmap.data = np.reshape(landclassmap.data, (-1, 360))
        print 'Class map loaded'      
        
    def getclass(self, loc):
        alat = loc[0]
        alon = loc[1]
        if alat <= -40.0 or alat >= 40.0:
            return(None)
        niter = 0
        while alon < -180.0:
            niter += 1
            alon += 360.0
            if niter > 3:
                return(None)
        while alon > 180.0:
            niter += 1
            alon -= 360.0
            if niter > 3:
                return(None)
    
        i = int(alat+40.0)
        j = int(alon+180.0)
        return(self.data[i,j])


LC = landclassmap()
#===============================
# Done with initializations        
#===============================



# <codecell>

def transform(iclass, tskin, tbs):
    global warmthresh

    if np.min(tbs) < 50.0:
        return(None, None)

    if tskin > warmthresh or iclass==0:
        suffix = 'w'
    else:
        suffix = 'c'
    cls = str(iclass) + suffix

    if cls == '0w' :
        if np.max(tbs) > tskin-3.0 :
            return(None,None)

        xo = np.log(tskin-tbs) - xmean_dict[cls]
        psch = np.dot(xo,coeff_dict[cls])[0:3]

    else:
        xl = tbs[2:]/tskin - xmean_dict[cls]
        psch = np.dot(xl,coeff_dict[cls])[0:3]

    return(psch, cls)


def getkey(tskin, tcwv, psch):

    global warmthresh
    
    if psch == None:
        return(None)
    
# Convert pseudochannel values to indices into database

    sig = 15.0 
    it1 = int(50.0 + np.arctan(psch[0]/sig)*sig) - 27  
    it2 = int(50.0 + np.arctan(psch[1]/sig)*sig) - 27  
    it3 = int(50.0 + np.arctan(psch[2]/sig)*sig) - 27

    if tskin > warmthresh:
        iskint = int(tskin/5.0) -54          #   1 - 11
    else:
        iskint = int(tskin/5.0) -43          #   1 - 11

  
    iwv = int(tcwv/10.0) + 1              #   1 - 9                 

    return(it1, it2, it3, iskint, iwv)


def retrieve(sfcclass, k3):
    if k3 == None:
        return(None)
    
#    print
#    print '---- next case ---'
    for ndim in range(3,-1,-1):
#        print ndim
        kp = k3[0:ndim]+k3[-2:]
#        print kp
#        print sfcclass, dbdims[ndim]
        entry = dbase_dict[sfcclass][dbdims[ndim]].get(kp)
        if entry:
#            print 'Valid entry found'
            entry.update({'NDIM': ndim})
            return(entry)

    return(None)
    
def algo(latlon,tskin,tcwv,tbs,idim):
    global LC
    
    iclass = LC.getclass(latlon)
        
    psch, cls = transform(iclass, tskin, tbs)
    key3 = getkey(tskin, tcwv, psch)
    if key3 == None:
        return(None, None)
    
    negones = np.ones(3-idim)
    negones = tuple(-np.ones(3-idim).astype(int))
    key = key3[0:idim] + negones + key3[-2:]
    rrtmi = retrieve(cls, key)
    return(rrtmi, cls)


# <codecell>

