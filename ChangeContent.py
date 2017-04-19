#!/data/apps/enthought_python/2.7.3/bin/python

import os
import time
import numpy as np
from datetime import date, datetime, timedelta
import sys

date1 = sys.argv[1]
print date1
fileIn1 = '../general_code.py'
fileIn2 = '../hoang_run_hoang_code.sh'
labels = np.array([  1,   2,   3,   4,   5,   6,   7,   8,   9,  10,  11,
        12,  14,  15,  16,  17,  18,  19,  21,  22,  23,  24,
        25,  27,  28,  29,  31,  32,  33,  34,  35,  36,  37,
        38,  39,  41,  42,  43])

for i in labels:
	fileOut1 = '../mini/general_code_'+str(int(i))+'_'+date1+'.py'
	fileOut2 = '../mini/hoang_run_hoang_code_'+str(int(i))+'_'+date1+'.sh'
	dt = [str(int(x)) for x in date1.split('-')]
	replacements1 = {'dt.year':dt[0],'dt.month':dt[1],'dt.day':dt[2],'labeli':str(i)}
	replacements2 = {'Glob_xx':'G'+str(int(i))+'_'+''.join(dt)[2:],\
					'general_code.py':'general_code_'+str(int(i))+'_'+date1+'.py'}
	
	lines1 = []
	with open(fileIn1,'r') as infile1:    
		for line in infile1:
			for src, target in replacements1.iteritems():
				line = line.replace(src, target)
			lines1.append(line)
    
	with open(fileOut1, 'w') as outfile1:     
		for line in lines1:
			outfile1.write(line)
	
	lines2 = []
	with open(fileIn2,'r') as infile2:    
		for line in infile2:
			for src, target in replacements2.iteritems():
				line = line.replace(src, target)
			lines2.append(line)
    
	with open(fileOut2, 'w') as outfile2:     
		for line in lines2:
			outfile2.write(line)
	
	os.system('qsub '+fileOut2)
#	os.remove(fileOut1)
#	os.remove(fileOut2)
	
	
