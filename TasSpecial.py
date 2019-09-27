# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 06:55:12 2017

@author: luowei
"""

import SciTas as st
import pandas as pd
import numpy as np
import TasCommand as tc
import matplotlib.pyplot as plt
# special function

# 1. reciprocal avaiable range


class PointsCreat():
    
    df = pd.DataFrame()
    

class ReciRange():
    # input : qe df 
    # output : + tas + limit
    def __init__(self,df):
        self.points = df
        self.len = len(df)
        df2 = pd.DataFrame()
        for x in self.points.index:
            junk = st.Scisoft(df.ix[x])
            now_ctas = junk.tas
            # adjust to tas configuration
            tc.ctas_config_adjust(now_ctas)
            df2 = df2.append(now_ctas,ignore_index=True)
        self.points= self.points.combine_first(df2)
    
    def plot(self):
        # 1 . qe limit
        # 2. soft limit
        # 3. s1s2 limit
        qe_limit_points = self.points[self.points.qe_limit == 0]
        soft_limit_points = self.points[self.points.soft_limit == 0]
        s1s2_limit_points = self.points[self.points.s1s2_limit == 0]
        plt.scatter(s1s2_limit_points.h,s1s2_limit_points.k,marker='*', color='green')
        plt.scatter(soft_limit_points.h,soft_limit_points.k,marker='*', color='black')
        plt.scatter(qe_limit_points.h,qe_limit_points.k,marker='*', color='blue')
       


startp = -4
endp = 4
step = 0.125
npoints = int((endp-startp)/step+1)
h = np.linspace(startp, endp, npoints)
k = np.linspace(startp, endp, npoints)
X, Y = np.meshgrid(h,k)
X1 = list(X.reshape(npoints**2,1))
Y1 = list(Y.reshape(npoints**2,1))
X2 = [float(x) for x in X1]
Y2 = [float(x) for x in Y1]

df = pd.DataFrame()
df['h'] = X2
df['k'] = Y2
df['l'] = 0
df['ei'] = 9
df['ef'] = 9
df = df.drop(df[df.h == 0][df.k == 0].index)
df = df.reset_index(drop=True)
a = ReciRange(df)
#df2 = tc.orderlist('./nightscan').points
a.plot()
#plt.scatter(df2.h,df2.k,marker='+', color='red')
#plt.savefig('./test.eps', format='eps',dpi = 1000,bbox_inches='tight') 
plt.show()
