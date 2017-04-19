#!/data/apps/enthought_python/2.7.3/bin/python

import numpy as np
import scipy.ndimage.morphology as ndimage
from skimage.morphology import rectangle
from copy import deepcopy

def filterseriesall(oyscacld0, sizey, sizen, sizec):
	[nday, nr, nc] = oyscacld0.shape
	oyscacldl = oyscacld0.swapaxes(1,2).reshape(oyscacld0.shape[0], -1)
	[nday, npix] = oyscacldl.shape
	oyscacldl = oyscacldl.astype(np.int8)
	oyscacldl2 = deepcopy(oyscacldl)
	oyscacldyl = 1*(oyscacldl >=1)
	oyscacldyl2 = np.vstack((np.zeros((1, npix)), oyscacldyl, np.zeros((1, npix))))
	oyscacldnl = 1*(oyscacldl <=1)
	oyscacldnl2 = np.vstack((np.zeros((1, npix)), oyscacldnl, np.zeros((1, npix))))
	oyscacldcl = 1*(oyscacldl ==1)
	oyscacldcl2 = np.vstack((np.zeros((1, npix)), oyscacldcl, np.zeros((1, npix))))
	ccc = ndimage.binary_hit_or_miss(oyscacldcl2, np.ones((sizec,1)))
	se = rectangle(sizec, 1)
	ccc = ndimage.binary_dilation(ccc, se)*1
	ccc = ccc[1:-1,:]
	
	yyy = ndimage.binary_hit_or_miss(oyscacldyl2, np.ones((sizey,1)))
	se = rectangle(sizey, 1)
	yyy = ndimage.binary_dilation(yyy, se)*1
	yyy = yyy[1:-1,:]
	yyy = yyy & 1*(ccc == 0)
	oyscacldl2[yyy==1] = 2
	
	nnn = ndimage.binary_hit_or_miss(oyscacldnl2, np.ones((sizen,1)))
	se = rectangle(sizen, 1)
	nnn = ndimage.binary_dilation(nnn, se)*1
	nnn = nnn[1:-1,:]
	nnn = nnn & 1*(ccc == 0)
	oyscacldl2[nnn==1] = 0
	oyscacldl2[(np.logical_and(yyy==1, nnn==1))] = 1
	oyscacld = oyscacldl2.reshape(nday, nr, nc, order='F')
	return oyscacld