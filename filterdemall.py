#!/data/apps/enthought_python/2.7.3/bin/python

import numpy as np
import ctypes
import logging
import datetime
import time
import multiprocessing as mp
from multiprocessing import Manager
from contextlib import closing
from copy import deepcopy

def filterdemall(scacld, dem):
	try:
		[n, nr, nc] = scacld.shape
	except:
		n = 1
		[nr, nc] = scacld.shape
	N = n*nr*nc
	oyscacld = mp.Array(ctypes.c_long, N)
	arr = tonumpyarray(oyscacld)
	arr[:] = scacld.flat
	with closing(mp.Pool(initializer=init, initargs=(oyscacld, nr, nc, dem,))) as p:
        # many processes access different slices of the same array
		p.map_async(filterdem, range(n))
	p.join()
	result = tonumpyarray(oyscacld)
	scacldf = result.astype(np.int8)
	return scacldf.reshape(n, nr, nc)

def init(oyscacld_, nr1, nc1, dem_):
	global oyscacld, nr, nc, dem
	oyscacld = oyscacld_ # must be inhereted, not passed as an argument
	nr = nr1
	nc = nc1
	dem = dem_

def tonumpyarray(mp_arr):
    return np.frombuffer(mp_arr.get_obj())

def filterdem(i):
	arr0 = tonumpyarray(oyscacld)
	arr1 = dem.copy()
	scacld1 = arr0[nr*nc*i:nr*nc*(i+1)].reshape(nr, nc)
	scacld1 = scacld1.astype(np.int8)
	[rr, cc] = scacld1.shape
	[nr1, nc1] = np.where(scacld1 == 1)
	scacldf = deepcopy(scacld1)
	[nr1, nc1] = zip(*sorted(zip(nr1,nc1)))
	for j in range(len(nr1)):
		nci = nc1[j]
		nri = nr1[j]
		if nri == 0 or nri == rr-1:
			continue
		if nci == 0 or nci == cc-1:
			continue
		datai = scacld1[nri-1:nri+2, nci-1:nci+2]
		datai = datai.flatten('F')
		datai_1 = np.delete(datai, 4)
		demi = arr1[nri-1:nri+2, nci-1:nci+2]
		demi = demi.flatten('F')
		dem0 = demi[4]
		demi_1 = np.delete(demi, 4)
		if sum(1*(datai_1==1)) > 4:
			continue
		if np.any(demi_1[np.where(datai_1 == 2)]):
			minsdem = min([demi_1[x] for x in np.where(datai_1 == 2)[0]])
		else:
			minsdem = 9999
		if np.any(demi_1[np.where(datai_1 == 0)]):
			maxldem = max([demi_1[x] for x in np.where(datai_1 == 0)[0]])
		else:
			maxldem = 0
		if minsdem > maxldem:
			if dem0	> minsdem:
				scacldf[nri, nci] = 2
			elif dem0 < maxldem:
				scacldf[nri, nci] = 0
		else:
			if dem0 > maxldem:
				scacldf[nri, nci] = 2
			elif dem0 < minsdem:
				scacldf[nri, nci] = 0
	arr0[nr*nc*i:nr*nc*(i+1)] =scacldf.flat