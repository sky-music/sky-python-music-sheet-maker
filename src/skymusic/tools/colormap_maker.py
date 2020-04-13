# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 18:08:40 2019

@author: jmmelkon
"""

from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np

mycm = cm.get_cmap('viridis',7)

#vals = mycm(np.arange(7))*255
#vals = vals[:,0:3]

for i in range(7):
    print('rgb'+str((int(mycm(i)[0]*255), int(mycm(i)[1]*255), int(mycm(i)[2]*255))))

bar = np.arange(7)
bar = np.vstack((bar,bar))

fig = plt.figure()

ax = fig.gca()

ax.imshow(bar, aspect='auto', cmap=mycm)