#!/data/apps/enthought_python/2.7.3/bin/python

import os
import numpy as np
from datetime import datetime, date, timedelta as td
from StringIO import StringIO
from gzip import GzipFile
import gzip
from urllib2 import urlopen
import csv

def GetClimateZone():
	try:
		url = urlopen('http://koeppen-geiger.vu-wien.ac.at/data/1976-2000_ASCII.txt.gz')
		compFile = StringIO()
		compFile.write(url.read())
		compFile.seek(0)
		decompFile = GzipFile(fileobj=compFile, mode='rb')
		content = decompFile.readlines()
	except:
		compFile = 'data/1976-2000_ASCII.txt.gz'
		f = gzip.open(compFile,'rb')
		content = f.readlines()
	lats=[]
	lons=[]
	cls=[]
	for i, line in enumerate(content):
		if i>1:
			ext_line = filter(None,line.replace('\r\n','').split(' '))
			lats.append(float(ext_line[0]))
			lons.append(float(ext_line[1]))
			cls.append(ext_line[2])
	classes = np.unique(cls)
	num_cls=[]
	for class1 in cls:
		idx = int(np.where(classes==class1)[0])+1
		num_cls.append(idx)
	ulx = np.min(lons)
	uly = np.max(lats)
	lrx = np.max(lons)
	lry = np.min(lats)
	rangex = int((lrx+.5-ulx)/.5)
	rangey = int((uly+.5-lry)/.5)
	GCZ_map = np.zeros((rangey,rangex)).astype(np.int8)
	for j, lon in enumerate(lons):
		idx = int((lon-ulx)/.5)
		idy = int((uly-lats[j])/.5)
		GCZ_map[idy,idx] = num_cls[j]
	return GCZ_map, classes