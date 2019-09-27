# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 19:32:27 2017

@author: luowei
    ctas simulation class
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.patches as mpatches
import matplotlib.animation as animation
import TasPara as cc
import TasCommand as tc
import Spice as spice
import SciTas as st
spice.exp_para()

class MyRectangle(mpatches.Rectangle):
    # adjus rotate center and rectangel center :
    #     xy = low,left --> center,center
    def __init__(self,xy,width,height,angle=0,**kargs):
        mpatches.Rectangle.__init__(self,xy,width,height,angle,**kargs)
        r = np.sqrt(width**2+height**2)/2.0
        theta = np.arctan(height/width)
        center1 = xy + [r*np.cos(theta+np.deg2rad(angle)),r*np.sin(theta+np.deg2rad(angle))]
        center2 = 2*xy - center1
        self.xy = center2  

##################################################################################################################################
# simulate ctas
class TasSimulate(object):
    Tg = cc.TasGeometry()
    def __init__(self,ax):
        self.ax = ax
        self.ax.set_ylim(0,cc.TasGeometry.appl*0.545)   
        self.ax.set_xlim(0,cc.TasGeometry.appl)
            
    def label(self,xy,text,color='black',size = 16):
        self.ax.text(xy[0],xy[1],text,ha = 'center',family='sans-serif',size=size,color=color)


    def Tas_coordinate(self,data):
        # get all the component coordinates
        # shielding wall
        # dance floor
        # mono
        # sample_stage
        # sample
        # analyser_stage
        # analyser
        # detector_stage
        # detector
        
        pass


    def tas_simulate(self,data):
             # dataframe
        # + - definition: same as polar coordinates
            
            Tg = TasSimulate.Tg
            self.ax.clear()
            
            # shielding wall
            shield_wall = MyRectangle(Tg.mono_center,Tg.guide_shield_width,Tg.guide_shield_height,ec='none',color='c',alpha=0.7)
            self.ax.add_patch(shield_wall)
        
            # dacne floor
            if data['soft_limit'] == 0:
                color = 'red'
            else:
                color = 'yellow'
            dance_floor = mpatches.Wedge(Tg.mono_center,Tg.dance_floor_radius,180,360,ec='none',alpha=0.2,color=color)
            self.ax.add_patch(dance_floor)
            
            # incident beam
            inci_beam = mpatches.Arrow(Tg.mono_center[0]+Tg.guide_shield_width/2.0+20,Tg.mono_center[1],\
                        -1*Tg.guide_shield_width/2.0-20,0,width=20,color='r')
            self.ax.add_patch(inci_beam)
        
            # monochromator crystal
            mono_crystal = MyRectangle(Tg.mono_center,Tg.mono_crystal_width,Tg.mono_crystal_height,angle=data.m1)
            self.ax.add_patch(mono_crystal)
            
            # sample stage
            sample_center = np.array([Tg.mono_center[0]+data.mts*np.cos(np.deg2rad(data.m2)),\
                            Tg.mono_center[1]+data.mts*np.sin(np.deg2rad(data.m2))])
            
            sample_stage = mpatches.Circle(sample_center,Tg.sample_stage_radius,ec='none',alpha = 0.6,color='g')    
            self.ax.add_patch(sample_stage)
            
            # sample stage zero point
            s11 = np.deg2rad(180+data.m2-data.s1)
            sample_zero = mpatches.Arrow(sample_center[0],sample_center[1],0.7*Tg.sample_stage_radius*np.cos(s11),\
                            0.7*Tg.sample_stage_radius*np.sin(s11),width=Tg.appl*0.01,alpha=0.7,color='yellow')
            self.ax.add_patch(sample_zero)
            
            # scattered beam to sample
            scat_beam = mpatches.Arrow(Tg.mono_center[0],Tg.mono_center[1],data.mts*np.cos(np.deg2rad(data.m2)),\
                        data.mts*np.sin(np.deg2rad(data.m2)),width=20,color='r')
            self.ax.add_patch(scat_beam)
            
            # analyser stage  
            ana_center = np.array([sample_center[0]+data.sta*np.cos(np.deg2rad(data.s2+data.m2)),\
                            sample_center[1]+data.sta*np.sin(np.deg2rad(data.s2+data.m2))])
        
            ana_stage = mpatches.Circle(ana_center,Tg.ana_stage_radius,ec='none',alpha = 0.7,color='purple')    
            self.ax.add_patch(ana_stage)
            
            # scattered beam to analyser
            ana_beam = mpatches.Arrow(sample_center[0],sample_center[1],data.sta*np.cos(np.deg2rad(data.m2+data.s2)),\
                        data.sta*np.sin(np.deg2rad(data.m2+data.s2)),width=20,color='r')
            self.ax.add_patch(ana_beam) 
            
            # analyser cyrstal
            ana_crystal = MyRectangle(ana_center,Tg.mono_crystal_width,Tg.mono_crystal_height,angle=data.m2+data.s2+data.a1)
            self.ax.add_patch(ana_crystal)
            
            det_center = np.array([ana_center[0]+data.dtx*np.cos(np.deg2rad(data.s2+data.m2+data.a2)),\
                            ana_center[1]+data.dtx*np.sin(np.deg2rad(data.s2+data.m2+data.a2))])
            
            # scattered beam to detector
            det_beam = mpatches.Arrow(ana_center[0],ana_center[1],data.dtx*np.cos(np.deg2rad(data.m2+data.s2+data.a2)),\
                        data.dtx*np.sin(np.deg2rad(data.m2+data.s2+data.a2)),width=20,color='r')
            self.ax.add_patch(det_beam)
            
            # detector stage
            det_stage = MyRectangle(det_center,Tg.detector_shielding_width,Tg.detector_shielding_height,\
                        ec='none',alpha = 0.7,color='brown',angle = data.m2+data.s2+data.a2)    
            self.ax.add_patch(det_stage) 
            
            # detector
            detector_2d = MyRectangle(det_center,Tg.detector_width,Tg.mono_crystal_height,angle=data.m2+data.s2+data.a2-90,color='g',alpha = 0.5)
            self.ax.add_patch(detector_2d)
            
            self.label(det_center,'Detector')
            self.label(Tg.mono_center,'Monochromator')
            
            # add some parameters to self
            self.sample_center  = sample_center
            self.ana_center  = ana_center
            self.det_center = det_center
            
            data1 = plot_to_scictas(data)
            self.label_print(data1)
            
            # refa
            s11 = s11 - np.deg2rad(st.Alignment.delta)
            radius_now = Tg.sample_stage_radius*0.7
            refa_dir = mpatches.Arrow(sample_center[0],sample_center[1],0.7*radius_now*np.cos(s11),\
            0.7*radius_now*np.sin(s11),width=Tg.appl*0.01,alpha=0.4,color='purple')
            self.ax.add_patch(refa_dir)
            
    def label_print(self,data):                
        # tas_status
            center = [9700,3200]
            self.label(center,'TAS : ',color = 'blue')
            center[1] = center[1]-200
            self.label(center,'-'*16)
            center[1] = center[1]-200
            for x in cc.TasStatus.tas_status.index:
                try:
                    if x == 's0' and cc.ModeChoice.mode ==3 :
                        color = 'purple'
                        self.label(center,'%5s' % ('s1p')+' : '+ '%.2f' % (data['s0']+data['s1']),color = color)
                        center[1] = center[1]-200
                    else:
                        color = 'black'
                    if data[x] != cc.TasStatus_temp.tas_status[x]:
                        color = 'red'
                    self.label(center,'%5s' % (x)+' : '+ '%.2f' % (data[x]),color = color)
                    center[1] = center[1]-200
                except:
                    pass

        # mode info
            center = [700,3800]
            numbmode = cc.ModeChoice.mode
            self.label(center,'Mode : ',color = 'brown',size = 18)
            center = [700,3600]
            self.label(center,cc.ModeChoice.Modename[numbmode-1],color = 'brown',size = 16)

        # qe_point
            center = [700,3200]
            self.label(center,'QE : ',color = 'blue')
            center[1] = center[1]-200
            self.label(center,'-'*16)
            center[1] = center[1]-200
            for x in cc.TasQe.tas_qe.index:
                try:
                    if data[x] != cc.TasQe_temp.tas_qe[x]:
                        color = 'red'
                    else:
                        color = 'black'
                    self.label(center,'%5s' % (x)+' : '+ '%.3f' % (data[x]),color = color)
                    center[1] = center[1]-200 
                except:
                    pass
        
        # copyright
            center = (1400,6500)
            self.label(center,'Copyright@2017- Luo Wei,INPC ',color = 'black',size = 10)      
            center = (1400,6300)
            self.label(center,'CTAS Simulator ',color = 'red',size = 14)      


        # order
            center = [5200,900]
            try:
                self.label(center,data['order'],color='blue')
            except:
                pass
        # write to status temp
            tc.update_status(data,tag = 'tas_temp')
            tc.update_status(data,tag = 'qe_temp')

