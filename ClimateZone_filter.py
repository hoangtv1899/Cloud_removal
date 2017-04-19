#!/data/apps/enthought_python/2.7.3/bin/python

import numpy as np
import time
from GetClimateZone import GetClimateZone
import scipy.ndimage
import multiprocessing as mp
from multiprocessing import Manager
from contextlib import closing
import ctypes
import logging

def ClimateZone_filter(oyscacld, Li):
	GCZ_map, classes = GetClimateZone()
	GCZ_map_scaled = scipy.ndimage.zoom(GCZ_map, 10, order=0)
	GCZ_map_scaled = np.vstack([np.zeros((3600-GCZ_map_scaled.shape[0],GCZ_map_scaled.shape[1])), GCZ_map_scaled])
	rows, cols = np.where(Li==1)
	[rl, ru, cl, cu] = [np.min(rows), np.max(rows), np.min(cols), np.max(cols)]
	GCZ_map_mini = GCZ_map_scaled[rl:ru+1, cl:cu+1]
	try:
		[n, nr, nc] = oyscacld.shape
	except:
		n = 1
		[nr, nc] = oyscacld.shape
	N = n*nr*nc
	sca = mp.Array(ctypes.c_long, N)
	arr0 = tonumpyarray(sca)
	arr0[:] = oyscacld.flat
	sca_vi = mp.Array(ctypes.c_long, N)
	arr1 = tonumpyarray(sca_vi)
	arr1[:] = np.zeros((n,nr,nc)).flat
	with closing(mp.Pool(initializer=init, initargs=(sca, nr, nc, GCZ_map_mini, sca_vi,))) as p:
        # many processes access different slices of the same array
		p.map_async(FilterCore, range(n))
	p.join()
	sca_final = tonumpyarray(sca_vi)
	return sca_final.reshape(-1,nr,nc).astype(np.uint8)

def init(sca_, nr1, nc1, GCZ_map_mini_, sca_vi_):
	global sca, nr, nc, GCZ_map_mini, sca_vi
	sca = sca_ # must be inhereted, not passed as an argument
	nr = nr1
	nc = nc1
	GCZ_map_mini = GCZ_map_mini_
	sca_vi = sca_vi_

def tonumpyarray(mp_arr):
    return np.frombuffer(mp_arr.get_obj())

def FilterCore(i):
	arr0 = tonumpyarray(sca)
	arr1 = tonumpyarray(sca_vi)
	modi = arr0[nr*nc*i:nr*nc*(i+1)].reshape(nr, nc)
	CldMap = np.where(modi==1)
	CZ_vals = GCZ_map_mini[CldMap]
	CldMapSno = [CldMap[0][CZ_vals>=20], CldMap[1][CZ_vals>=20]]
#	SnoMap = np.where(GCZ_map_mini>=20)
	modi[CldMapSno] = 2
	arr1[nr*nc*i:nr*nc*(i+1)] = modi.flat
	
	
