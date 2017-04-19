#!/data/apps/enthought_python/2.7.3/bin/python

import numpy as np
import scipy.io
from datetime import date
from ClearCloud import ClearCloud

def BootstrapTest(oyscacld, ntimes):
	cld = scipy.io.loadmat('cloud_lib.mat')['cld']
	cldpct = scipy.io.loadmat('cloud_lib.mat')['cldpct']
	[nday, nr, nc] = oyscacld.shape
	pod = np.array([]).reshape(0,4).astype(np.float32)
	far = np.array([]).reshape(0,4).astype(np.float32)
	csi = np.array([]).reshape(0,4).astype(np.float32)
	for jk in range(ntimes):
		lowcldday = np.zeros((nday, nr, nc)).astype(np.uint8)
		medcldday = np.zeros((nday, nr, nc)).astype(np.uint8)
		highcldday = np.zeros((nday, nr, nc)).astype(np.uint8)
		sevcldday = np.zeros((nday, nr, nc)).astype(np.uint8)
		for i in range(nday):
			##Low cloud hindrance
			pctls = np.where((cldpct > 0.03) & (cldpct <= 0.05))[1]
			iii = np.random.randint(len(pctls),size=1)[0]
			lowcld = cld[:,:,pctls[iii]]
			lowcld1 = oyscacld[i,:,:]*2+lowcld
			lowcld1[lowcld1==3]=1
			lowcldday[i,:,:] = lowcld1
			##Med cloud hindrance
			pctls = np.where((cldpct > 0.07) & (cldpct <= 0.09))[1]
			iii = np.random.randint(len(pctls),size=1)[0]
			medcld = cld[:,:,pctls[iii]]
			medcld1 = oyscacld[i,:,:]*2+medcld
			medcld1[medcld1==3]=1
			medcldday[i,:,:] = medcld1
			##High cloud hindrance
			pctls = np.where((cldpct > 0.15) & (cldpct <= 0.2))[1]
			iii = np.random.randint(len(pctls),size=1)[0]
			highcld = cld[:,:,pctls[iii]]
			highcld1 = oyscacld[i,:,:]*2+highcld
			highcld1[highcld1==3]=1
			highcldday[i,:,:] = highcld1
			##Severe cloud hindrance
			pctls = np.where((cldpct > 0.2) & (cldpct <= 0.4))[1]
			iii = np.random.randint(len(pctls),size=1)[0]
			sevcld = cld[:,:,pctls[iii]]
			sevcld1 = oyscacld[i,:,:]*2+sevcld
			sevcld1[sevcld1==3]=1
			sevcldday[i,:,:] = sevcld1
		sca1 = ClearCloud(lowcldday, date(2009,9,9),date(2009,9,10), date(2009,9,15))
		sca2 = ClearCloud(medcldday, date(2009,9,9),date(2009,9,10), date(2009,9,15))
		sca3 = ClearCloud(highcldday, date(2009,9,9),date(2009,9,10), date(2009,9,15))
		sca4 = ClearCloud(sevcldday, date(2009,9,9),date(2009,9,10), date(2009,9,15))
		lowhit = np.sum(np.logical_and(oyscacld[2,:,:]==1, sca1[2,:,:]==1))
		lowmiss = np.sum(np.logical_and(oyscacld[2,:,:]==1, sca1[2,:,:]==0))
		lowfalse = np.sum(np.logical_and(oyscacld[2,:,:]==0, sca1[2,:,:]==1))
		medhit = np.sum(np.logical_and(oyscacld[2,:,:]==1, sca2[2,:,:]==1))
		medmiss = np.sum(np.logical_and(oyscacld[2,:,:]==1, sca2[2,:,:]==0))
		medfalse = np.sum(np.logical_and(oyscacld[2,:,:]==0, sca2[2,:,:]==1))
		highhit = np.sum(np.logical_and(oyscacld[2,:,:]==1, sca3[2,:,:]==1))
		highmiss = np.sum(np.logical_and(oyscacld[2,:,:]==1, sca3[2,:,:]==0))
		highfalse = np.sum(np.logical_and(oyscacld[2,:,:]==0, sca3[2,:,:]==1))
		sevhit = np.sum(np.logical_and(oyscacld[2,:,:]==1, sca4[2,:,:]==1))
		sevmiss = np.sum(np.logical_and(oyscacld[2,:,:]==1, sca4[2,:,:]==0))
		sevfalse = np.sum(np.logical_and(oyscacld[2,:,:]==0, sca4[2,:,:]==1))
		pod = np.vstack([pod, np.array([lowhit/float(lowhit+lowmiss),
										medhit/float(medhit+medmiss),
										highhit/float(highhit+highmiss),
										sevhit/float(sevhit+sevmiss)])])
		far = np.vstack([far, np.array([lowfalse/float(lowhit+lowfalse),
										medfalse/float(medhit+medfalse),
										highfalse/float(highhit+highfalse),
										sevfalse/float(sevhit+sevfalse)])])
		csi = np.vstack([csi, np.array([lowhit/float(lowhit+lowmiss+lowfalse),
										medhit/float(medhit+medmiss+medfalse),
										highhit/float(highhit+highmiss+highfalse),
										sevhit/float(sevhit+sevmiss+sevfalse)])])
	return pod, far, csi