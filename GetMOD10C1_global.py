#!/data/apps/enthought_python/2.7.3/bin/python

import os
import numpy as np
import urllib, urllib2
from pyhdf.SD import SD, SDC
from datetime import datetime, date, timedelta as td

def DownWriteJr(dir1,sca,cld):
#	list_files = urllib.urlopen(ftp_path+dir1).read().splitlines()
#	hdf_file1 = [x for x in list_files if ('.hdf' in x and '.xml' not in x)]
#	hdf_file = hdf_file1[0].split(' ')[-1]
#	f=urllib2.urlopen(ftp_path+dir1+'/'+hdf_file)
#	with open('tempdata/'+hdf_file, "wb") as code:
#		code.write(f.read())
#	print 'download complete'
	list_files = next(os.walk(dir1))[2]
	hdf_file = [x for x in list_files if os.path.splitext(x)[1] == '.hdf'][0]
#	hf = SD('tempdata/'+hdf_file, SDC.READ)
	hf = SD(dir1+'/'+hdf_file, SDC.READ)
	mydsca = hf.select('Day_CMG_Snow_Cover')[:][600:3000,:]
	mydcld = hf.select('Day_CMG_Cloud_Obscured')[:][600:3000,:]
	sca = np.concatenate([sca, mydsca.reshape(-1,2400,7200)],axis=0)
	cld = np.concatenate([cld, mydcld.reshape(-1,2400,7200)],axis=0)
	return sca, cld

def DownWrite(mydsca, mydcld, modsca, modcld, dn, n, t):
	if n == 1:
		return mydsca, mydcld, modsca, modcld
	for i in range(t,n):
		ids = datetime.strftime(dn + td(days=i), '%Y.%m.%d')
		print '========'+ids+'========='
#		ftp_path = 'ftp://n5eil01u.ecs.nsidc.org'
		myddir = 'MYD10C1.006/' + ids
		moddir = 'MOD10C1.006/' + ids
		try:
#			mydsca, mydcld = DownWriteJr(myddir, ftp_path, mydsca, mydcld)
			mydsca, mydcld = DownWriteJr(myddir, mydsca, mydcld)
		except:
			print myddir
			mydsca = np.concatenate([mydsca, np.zeros((2400,7200)).reshape(-1,2400,7200)],axis=0)
			mydcld = np.concatenate([mydcld, np.zeros((2400,7200)).reshape(-1,2400,7200)],axis=0)
			pass
		try:
#			modsca, modcld = DownWriteJr(moddir, ftp_path, modsca, modcld)
			modsca, modcld = DownWriteJr(moddir, modsca, modcld)
		except:
			print moddir
			modsca = np.concatenate([modsca, np.zeros((2400,7200)).reshape(-1,2400,7200)],axis=0)
			modcld = np.concatenate([modcld, np.zeros((2400,7200)).reshape(-1,2400,7200)],axis=0)
			pass
#	os.system('rm tempdata/*.hdf')
	return mydsca, mydcld, modsca, modcld


def GetMOD10C1_global(yyyy0, mm0, dd0, yyyy1, mm1, dd1):
	if os.path.isfile('log/date_range.txt'):
		[dn0_old, dn1_old] = [datetime.strptime(x.split(' ')[0], '%Y-%m-%d') for x in open('log/date_range.txt','rb').readlines()]
	else:
		dn1_old = datetime(1900,1,1)
		dn0_old = datetime(1900,1,1)
	dn0 = datetime(yyyy0, mm0, dd0)
	dn1 = datetime(yyyy1, mm1, dd1)
	if dn0 > dn1_old:
		camydsca =np.array([]).reshape(0,2400,7200)
		camydcld =np.array([]).reshape(0,2400,7200)
		camodsca =np.array([]).reshape(0,2400,7200)
		camodcld =np.array([]).reshape(0,2400,7200)
		return DownWrite(camydsca, camydcld, camodsca, camodcld, dn0, (dn1-dn0).days+1, 0)
	elif os.path.isfile('data/mydsca.npy'):
		camydsca = np.load('data/mydsca.npy')
		camydcld = np.load('data/mydcld.npy')
		camodsca = np.load('data/modsca.npy')
		camodcld = np.load('data/modcld.npy')
		camydsca = camydsca[(dn0 - dn0_old).days:,:,:]
		camydcld = camydcld[(dn0 - dn0_old).days:,:,:]
		camodsca = camodsca[(dn0 - dn0_old).days:,:,:]
		camodcld = camodcld[(dn0 - dn0_old).days:,:,:]
		return DownWrite(camydsca, camydcld, camodsca, camodcld, dn1_old, (dn1-dn1_old).days+1, 1)
	else:
		camydsca =np.array([]).reshape(0,2400,7200)
		camydcld =np.array([]).reshape(0,2400,7200)
		camodsca =np.array([]).reshape(0,2400,7200)
		camodcld =np.array([]).reshape(0,2400,7200)
		return DownWrite(camydsca, camydcld, camodsca, camodcld, dn0, (dn1-dn0).days+1, 0)

