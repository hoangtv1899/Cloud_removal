#!/data/apps/enthought_python/2.7.3/bin/python

import os
from time import time
import scipy.io
import numpy as np
from glob import glob
from datetime import datetime, date, timedelta as td
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
#plt.style.use('ggplot')
from GetClimateZone import GetClimateZone
from MapDivide import MapDivide
from RastRead import RastRead
from preproc4filterMOYD import preproc4filterMOYD
from Merging_TerAqu import Merging_TerAqu
from filterdemall import filterdemall
from filterspa import filterspa
from filterseriesall import filterseriesall
from pyhdf.SD import SD, SDC
import ctypes
import logging
import multiprocessing as mp
from multiprocessing import Manager
from contextlib import closing

def init(glomydsca1,glomydcld1,glomodsca1,glomodcld1,missing_MYD1,missing_MOD1,t01,fill_mat1):
	global glomydsca,glomydcld,glomodsca,glomodcld,missing_MYD,missing_MOD,t0,fill_mat
	glomydsca = glomydsca1
	glomydcld = glomydcld1
	glomodsca = glomodsca1
	glomodcld = glomodcld1
	t0 = t01
	fill_mat = fill_mat1
	missing_MYD = missing_MYD1
	missing_MOD = missing_MOD1

def tonumpyarray(mp_arr):
    return np.frombuffer(mp_arr.get_obj())

def readHDF(i):
	arr0 = tonumpyarray(glomydsca)
	arr1 = tonumpyarray(glomydcld)
	arr2 = tonumpyarray(glomodsca)
	arr3 = tonumpyarray(glomodcld)
	dt = t0 + td(days=i)
	dt1 = dt.strftime('%Y.%m.%d')
	if dt1 in missing_MYD:
		mydsca, mydcld = fill_mat.copy(), fill_mat.copy()
	else:
		mydhf_file = glob('MYD10C1.006/'+dt1+'/*.hdf')[0]
		mydhf = SD(mydhf_file, SDC.READ)
		mydsca = mydhf.select('Day_CMG_Snow_Cover')[:][600:3000,:]
		mydcld = mydhf.select('Day_CMG_Cloud_Obscured')[:][600:3000,:]
	if dt1 in missing_MOD:
		modsca, modcld = fill_mat.copy(), fill_mat.copy()
	else:
		modhf_file = glob('MOD10C1.006/'+dt1+'/*.hdf')[0]
		modhf = SD(modhf_file, SDC.READ)
		modsca = modhf.select('Day_CMG_Snow_Cover')[:][600:3000,:]
		modcld = modhf.select('Day_CMG_Cloud_Obscured')[:][600:3000,:]
	arr0[2400*7200*i:2400*7200*(i+1)] = mydsca.flat
	arr1[2400*7200*i:2400*7200*(i+1)] = mydcld.flat
	arr2[2400*7200*i:2400*7200*(i+1)] = modsca.flat
	arr3[2400*7200*i:2400*7200*(i+1)] = modcld.flat


t0 = datetime(2000,2,24)
t1 = datetime(2017,3,15)
ndays = (t1-t0).days+1

list_MOD = sorted(glob('MOD10C1.006/*/'))
list_MYD = sorted(glob('MYD10C1.006/*/'))

list_MOD = [x.split('/')[1] for x in list_MOD]
list_MYD = [x.split('/')[1] for x in list_MYD]

missing_MOD = []
missing_MYD = []
for i in range(ndays):
	dt = t0 + td(days=i)
	dt1 = dt.strftime('%Y.%m.%d')
	if dt1 not in list_MOD:
		missing_MOD.append(dt1)
	if dt1 not in list_MYD:
		missing_MYD.append(dt1)

# for dir1 in missing_MOD:
	# os.system('wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies -r --no-parent --no-check-certificate --auth-no-challenge=on -nH --cut-dirs=1 -e robots=off --wait 1 --reject "index.html*" https://n5eil01u.ecs.nsidc.org/MOST/MOD10C1.006/'+dir1+'/')

# for dir1 in missing_MYD:
	# os.system('wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies -r --no-parent --no-check-certificate --auth-no-challenge=on -nH --cut-dirs=1 -e robots=off --wait 1 --reject "index.html*" https://n5eil01u.ecs.nsidc.org/MOSA/MYD10C1.006/'+dir1+'/')