class TasSimulate_advanced(TasSimulate):
    def tas_simulate(self, data):
        se = cc.SampleEnviGeometry()
        TasSimulate.tas_simulate(self,data)
        # add sample enviroment
        for x in se.dead_angle:
            
            if data['s1s2_limit'] == 0:
                color = 'red'
            else:
                color = 'black'            
            se_dead = mpatches.Wedge(self.sample_center,se.radius,180+data.m2-x[1]-data.s1,180+data.m2-x[0]-data.s1,ec='none',alpha=0.7,color=color)
            self.ax.add_patch(se_dead)

class TasSimulate_premium(TasSimulate_advanced):
    def tas_simulate(self, data):
        Tg = TasSimulate_advanced.Tg
        TasSimulate_advanced.tas_simulate(self,data)
        # add sample stick
        s10 = np.deg2rad(180+data.m2-data.s1-data.s0)
        sample_stick = mpatches.Arrow(self.sample_center[0],self.sample_center[1],Tg.sample_stage_radius*np.cos(s10),\
            Tg.sample_stage_radius*np.sin(s10),width=100,alpha=0.7,color='white')
        self.ax.add_patch(sample_stick)

class TasSimulate_plan(TasSimulate):
    def tas_simulate(self, data):
        TasSimulate.tas_simulate(self,data)
        Tg = TasSimulate.Tg
        data1 = plot_to_scictas(data)
        # s1: 
        center  = -1*data1.s1
        self.write_sec(center)
        # s2:
        center = 180+data1.s2 - data1.s1
        self.write_sec(center)
        # add window section
        se = cc.SampleEnviPlan()
        for x in se.window_sec:
            se_window = mpatches.Wedge(self.sample_center,se.radius*0.85,180+data.m2-x[1]-data.s1,180+data.m2-x[0]-data.s1,width =se.radius*0.85*0.65, ec='none',alpha=1,color='white')
            self.ax.add_patch(se_window)
        
        # sample zero
        s11 = np.deg2rad(180+data.m2-data.s1)
        sample_zero = mpatches.Arrow(self.sample_center[0],self.sample_center[1],0.7*Tg.sample_stage_radius*np.cos(s11),\
                            0.7*Tg.sample_stage_radius*np.sin(s11),width=Tg.appl*0.01,alpha=0.9,color='black')
        self.ax.add_patch(sample_zero)
        
        # refa
        s11 = s11 - np.deg2rad(st.Alignment.delta)
        radius_now = Tg.sample_stage_radius*0.7
        refa_dir = mpatches.Arrow(self.sample_center[0],self.sample_center[1],0.7*radius_now*np.cos(s11),\
        0.7*radius_now*np.sin(s11),width=Tg.appl*0.01,alpha=0.9,color='purple')
        self.ax.add_patch(refa_dir)

    def write_sec(self,center):
        import SciTas as st
        exp_width = 2
        window_sec = [center-exp_width,center+exp_width]
        # adjust s1,s2 to [0,360) range
        window_sec = [st.range360(window_sec[0]),st.range360(window_sec[1])]
        # cross 0 section
        if window_sec[1] < window_sec[0]:
            window_sec[1] = window_sec[1] + 360
        cc.SampleEnviPlan.window_sec.append(window_sec)

