#!/data/apps/enthought_python/2.7.3/bin/python

from urllib import urlretrieve
import zipfile
import pandas as pd
from datetime import datetime
from glob import glob

#blend_data_url = 'http://www.ecad.eu/utils/downloadfile.php?file=download/ECA_blend_sd.zip'
#non_blend_data_url = 'http://www.ecad.eu/utils/downloadfile.php?file=download/ECA_nonblend_sd.zip'

#blend_handle, _ = urlretrieve(blend_data_url)
blend_handle = 'data/ECA_blend_sd.zip'
non_blend_handle = 'data/ECA_nonblend_sd.zip'
blend_dir = 'data/ECA_blend_sd/'
non_blend_dir = 'data/ECA_nonblend_sd/'

blend_zipfile = zipfile.ZipFile(blend_handle,'r')
blend_zipfile.extractall(blend_dir)
blend_zipfile.close()

non_blend_zipfile = zipfile.ZipFile(non_blend_handle,'r')
non_blend_zipfile.extractall(non_blend_dir)
non_blend_zipfile.close()

#Create metadata table from sources.txt
blend_source_file = blend_dir+'sources.txt'
f_blend = open(blend_source_file,'r').readlines()
f_blend_idx = [i for i, line in enumerate(f_blend) if 'STAID, SOUID' in line][0]
blend_meta = pd.read_csv(blend_source_file, skiprows=f_blend_idx, sep=',')
blend_meta.columns = [filter(None, x.split(' '))[0] for x in blend_meta.columns.tolist()]
blend_meta['SOUNAME'] = [' '.join(filter(None, x.split(' '))) for x in blend_meta['SOUNAME'].tolist()]
blend_meta['PARNAME'] = [' '.join(filter(None, x.split(' '))) for x in blend_meta['PARNAME'].tolist()]
blend_meta['LAT'] = [round(float(x.split(':')[0])+float(x.split(':')[1])/60+float(x.split(':')[2])/3600,3) for x in blend_meta['LAT'].tolist()]
blend_meta['LON'] = [round(float(x.split(':')[0])+float(x.split(':')[1])/60+float(x.split(':')[2])/3600,3) for x in blend_meta['LON'].tolist()]
blend_meta['START'] = [str(x)[:4]+'-'+str(x)[4:6]+'-'+str(x)[6:] for x in blend_meta['START'].tolist()]
blend_meta['STOP'] = [str(x)[:4]+'-'+str(x)[4:6]+'-'+str(x)[6:] for x in blend_meta['STOP'].tolist()]

non_blend_source_file = non_blend_dir+'sources.txt'
f_non_blend = open(non_blend_source_file,'r').readlines()
f_non_blend_idx = [i for i, line in enumerate(f_non_blend) if 'SOUID,SOUNAME' in line][0]
non_blend_meta = pd.read_csv(non_blend_source_file, skiprows=f_non_blend_idx, sep=',')
non_blend_meta.columns = [filter(None, x.split(' '))[0] for x in non_blend_meta.columns.tolist()]
non_blend_meta = non_blend_meta[np.isnan(non_blend_meta['START'])==False]
non_blend_meta['SOUNAME'] = [' '.join(filter(None, x.split(' '))) for x in non_blend_meta['SOUNAME'].tolist()]
non_blend_meta['PARNAME'] = [' '.join(filter(None, x.split(' '))) for x in non_blend_meta['PARNAME'].tolist()]
non_blend_meta['LAT'] = [round(float(x.split(':')[0])+float(x.split(':')[1])/60+float(x.split(':')[2])/3600,3) for x in non_blend_meta['LAT'].tolist()]
non_blend_meta['LON'] = [round(float(x.split(':')[0])+float(x.split(':')[1])/60+float(x.split(':')[2])/3600,3) for x in non_blend_meta['LON'].tolist()]
non_blend_meta['START'] = [str(x)[:4]+'-'+str(x)[4:6]+'-'+str(x)[6:8] for x in non_blend_meta['START'].tolist()]
non_blend_meta['STOP'] = [str(x)[:4]+'-'+str(x)[4:6]+'-'+str(x)[6:8] for x in non_blend_meta['STOP'].tolist()]

blist = sorted(glob(blend_dir+'SD*.txt'))
bdf = pd.DataFrame([], columns=['STAID','SOUID','DATE','SD','Q_SD'])

for file in blist:
	f = open(file,'r').readlines()
	idx = [jj for jj, y in enumerate(f) if 'STAID, SOUID' in y][0]
	df1 = pd.read_csv(file, skiprows=idx, sep=',')
	df1.columns = [filter(None, x.split(' '))[0] for x in df1.columns.tolist()]
	bdf = bdf.append(df1)

nlist = sorted(glob(non_blend_dir+'SD*.txt'))
ndf = pd.DataFrame([], columns=['STAID','SOUID','DATE','SD','Q_SD'])

for file in nlist:
	f = open(file,'r').readlines()
	idx = [jj for jj, y in enumerate(f) if 'STAID,    SOUID' in y][0]
	df2 = pd.read_csv(file, skiprows=idx, sep=',')
	df2.columns = [filter(None, x.split(' '))[0] for x in df2.columns.tolist()]
	ndf = ndf.append(df2)
	
	
	
	
	
	
	
	
	
	
	
	
	
	


