#!/data/apps/enthought_python/2.7.3/bin/python

import os
from datetime import date, timedelta
import scipy.io
import numpy as np
import gdal
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from GetClimateZone import GetClimateZone
from MapDivide import MapDivide
from ClearCloud import ClearCloud

GCZ_map, classes = GetClimateZone()
LabelMap, PolarMap = MapDivide(GCZ_map, 35)
mapUS = LabelMap[194:722,984:2320] #Clip the region of interest
labels = np.unique(mapUS)[1:]
US_labels = [int(x) for x in labels]
for jj in range(14,20):
	Li = (LabelMap==jj).astype(np.uint8)
	rows, cols = np.where(Li==1)
	[rl,ru,cl,cr] = [np.min(rows),np.max(rows),np.min(cols),np.max(cols)]
	print jj, [rl,ru,cl,cr]
	

r17 = np.load('/ssd-scratch/htranvie/Snow_dataset/filtered_multiparts/oyscacldf4_17.0.npy')
t0 = date(2000,2,24)
t_check = date(2003,7,6)
t_start = t_check - timedelta(days=15)
t_end = t_check + timedelta(days=14)
ndays = (t_end-t_start).days/2+1
dn_start1 = (t_start - t0).days
dn_end1 = (t_end - t0).days
oyscacldf4_17 = r17[dn_start1:dn_end1,:,:]
oyscacldf4_18 = r18[dn_start1:dn_end1,:,:]

oyscacldf4_17i = ClearCloud(oyscacldf4_17, t_start, t_end)
oyscacldf4_18i = ClearCloud(oyscacldf4_18, t_start, t_end)
oyscacldf4 = np.vstack([oyscacldf4_17i,oyscacldf4_18i])
oyscacldf4 = oyscacldf4[:,984 - 897:]
fvi = gdal.Open('result_US/SnowUS_'+t_check.strftime('%Y-%m-%d')+'.asc').ReadAsArray()
oyscacldf4_fvi = fvi[216-194:657-194+1, :1546-984+1]