#############################################################################################################################################
# animate ctas
class TasAnimate():
    # input is data_plot, pd.Series
    def __init__(self,fig,data):
        # define fig,ax
        self.fig = fig
        self.data = data
        self.ax = self.fig.add_subplot(111)
        
    def data_gen(self): 
        # DataFrame for scan
        if type(self.data) is pd.core.frame.DataFrame:
            i=0
            while i < len(self.data):
                # update temp status : offer to an
                yield self.data.ix[i]
                i += 1
        # Series for move
        elif type(self.data) is pd.core.series.Series:
                yield self.data
        
    def tas_animate(self):
        Simulate = self.modechoice()
        self.func =Simulate(self.ax).tas_simulate
        self.ani = animation.FuncAnimation(self.fig,self.func,self.data_gen,interval = 300,repeat = False)
        if cc.config_ani_save == 1:
            self.ani.save('./gif/'+self.data.name+'.gif',fps=cc.config_ani_save_fps,writer = 'imagemagick')
        

        
    def modechoice(self):
        mode = cc.ModeChoice.mode
        if mode == 1:
            Simulate = TasSimulate
        elif mode == 2:
            Simulate = TasSimulate_advanced
        elif mode == 3:
            Simulate = TasSimulate_premium
        elif mode == 4:
            Simulate = TasSimulate_plan
        return Simulate
        
 

