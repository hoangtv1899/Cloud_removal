#!/data/apps/enthought_python/2.7.3/bin/python

from contextlib import closing
import numpy as np
import scipy.signal
import ctypes
import multiprocessing as mp

# spatial filter
# if most area is snow, set the cloud area as snow
# if most area is land, set the cloud area as land
# is most area is cloud, do nothing.

def filterspa(oyscacld0):
	try:
		[n, nr, nc] = oyscacld0.shape
	except:
		n = 1
		[nr, nc] = oyscacld0.shape
	N = n*nr*nc
	oyscacld = mp.Array(ctypes.c_long, N)
	arr = tonumpyarray(oyscacld)
	arr[:] = oyscacld0.flat
    # write to arr from different processes
	with closing(mp.Pool(initializer=init, initargs=(oyscacld, nr, nc,))) as p:
        # many processes access different slices of the same array
		p.map_async(FilterSpaSub, range(n))
	p.join()
	result = tonumpyarray(oyscacld)
	result = result.astype(np.int8)
	return result.reshape(n, nr, nc)

def init(camodcld_, nr1, nc1):
	global oyscacld, nr, nc
	oyscacld = camodcld_ # must be inhereted, not passed as an argument
	nr = nr1
	nc = nc1

def tonumpyarray(mp_arr):
    return np.frombuffer(mp_arr.get_obj())

def FilterSpaSub(i):
	"""no synchronization."""
	arr = tonumpyarray(oyscacld)
	cld0 = arr[nr*nc*i:nr*nc*(i+1)].reshape(nr, nc)
	camodcldi = np.multiply(scipy.signal.medfilt2d(cld0), 1*(cld0==1)) + np.multiply(cld0, 1*(cld0!=1))
	arr[nr*nc*i:nr*nc*(i+1)] = camodcldi.flat
