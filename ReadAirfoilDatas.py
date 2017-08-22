#!/usr/bin/env python

from __future__ import print_function

print("Start   " + __file__)

TAB     = r"\t"
NEWLINE = r"\n"

import sys
if sys.version_info.major <= 2 :
    import urllib2 as urllib
else:
    import urllib.request as urllib
    #x = urllib.request.urlopen('https://www.google.com/')
    #print(x.read())

import numpy as np
#from scipy import misc
import matplotlib.pyplot as plt

URL = "http://www.airfoildb.com/airfoils"

def readFileAtUrl(url, localFileName):  
    #read urls and store file in local
    
    print("urlopen(%s)"%url)
    usock = urllib.urlopen(url)
    
    print("local file open for write :", localFileName)
    localFile = open(localFileName, "w")
    
    localFile.write(usock.read())
    localFile.close()
    usock.close()

def openAirFoilDatas(foilcode):
    localfoilFileName = foilcode + ".foil"
    try:
        foilFile = open(localfoilFileName,"r")
    except:
        foilUrl  = URL + "/%s.dat"%foilcode
        readFileAtUrl(foilUrl, localfoilFileName)
        foilFile = open(localfoilFileName,"r")
    
    localPolarFileName = foilcode + ".polar"
    try:
        polarFile = open(localPolarFileName,"r")
    except:
        polarUrl = URL + "/getpolar/%s.dat"%foilcode
        readFileAtUrl(polarUrl, localPolarFileName)
        polarFile = open(localPolarFileName,"r")
        
    return foilFile, polarFile
    
#-----------------------------------------------------------
    
#foilcode = "1295" # Eppler385
foilcode = "1301" # Eppler374

foilFile, polarFile = openAirFoilDatas(foilcode)
  
#---------------- Analyses profil datas ---------------------

print("reading foil datas ...")
lineIn = foilFile.readline()
FoilName = lineIn.rstrip()
print("FoilName :", FoilName)

Xl = list()
Yl = list()

for lineIn in foilFile:
    line = lineIn.rstrip()
    if len(line) == 0 : break
    
    #print(line)
    sx, sy = line.split(',')
    Xl.append(float(sx))
    Yl.append(float(sy))
    
Xs = np.array(Xl, dtype=np.float)
Ys = np.array(Yl, dtype=np.float)

foilFile.close()    

f1 = plt.figure()#(figsize=(8, 6))
plt.suptitle(FoilName)

ax0 = plt.subplot2grid((3, 2), (0, 0), colspan=2)
plt.title('Airfoil')
ax0.plot(Xs, Ys, '.-')
ax0.axis('equal')
#plt.axis((0.0,1.0,-0.1,0.2))
ax0.grid()
if 0:
    plt.show()
    quit()
#------------------------ Analyses polars datas ---------------------------
print("reading polars datas ...")

Reynolds = np.zeros(4, dtype=np.float)
Alphas = np.arange(-15, 15.5, 0.5, dtype=np.float)

n_alpha    = Alphas  .shape[0]
n_reynolds = Reynolds.shape[0]

Cls    = np.zeros((n_alpha,n_reynolds), dtype=np.float) 
Cds    = np.zeros((n_alpha,n_reynolds), dtype=np.float) 
Cms    = np.zeros((n_alpha,n_reynolds), dtype=np.float) 

class PolarFileReader:
    def __init__(self, polarFile):
        rawTxt = polarFile.read()
        polarFile.close()
        self.lines = rawTxt.split(NEWLINE)
        print("%3d lines read"%(len(self.lines)))
        self.idx = 0
        
    def readline(self):
        line = self.lines[self.idx]
        self.idx += 1
        return line
    
pfr =  PolarFileReader(polarFile)   
    
for r in range(n_reynolds) :

    lineIn = pfr.readline()
    line = lineIn.rstrip('\n')
    name, val = line.split('=')
    Name = name.strip()
    valUp = val.strip().upper()
    assert FoilName == valUp , "%s <> %s"%(FoilName, valUp)
    #print name, '=', FoilName

    lineIn = pfr.readline()
    line = lineIn.rstrip('\n')
    fields = line.split(';')
    name , val = fields[1].split('=')
    Name     = name.strip()
    Reynolds[r] = float(val) 
    print(Name, '=', Reynolds[r])

    lineIn = pfr.readline()
    line = lineIn.rstrip('\n')
    print(line)

    lineIn = pfr.readline()
    line = lineIn.rstrip('\n')
    columnTitles = line.split(TAB)
    s = ""
    for t in columnTitles : s += str(t)
    print(s)

    lineIn = pfr.readline()

    for n in range(61) :
        lineIn = pfr.readline()
        line = lineIn.rstrip('\n')
        columns = line.split(TAB)
        assert Alphas[n] == float(columns[0])
        Cls   [n,r] = float(columns[1])
        Cds   [n,r] = float(columns[2])
        Cms   [n,r] = float(columns[3])
        #print(Alphas[n], Cls[n], Cds[n], Cms[n])
        
    lineIn = pfr.readline() # blank line
    print

#-----------------------------------------------------

#f2 = plt.figure()

#plt.subplot(221)
ax1 = plt.subplot2grid((3, 2), (1, 0))
plt.title('Lift')
ax1.plot(Alphas, Cls, '.-')
ax1.axis((-15.0,15.0,-1.5,1.5))
ax1.grid()

#plt.subplot(223)
ax2 = plt.subplot2grid((3, 2), (2, 0))
plt.title('Drag')
ax2.plot(Alphas, Cds, '.-')
ax2.axis((-15.0,15.0,0.0,0.25))
ax2.grid()

#plt.subplot(224)
ax3 = plt.subplot2grid((3, 2), (2, 1))
plt.title('Moment')
ax3.plot(Alphas, Cms, '.-')
ax3.grid()

#plt.subplot(222)
ax4 = plt.subplot2grid((3, 2), (1, 1))
plt.title('Polaire')
ax4.plot(Cds, Cls, '.-')
ax4.axis((0.0,0.25,-1.5,1.5))
ax4.grid()

plt.show()

print("End   " + __file__)
