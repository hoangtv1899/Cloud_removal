#!/data/apps/enthought_python/2.7.3/bin/python

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from glob import glob
from time import time

#Snotel validation
def latlon2pixzone(xll, yll, dx, dy, lat0,lon0):
	rl = abs((yll - lat0)/dy)
	cu = abs((lon0 - xll)/dx)
	return int(round(rl)), int(round(cu))

def SnotelVal(im, yyyy0, mm0, dd0,ndays,type='res',prefix=''):
	if type == 'res':
		snow0 = 1
	elif type == 'merged':
		snow0 = 2
	t0 = datetime(yyyy0,mm0,dd0).strftime("%Y-%m-%d")
	station_data = pd.read_csv('data/stat_16111702.csv')
	station_query = station_data[(station_data['SNWD'] > 0) & (station_data['Date time']==t0)& (station_data['Lat'] <= 50)& (station_data['Lon'] > -130)& (station_data['Lon'] < -63)][['Station name','ID', 'Lat', 'Lon', 'Date time', 'SNWD']]
	station_negative = station_data[(station_data['SNWD'] == 0) & (station_data['Date time']==t0)& (station_data['Lat'] <= 50)& (station_data['Lon'] > -130)& (station_data['Lon'] < -63)][['Station name','ID', 'Lat', 'Lon', 'Date time', 'SNWD']]
	station_hit = pd.DataFrame()
	station_miss = pd.DataFrame()
	test = im.copy()
	for ii, x in enumerate(station_query['Lat']):
		[rr,cc]=latlon2pixzone(-130.75, 50.3, 0.05, 0.05, x, station_query['Lon'].values.tolist()[ii])
		if test[rr,cc] == snow0:
			station_hit = station_hit.append(station_query[(station_query['Lat'] == x) &
																(station_query['Lon'] == station_query['Lon'].values.tolist()[ii])
															])
		else:
			station_miss = station_miss.append(station_query[(station_query['Lat'] == x) &
																(station_query['Lon'] == station_query['Lon'].values.tolist()[ii])
															])
	station_corneg = pd.DataFrame()
	station_false = pd.DataFrame()
	for ii, x in enumerate(station_negative['Lat']):
		[rr,cc]=latlon2pixzone(-130.75, 50.3, 0.05, 0.05, x, station_negative['Lon'].values.tolist()[ii])
		if test[rr,cc] == 0:
			station_corneg = station_corneg.append(station_negative[(station_negative['Lat'] == x) &
																(station_negative['Lon'] == station_negative['Lon'].values.tolist()[ii])
															])
		else:
			station_false = station_false.append(station_negative[(station_negative['Lat'] == x) &
																(station_negative['Lon'] == station_negative['Lon'].values.tolist()[ii])
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
	#Critical Success Index
	CSI = NoHit/float(NoHit+NoFalse+NoMiss)
	result1 = np.vstack([NoHit, NoMiss, NoFalse, POD, FAR, BIAS, HSS, HK, ETS, CSI])
	resultPD = pd.DataFrame(data=result1.transpose(), columns=['NoHit', 'NoMiss', 'NoFalse', 'POD', 'FAR', 'BIAS', 'HSS', 'HK', 'ETS', 'CSI'])
	resultPD['Date time'] = [t0]
	resultPD['Type'] = [prefix]
	resultPD['Nod'] = [ndays]
	resultPD = resultPD[['Nod','Type','Date time', 'NoHit', 'NoMiss', 'NoFalse', 'POD', 'FAR', 'BIAS', 'HSS', 'HK', 'ETS', 'CSI']]
	return resultPD, station_hit, station_miss, station_false, station_corneg

def SnotelValMODIS(im, yyyy0, mm0, dd0,ndays,prefix=''):
	t0 = datetime(yyyy0,mm0,dd0).strftime("%Y-%m-%d")
	station_data = pd.read_csv('data/stat_16111702.csv')
	station_query = station_data[(station_data['SNWD'] > 0) & (station_data['Date time']==t0)& (station_data['Lat'] <= 50)& (station_data['Lon'] > -130)& (station_data['Lon'] < -63)][['Station name','ID', 'Lat', 'Lon', 'Date time', 'SNWD']]
	station_negative = station_data[(station_data['SNWD'] == 0) & (station_data['Date time']==t0)& (station_data['Lat'] <= 50)& (station_data['Lon'] > -130)& (station_data['Lon'] < -63)][['Station name','ID', 'Lat', 'Lon', 'Date time', 'SNWD']]
	station_hit = pd.DataFrame()
	station_miss = pd.DataFrame()
	test = im.copy()
	for ii, x in enumerate(station_query['Lat']):
		[rr,cc]=latlon2pixzone(-130.75, 50.3, 0.05, 0.05, x, station_query['Lon'].values.tolist()[ii])
		if test[rr,cc] == 2:
			station_hit = station_hit.append(station_query[(station_query['Lat'] == x) &
																(station_query['Lon'] == station_query['Lon'].values.tolist()[ii])
															])
		elif test[rr,cc] == 0:
			station_miss = station_miss.append(station_query[(station_query['Lat'] == x) &
																(station_query['Lon'] == station_query['Lon'].values.tolist()[ii])
															])
	station_corneg = pd.DataFrame()
	station_false = pd.DataFrame()
	for ii, x in enumerate(station_negative['Lat']):
		[rr,cc]=latlon2pixzone(-130.75, 50.3, 0.05, 0.05, x, station_negative['Lon'].values.tolist()[ii])
		if test[rr,cc] == 0:
			station_corneg = station_corneg.append(station_negative[(station_negative['Lat'] == x) &
																(station_negative['Lon'] == station_negative['Lon'].values.tolist()[ii])
															])
		elif test[rr,cc] == 2:
			station_false = station_false.append(station_negative[(station_negative['Lat'] == x) &
																(station_negative['Lon'] == station_negative['Lon'].values.tolist()[ii])
															])
	NoHit = len(station_hit)
	NoFalse = len(station_false)
	NoMiss = len(station_miss)
	NoCorrNeg = len(station_corneg)
	return NoHit,NoMiss,NoFalse,NoCorrNeg
	#Probability of Detection
	# POD = NoHit/float(NoHit+NoMiss)
	# #False Alarm Ratio
	# FAR = NoFalse/float(NoHit+NoFalse)
	# #Bias score
	# BIAS = (NoHit + NoFalse)/float(NoHit + NoMiss)
	# #Total
	# Tot = (NoHit + NoFalse + NoMiss + NoCorrNeg)
	# #Heidke skill score
	# exp_ect_corr = ((NoHit+NoMiss)*(NoHit+NoFalse)+(NoCorrNeg+NoMiss)*(NoCorrNeg+NoFalse))/float(Tot)
	# HSS = (NoHit+NoCorrNeg - exp_ect_corr)/float(Tot - exp_ect_corr)
	# #Hanssen-Kuipers score
	# HK = NoHit/float(NoHit+NoMiss) - NoFalse/float(NoFalse + NoCorrNeg)
	# #Equitable threat score
	# hits_rand = ((NoHit+NoMiss)*(NoHit+NoFalse))/float(Tot)
	# ETS = (NoHit - hits_rand)/float(NoHit+NoMiss+NoFalse-hits_rand)
	# #Critical Success Index
	# CSI = NoHit/float(NoHit+NoFalse+NoMiss)
	# result1 = np.vstack([NoHit, NoMiss, NoFalse, POD, FAR, BIAS, HSS, HK, ETS, CSI])
	# resultPD = pd.DataFrame(data=result1.transpose(), columns=['NoHit', 'NoMiss', 'NoFalse', 'POD', 'FAR', 'BIAS', 'HSS', 'HK', 'ETS', 'CSI'])
	# resultPD['Date time'] = [t0]
	# resultPD['Type'] = [prefix]
	# resultPD['Nod'] = [ndays]
	# resultPD = resultPD[['Nod','Type','Date time', 'NoHit', 'NoMiss', 'NoFalse', 'POD', 'FAR', 'BIAS', 'HSS', 'HK', 'ETS', 'CSI']]
#	return resultPD, station_hit, station_miss, station_false, station_corneg

def animate(i):
	arr0 = merged_map[i,:,:]
	arr1 = res_map[i,:,:]
#	im1.set_array(arr0)
	im1.set_array(np.flipud(arr0))
#	im2.set_array(arr1)
	im2.set_array(np.flipud(arr1))
	box1.set_width(-121+i)
	title1.set_text('Day: '+(t0+timedelta(days=i)).strftime('%Y-%m-%d'))
	return im1,im2,box1,title1

list_result = sorted(glob('data/result*.npy'))
list_result1 = [np.load(x) for x in list_result]
res_map = np.swapaxes(np.swapaxes(np.dstack(list_result1),0,2),1,2)
merged_map = np.load('data/merged_global101516031517.npy')[17:137,:,:]
totArea = 4937863
t0 = datetime(2016,11,1)
pos_merged = [np.sum(merged_map[i,:,:]==2)/float(totArea) for i in range(merged_map.shape[0])]
pos_res = [np.sum(res_map[i,:,:]==1)/float(totArea) for i in range(res_map.shape[0])]
lons = np.arange(-180.,180.,0.05)
lats = np.arange(-60., 60., 0.05)[::-1]
lons1, lats1 = np.meshgrid(lons,lats)

fig=plt.figure()
ax1 = plt.subplot2grid((7,6),(0,0), colspan = 6, rowspan = 3)
m1 = Basemap(llcrnrlon=-180.,llcrnrlat=-60.,urcrnrlon=180.,urcrnrlat=60.,\
				projection='mill',lon_0=0)
m1.drawcountries(linewidth=0.2)
m1.drawcoastlines(linewidth=0.3)
m1.drawparallels(np.arange(-60.,60.,30.), linewidth=0.05)
m1.drawmeridians(np.arange(-180.,180.,60.), linewidth=0.05)
cmap = LinearSegmentedColormap.from_list('mycmap', [(0 / 2., 'gray'),
															(1 / 2., 'black'),
															(2 / 2., 'white')]
												)
#im1 = m1.pcolormesh(lons1, lats1, merged_map[0,:,:],shading='flat', cmap=cmap, latlon=True)
im1 = m1.imshow(np.flipud(merged_map[0,:,:]), cmap=cmap)
ax1.set_ylabel('Merged MODIS image', fontsize=10)
cb1=m1.colorbar(im1,'right',pad='1%', ticks=[0,1,2],boundaries=[0,0.1,1.9,2])
cb1.ax.set_yticklabels(['Ground', 'Cloud', 'Snow'], size='x-small')
title1 = ax1.set_title('Day: '+t0.strftime('%Y-%m-%d'))
ax2 = plt.subplot2grid((7,6),(3,0), colspan = 6, rowspan = 3)
m2 = Basemap(llcrnrlon=-180.,llcrnrlat=-60.,urcrnrlon=180.,urcrnrlat=60.,\
				projection='mill',lon_0=0)
m2.drawcountries(linewidth=0.2)
m2.drawcoastlines(linewidth=0.3)
m2.drawparallels(np.arange(-60.,60.,30.), linewidth=0.05)
m2.drawmeridians(np.arange(-180.,180.,60.), linewidth=0.05)
#im2 = m2.pcolormesh(lons1, lats1,res_map[0,:,:],shading='flat', cmap=cmap, latlon=True)
im2 = m2.imshow(np.flipud(res_map[0,:,:]), cmap=cmap)
cb2=m2.colorbar(im2,'right',pad='1%', ticks=[0.05,1.1],boundaries=[0,0.1,2])
cb2.ax.set_yticklabels(['Ground', 'Snow'], size='x-small')
cb2.ax.tick_params(length=0)
ax2.set_ylabel('Cloud free snow cover image', fontsize=10)
ax3 = plt.subplot2grid((7,6),(6,1), colspan = 4, rowspan=1)
ax3.set_ylim(0,0.3)
ax3.set_xlim(0,120)
ax3.set_yticks([0,0.15,0.3])
labels = [item.get_text() for item in ax3.get_xticklabels()]
date_step = 120/(len(labels)-1)
for jj in range(len(labels)):
	labels[jj] = (t0 + timedelta(days=date_step*jj)).strftime('%Y-%m-%d')

ax3.set_xticklabels(labels, rotation=30, size='x-small')
ax3.set_yticklabels([0,0.15,0.3],size='x-small')
ax3.set_ylabel('POS')
ax3.plot(range(len(pos_res)),pos_res, lw=2, color='r',label='MODIS')
ax3.plot(range(len(pos_res)),pos_merged, lw=2, color='b', label='Cloud free')
ax3.legend(bbox_to_anchor=(1.01, .42), borderaxespad=0.,loc=3,prop={'size':8})
box1 = ax3.add_patch(Rectangle((121,.5),-121,-1,facecolor="#b2b9c4",\
								alpha=0.8, edgecolor="yellow", linewidth=1.2))

anim = animation.FuncAnimation(fig, animate,
                               frames=120, interval=120)
start = time()
anim.save('snow_animation.gif', writer='imagemagick', fps=3)
end = time()
print str(end-start)+' s'

###For US

def animateUS(i):
	arr0 = merged_map_US[i,:,:]
	arr1 = res_map_US[i,:,:]
	arr2 = station_hit_merged[i]
	arr3 = station_miss_merged[i]
	lat2, lon2 = arr2['Lat'].values.tolist(), arr2['Lon'].values.tolist()
	xpt2,ypt2 = m1(lon2,lat2)
	coor_hit1.set_data(xpt2, ypt2)
	lat3, lon3 = arr3['Lat'].values.tolist(), arr3['Lon'].values.tolist()
	xpt3,ypt3 = m1(lon3,lat3)
	coor_miss1.set_data(xpt3, ypt3)
	arr4 = station_hit[i]
	arr5 = station_miss[i]
	lat4, lon4 = arr4['Lat'].values.tolist(), arr4['Lon'].values.tolist()
	xpt4,ypt4 = m2(lon4,lat4)
	coor_hit2.set_data(xpt4,ypt4)
	lat5, lon5 = arr5['Lat'].values.tolist(), arr5['Lon'].values.tolist()
	xpt5,ypt5 = m2(lon5,lat5)
	coor_miss2.set_data(xpt5, ypt5)
#	im1.set_array(arr0.ravel())
#	im2.set_array(arr1.ravel())
	im1.set_array(np.flipud(arr0))
	im2.set_array(np.flipud(arr1))
	box1.set_width(-120+i)
	box2.set_width(-120+i)
	box3.set_width(-120+i)
	ylabel1.set_text('Day: '+(t0+timedelta(days=i)).strftime('%Y-%m-%d'))
	return im1,im2,box1,box2,box3,ylabel1,coor_hit1,coor_hit2,coor_miss1,coor_miss2,

list_result = sorted(glob('data/result*.npy'))
list_result1_US = [np.load(x)[194:722,984:2320] for x in list_result]
res_map_US = np.swapaxes(np.swapaxes(np.dstack(list_result1_US),0,2),1,2)
merged_map_US = np.load('data/merged_global101516031517.npy')[17:137,194:722,984:2320]
totArea_US = 334513
t0 = datetime(2016,11,1)

pos_merged_US = [np.sum(merged_map_US[i,:,:]==2)/float(totArea_US) for i in range(merged_map_US.shape[0])]
pos_res_US = [np.sum(res_map_US[i,:,:]==1)/float(totArea_US) for i in range(res_map_US.shape[0])]
#Snow validation
resultPD = []
station_hit = []
station_miss = []
resultPD_merged = []
station_hit_merged = []
station_miss_merged = []
for j in range(120):
	dt = t0+timedelta(days=j)
	print dt
	A,B,C,D,E = SnotelVal(res_map_US[j,:,:],dt.year,dt.month,dt.day,29)
	A['POD'].tolist()[0]
	resultPD.append(A)
	station_hit.append(B)
	station_miss.append(C)
	A1,B1,C1,D1,E1 = SnotelVal(merged_map_US[j,:,:],dt.year,dt.month,dt.day,29, 'merged')
	resultPD_merged.append(A1)
	station_hit_merged.append(B1)
	station_miss_merged.append(C1)

POD_res = [x['POD'].tolist()[0] for x in resultPD]
POD_merged = [x['POD'].tolist()[0] for x in resultPD_merged]
FAR_res = [x['FAR'].tolist()[0] for x in resultPD]
FAR_merged = [x['FAR'].tolist()[0] for x in resultPD_merged]

lons = np.arange(-130.75,-63.95,0.05)
lats = np.arange(23.90, 50.3, 0.05)[::-1]
lons1, lats1 = np.meshgrid(lons,lats)
##Create figure
fig_US=plt.figure()
##Plot MODIS map
ax1 = plt.subplot2grid((6,6),(0,0), colspan = 3, rowspan = 3)
m1 = Basemap(llcrnrlon=-130.75,llcrnrlat=23.90,urcrnrlon=-64.0,urcrnrlat=50.3,\
				projection='mill',lon_0=0)
x,y = m1(lons1,lats1)
lat0, lon0 = station_hit_merged[0]['Lat'].values.tolist(), station_hit_merged[0]['Lon'].values.tolist()
xpt0,ypt0 = m1(lon0,lat0)
lat1, lon1 = station_miss_merged[0]['Lat'].values.tolist(), station_miss_merged[0]['Lon'].values.tolist()
xpt1,ypt1 = m1(lon1,lat1)
m1.drawcountries(linewidth=0.35,color='y')
m1.drawcoastlines(linewidth=0.45,color='y')
m1.drawstates(linewidth=0.2,color='y')
m1.drawparallels(np.arange(-60.,60.,30.), linewidth=0.05)
m1.drawmeridians(np.arange(-180.,180.,60.), linewidth=0.05)
cmap = LinearSegmentedColormap.from_list('mycmap', [(0 / 2., 'gray'),
															(1 / 2., 'black'),
															(2 / 2., 'white')]
												)
im1 = m1.imshow(np.flipud(merged_map_US[0,:,:]), cmap=cmap)
#im1 = ax1.pcolormesh(x, y, merged_map_US[0,:,:], shading='flat', cmap=cmap)
coor_miss1 = m1.plot(xpt1,ypt1,'rx', markersize=2)[0]
coor_hit1 = m1.plot(xpt0,ypt0,'bx', markersize=2)[0]
ax1.set_title('Merged MODIS image', fontsize=10)
ylabel1 = ax1.set_ylabel('Day: '+t0.strftime('%Y-%m-%d'), fontsize=9)
ax1.bar(0,0,color='grey',label='Ground')
ax1.bar(0,0,color='black',label='Cloud')
ax1.bar(0,0,color='white',label='Snow')
ax1.legend(bbox_to_anchor=(0., -0.1, 1, 0), borderaxespad=0., ncol=3,mode='expand',loc=8,prop={'size':6})
##Plot Snow map
ax2 = plt.subplot2grid((6,6),(0,3), colspan = 3, rowspan = 3)
m2 = Basemap(llcrnrlon=-130.75,llcrnrlat=23.90,urcrnrlon=-64.0,urcrnrlat=50.3,\
				projection='mill',lon_0=0)
lat2, lon2 = station_hit[0]['Lat'].values.tolist(), station_hit[0]['Lon'].values.tolist()
xpt2,ypt2 = m2(lon2,lat2)
lat3, lon3 = station_miss[0]['Lat'].values.tolist(), station_miss[0]['Lon'].values.tolist()
xpt3,ypt3 = m2(lon3,lat3)
m2.drawcountries(linewidth=0.35,color='y')
m2.drawcoastlines(linewidth=0.45,color='y')
m2.drawstates(linewidth=0.2,color='y')
m2.drawparallels(np.arange(-60.,60.,30.), linewidth=0.05)
m2.drawmeridians(np.arange(-180.,180.,60.), linewidth=0.05)
im2 = m2.imshow(np.flipud(res_map_US[0,:,:]), cmap=cmap)
#im2 = ax2.pcolormesh(x, y, res_map_US[0,:,:], shading='flat', cmap=cmap)
coor_miss2 = m2.plot(xpt3,ypt3,'rx', markersize=2,label = 'Station miss')[0]
coor_hit2 = m2.plot(xpt2,ypt2,'bx', markersize=2,label = 'Station hit')[0]
ax2.set_title('Cloud free snow cover image', fontsize=10)
ax2.legend(bbox_to_anchor=(0., -0.1, 1, 0), borderaxespad=0., ncol=2,mode='expand',loc=8,prop={'size':6})

#Plot area percentage graph
ax3 = plt.subplot2grid((6,6),(3,0), colspan = 6, rowspan=1)
ax3.set_ylim(0,1)
ax3.set_xlim(0,120)
ax3.set_yticks([0,0.25,0.5,0.75,1])
ax3.set_xticks([])
ax3.set_yticklabels([0,0.25,0.5,0.75,1],size='xx-small')
ax3.plot(range(120),pos_res_US, lw=1.2, color='b',label='Cloud free')
ax3.plot(range(120),pos_merged_US, lw=1.2, color='r',label='MODIS')
ax3.set_ylabel('POS', fontsize=9)
ax3.legend(bbox_to_anchor=(0.77, 1.24), borderaxespad=0.,loc=2,prop={'size':6},ncol=2)
box1 = ax3.add_patch(Rectangle((120,1),-120,-1,facecolor="#b2b9c4",\
								alpha=0.9, edgecolor="yellow", linewidth=1))
#Plot POD graph
ax4 = plt.subplot2grid((6,6),(4,0), colspan = 6, rowspan=1)
ax4.set_ylim(0,1)
ax4.set_xlim(0,120)
ax4.set_yticks([0,0.25,0.5,0.75,1])
ax4.set_xticks([])
ax4.set_yticklabels([0,0.25,0.5,0.75,1],size='xx-small')
ax4.plot(range(120),POD_res, lw=1.2, color='b')
ax4.plot(range(120),POD_merged, lw=1.2, color='r')
ax4.set_ylabel('POD', fontsize=9)
box2 = ax4.add_patch(Rectangle((120,1),-120,-1,facecolor="#b2b9c4",\
								alpha=0.9, edgecolor="yellow", linewidth=1))
#Plot FAR graph
ax5 = plt.subplot2grid((6,6),(5,0), colspan = 6, rowspan=1)
ax5.set_ylim(0,1)
ax5.set_xlim(0,120)
ax5.set_yticks([0,0.25,0.5,0.75,1])
labels = [item.get_text() for item in ax5.get_xticklabels()]
date_step = 120/(len(labels)-1)
for jj in range(len(labels)):
	labels[jj] = (t0 + timedelta(days=date_step*jj)).strftime('%Y-%m-%d')

ax5.set_xticklabels(labels, rotation=30, size='xx-small')
ax5.set_yticklabels([0,0.25,0.5,0.75,1],size='xx-small')
ax5.plot(range(120),FAR_res, lw=1.2, color='b')
ax5.plot(range(120),FAR_merged, lw=1.2, color='r')
ax5.set_ylabel('FAR',fontsize=9)
box3 = ax5.add_patch(Rectangle((120,1),-120,-1,facecolor="#b2b9c4",\
								alpha=0.9, edgecolor="yellow", linewidth=1))

anim = animation.FuncAnimation(fig_US, animateUS,
                               frames=120, interval=120)
start = time()
anim.save('animation4US.gif', writer='imagemagick', fps=3)
end = time()
print str(end-start)+' s'

#Validate MODIS with snotel data
#resultPD_merged = []
station_hit_merged = []
station_miss_merged = []
station_false_merged = []
station_corneg_merged = []
for j in range(120):
	dt = t0+timedelta(days=j)
	print dt
	A1,B1,C1,D1 = SnotelValMODIS(merged_map_US[j,:,:],dt.year,dt.month,dt.day,29)
#	resultPD_merged.append(A1)
	station_hit_merged.append(A1)
	station_miss_merged.append(B1)
	station_false_merged.append(C1)
	station_corneg_merged.append(D1)

station_hit_merged = np.asarray(station_hit_merged)
station_miss_merged = np.asarray(station_miss_merged)
station_false_merged = np.asarray(station_false_merged)
station_corneg_merged = np.asarray(station_corneg_merged)

POD_merged = [x['POD'].tolist()[0] for x in resultPD_merged]
FAR_merged = [x['FAR'].tolist()[0] for x in resultPD_merged]

def animateMODIS(i):
	arr0 = merged_map_US[i,:,:]
	im1.set_array(np.flipud(arr0))
	arr2 = station_false_positive[i]
	title1.set_text('Day: '+(t0+timedelta(days=i)).strftime('%Y-%m-%d'))
	if arr2.empty:
		return im1,coor_false_miss1.set_data([], []),title1,
	lat2, lon2 = arr2['Lat'].values.tolist(), arr2['Lon'].values.tolist()
	xpt2,ypt2 = m1(lon2,lat2)
	coor_false_miss1.set_data(xpt2, ypt2)
	return im1,coor_false_miss1,title1,

##Create figure
fig_MODIS=plt.figure()
##Plot MODIS map
m1 = Basemap(llcrnrlon=-130.75,llcrnrlat=23.90,urcrnrlon=-64.0,urcrnrlat=50.3,\
				projection='mill',lon_0=0)
lat0, lon0 = station_false_positive[0]['Lat'].values.tolist(), station_false_positive[0]['Lon'].values.tolist()
xpt0,ypt0 = m1(lon0,lat0)

m1.drawcountries(linewidth=0.35,color='y')
m1.drawcoastlines(linewidth=0.45,color='y')
m1.drawstates(linewidth=0.2,color='y')
m1.drawparallels(np.arange(-60.,60.,30.), linewidth=0.05)
m1.drawmeridians(np.arange(-180.,180.,60.), linewidth=0.05)
cmap = LinearSegmentedColormap.from_list('mycmap', [(0 / 2., 'gray'),
															(1 / 2., 'black'),
															(2 / 2., 'white')]
												)
im1 = m1.imshow(np.flipud(merged_map_US[0,:,:]), cmap=cmap)
coor_false_miss1 = m1.plot(xpt0,ypt0,'rx', markersize=2)[0]
title1 = plt.title('Day: '+t0.strftime('%Y-%m-%d'))

anim = animation.FuncAnimation(fig_MODIS, animateMODIS,
                               frames=120, interval=120)
start = time()
anim.save('gif/false_positive_station_US.gif', writer='imagemagick', fps=3)
end = time()
print str(end-start)+' s'