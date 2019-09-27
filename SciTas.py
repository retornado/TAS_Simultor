# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 23:36:44 2017

@author: luowei
test class

"""
import TasPara as tp
# from mantid.geometry import OrientedLattice
from mantid.geometry import OrientedLattice
import math
import pandas as pd
import TasLimit as tl

class Monochromator():
    # only for PG
    __slots__ = ['lambdan','tth','en']
    def __init__(self,reflect=[0,0,2],**kargs):
        self.kargs = kargs
        self.pgo = OrientedLattice(2.461,2.461,6.708,90,90,60)
        self.q = self.pgo.qFromHKL(reflect).norm()        
        if 'lambdan' in self.kargs.keys():
            self.lambdan = self.kargs['lambdan']
            self.en = (9.045/self.lambdan)**2
            self.k = 2*math.pi/self.lambdan
            self.lambda2m2()
        if 'tth' in self.kargs.keys():
            self.tth = abs(self.kargs['tth'])
            self.monolambda()
        if 'en' in self.kargs.keys():
            self.en = self.kargs['en']
            self.lambdan = 9.045/(math.sqrt(self.en))
            self.k = 2*math.pi/self.lambdan
            self.lambda2m2()
    
    def lambda2m2(self):
        stth=self.q/2.0/self.k
        self.tth=math.asin(stth)*360/math.pi

    def monolambda(self):
        self.k=self.q/2/math.sin(self.tth*math.pi/360)
        self.lambdan=2*math.pi/self.k
        self.en=(9.045/self.lambdan)**2

class Alignment():
     # the s1 is physical s1
     # ? physical s1 range? (-180,180)
      para = [5.1200,5.1200,5.1200,90.0000,90.0000,90.0000]
      index = ['h','k','l','s1','s2']
      s0 = 0
      refa = pd.Series([0.0000,4.0000,0.0000,41.4400,-117.1200],index = index)
      refb = pd.Series([4.0000,0.0000,0.0000,-48.5600,-117.1200],index = index)
      # refa:  along ki direction
      # delta : angle between refa and ki direction
      #         + : right   /  - : left
      # s2 + : s1 = -delta - 90 + s2/2
      # s2 - : s1 = -delta + 90 + s2/2
      delta = refa.s2/2.0 - refa.s1 - 90*refa.s2/abs(refa.s2)
      try:
          delta = delta + tp.TasStatus.tas_status.s0
      except:
          pass 
    
class Scisoft():
    def __init__(self,point):
        # input  : qe
        # output : qe+tas
        self.point = point
        self.qe_para()
        self.qe_limit()
        if self.limit_qe == 1:   
            self.scisoft()
            if tp.ModeChoice.mode == 3:
                # add sample stick rotation s0
                self.scisoft_premium()
                self.tas = tl.TasLimit(self.tas).point
            else:
                self.tas = tl.TasLimit(self.tas).point
        else:            
            self.tas = pd.Series(data = None,index = tp.TasStatus.tas_status.index.drop(['mts','sta','dtx']).copy())
            self.tas['s1s2_limit'] = 1
            self.tas['soft_limit'] = 1
        self.tas['qe_limit'] = self.limit_qe
            # raise Exception as
    
    def qe_para(self):
        self.orien = OrientedLattice(*Alignment.para)
        self.para = Alignment.para
        self.hkl = [self.point.h,self.point.k,self.point.l]
        self.len = self.orien.qFromHKL(self.hkl).norm()
        self.mono = Monochromator(en = self.point.ei)
        self.ana = Monochromator(en = self.point.ef)
        
    def qe_limit(self):
        if self.mono.k+self.ana.k < self.len:
            self.limit_qe = tp.LimitNumb.Modenumb[tp.LimitNumb.mode]
        else:
            self.limit_qe = 1
        
    def angdif(self):
        # angle between point and refa
        p0 = self.hkl
        p1 = Alignment.refa
        p2 = Alignment.refb
        theta1 = self.orien.recAngle(p0[0],p0[1],p0[2],p1.h,p1.k,p1.l)
        valcos1 = math.cos(math.radians(theta1))
        theta2 = self.orien.recAngle(p0[0],p0[1],p0[2],p2.h,p2.k,p2.l)
        valcos2 = math.cos(math.radians(theta2))
        if valcos1*valcos2 == 0:
            self.angdiff=theta1*(valcos1+valcos2)
        else:
            self.angdiff=theta1*abs(valcos2)/valcos2	
        
    def scisoft(self):
        s2_value=(self.mono.k**2+self.ana.k**2-self.len**2)/2.0/self.mono.k/self.ana.k
        self.tth=math.degrees(math.acos(s2_value))
        self.angdif()
        s2 = self.tth*tp.TasConfig.tas_config.s
        s1dif=(self.mono.k**2-self.ana.k**2+self.len**2)/2.0/self.mono.k/self.len
        s1dif=math.acos(s1dif)
        s1dif=s1dif*180/math.pi
        s1=-1*Alignment.delta-self.angdiff-s1dif*tp.TasConfig.tas_config.s
        index = ['m1','m2','s1','s2','a1','a2']
        self.tas = pd.Series(data=[self.mono.tth/2,self.mono.tth,s1,s2,self.ana.tth/2,self.ana.tth],index = index)
        
    def s1p_split(self):
        # s0 first : magnet
        # s1 first : crystat
        s1p = self.tas.s1
        delta_s1p = s1p - (tp.TasStatus.tas_status.s1+tp.TasStatus.tas_status.s0)
        if tp.SplitMode.mode == 0:
            s0 = tp.TasStatus.tas_status.s0 + delta_s1p
            s1 = tp.TasStatus.tas_status.s1
        elif tp.SplitMode.mode == 1:
            s1 = tp.TasStatus.tas_status.s1 + delta_s1p
            s0 = tp.TasStatus.tas_status.s0
        return pd.Series(data=[s0,s1],index = ['s0','s1'])
    
    def scisoft_premium(self):
        junk = self.tas
        addition = self.s1p_split()
        junk.pop('s1')
        self.tas = junk.append(addition)

# definition of the one_value section at sample stage
def range180(x):
    # (-180,180]
    x = range360(x)
    if x > 180:
        x = x - 360
    return x

def range360(x):
    # [0,360)
    if x < 0:
        x = x - math.ceil(x/360)*360
    else:
        x = x - math.floor(x/360)*360
    return x
    
if __name__ == '__main__':
    # test scisoft
    a = pd.Series(data = [1,1,0,10,10],index = tp.TasQe.tas_qe.index)
    b = pd.Series(data = [5,2,0,10,10],index = a.index)
    sa = Scisoft(a)
    sb = Scisoft(b)


    
    



    


      
      

      
      
            
        
