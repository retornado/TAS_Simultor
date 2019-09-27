# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 16:43:45 2017

@author: luowei
nuclear struct factor from .cif file

for magnetic?
# Element symbol, x, y, z (fractional coordinates), occupancy (between 0 and 1) and isotropic atomic displacement parameter
silicon = CrystalStructure("5.431 5.431 5.431", "F d -3 m", "Si 0 0 0 1.0 0.05")
generator = ReflectionGenerator(silicon)
# 0.7 3.0 is d value  : need to change to k

"""
from mantid.geometry import ReflectionGenerator, ReflectionConditionFilter
from mantid.kernel import V3D
import numpy as np
import pandas as pd
from mantid.simpleapi import CreateSampleWorkspace,LoadCIF
import matplotlib.patches as mpatches
from SciTas import Monochromator

class StructFactor():
    def __init__(self,cif_file,qrange=[1,6],unique = False):
        self.cif = cif_file
        self.qrange = qrange
        self.unique = unique
        self.structf()
    
    def structf(self):
        sample_ws = CreateSampleWorkspace()
        LoadCIF(sample_ws, self.cif)
        self.sample = sample_ws.sample().getCrystalStructure()
        self.generator = ReflectionGenerator(self.sample)
        if self.unique == True:
            hkls = self.generator.getUniqueHKLsUsingFilter(self.qrange[0],self.qrange[1], ReflectionConditionFilter.StructureFactor)
        else:
            hkls = self.generator.getHKLsUsingFilter(self.qrange[0],self.qrange[1], ReflectionConditionFilter.StructureFactor)
        
        pg = self.sample.getSpaceGroup().getPointGroup()       

        df = pd.DataFrame(data = np.array(hkls),columns = list('hkl'))

        df['d(A)'] = self.generator.getDValues(hkls)
        df['F^2'] = self.generator.getFsSquared(hkls)
        df['hkl'] = hkls
        df['M'] = df['hkl'].map(lambda x : len(pg.getEquivalents(x)))
        df['II_powder'] = df['F^2']*df['M']
        df['q'] = 2*np.pi/df['d(A)']
        df['qh'] = df['h'].map(lambda x : np.sign(x)*2*np.pi/self.generator.getDValues([V3D(x,0,0)])[0])
        df['qk'] = df['k'].map(lambda x : np.sign(x)*2*np.pi/self.generator.getDValues([V3D(0,x,0)])[0])
        df['ql'] = df['l'].map(lambda x : np.sign(x)*2*np.pi/self.generator.getDValues([V3D(0,0,x)])[0])
        self.data = df

class Powder_ring(StructFactor):
    def __init__(self,cif_file,qrange = [1,6],unique = True):
        StructFactor.__init__(self,cif_file,qrange = qrange,unique = unique)
    
    def plot(self,ax,nring=5,color='red'):
        df = self.data.sort_values(by = 'II_powder',ascending=False).reset_index(drop = True)
        numb = min(len(df),nring)
        for x in range(numb):
            width = df.ix[x]['II_powder']/df['II_powder'].max()/20.0
            alpha = 0.2*df.ix[x]['II_powder']/df['II_powder'].max()
            wdg = mpatches.Wedge((0,0),df.ix[x]['q'],0,360,width=width,alpha = alpha,color = color)
            ax.add_patch(wdg) 

class limit_range(Monochromator):
    # s2s1 limit range
    def __init__(self,reflect = [0,0,2],**kargs):
        Monochromator.__init__(self,reflect= reflect,**kargs)
        s2limit = [10,120]
        self.q0 = self.tth2q(s2limit[0])
        self.q1 = self.tth2q(s2limit[1])
    
    def plot(self,ax,color = 'yellow',s1limit = [0,360]):
        wdg = mpatches.Wedge((0,0),self.q1,s1limit[0],s1limit[1],width=self.q1-self.q0,alpha = 0.1,color = color)
        ax.add_patch(wdg)

    def tth2q(self,tth):
        q = np.sin(np.deg2rad(tth))/self.lambdan*4*np.pi
        return q
        

def plot_sf(plt,ax,df_select,tick_x,tick_y,radius_amplify = 1.0,label = [0,0],xtitle = 'qx',ytitle='qy',title = ''):
    # how to rescale the x,y according to real length?
    ax.set_xlim(df_select['qx'].min()-1,df_select['qx'].max()+1)
    ax.set_ylim(df_select['qy'].min()-1,df_select['qy'].max()+1)
    numb = len(df_select)
    plt.xticks(df_select['qx'],df_select[tick_x])
    plt.yticks(df_select['qy'],df_select[tick_y])
    for x in range(numb):
        radius = np.sqrt(df_select.ix[x]['F^2']/df_select['F^2'].max())/radius_amplify
        center = (df_select.ix[x]['qx'],df_select.ix[x]['qy'])
        point = mpatches.Circle(center,radius,ec='none',alpha = 0.4,color='blue')
        ax.add_patch(point)
        if label[0] == 1:
            ax.text(center[0],center[1]-0.4,df_select.ix[x]['hkl'],ha = 'center',family='sans-serif',size = 12,color='black')
        if label[1] == 1:        
            ax.text(center[0],center[1],'%.2f' % (df_select.ix[x]['F^2']),ha = 'center',family='sans-serif',size = 12,color='red')
    plt.xlabel(xtitle,color = 'black',size = 16)
    plt.ylabel(ytitle,color = 'black',size = 16)
    plt.title(title,color = 'black',size = 20)
    plt.grid(True)
 





