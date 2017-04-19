#!/data/apps/enthought_python/2.7.3/bin/python

import numpy as np

def AscRead(ascFile):
	Array1 = np.loadtxt(ascFile, skiprows=6)
	Array2 = np.ma.masked_where(Array1 == -9999, Array1)
	return Array2