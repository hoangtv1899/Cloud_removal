#!/data/apps/enthought_python/2.7.3/bin/python

import numpy as np

def filterMOYD(modsca, modcld, mydsca, mydcld):
	[nday, nr, nc] = modsca.shape
	oyscacld = np.zeros((nday-2, nr, nc)).astype(np.int8)
	oyscay = np.zeros((nday, nr, nc))
	oyscan = np.zeros((nday, nr, nc))
	for i in range(nday):
		osca = np.multiply(modsca[i,:,:], 1*(np.logical_and(modsca[i,:,:]>0, modsca[i,:,:]<=100)))
		ysca = np.multiply(mydsca[i,:,:], 1*(np.logical_and(mydsca[i,:,:]>0, mydsca[i,:,:]<=100)))
		ocld = np.multiply(modcld[i,:,:], 1*(np.logical_and(modcld[i,:,:]>0, modcld[i,:,:]<=100)))
		ycld = np.multiply(mydcld[i,:,:], 1*(np.logical_and(mydcld[i,:,:]>0, mydcld[i,:,:]<=100)))
		oscay0 = 1*(osca>=50)
		oscan0 = 1*(osca + ocld < 50)
		yscay0 = 1*(ysca>=50)
		yscan0 = 1*(ysca + ycld < 50)
		oscay = oscay0 & 1*(yscan0==0)
		oscan = oscan0 & 1*(yscay0==0)
		yscay = yscay0 & 1*(oscan0==0)
		yscan = yscan0 & 1*(oscay0==0)
		oyscay[i,:,:] = oscay | yscay
		oyscan[i,:,:] = oscan | yscan
	for i in range(1,nday-1):
		oyscayi = oyscay[i,:,:]
		oyscani = oyscan[i,:,:]
		oyscay0 = oyscay[i-1,:,:]
		oyscay1 = oyscay[i+1,:,:]
		oyscan0 = oyscan[i-1,:,:]
		oyscan1 = oyscan[i+1,:,:]
		oyscayi = oyscayi.astype(int) | (oyscay0.astype(int) & oyscay1.astype(int))
		oyscani = oyscani.astype(int) | (oyscan0.astype(int) & oyscan1.astype(int))
		oyscapi = 1*(oyscayi==0) & 1*(oyscani==0)
		oyscacld[i-1,:,:] = oyscayi*2 + oyscapi
	return oyscacld