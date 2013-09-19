import numpy as np

datapath = '/Users/gpetty/Dropbox/Public/UWALGO/DBASE/'
dataurl = 'https://dl.dropboxusercontent.com/u/1653737/UWALGO/DBASE/'

sfcclasses = ['0w', '1w', '1c', '2w', '2c', '3w', '3c', '4w', '4c', '5w', '5c', '6w', '6c']
dbdims = ['db0', 'db1', 'db2', 'db3']

dbbasename = '_class'
coeffbasename = 'pc_coeffs'
xmeanbasename = 'xmeans'

dbaselocal = False
if not dbaselocal:
    from urllib import URLopener


# Initialize database

dbase_dict = {}
coeff_dict = {}
xmean_dict = {}

for cls in sfcclasses:   # Loop over classes
    print cls
    
    if dbaselocal:
        fname1 = datapath + coeffbasename +cls+'.dat'
        f1 = open(fname1, 'r')
        fname2 = datapath + xmeanbasename +cls+'.dat'
        f2 = open(fname2, 'r')
    else:
        fname1 = dataurl + coeffbasename +cls+'.dat'
        f1 = URLopener().open(fname1)            
        fname2 = dataurl + xmeanbasename +cls+'.dat'
        f2 = URLopener().open(fname2)            
    print 'Loading data from ',fname1
    print 'Loading data from ',fname2

# load linear coefficients  and means needed for pseudochannel transformations
    tmpa = []
    for line in f1:
        columns = line.split()
        tmpa.append([float(c) for c in columns])    
            
    f1.close()        
    coeff_dict.update({cls : np.array(tmpa)})

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
            fname = dataurl + dbbasename +cls+'.'+dbd
            f = URLopener().open(fname)
                
        print 'Loading data from ',fname
        
        
        for line in f:
            columns = line.split()
            
            ic = int(columns[0])
            ikey = tuple([int(c) for c in columns[1:3+idim]])
            rr = float(columns[-17])
            fracs = [float(x) for x in columns[-16:]]
            dictentry = {'NCOUNT': ic, 'RR' : rr, 'FR' : fracs}
            dbase_dict[cls][dbd].update({ikey : dictentry}) 
            
        f.close()        
    
#===============================
# Done with initializations        
#===============================


def transform(iclass, tskin, tbs):

    iwarm = tskin > 275.0

    if np.min(tbs) < 50.0:
        return(NaN)

    if iclass == 0:
        cls = '0w'

        if np.max(tbs) > tskin-3.0 :
            return(NaN)

        xo = np.log(tskin-tbs) - xmean_dict[cls]
        psch = np.dot(xo,coeff_dict[cls])[0:3]

    else:
        cls = str(iclass)
        if iwarm:
            cls = cls + 'w'
        else:
            cls = cls + 'c'

        xl = tbs[2:]/tskin - xmean_dict[cls]
        psch = np.dot(xl,coeff_dict[cls])

    return(psch)


def getkey(tskin, iwv, psch):

# Convert pseudochannel values to indices into database

    sig = 15.0 
    it1 = int(50.0 + np.atan(psch[0]/sig)*sig) - 27  
    it2 = int(50.0 + np.atan(psch[1]/sig)*sig) - 27  
    it3 = int(50.0 + np.atan(psch[2]/sig)*sig) - 27

    if iwarm == True:
        iskint = int(tskin/5.0) -54          #   1 - 11
    else:
        iskint = int(tskin/5.0) -43          #   1 - 11

  
    iwv = tcwv/10.0 + 1              #   1 - 9                 

    return(it1, it2, it3, iskint, iwv)


def retrieve(sfcclass, k3):
    print
    print '---- next case ---'
    for ndim in range(3,-1,-1):
        print ndim
        kp = k3[0:ndim]+k3[-2:]
        print kp
        print sfcclass, dbdims[ndim]
        entry = dbase_dict[sfcclass][dbdims[ndim]].get(kp)
        if entry:
            print 'Valid entry found'
            entry.update({'NDIM': ndim})
            return(entry)

    return(None)
    
    


f = open("test.out","r")
f.readline()

for line in f.readline():
    cols = line.split()
    iclass = int(cols[0])
    tskin = float(cols[1])
    tcwv = float(cols[2])
    tbs = float(np.array(cols[3:12]))
    pc0 = float(np.array(cols[12:15]))
    iwarm = int(cols[15])
    rrpr = float(cols[16])

    print line
    print iclass,tskin,tcwv,tbs,pc0,iwarm,rrpr
    print

f.close()

