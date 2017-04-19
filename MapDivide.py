#!/data/apps/enthought_python/2.7.3/bin/python

import os
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Polygon
#plt.style.use('ggplot')
from sklearn.cluster import Birch
import scipy.ndimage

def draw_screen_poly( lats, lons, m):
	x, y = m( lons, lats )
	xy = zip(x,y)
	poly = Polygon( xy, edgecolor='red',linewidth=.7, facecolor='none' )
	plt.gca().add_patch(poly)

def pixzone2latlon(args):
	lat0 = args[0]
	lat1 = args[1]
	lon0 = args[2]
	lon1 = args[3]
	ru = 60 - lat0*0.5
	rl = 60 - lat1*0.5
	cl = lon0*0.5 - 180
	cr = lon1*0.5 - 180
	return np.array([ru, rl, rl, ru]), np.array([cl, cl, cr, cr])

def MapDivide(GCZ_map, threshold):
	test = GCZ_map[48:288,:].copy()
	test1 = np.logical_and(test>9,test<30).astype(np.uint8)
	test1 += (test==6).astype(np.uint8)
	test1 += (test==8).astype(np.uint8)
	test3 = test1.copy()
	test2 = (test>=30).astype(np.uint8)
	x, y = np.where(test1==1)
	dataxy = np.hstack([x.reshape(-1,1), y.reshape(-1,1)])
	brc = Birch(threshold=threshold)
	brc.fit(dataxy)
	n_clusters = len(brc.subcluster_centers_)
	brc1 = Birch(threshold=threshold,n_clusters=n_clusters)
	brc1.fit(dataxy)
	L = brc1.labels_+1
	labs = np.unique(L)
	test1[x,y] = L
	coords = np.zeros((len(labs),4))
	for ii in labs:
		hk = (test1==ii)
		rows, cols = np.where(hk==True)
		[ru, rl, cl, cr] = [np.min(rows), np.max(rows), np.min(cols), np.max(cols)]
		coords[ii-1,:] = np.array([ru, rl, cl, cr])
	outliner_idx = [i1 for i1, x1 in enumerate(coords[:,0]) if x1>0]
	north_pole = [y1 for y1 in range(coords.shape[0]) if y1 not in outliner_idx]
	coords1 = coords[north_pole,:]
	coords1 = coords1[np.argsort(coords1[:,2])]
	for ik in range(coords1.shape[0]):
		if coords1[ik, 1]< 95:
			coords1[ik,1] += 1
		if ik < coords1.shape[0]-1:
			if coords1[ik,3] == coords1[ik+1,2]:
				continue
			elif coords1[ik,3] < coords1[ik+1,2]:
				if (coords1[ik+1,2] - coords1[ik,3]) > 10:
					coords1[ik,3] += 1
				else:
					coords1[ik,3] = coords1[ik+1,2]
			elif coords1[ik,3] > coords1[ik+1,2] :
				if coords1[ik,1] < coords1[ik+1,1]:
					coords1[ik,3] = coords1[ik+1,2]
				else:
					coords1[ik+1,2] = coords1[ik,3]
		else:
			coords1[ik,3] += 1
	coords[north_pole,:] = coords1
	coords[outliner_idx,0] = [x if x > 100 else x+3 for x in coords[outliner_idx,0]]
	coords[outliner_idx,:] += np.hstack([np.zeros((len(outliner_idx),1)),
										np.ones((len(outliner_idx),1)),
										np.zeros((len(outliner_idx),1)),
										np.ones((len(outliner_idx),1))])
	RecClus = np.zeros(test1.shape)
	extra = 1
	for jk in labs:
		[ru, rl, cl, cr] = coords[jk-1,:]
		app_sum = np.sum(test1[ru:rl,cl:cr]!=0)
		if app_sum > 2500:
			RecClus[ru:ru+(rl-ru)/4,cl:cr]=jk
			extra+=1
			if np.sum(test1[ru:ru+(rl-ru)/4,cl:cr]!=0) > 1000:
				RecClus[ru+(rl-ru)/8:ru+(rl-ru)/4,cl:cl+(cr-cl)/2]=labs[-1]+extra
				extra += 1
				RecClus[ru+(rl-ru)/8:ru+(rl-ru)/4,cl+(cr-cl)/2:cr]=labs[-1]+extra
				extra += 1
				RecClus[ru:ru+(rl-ru)/8,cl+(cr-cl)/2:cr]=labs[-1]+extra
				extra += 1
			RecClus[ru+(rl-ru)/4:ru+(rl-ru)/2,cl:cr]=labs[-1]+extra
			extra+=1
			if np.sum(test1[ru+(rl-ru)/4:ru+(rl-ru)/2,cl:cr]!=0) > 1000:
				RecClus[ru+(rl-ru)/4:ru+3*(rl-ru)/8,cl+(cr-cl)/2:cr]=labs[-1]+extra
				extra += 1
				RecClus[ru+3*(rl-ru)/8:ru+(rl-ru)/2,cl+(cr-cl)/2:cr]=labs[-1]+extra
				extra += 1
				RecClus[ru+3*(rl-ru)/8:ru+(rl-ru)/2,cl:cl+(cr-cl)/2]=labs[-1]+extra
				extra += 1
			RecClus[ru+(rl-ru)/2:ru+3*(rl-ru)/4,cl:cr]=labs[-1]+extra
			extra+=1
			if np.sum(test1[ru+(rl-ru)/2:ru+3*(rl-ru)/4,cl:cr]!=0) > 1000:
				RecClus[ru+5*(rl-ru)/8:ru+3*(rl-ru)/4,cl+(cr-cl)/2:cr]=labs[-1]+extra
				extra += 1
				RecClus[ru+(rl-ru)/2:ru+5*(rl-ru)/8,cl+(cr-cl)/2:cr]=labs[-1]+extra
				extra += 1
				RecClus[ru+5*(rl-ru)/8:ru+3*(rl-ru)/4,cl:cl+(cr-cl)/2]=labs[-1]+extra
				extra += 1
			RecClus[ru+3*(rl-ru)/4:rl,cl:cr]=labs[-1]+extra
			extra+=1
			if np.sum(test1[ru+3*(rl-ru)/4:rl,cl:cr]!=0) > 1000:
				RecClus[ru+3*(rl-ru)/4:ru+7*(rl-ru)/8,cl+(cr-cl)/2:cr]=labs[-1]+extra
				extra += 1
				RecClus[ru+7*(rl-ru)/8:rl,cl+(cr-cl)/2:cr]=labs[-1]+extra
				extra += 1
				RecClus[ru+7*(rl-ru)/8:rl,cl:cl+(cr-cl)/2]=labs[-1]+extra
				extra += 1
		elif app_sum > 1500 and app_sum < 2000:
			RecClus[ru:rl,cl:cl+(cr-cl)/2]=jk
			extra+=1
			if np.sum(test1[ru:rl,cl:cl+(cr-cl)/2]!=0) > 1000:
				RecClus[ru+(rl-ru)/2:rl,cl:cl+(cr-cl)/4]=labs[-1]+extra
				extra += 1
				RecClus[ru+(rl-ru)/2:rl,cl+(cr-cl)/4:cl+(cr-cl)/2]=labs[-1]+extra
				extra += 1
				RecClus[ru:ru+(rl-ru)/2,cl+(cr-cl)/4:cl+(cr-cl)/2]=labs[-1]+extra
				extra += 1
			RecClus[ru:rl,cl+(cr-cl)/2:cr]=labs[-1]+extra
			extra+=1
			if np.sum(test1[ru:rl,cl+(cr-cl)/2:cr]!=0) > 1000:
				RecClus[ru+(rl-ru)/2:rl,cl+(cr-cl)/2:cl+3*(cr-cl)/4]=labs[-1]+extra
				extra += 1
				RecClus[ru+(rl-ru)/2:rl,cl+3*(cr-cl)/4:cr]=labs[-1]+extra
				extra += 1
				RecClus[ru:ru+(rl-ru)/2,cl+3*(cr-cl)/4:cr]=labs[-1]+extra
				extra += 1
		else:
			RecClus[ru:rl,cl:cr] = jk
	new_labs0 = np.unique(RecClus)[1:]
	for ih in new_labs0:
		rows, cols = np.where(RecClus==ih)
		[ru, rl, cl, cr] = [np.min(rows), np.max(rows), np.min(cols), np.max(cols)]
		if np.sum(test1[rows, cols]!=0) < 50:
			RecClus[rows,cols]=0
	new_labs = np.unique(RecClus)[1:]
	new_coords = np.zeros((len(new_labs),4))
	for kk,lab in enumerate(new_labs):
		hk1 = (RecClus==lab)
		rows, cols = np.where(hk1==True)
		[ru, rl, cl, cr] = [np.min(rows), np.max(rows), np.min(cols), np.max(cols)]
		new_coords[kk,:] = np.array([ru, rl+1, cl, cr+1])
	lons = np.arange(-180.,180.,0.05)
	lats = np.arange(-60., 60., 0.05)[::-1]
	lons1, lats1 = np.meshgrid(lons,lats)
	f = plt.figure()
	m = Basemap(llcrnrlon=-180.,llcrnrlat=-60.,urcrnrlon=180.,urcrnrlat=60.,\
							projection='mill',lon_0=0)
	m.drawmapboundary(fill_color='0.3')
	im = scipy.ndimage.zoom(test3,10,order=0)
	cmap = LinearSegmentedColormap.from_list('mycmap', [(0 / 2., 'gray'),
														(1 / 2., 'black'),
														(2 / 2., 'white')]
											)
	im0 = m.pcolormesh(lons1, lats1, im, shading='flat', cmap=cmap, latlon=True)
	m.drawparallels(np.arange(-60.,60.,30.), linewidth=0.25)
	m.drawmeridians(np.arange(-180.,180.,60.), linewidth=0.25)
	m.drawcoastlines(linewidth=0.3,color='y')
	for hh in range(new_coords.shape[0]):
			lats2, lons2 = pixzone2latlon(new_coords[hh,:].tolist())
			draw_screen_poly(lats2, lons2, m)
	plt.show()
	L1 = scipy.ndimage.zoom(RecClus,10,order=0)
	L2 = scipy.ndimage.zoom(test2,10,order=0)
	f.savefig('map_divided.png')
	return L1, L2