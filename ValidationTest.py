#!/data/apps/enthought_python/2.7.3/bin/python

import os
import time
import scipy.io
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta as td
from plotWhole import plotSnotel
from SnotelDownload import SnotelDownload
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

def latlon2pixzone(xll, yll, dx, dy, lat0,lon0):
	rl = abs((yll - lat0)/dy)
	cu = abs((lon0 - xll)/dx)
	return int(round(rl)), int(round(cu))

def ValidationFunction(obs, sim):
	ndays = obs.shape[0]
	observed = obs.reshape(ndays,-1)
	simulated = sim.reshape(ndays,-1)
	#Number of correct negatives
	NoCorrNeg = np.sum(np.logical_and(simulated == 0, observed == 0), axis=1)
	#Number of hit
	NoHit = np.sum(np.logical_and(simulated > 0, observed > 0), axis=1)
	#Number of miss
	NoMiss = np.sum(np.logical_and(simulated == 0, observed > 0), axis=1)
	#Number of false
	NoFalse = np.sum(np.logical_and(simulated > 0, observed == 0), axis=1)
	#Probability of Detection
	POD = np.divide(NoHit.astype(np.float32), NoHit+NoMiss)
	#False Alarm Ratio
	FAR = np.divide(NoFalse.astype(np.float32), NoHit+NoFalse)
	#Bias score
	BIAS = np.divide((NoHit + NoFalse).astype(np.float32),NoHit + NoMiss)
	#Total
	Tot = (NoHit + NoFalse + NoMiss + NoCorrNeg)[0]
	#Heidke skill score
	exp_ect_corr = ((NoHit+NoMiss)*(NoHit+NoFalse)+(NoCorrNeg+NoMiss)*(NoCorrNeg+NoFalse))/float(Tot)
	HSS = np.divide(NoHit+NoCorrNeg - exp_ect_corr, Tot - exp_ect_corr)
	#Hanssen-Kuipers score
	HK = np.divide(NoHit.astype(np.float32), NoHit+NoMiss) - np.divide(NoFalse.astype(np.float32),NoFalse + NoCorrNeg)
	#Equitable threat score
	hits_rand = np.multiply((NoHit+NoMiss),(NoHit+NoFalse))/float(Tot)
	ETS = np.divide(NoHit - hits_rand,NoHit+NoMiss+NoFalse-hits_rand)
	result = np.vstack([NoHit, NoMiss, NoFalse, POD, FAR, BIAS, HSS, HK, ETS])
	resultPD = pd.DataFrame(data=result.transpose(), columns=['NoHit', 'NoMiss', 'NoFalse', 'POD', 'FAR', 'BIAS', 'HSS', 'HK', 'ETS'])
	return resultPD

# old_res = scipy.io.loadmat('data/global_test2.mat')['global_test2']
# new_res = np.load('data/result2.npy')

# dn1_old = datetime(2016, 12, 18); dn2_old = datetime(2017, 1, 2)
# dn1_new = datetime(2016, 12, 30); dn2_new = datetime(2017, 1, 14)

old_res = np.load('data/result6.npy')
new_res = np.load('data/result7.npy')

dn1_old = datetime(2017,1,19); dn2_old = datetime(2017,1,24)
dn1_new = datetime(2017,1,15); dn2_new = datetime(2017,1,29)


arr_1 = old_res[-5:,:,:]
arr_2 = new_res[5:10:,:,:]

FinalRes = ValidationFunction(arr_2, arr_1)
FinalRes.index = [(datetime(2017,1,20)+td(days=x)).strftime('%Y-%m-%d') for x in range(5)]

#Validate by SNOTEL

def SnotelVal(yyyy0, mm0, dd0):
	t0 = datetime(yyyy0,mm0,dd0)
	result = np.load('data/result'+t0.strftime("%Y.%m.%d")+'.npy')
	station_data, station_metadata = SnotelDownload(yyyy0, mm0, dd0,yyyy0, mm0, dd0)
	station_query = station_data[station_data['SNWD'] > 0][['Station name','ID']]
	station_positive = station_metadata[(station_metadata['site_name'].isin(station_query['Station name'])) & (station_metadata[' lat'] <= 60)][['station id', ' lat', 'lon']]
	station_query_neg = station_data[station_data['SNWD'] == 0][['Station name','ID']]
	station_negative = station_metadata[(station_metadata['site_name'].isin(station_query_neg['Station name'])) & (station_metadata[' lat'] <= 60)][['station id', ' lat', 'lon']]
	station_hit = pd.DataFrame()
	station_miss = pd.DataFrame()
	test = result[-1,:,:].copy()
	for ii, x in enumerate(station_positive[' lat']):
		[rr,cc]=latlon2pixzone(-180, 60, 0.05, 0.05, x, station_positive['lon'].values.tolist()[ii])
		if test[rr,cc] == 1:
			station_hit = station_hit.append(station_positive[(station_positive[' lat'] == x) &
																(station_positive['lon'] == station_positive['lon'].values.tolist()[ii])
															])
		else:
			station_miss = station_miss.append(station_positive[(station_positive[' lat'] == x) &
																(station_positive['lon'] == station_positive['lon'].values.tolist()[ii])
															])
	station_corneg = pd.DataFrame()
	station_false = pd.DataFrame()
	for ii, x in enumerate(station_negative[' lat']):
		[rr,cc]=latlon2pixzone(-180, 60, 0.05, 0.05, x, station_negative['lon'].values.tolist()[ii])
		if test[rr,cc] == 0:
			station_corneg = station_corneg.append(station_negative[(station_negative[' lat'] == x) &
																(station_negative['lon'] == station_negative['lon'].values.tolist()[ii])
															])
		else:
			station_false = station_false.append(station_negative[(station_negative[' lat'] == x) &
																(station_negative['lon'] == station_negative['lon'].values.tolist()[ii])
															])
	NoHit = len(station_hit)
	NoFalse = len(station_false)
	NoMiss = len(station_miss)
	NoCorrNeg = len(station_corneg)
	#Probability of Detection
	POD = NoHit/float(NoHit+NoMiss)
	#False Alarm Ratio
	FAR = NoFalse/float(NoHit+NoFalse)
	#Bias score
	BIAS = (NoHit + NoFalse)/float(NoHit + NoMiss)
	#Total
	Tot = (NoHit + NoFalse + NoMiss + NoCorrNeg)
	#Heidke skill score
	exp_ect_corr = ((NoHit+NoMiss)*(NoHit+NoFalse)+(NoCorrNeg+NoMiss)*(NoCorrNeg+NoFalse))/float(Tot)
	HSS = (NoHit+NoCorrNeg - exp_ect_corr)/float(Tot - exp_ect_corr)
	#Hanssen-Kuipers score
	HK = NoHit/float(NoHit+NoMiss) - NoFalse/float(NoFalse + NoCorrNeg)
	#Equitable threat score
	hits_rand = ((NoHit+NoMiss)*(NoHit+NoFalse))/float(Tot)
	ETS = (NoHit - hits_rand)/float(NoHit+NoMiss+NoFalse-hits_rand)
	result1 = np.vstack([NoHit, NoMiss, NoFalse, POD, FAR, BIAS, HSS, HK, ETS])
	resultPD = pd.DataFrame(data=result1.transpose(), columns=['NoHit', 'NoMiss', 'NoFalse', 'POD', 'FAR', 'BIAS', 'HSS', 'HK', 'ETS'])
	return resultPD, station_hit, station_miss, station_false, station_corneg

