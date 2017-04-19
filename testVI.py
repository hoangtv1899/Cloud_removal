#!/data/apps/enthought_python/2.7.3/bin/python

import os
from datetime import date
import scipy.io
import numpy as np
from ClearCloud import ClearCloud
from GetVICoef import GetVICoef

#oyscacld89f4 = scipy.io.loadmat('usoyscacld89f4.mat')['usoyscacld89f4'].swapaxes(2,0).swapaxes(2,1)
#date_start = [date(2007,3,24)]*10+[date(2007,3,20)]*10+[date(2007,3,10)]*10
#date_end = [date(2007,3,28)]*10+[date(2007,3,30)]*20
#oyscacld67fi = ClearCloud(oyscacld89f4, date(2008,10,1), date(2009,1,1), date(2009,1,10))
#scipy.io.savemat('caoyscacld67fi_py.mat', mdict={'caoyscacld67fi_py':oyscacld67fi})
c = np.load('c010109.npy')
h = np.load('h010109.npy')
coef = GetVICoef(c,h,0)
np.save('coef_test',coef)
