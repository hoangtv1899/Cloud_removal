#!/data/apps/enthought_python/2.7.3/bin/python

import numpy as np
import ctypes
import logging
import multiprocessing as mp
from multiprocessing import Manager
from contextlib import closing

def Merging_TerAqu(modsca, modcld, mydsca, mydcld):
	[nday, nr, nc] = modsca.shape
	N = nday*nr*nc
	oyscacld = mp.Array(ctypes.c_long, N)
	arr0 = tonumpyarray(oyscacld)
	arr0[:] = np.zeros((nday, nr, nc)).flat
	with closing(mp.Pool(initializer=init, initargs=(oyscacld, modsca, modcld, mydsca, mydcld, nr, nc,))) as p:
        # many processes access different slices of the same array
		p.map_async(MergeData, range(nday))
	p.join()
	return tonumpyarray(oyscacld).reshape(-1,nr,nc).astype(np.uint8)

def init(oyscacld_, modsca_, modcld_, mydsca_, mydcld_, nr1, nc1):
	global oyscacld, modsca, modcld, mydsca, mydcld, nr, nc
	oyscacld = oyscacld_
	modsca = modsca_
	modcld = modcld_
	mydsca = mydsca_
	mydcld = mydcld_
	nr = nr1
	nc = nc1

def tonumpyarray(mp_arr):
    return np.frombuffer(mp_arr.get_obj())

def MergeData(i):
	arr0 = tonumpyarray(oyscacld)
	modscai = modsca[i,:,:]
	mydscai = mydsca[i,:,:]
	modcldi = modcld[i,:,:]
	mydcldi = mydcld[i,:,:]
	osca = np.multiply(modscai, 1*(np.logical_and(modscai>0, modscai<=100)))
	ysca = np.multiply(mydscai, 1*(np.logical_and(mydscai>0, mydscai<=100)))
	ocld = np.multiply(modcldi, 1*(np.logical_or(np.logical_and(modcldi>0, modcldi<=100), modcldi==111)))
	ycld = np.multiply(mydcldi, 1*(np.logical_or(np.logical_and(mydcldi>0, mydcldi<=100),mydcldi==111)))
	oscay0 = 1*(osca>=50)
	oscan0 = 1*(osca + ocld < 50)
	yscay0 = 1*(ysca>=50)
	yscan0 = 1*(ysca + ycld < 50)
	oscay = oscay0 & 1*(yscan0==0)
	oscan = oscan0 & 1*(yscay0==0)
	yscay = yscay0 & 1*(oscan0==0)
	yscan = yscan0 & 1*(oscay0==0)
	oyscay = oscay | yscay
	oyscan = oscan | yscan
	oyscap = 1*(oyscay==0) & 1*(oyscan==0)
	oyscacldi = oyscay*2 + oyscap
	arr0[nr*nc*i:nr*nc*(i+1)] =oyscacldi.flat