#############################################################################################################################################
# data configuration
# spice  scictas  plot
class Numb_to_points():
    def __init__(self,numb):
        junk = []
        junk.extend(list(cc.TasQe.tas_qe.index))
        junk.extend(list(cc.TasStatus.tas_status.index))
        self.points = spice.rawctas(numb)['data'][junk]
        self.data_plot = spice_to_plot_df(self.points)

def spice_to_plot_df(df):
    # dataframe
    data = df.copy()
    for x in range(len(df)):
        data.ix[x] = spice_to_scictas(df.ix[x])
        data.ix[x] = scictas_to_plot(data.ix[x])
    return data
    
def scictas_to_plot_df(df):
    # dataframe
    data = df.copy()
    for x in range(len(df)):
        data.ix[x] = scictas_to_plot(data.ix[x])
    return data    
        
def spice_to_scictas(data):
    # change the configuration of spice to plot
    # pd.Series
    data1 = data.copy()
    data1.m1 = 180-data.m1
    data1.m2 = -data.m2
    data1.a1 = data.a1-180
    data1.s2 = data.s2
    data1.a2 = data.a2
    return data1

def scictas_to_plot(data):
    # pd.Series
    data1 = data.copy()
    if not data.isnull().any() :
        data1.m1 = 180+data.m1
        data1.m2 = 180+data.m2
        data1.a1 = -1*data.a1
        data1.s2 = -1*data.s2
        data1.a2 = -1*data.a2
    return data1

def plot_to_scictas(data):
    # pd.Series
    data1 = data.copy()
    data1.m1 = data.m1-180
    data1.m2 = data.m2-180
    data1.a1 = -1*data.a1
    data1.s2 = -1*data.s2
    data1.a2 = -1*data.a2
    return data1

#############################################################################################################################################
# test part.
if __name__  == '__main__':   
    def test_simulate_advanced():
        spice.exp_para()
        fig = plt.figure(figsize=(11*2,6*2))
        ax = fig.add_subplot(111)
        a = TasSimulate(ax)
        data = spice.rawctas(450)['data'].ix[1]
        #data = pd.Series(data = [30,60,20,-40,18,36],index = ['m1','m2','s1','s2','a1','a2'])
        #data = tc.se_expand(data,tag = 'tas')
        #data_plot = scictas_to_plot(data)
        junk = spice_to_scictas(data)
        data_plot = scictas_to_plot(junk)
        # plot tas
        a.tas_simulate(data_plot)
    
    def test_animate():
        data = spice.rawctas(450)['data']
        data_plot = spice_to_plot_df(data)
        fig = plt.figure(figsize=(11*2,6*2))
        a = TasAnimate(fig,data_plot)
        a.tas_animate()

        
        