fill_mat = np.empty((2400,7200))
fill_mat[:] = np.nan
###Done this part
# for yr in range(2002,2017):
	# start = time()
	# t1_temp = datetime(yr,1,1)
	# ndays_temp = (t1_temp - t0).days
	# N = ndays_temp*2400*7200
	# glomydsca = mp.Array(ctypes.c_long, N)
	# glomydcld = mp.Array(ctypes.c_long, N)
	# glomodsca = mp.Array(ctypes.c_long, N)
	# glomodcld = mp.Array(ctypes.c_long, N)
	# with closing(mp.Pool(processes=64, initializer=init, initargs=(glomydsca,\
																	# glomydcld,\
																	# glomodsca,\
																	# glomodcld,\
																	# missing_MYD,\
																	# missing_MOD,\
																	# t0,fill_mat,))) as p:
		# p.map_async(readHDF, range(ndays_temp))
	# p.join()
	# glomydsca0 = tonumpyarray(glomydsca)
	# glomydcld0 = tonumpyarray(glomydcld)
	# glomodsca0 = tonumpyarray(glomodsca)
	# glomodcld0 = tonumpyarray(glomodcld)
	# glomydsca2 = glomydsca0.reshape(-1,2400,7200)
	# glomydcld2 = glomydcld0.reshape(-1,2400,7200)
	# glomodsca2 = glomodsca0.reshape(-1,2400,7200)
	# glomodcld2 = glomodcld0.reshape(-1,2400,7200)
	# end = time()
	# print 'time elapsed: '+str(end-start)+' s'
	# glomodcld2 = preproc4filterMOYD(glomodcld2)
	# glomydcld2 = preproc4filterMOYD(glomydcld2)
	# end1 = time()
	# print 'preprocessing for filter '+str(end1 - end)+' s'
	# np.save('/ssd-scratch/htranvie/Snow_dataset/original/glomodcld'+str(yr),glomodcld2)
	# np.save('/ssd-scratch/htranvie/Snow_dataset/original/glomydcld'+str(yr),glomydcld2)
	# glomydsca2[np.isnan(glomydsca2)] = -99
	# np.save('/ssd-scratch/htranvie/Snow_dataset/original/glomydsca'+str(yr),glomydsca2.astype(np.int16))
	# glomodsca2[np.isnan(glomodsca2)] = -99
	# np.save('/ssd-scratch/htranvie/Snow_dataset/original/glomodsca'+str(yr),glomodsca2.astype(np.int16))
	# end2 = time()
	# print 'saving to ssd-scratch '+str(end2-end1)+ ' s'
	# t0 = t1_temp
###Done

GCZ_map, classes = GetClimateZone()
LabelMap, PolarMap = MapDivide(GCZ_map, 35)
labels = np.unique(LabelMap)[1:]
org_path = '/share/ssd-scratch/htranvie/Snow_dataset/original/'
multiparts = '/share/ssd-scratch/htranvie/Snow_dataset/multiparts/'
filtered = '/share/ssd-scratch/htranvie/Snow_dataset/filtered_multiparts/'

for yr in range(2001,2017):
	print yr
	start = time()
	glomodcld = np.load(org_path+'glomodcld'+str(yr)+'.npy')
	glomydcld = np.load(org_path+'glomydcld'+str(yr)+'.npy')
	glomodsca = np.load(org_path+'glomodsca'+str(yr)+'.npy')
	glomydsca = np.load(org_path+'glomydsca'+str(yr)+'.npy')
	end = time()
	print 'load time '+str(end-start)+' s'
	for i in labels:
		end = time()
		print str(i)
		if os.path.isfile(multiparts+'oyscacldf3_'+str(yr)+'_'+str(i)+'.npy'):
			continue
		Li = (LabelMap==i).astype(np.uint8)
		rows, cols = np.where(Li==1)
		[rl, ru, cl, cu] = [np.min(rows), np.max(rows), np.min(cols), np.max(cols)]
		glomodcldi = glomodcld[:,rl:ru+1,cl:cu+1]
		glomydcldi = glomydcld[:,rl:ru+1,cl:cu+1]
		glomodscai = glomodsca[:,rl:ru+1,cl:cu+1]
		glomydscai = glomydsca[:,rl:ru+1,cl:cu+1]
		end1 = time()
		print 'subsetting time '+str(end1-end)+' s'
		oyscacldf1i = Merging_TerAqu(glomodscai, glomodcldi, glomydscai, glomydcldi)
		end2 = time()
		print 'merging time '+str(end2-end1)+' s' 
		oyscacldf3i = filterspa(oyscacldf1i)
		end3 = time()
		print 'filtering spatial time '+str(end3-end2)+' s'
		np.save(multiparts+'oyscacldf3_'+str(yr)+'_'+str(i), oyscacldf3i)

for i in labels[:-1][::-1]:
	print str(i)
	if os.path.isfile(filtered+'oyscacldf4_'+str(i)+'.npy'):
		continue
	list_labeli = sorted(glob(multiparts+'oyscacldf3*_'+str(i)+'.npy'))
	Li = (LabelMap==i).astype(np.uint8)
	rows, cols = np.where(Li==1)
	[rl, ru, cl, cu] = [np.min(rows), np.max(rows), np.min(cols), np.max(cols)]
	oyscacldf3i = np.array([]).reshape(0,ru-rl+1,cu-cl+1)
	for yr in list_labeli:
		oyscacldf3i = np.vstack([oyscacldf3i, np.load(yr)])
	n, nr, nc = oyscacldf3i.shape
	if nr*nc > 300000:
		start = time()
		oyscacldf4i_1 = filterseriesall(oyscacldf3i[:,:(nr/4),:],31,31,11)
		oyscacldf4i_2 = filterseriesall(oyscacldf3i[:,(nr/4):(nr/2),:],31,31,11)
		oyscacldf4i_3 = filterseriesall(oyscacldf3i[:,(nr/2):(3*nr/4),:],31,31,11)
		oyscacldf4i_4 = filterseriesall(oyscacldf3i[:,(3*nr/4):nr,:],31,31,11)
		oyscacldf4i = np.hstack([oyscacldf4i_1,oyscacldf4i_2,oyscacldf4i_3,oyscacldf4i_4])
		end = time()
	else:
		start = time()
		oyscacldf4i = filterseriesall(oyscacldf3i,31,31,11)
		end = time()
	print 'filter series all '+str(end-start)+' s'
	np.save(filtered+'oyscacldf4_'+str(i),oyscacldf4i)
