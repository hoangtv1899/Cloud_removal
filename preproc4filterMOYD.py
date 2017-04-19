#!/data/apps/enthought_python/2.7.3/bin/python

import ctypes
import multiprocessing as mp
import scipy.ndimage.morphology as ndimage
from contextlib import closing
import numpy as np

def preproc4filterMOYD(camodcld0):
	try:
		[n, nr, nc] = camodcld0.shape
	except:
		n = 1
		[nr, nc] = camodcld0.shape
	N = n*nr*nc
	camodcld = mp.Array(ctypes.c_long, N)
	arr = tonumpyarray(camodcld)
	arr[:] = camodcld0.flat
    # write to arr from different processes
	with closing(mp.Pool(initializer=init, initargs=(camodcld, nr, nc,))) as p:
        # many processes access different slices of the same array
		p.map_async(PreProc, range(n))
	p.join()
	result = tonumpyarray(camodcld)
	return result.reshape(n, nr, nc).astype(np.uint8)

def init(camodcld_, nr1, nc1):
	global camodcld, nr, nc
	camodcld = camodcld_ # must be inhereted, not passed as an argument
	nr = nr1
	nc = nc1

def tonumpyarray(mp_arr):
    return np.frombuffer(mp_arr.get_obj())

def PreProc(i):
	"""no synchronization."""
	arr = tonumpyarray(camodcld)
	cld0 = arr[nr*nc*i:nr*nc*(i+1)].reshape(nr, nc)
	camodcldi = np.multiply(cld0, 1*(np.logical_and(cld0>0, cld0<=100)))
	if (np.sum(np.abs(camodcldi - 1), dtype = np.int32) == 0) or (np.sum(np.abs(camodcldi), dtype = np.int32) == 0):
		arr[nr*nc*i:nr*nc*(i+1)] = (np.ones((nr, nc))*100).flat
	else:
		struct = ndimage.generate_binary_structure(2,2)
		camodcldi = cld0
		camodcldi[ndimage.binary_dilation(camodcldi==255, structure = struct)] = 100
		arr[nr*nc*i:nr*nc*(i+1)] = camodcldi.flat
	
	