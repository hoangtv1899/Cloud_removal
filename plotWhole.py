#!/data/apps/enthought_python/2.7.3/bin/python

import numpy as np
import pandas as pd
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import LinearSegmentedColormap
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

def plotWhole(im, name_im=None):
	lons = np.arange(-180.,180.,0.05)
	lats = np.arange(-60., 60., 0.05)[::-1]
	lons1, lats1 = np.meshgrid(lons,lats)
	f = plt.figure()
	m = Basemap(llcrnrlon=-180.,llcrnrlat=-60.,urcrnrlon=180.,urcrnrlat=60.,\
				projection='mill',lon_0=0)
	m.drawmapboundary(fill_color='0.3')
	if len(np.unique(im)) <= 3:
		cmap = LinearSegmentedColormap.from_list('mycmap', [(0 / 2., 'gray'),
                                                    (1 / 2., 'black'),
                                                    (2 / 2., 'white')]
                                        )
	else:
		cmap = plt.cm.get_cmap('RdYlBu')
	im0 = m.pcolormesh(lons1, lats1, im, shading='flat', cmap=cmap, latlon=True)
	m.drawparallels(np.arange(-60.,60.,30.), linewidth=0.25)
	m.drawmeridians(np.arange(-180.,180.,60.), linewidth=0.25)
	m.drawcoastlines(linewidth=0.3,color='y')
	plt.show()
	if not name_im:
		name_im = 'h1'
	f.savefig(name_im+'.png')
	plt.close(f)


def plotWholeMult(im1, im2, im3, name_im=None):
	list_arr = [im1, im2, im3]
	f = plt.figure()
	for ii in range(1,6):
		for jj in range(3):
			ax = f.add_subplot(5,3,3*(ii-1)+jj+1)
			m = Basemap(llcrnrlon=-180.,llcrnrlat=-60.,urcrnrlon=180.,urcrnrlat=60.,\
						projection='mill',lon_0=0)
			m.drawmapboundary(fill_color='0.3')
			im = list_arr[jj][ii-1,:,:]
			if len(np.unique(im)) <= 3:
				cmap = LinearSegmentedColormap.from_list('mycmap', [(0 / 2., 'gray'),
															(1 / 2., 'black'),
															(2 / 2., 'white')]
												)
			else:
				cmap = plt.cm.get_cmap('RdYlBu')
			m.imshow(np.flipud(im), cmap=cmap)
			m.drawparallels(np.arange(-60.,60.,30.), linewidth=0.25)
			m.drawmeridians(np.arange(-180.,180.,60.), linewidth=0.25)
			m.drawcoastlines(linewidth=0.3,color='y')
	plt.show()
	if not name_im:
		name_im = 'h1'
	f.savefig(name_im+'.png')
	plt.close(f)


def plotSnotel(station_positive, station_negative, im, name_im=None):
	f = plt.figure()
	m = Basemap(llcrnrlon=-130.75,llcrnrlat=23.90,urcrnrlon=-64.05,urcrnrlat=50.3,\
				projection='mill',lon_0=0)
	lons = np.arange(-130.75,-63.95,0.05)
	lats = np.arange(23.90, 50.3, 0.05)[::-1]
	lons1, lats1 = np.meshgrid(lons,lats)
	m.drawparallels(np.arange(-60.,60.,30.), linewidth=0.25)
	m.drawmeridians(np.arange(-180.,180.,60.), linewidth=0.25)
	m.drawcoastlines(linewidth=0.4)
	m.drawcountries(linewidth=0.4)
	m.drawstates(linewidth=0.1)
	if len(np.unique(im)) <= 3:
		cmap = LinearSegmentedColormap.from_list('mycmap', [(0 / 2., 'gray'),
                                                    (1 / 2., 'black'),
                                                    (2 / 2., 'white')]
                                        )
	else:
		cmap = plt.cm.get_cmap('RdYlBu')
	m.pcolormesh(lons1, lats1, im, shading='flat', cmap=cmap, latlon=True)
	lat, lon = station_positive['Lat'].values.tolist(), station_positive['Lon'].values.tolist()
	xpt,ypt = m(lon,lat)
	pos_val = station_positive['SNWD']
	lat1, lon1 = station_negative['Lat'].values.tolist(), station_negative['Lon'].values.tolist()
	xpt1,ypt1 = m(lon1,lat1)
	m.plot(xpt,ypt,'bx', markersize=2)
	m.plot(xpt1,ypt1,'rx', markersize=2)
	plt.show()
	if not name_im:
		name_im = 'h1'
	f.savefig(name_im+'.png')
	plt.close(f)