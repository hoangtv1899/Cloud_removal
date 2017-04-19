#!/data/apps/enthought_python/2.7.3/bin/python

import os
import time
import scipy.io
import numpy as np
from datetime import date, datetime, timedelta
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
#plt.style.use('ggplot')
from GetClimateZone import GetClimateZone
from MapDivide import MapDivide
from ClearCloud import ClearCloud
from plotWhole import plotWhole

def CloudRemoval(yyyy0,mm0,dd0,yyyy1,mm1,dd1,yyyy2,mm2,dd2):
	t0 = date(yyyy0,mm0,dd0)
	t_start = date(yyyy1,mm1,dd1)
	t_end = date(yyyy2,mm2,dd2)
	ndays = (t_end-t_start).days/2+1
	dn_start1 = (t_start - t0).days
	dn_end1 = (t_end - t0).days +1
	GCZ_map, classes = GetClimateZone()
	LabelMap, PolarMap = MapDivide(GCZ_map, 35)
	labels = np.unique(LabelMap)[1:]
	oyscacldf4 = np.load('data/after_filter_global101516031517.npy')[dn_start1:dn_end1,:,:]
	oyscacldf1 = np.load('data/merged_global101516031517.npy')[dn_start1:dn_end1,:,:]
	n, nr, nc = oyscacldf1.shape
	arr1 = np.zeros((nr,nc))
	Polar_add = np.logical_and(PolarMap==1, LabelMap==0).astype(np.uint8)
	start_tot = time.time()
	for i in labels:
		print str(i)
		Li = (LabelMap==i).astype(np.uint8)
		rows, cols = np.where(Li==1)
		[rl, ru, cl, cu] = [np.min(rows), np.max(rows), np.min(cols), np.max(cols)]
		Li_mini = Li[rl:ru+1,cl:cu+1]
		Polar_mini = PolarMap[rl:ru+1,cl:cu+1]
		oyscacldf4i = oyscacldf4[:,rl:ru+1,cl:cu+1]
		start = time.time()
		oyscacldfi = ClearCloud(oyscacldf4i, t_start, t_end)
		if oyscacldfi == 'need to divide array':
			oyscacldfi_1 = ClearCloud(oyscacldf4i[:,:,:(cu+1-cl)/2], t_start, t_end)
			if oyscacldfi_1 == 'need to divide array':
				oyscacldfi_10 = ClearCloud(oyscacldf4i[:,:,:(cu+1-cl)/4], t_start, t_end)
				if oyscacldfi_10 == 'need to divide array':
					oyscacldfi_100 = ClearCloud(oyscacldf4i[:,:(ru+1-rl)/2,:(cu+1-cl)/4], t_start, t_end)
					oyscacldfi_101 = ClearCloud(oyscacldf4i[:,(ru+1-rl)/2:,:(cu+1-cl)/4], t_start, t_end)
					oyscacldfi_10 = np.vstack([oyscacldfi_100,oyscacldfi_101])
				oyscacldfi_11 = ClearCloud(oyscacldf4i[:,:,(cu+1-cl)/4:(cu+1-cl)/2], t_start, t_end)
				if oyscacldfi_11 == 'need to divide array':
					oyscacldfi_110 = ClearCloud(oyscacldf4i[:,:(ru+1-rl)/2,(cu+1-cl)/4:(cu+1-cl)/2], t_start, t_end)
					oyscacldfi_111 = ClearCloud(oyscacldf4i[:,(ru+1-rl)/2:,(cu+1-cl)/4:(cu+1-cl)/2], t_start, t_end)
					oyscacldfi_11 = np.vstack([oyscacldfi_110,oyscacldfi_111])
				oyscacldfi_1 = np.hstack([oyscacldfi_10,oyscacldfi_11])
			oyscacldfi_2 = ClearCloud(oyscacldf4i[:,:,(cu+1-cl)/2:], t_start, t_end)
			if oyscacldfi_2 == 'need to divide array':
				oyscacldfi_20 = ClearCloud(oyscacldf4i[:,:,(cu+1-cl)/2:3*(cu+1-cl)/4], t_start, t_end)
				if oyscacldfi_20 == 'need to divide array':
					oyscacldfi_200 = ClearCloud(oyscacldf4i[:,:(ru+1-rl)/2,(cu+1-cl)/2:3*(cu+1-cl)/4], t_start, t_end)
					oyscacldfi_201 = ClearCloud(oyscacldf4i[:,(ru+1-rl)/2:,(cu+1-cl)/2:3*(cu+1-cl)/4], t_start, t_end)
					oyscacldfi_20 = np.vstack([oyscacldfi_200,oyscacldfi_201])
				oyscacldfi_21 = ClearCloud(oyscacldf4i[:,:,3*(cu+1-cl)/4:], t_start, t_end)
				if oyscacldfi_21 == 'need to divide array':
					oyscacldfi_210 = ClearCloud(oyscacldf4i[:,:(ru+1-rl)/2,(cu+1-cl)/2:3*(cu+1-cl)/4:], t_start, t_end)
					oyscacldfi_211 = ClearCloud(oyscacldf4i[:,(ru+1-rl)/2:,3*(cu+1-cl)/4:], t_start, t_end)
					oyscacldfi_21 = np.vstack([oyscacldfi_210,oyscacldfi_211])
				oyscacldfi_2 = np.hstack([oyscacldfi_20,oyscacldfi_21])
			oyscacldfi = np.hstack([oyscacldfi_1,oyscacldfi_2])
		V = np.logical_and(np.logical_and(oyscacldf1[ndays,rl:ru+1,cl:cu+1]==1,
													oyscacldfi==0),
													Polar_mini==1)
		oyscacldfi[V] = 1
		end6 = time.time()
		print 'VI process '+str(end6-start)+' s'
		arr1[Li==1] = oyscacldfi[Li_mini==1]
		f = plt.figure()
		plt.imshow(arr1)
		f.savefig('h'+(t_start+timedelta(days=ndays)).strftime('%Y-%m-%d')+'.png')
	arr_tot = arr1 + Polar_add
	arr_tot = arr_tot.astype(np.uint8)
	end_tot = time.time()
	print 'Total time '+str(end_tot-start_tot)+' s'
	plotWhole(arr_tot, 'final_'+(t_start+timedelta(days=ndays)).strftime('%Y-%m-%d'))
	np.save('data/result_'+(t_start+timedelta(days=ndays)).strftime('%Y-%m-%d'),arr_tot)