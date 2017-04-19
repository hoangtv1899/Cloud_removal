#!/data/apps/enthought_python/2.7.3/bin/python

import scipy.io
import os
import numpy as np
import gdal
from glob import glob
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from sklearn.ensemble import RandomForestClassifier

fileP = 'Landsat/'
listF = sorted(glob(fileP+'*.TIF'))
list_band = ['B1','B2','B3','B4','B5','B6_VCID_1','B6_VCID_2','B7','B8']
listN = []
for band in list_band:
	same_band = [x for x in listF if band in x]
	listN.append('Landsat/final_'+band+'.tif')
	os.system('gdal_merge.py -o Landsat/final_'+band+'.tif -co "COMPRESS=LZW" '+same_band[0]+' '+same_band[1])
ds0 = gdal.Open(listF[0])
totBand = np.zeros((ds0.ReadAsArray().shape))
for i,file in enumerate(listF):
	if i in [3,4,5]:
		ds = gdal.Open(file).ReadAsArray()
		totBand += ds

weights={1:4, 2:3, 3:2, 4:1}
rf = RandomForestClassifier(class_weight=weights, n_estimators=100, criterion='gini',\
							max_depth=4, min_samples_split=2, min_samples_leaf=1, max_features='auto',\
							bootstrap=True, oob_score=True, n_jobs=-1, random_state=None, verbose=True)

train_arr = np.zeros((totBand.shape))

#manual collect training points
train_arr[1760:1940,6230:6290] = 1
train_arr[2020:2160,6575:6615] = 1
train_arr[3920:4040,2895:2940] = 1
train_arr[920:950,2900:2914] = 1
train_arr[2370:2400, 3812:3826] = 1
train_arr[3860:3960,1270:1290] = 1
train_arr[5820:5870, 345:385] = 1

train_arr[5440:5580,4335:4375] = 2
train_arr[3090:3110,4646:4655] = 2
train_arr[4680:4880, 6840:6960] = 2
train_arr[1000:1100, 7500:7590] = 2

train_arr[1100:1400,220:400] = 3
train_arr[420:600,7100:7280] = 3
train_arr[1150:1350,4160:4340] = 4
train_arr[3060:3260,1860:2000] = 4

rf.fit(totBand[train_arr>0].reshape(-1,1), train_arr[train_arr>0].reshape(-1,1))

result = rf.predict(totBand.reshape(-1,1))
result = result.reshape(train_arr.shape)
