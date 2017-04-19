#!/data/apps/enthought_python/2.7.3/bin/python

import os
import sys
import codecs
from datetime import datetime, timedelta as td
from CloudRemoval import CloudRemoval
import numpy as np

def downloadDir(type1, dir_name):
	if type1 == 'MOD':
		print dir_name
		os.system('wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies -r --no-parent --no-check-certificate --auth-no-challenge=on -nH --cut-dirs=1 -e robots=off --wait 1 --reject "index.html*" https://n5eil01u.ecs.nsidc.org/MOST/MOD10C1.006/'+dir_name+'/')
	elif type1 == 'MYD':
		print dir_name
		os.system('wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies -r --no-parent --no-check-certificate --auth-no-challenge=on -nH --cut-dirs=1 -e robots=off --wait 1 --reject "index.html*" https://n5eil01u.ecs.nsidc.org/MOSA/MYD10C1.006/'+dir_name+'/')

def checkRemoteDir(type1):
	if type1 == 'MOD':
		url = 'https://n5eil01u.ecs.nsidc.org/MOST/MOD10C1.006/'
		html_file = 'MOD10C1.006/index.html'
	elif type1 == 'MYD':
		url = 'https://n5eil01u.ecs.nsidc.org/MOSA/MYD10C1.006/'
		html_file = 'MYD10C1.006/index.html'
	os.system('wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --keep-session-cookies -r --no-parent --no-check-certificate --auth-no-challenge=on -nH --cut-dirs=1 '+url)
	if os.path.isfile('robots.txt'):
		os.remove("robots.txt")
	content = codecs.open(html_file,'r','utf-8').readlines()
	table_start = [i for i,x in enumerate(content) if '<table' in x][0]
	table_end = [j for j,y in enumerate(content) if '</table' in y][0]
	table = content[table_start:table_end]
	folder_list = []
	mod_list = []
	for line in table:
		if 'alt="[DIR]"' in line:
			folder_list.append(str(line.split('a href="')[1].split('/')[0]))
			mod_list.append(datetime.strptime(str(line.split('"indexcollastmod">')[1].split('</td>')[0]), "%Y-%m-%d %H:%M "))
	idx_mod_latest = [k for k, z in enumerate(mod_list) if z == max(mod_list)][0]
	mod_latest = folder_list[idx_mod_latest]
	return mod_latest

def checkLocalDir(type1, date_start, date_end):
	if type1 == 'MOD':
		path ='MOD10C1.006/'
	elif type1 == 'MYD':
		path = 'MYD10C1.006/'
	list_dir = next(os.walk(path))[1]
	for i in range((date_end - date_start).days+1):
		date_dir = (date_start+td(days=i)).strftime("%Y.%m.%d")
		if date_dir not in list_dir:
			downloadDir(type1, date_dir)

#Read the current date_range.txt file
file = 'log/date_range.txt'
if os.path.isfile(file):
	content = open(file, 'rb').readlines()
	curr_start = datetime.strptime(content[0][:-2], "%Y-%m-%d")
	curr_end = datetime.strptime(content[1][:-2], "%Y-%m-%d")
else:
	liFi = sorted(next(os.walk('MOD10C1.006/'))[1])
	curr_start = datetime.strptime(liFi[0], "%Y.%m.%d")
	curr_end = datetime.strptime(liFi[-1], "%Y.%m.%d")

#Update current directories of MOD and MYD
checkLocalDir('MOD', curr_start, curr_end)
checkLocalDir('MYD', curr_start, curr_end)

#Check MOD and MYD from nsidc https website
MOD_latest = checkRemoteDir('MOD')
MYD_latest = checkRemoteDir('MYD')

#Update current directories with latest date of MOD and MYD
checkLocalDir('MOD', curr_end, datetime.strptime(MOD_latest,"%Y.%m.%d"))
checkLocalDir('MYD', curr_end, datetime.strptime(MYD_latest,"%Y.%m.%d"))

if MOD_latest == MYD_latest:
	if datetime.strptime(MOD_latest,"%Y.%m.%d") > curr_end:
		new_curr_end = datetime.strptime(MOD_latest,"%Y.%m.%d")
		new_curr_start = new_curr_end - td(days=5)
		new_pred0 = new_curr_start - td(days=30)
		for m in range((new_pred0 - curr_start).days):
			date_del = (curr_start + td(days=m)).strftime("%Y.%m.%d")
			os.system('rm -rf MOD10C1.006/'+date_del)
			os.system('rm -rf MYD10C1.006/'+date_del)
		yyyy2 = new_curr_end.year
		mm2 = new_curr_end.month
		dd2 = new_curr_end.day
		yyyy1 = new_curr_start.year
		mm1 = new_curr_start.month
		dd1 = new_curr_start.day
		yyyy0 = new_pred0.year
		mm0 = new_pred0.month
		dd0 = new_pred0.day
		ff = open('log/date_his.txt','a')
		ff.write(new_pred0.strftime("%Y-%m-%d")+' \n')
		ff.write(new_curr_start.strftime("%Y-%m-%d")+' \n')
		ff.write(new_curr_end.strftime("%Y-%m-%d")+' \n')
		ff.write('=========================== \n')
		ff.close()
		replacements = {'yyyy0':str(yyyy0), 'mm0':str(mm0), 'dd0':str(dd0),
						'yyyy1':str(yyyy1), 'mm1':str(mm1), 'dd1':str(dd1),
						'yyyy2':str(yyyy2), 'mm2':str(mm2), 'dd2':str(dd2),
						'data/result6':'data/result'+MOD_latest}
		lines1 = []
		infile1 = open('general_code.py')
		try :
			for line in infile1:
				for src, target in replacements.iteritems():
					line = line.replace(src, target)
				lines1.append(line)
		finally:
			infile1.close()
		outfile1 = open('general_code1.py', 'w')
		try:        
			for line in lines1:
				outfile1.write(line)
		finally:
			outfile1.close()
		os.system("qsub hoang_run_hoang_code.sh")
	else:
		print "NO UPDATE"
else:
	print "NO UPDATE"