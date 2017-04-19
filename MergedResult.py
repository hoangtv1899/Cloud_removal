#!/data/apps/enthought_python/2.7.3/bin/python

import numpy as np
from GetClimateZone import GetClimateZone
from MapDivide import MapDivide
from glob import glob
import time
import pandas as pd
import gdal
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from plotWhole import plotWhole
import multiprocessing as mp

def init1(US_labels1,arr_temp01, name_list1,LabelMap1,mapUS1):
	global US_labels,arr_temp0, list_full,LabelMap,mapUS
	US_labels=US_labels1
	arr_temp0=arr_temp01
	list_full = name_list1
	LabelMap = LabelMap1
	mapUS = mapUS1

def MergeMap(i):
	dt0 = list_full[i]
	for lab in US_labels:
		arr0 = np.load(result_path+str(lab)+'/result_'+str(lab)+'_'+dt0+'.npy')
		arr_temp0[LabelMap == lab] = arr0.ravel()
		arr_temp = arr_temp0[194:722,984:2320]
		arrT[i,mapUS == lab] = arr_temp[mapUS == lab]

def init2(big_arr1, name_list1):
	global arrT, list_full 
	arrT = big_arr1
	list_full = name_list1

def Write2Asc_Batch(i):
	arr = arrT[i,:,:]
	name = list_full[i]
	#define header
	header = "ncols     %s\n" % 1336
	header += "nrows    %s\n" % 528
	header += "xllcorner %.2f\n" % -130.75
	header += "yllcorner %.2f\n" % 23.90
	header += "cellsize %.2f\n" % 0.05
	header += "NODATA_value -99\n"
	#write header
	with open('/ssd-scratch/htranvie/Snow_dataset/result_US/SnowUS_'+name+'.asc','w') as fo:
		fo.write(header)
		np.savetxt(fo,arr,fmt='%d')

def Write2Asc(arr, name):
	#define header
	header = "ncols     %s\n" % 1336
	header += "nrows    %s\n" % 528
	header += "xllcorner %.2f\n" % -130.75
	header += "yllcorner %.2f\n" % 23.90
	header += "cellsize %.2f\n" % 0.05
	header += "NODATA_value -99\n"
	#write header
	with open('/ssd-scratch/htranvie/Snow_dataset/result_US/SnowUS_'+name+'.asc','w') as fo:
		fo.write(header)
		np.savetxt(fo,arr,fmt='%d')

GCZ_map, classes = GetClimateZone()
LabelMap, PolarMap = MapDivide(GCZ_map, 35)
mapUS = LabelMap[194:722,984:2320] #Clip the region of interest
labels = np.unique(mapUS)[1:]
US_labels = [int(x) for x in labels]

result_path = '/ssd-scratch/htranvie/Snow_dataset/results/'
file_list = [sorted(glob(result_path+str(x)+'/*.npy')) for x in US_labels]
file_list_short = [[x.split('_')[-1].split('.')[0] for x in ll] for ll in file_list]
list_len = [len(y) for y in file_list]
for i,k in enumerate(list_len):
	print US_labels[i], k

snowUS_list = sorted(glob('/ssd-scratch/htranvie/Snow_dataset/result_US/SnowUS_*.asc'))
snowUS_dates = [x.split('_')[-1].split('.')[0] for x in snowUS_list]
#list date name
t_start = datetime(2000,3,10)
t_end = datetime(2016,12,31)
ndays = (t_end-t_start).days+1
list_date = [(t_start+timedelta(days=jk)).strftime('%Y-%m-%d') for jk in range(ndays)]
#check which file is fully avaiable:
list_full = []
for dt in list_date:
	if (all(dt in l for l in file_list_short)) and (dt not in snowUS_dates):
		list_full.append(dt)

length = len(list_full)

start = time.time()
arrT = np.zeros((length,mapUS.shape[0],mapUS.shape[1]))
arr_temp0 = np.zeros(LabelMap.shape)
for i in range(length):
	MergeMap(i)

end = time.time()
print str(end-start)+' s'

start1 = time.time()
pool2 = mp.Pool(initializer=init2, processes=8, initargs=(arrT,list_full,))
pool2.map(Write2Asc_Batch, range(length))
pool2.close()
pool2.join()
end1 = time.time()
print str(end1-start1)+' s'

#load result numpy
result_file = sorted(glob('data/result_*.npy'))
list_full = []
for file1 in result_file:
	dt_file = file1.split('_')[-1].split('.')[0]
	Write2Asc(np.load(file1)[194:722,984:2320], dt_file)
	list_full.append(dt_file)

#load the CONUS raster
conus = gdal.Open('data/US_map.tif').ReadAsArray()
averageSC = pd.DataFrame(columns=['Date','Snow Cover Extent'])
averageSC['Date'] = snowUS_dates
PC = []
for ii in snowUS_dates:
	arrT0 = np.loadtxt('/ssd-scratch/htranvie/Snow_dataset/result_US/SnowUS_'+ii+'.asc',skiprows=6)
	a0 = arrT0[conus==1]
	PC.append(np.sum(a0==1)*25)

averageSC['Snow Cover Extent'] = PC
averageSC.to_csv('averageSC1.csv',index=False,encoding='utf-8')
