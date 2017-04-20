#!/data/apps/enthought_python/2.7.3/bin/python

import os
import sys
import numpy as np
from datetime import datetime, timedelta
from pyhdf.SD import SD, SDC
from glob import glob
from GetClimateZone import GetClimateZone
from MapDivide import MapDivide
from preproc4filterMOYD import preproc4filterMOYD
from Merging_TerAqu import Merging_TerAqu
import multiprocessing as mp

#num = sys.argv[1]

def init(LabelMap1, list_date1, labeli1, list_MOD_miss1, list_MYD_miss1):
	global LabelMap, list_date, labeli, list_MOD_miss, list_MYD_miss
	LabelMap = LabelMap1
	list_date = list_date1
	labeli = labeli1
	list_MOD_miss = list_MOD_miss1
	list_MYD_miss = list_MYD_miss1

def DownWriteJr(yeari):
	if os.path.isfile('/ssd-scratch/htranvie/Snow_dataset/merged_multiparts/modsca_'+str(labeli)+'_'+str(yeari)+'.npy'):
		return
	list_date1 = [x for x in list_date if str(yeari) in x]
	Li = (LabelMap==labeli).astype(np.uint8)
	rows, cols = np.where(Li==1)
	[rl, ru, cl, cu] = [np.min(rows), np.max(rows), np.min(cols), np.max(cols)]
	modsca = np.array([]).reshape(0,ru-rl+1,cu-cl+1)
	modcld = np.array([]).reshape(0,ru-rl+1,cu-cl+1)
	mydsca = np.array([]).reshape(0,ru-rl+1,cu-cl+1)
	mydcld = np.array([]).reshape(0,ru-rl+1,cu-cl+1)
	for dt in list_date1:
		if (dt in list_MOD_miss) or (not glob('MOD10C1.006/'+dt+'/*.hdf')):
			modsca = np.concatenate([modsca, 
									(np.ones((ru-rl+1,cu-cl+1))*-99).reshape(-1,ru-rl+1,cu-cl+1)], axis = 0)
			modcld = np.concatenate([modcld, 
									(np.ones((ru-rl+1,cu-cl+1))*-99).reshape(-1,ru-rl+1,cu-cl+1)], axis = 0)
		else:
			hdf_file = glob('MOD10C1.006/'+dt+'/*.hdf')[0]
			try:
				hfi0 = SD(hdf_file, SDC.READ)
			except:
				print hdf_file
				return
			scai = hfi0.select('Day_CMG_Snow_Cover')[:][600+rl:600+ru+1,cl:cu+1]
			cldi = hfi0.select('Day_CMG_Cloud_Obscured')[:][600+rl:600+ru+1,cl:cu+1]
			modsca = np.concatenate([modsca,
									scai.reshape(-1,ru-rl+1,cu-cl+1)],axis=0)
			modcld = np.concatenate([modcld,
									cldi.reshape(-1,ru-rl+1,cu-cl+1)],axis=0)
		if (dt in list_MYD_miss) or (not glob('MYD10C1.006/'+dt+'/*.hdf')):
			mydsca = np.concatenate([mydsca, 
									(np.ones((ru-rl+1,cu-cl+1))*-99).reshape(-1,ru-rl+1,cu-cl+1)], axis = 0)
			mydcld = np.concatenate([mydcld, 
									(np.ones((ru-rl+1,cu-cl+1))*-99).reshape(-1,ru-rl+1,cu-cl+1)], axis = 0)
		else:
			hdf_file = glob('MYD10C1.006/'+dt+'/*.hdf')[0]
			try:
				hfi1 = SD(hdf_file, SDC.READ)
			except:
				print hdf_file
				return
			scai = hfi1.select('Day_CMG_Snow_Cover')[:][600+rl:600+ru+1,cl:cu+1]
			cldi = hfi1.select('Day_CMG_Cloud_Obscured')[:][600+rl:600+ru+1,cl:cu+1]
			mydsca = np.concatenate([mydsca,
									scai.reshape(-1,ru-rl+1,cu-cl+1)],axis=0)
			mydcld = np.concatenate([mydcld,
									cldi.reshape(-1,ru-rl+1,cu-cl+1)],axis=0)
	np.save('/ssd-scratch/htranvie/Snow_dataset/merged_multiparts/modsca_'+str(labeli)+'_'+str(yeari),modsca)
	np.save('/ssd-scratch/htranvie/Snow_dataset/merged_multiparts/mydsca_'+str(labeli)+'_'+str(yeari),mydsca)
	np.save('/ssd-scratch/htranvie/Snow_dataset/merged_multiparts/modcld_'+str(labeli)+'_'+str(yeari),modcld)
	np.save('/ssd-scratch/htranvie/Snow_dataset/merged_multiparts/mydcld_'+str(labeli)+'_'+str(yeari),mydcld)

