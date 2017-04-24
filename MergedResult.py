#!/data/apps/enthought_python/2.7.3/bin/python

import os
import numpy as np
from GetClimateZone import GetClimateZone
from MapDivide import MapDivide
from glob import glob
from pyhdf.SD import SD, SDC
import time
import pandas as pd
import gdal
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from plotWhole import plotWhole
import multiprocessing as mp

def latlon2pixzone(xll, yll, dx, dy, lat0,lon0):
	rl = abs((yll - lat0)/dy)
	cu = abs((lon0 - xll)/dx)
	return int(round(rl)), int(round(cu))

def find_err(A):
	if np.unique(A).tolist() ==[1]:
		return 1
	else:
		return 0

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
	with open('result_US/SnowUS_'+name+'.asc','w') as fo:
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
	with open('result_US/SnowUS_'+name+'.asc','w') as fo:
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

snowUS_list = sorted(glob('result_US/SnowUS_*.asc'))
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
grid_area = gdal.Open('data/US_area_by_grid1.tif').ReadAsArray()
averageSC = pd.DataFrame(columns=['Date','Snow Cover Extent'])
averageSC['Date'] = snowUS_dates
PC = []
for ii in snowUS_dates:
	arrT0 = np.loadtxt('result_US/SnowUS_'+ii+'.asc',skiprows=6)
	a0 = arrT0[conus==1]
	a1 = grid_area[conus==1]
	PC.append(np.dot(a0,a1.T))

averageSC['Snow Cover Extent'] = PC
averageSC.to_csv('averageSC1.csv',index=False,encoding='utf-8')

#Count snowy day in both mModis and Cloud free
#define header
header = "ncols     %s\n" % 1336
header += "nrows    %s\n" % 528
header += "xllcorner %.2f\n" % -130.75
header += "yllcorner %.2f\n" % 23.90
header += "cellsize %.2f\n" % 0.05
header += "NODATA_value 0\n"
for yr in range(2001,2018):
	print yr
	snowUS_yr = sorted(glob('result_US/SnowUS_'+str(yr)+'*.asc'))
	os.system('gdalbuildvrt -separate result_US/SnowUS_'+str(yr)+'.vrt '+' '.join(snowUS_yr))
	snowUS = gdal.Open('result_US/SnowUS_'+str(yr)+'.vrt').ReadAsArray()
#	os.remove('result_US/SnowUS_'+str(yr)+'.vrt')
	mModis = np.load('mMODIS/mMODIS_'+str(yr)+'.npy')
	n,nr,nc = mModis.shape
	b = []
	for jk in range(n):
		b.append(find_err(mModis[jk,:,:]))
	mModis = mModis[np.asarray(b)==0,:,:]
	mModis[mModis==1]=0
	mModis[mModis==2]=1
	snowUS_count = np.sum(snowUS, axis=0)
	mModis_count = np.sum(mModis, axis=0)
	inv = np.logical_and(mModis_count>=1, snowUS_count==0)
	aa,bb = np.where(inv==1)
	if aa.size:
		x1,x2 = np.where(mModis[:,aa,bb]==1)
		list_err = np.unique(x1).tolist()
		snowUS_count[inv] = mModis_count[inv]
		print list_err
		for jj in list_err:
			file_err = snowUS_yr[jj]
			arrS = np.loadtxt(file_err, skiprows=6)
			arrS[np.logical_and(arrS==0, mModis[jj,:,:]==1)] = 1
			with open(file_err,'w') as ff:
				ff.write(header)
				np.savetxt(ff,arrS,fmt='%d')
	#write header
	with open('count/SnowUS_'+str(yr)+'.asc','w') as fo:
		fo.write(header)
		np.savetxt(fo,snowUS_count,fmt='%d')
	# #write header
	# with open('count/mModis_'+str(yr)+'.asc','w') as fo1:
		# fo1.write(header)
		# np.savetxt(fo1,mModis_count,fmt='%d')

