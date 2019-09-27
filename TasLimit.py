# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 19:32:27 2017

@author: luowei
    ctas simulation class
"""
import TasPara as tp
import numpy as np
import SciTas as st
import pandas as pd

# take point as unit

class TasLimit():
    # input: point  (pd.Series)
    # ouput : softlimit, s1s2limit, smotor_search
    def __init__(self,point):
        self.point = point 
        # softlimit
        self.softlimit()
        self.point['soft_limit'] = self.limitsoft     
        # s1s2limit
        self.stat_s1s2 = 1         
        if tp.ModeChoice.mode == 3 or tp.ModeChoice.mode == 2:
            self.s1s2limit()
            if self.stat_s1s2 != 1 and tp.ModeChoice.mode == 3:
                self.smotor_search()
        self.point['s1s2_limit'] = self.stat_s1s2
    
    def softlimit(self):
        # s1,s2,m1,m2,a1,a2,s0
        self.limitsoft = 1
        for x in tp.TasStatus.tas_status.index:
            if x in self.point.index:
                if self.point[x] > tp.LimitRange.softlimit[x].high or \
                    self.point[x] < tp.LimitRange.softlimit[x].low :
                    self.limitsoft = tp.LimitNumb.Modenumb[tp.LimitNumb.mode]
                    break
                
    def s1s2limit(self):
        # this s1 is the rotate of sample stage
        # ? s1 range?
        self.stat_s1s2 = 1         
        s1block = tp.SampleEnviGeometry.dead_angle
        for i in range(len(s1block)):
            low = s1block[i][0]+self.point.s1
            high =s1block[i][1]+self.point.s1
            low = low - int(low/360)*360
            high = high - int(high/360)*360
            if low*high <= 0 or low >= high:
                self.stat_s1s2 = tp.LimitNumb.Modenumb[tp.LimitNumb.mode]
            if self.point.s2 >= low-180 and self.point.s2 <= high-180:
                self.stat_s1s2 = tp.LimitNumb.Modenumb[tp.LimitNumb.mode]

    def smotor_search(self):
            # scattering triangle condition
            # s1 here is physical s1
            smotordev=182
            for i in range(smotordev):
                self.point.s0 = self.point.s0-i
                self.point.s1 = self.point.s1+i
                self.s1s2limit()
                if self.stat_s1s2 != 1:
                    self.point.s0 = self.point.s0+i
                    self.point.s1 = self.point.s1-i
                    self.s1s2limit()
                    if self.stat_s1s2 == 1:
                        break
                else:
                    break


def TasLimit_df(points):
    df = pd.DataFrame()
    for x in range(len(points)):
        junk = TasLimit(points.ix[x]).point
        df = df.append(junk,ignore_index=True)
    return df
            

def Dynamic_limit(points):
    # 1. detector
    # check point
    pass    

def Double_scatt(points):
    pass


if __name__ == '__main__':
    import TasCommand as tc
    a = tc.tas_move('h',-2,'k',1)
    b = TasLimit(a.points)

    

    
    
    
    