def init1(LabelMap1, list_date1, US_labels1, mapUS1):
	global LabelMap, list_date, US_labels, mapUS
	LabelMap = LabelMap1
	list_date = list_date1
	US_labels = US_labels1
	mapUS = mapUS1

def MergeMap(yeari):
	if os.path.isfile('mMODIS/mMODIS_'+str(yeari)+'.npy'):
		return
	list_date1 = [x for x in list_date if str(yeari) in x]
	arrT = np.zeros((len(list_date1),mapUS.shape[0],mapUS.shape[1]))
	for lab in US_labels + [30]:
		if lab != 30:
			Li = (LabelMap==lab).astype(np.uint8)
			rows, cols = np.where(Li==1)
			[rl, ru, cl, cu] = [np.min(rows), np.max(rows), np.min(cols), np.max(cols)]
		else:
			[rl, ru, cl, cu] = 377,506,2048,2548
		if rl < 194:
			shift1 = 194 - rl
		else:
			shift1 = 0
		if ru > 721:
			shift2 = 722 - rl
		else:
			shift2 = None
		if cl < 984:
			shift3 = 984 - cl
		else:
			shift3 = 0
		if cu > 2319:
			shift4 = 2320 - cl
		else:
			shift4 = None
		arr0 = np.load('/ssd-scratch/htranvie/Snow_dataset/merged_multiparts/oyscacldf1_'+str(lab)+'_'+str(yeari)+'.npy')
		arr_temp0 = arr0[:,shift1:shift2,shift3:shift4]
		if lab != 30:
			arrT[:,mapUS == lab] = arr_temp0.reshape(arrT.shape[0],-1)
		else:
			arrT[:,rl-194:ru+1-194,cl-984:cu+1-984] = arr_temp0
	np.save('mMODIS/mMODIS_'+str(yeari),arrT)
	
GCZ_map, classes = GetClimateZone()
LabelMap, PolarMap = MapDivide(GCZ_map, 35)
mapUS = LabelMap[194:722,984:2320] #Clip the region of interest
labels = np.unique(mapUS)[1:] #Get only regions contain US
US_labels = [int(x) for x in labels]

#MODIS start
tm_0 = datetime(2000,3,10)
#MODIS end
tm_end = datetime(2017,2,28)
ndays = (tm_end-tm_0).days+1

#list date
list_date = [(tm_0+timedelta(days=i)).strftime('%Y.%m.%d') for i in range(ndays)]
#list MOD
list_MOD = sorted(glob('MOD10C1.006/*/'))
list_MOD_date = [x.split('/')[-2] for x in list_MOD]
list_MOD_miss = [y for y in list_date if y not in list_MOD_date]
#list MYD
list_MYD = sorted(glob('MYD10C1.006/*/'))
list_MYD_date = [x.split('/')[-2] for x in list_MYD]
list_MYD_miss = [y for y in list_date if y not in list_MYD_date]

#labeli
labeli = 30
pool = mp.Pool(initializer=init, processes=64, initargs=(LabelMap, list_date, labeli, list_MOD_miss, list_MYD_miss,))
pool.map(DownWriteJr, range(2000,2018))
pool.join()
pool.close()
for yr in range(2000,2018):
	nmodcld, nmodsca, nmydcld, nmydsca = sorted(glob('/ssd-scratch/htranvie/Snow_dataset/merged_multiparts/*_'+str(labeli)+'_'+str(yr)+'.npy'))
	modcld = preproc4filterMOYD(np.load(nmodcld))
	mydcld = preproc4filterMOYD(np.load(nmydcld))
	modsca = np.load(nmodsca)
	mydsca = np.load(nmydsca)
	oyscacldf1 = Merging_TerAqu(modsca, modcld, mydsca, mydcld)
	np.save('/ssd-scratch/htranvie/Snow_dataset/merged_multiparts/oyscacldf1_'+str(labeli)+'_'+str(yr),oyscacldf1)

#Merge parts together
pool1 = mp.Pool(initializer=init1, processes=64, initargs=(LabelMap, list_date, US_labels, mapUS,))
pool1.map(MergeMap, range(2000,2018))
pool1.join()
pool1.close()

