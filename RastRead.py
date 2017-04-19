#!/data/apps/enthought_python/2.7.3/bin/python

import numpy as np
import gdal

def RastRead(TifFile, LabelMap):
	rows, cols = np.where(LabelMap==1)
	[rl, ru, cl, cu] = [np.min(rows), np.max(rows), np.min(cols), np.max(cols)]
	ds = gdal.Open(TifFile)
	Array = ds.ReadAsArray()[600:3000,:]
	Array = np.ma.masked_where(LabelMap!=1,Array)
	Array2 = Array[rl:ru+1, cl:cu+1]
	return Array2