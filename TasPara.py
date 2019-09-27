# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 02:05:34 2017

@author: luowei
"""

import pandas as pd
import numpy as np

config_ani_save = 0
config_ani_save_fps = 2

class LimitNumb():
    mode = 1
    # 0 : qelimit will not plot, but soft and s1s2 limit will
    # None : all limit statu will not plot
    Modenumb = [None,0]
    limit_example = pd.Series(data = [1,1,1],index = ['s1s2_limit','qe_limit','soft_limit'])

class ModeChoice():
    mode = 1
    Modename = ['basic','sampleenvi','samplestick','plan']
    
class SplitMode():
    mode = 1
    Modename = ['s0_first','s1_first']

class TasStatus():
    tas_status = pd.Series(index = ['m1','m2','s1','s2','a1','a2','mts','sta','dtx'],\
                           data=[45,90,0,0,0,0.0,2300.0,1400,700])
    if ModeChoice.mode == 3:
        tas_status['s0'] = 0

    
class TasStatus_temp(TasStatus): pass

class TasQe():
    tas_qe = pd.Series(index = ['h','k','l','ei','ef'],data=[1.0,1.0,0.0,13,13])

class TasQe_temp(TasQe): pass

class TasConfig():
    tas_config = pd.Series(index = ['m','s','a'],data = [1,-1,1])
   
class TasGeometry():
    appl = 11000
    mono_center = np.array([0.5,0.6-0.075])*appl
    dance_floor_radius = 0.43*appl
    guide_shield_width = 0.9*appl
    guide_shield_height = 0.10*appl
    mono_crystal_width = 0.025*appl
    mono_crystal_height = 0.003*appl
    sample_stage_radius = 0.09*appl
    ana_stage_radius = 0.03*appl
    detector_shielding_width = 0.05*appl
    detector_shielding_height = 0.04*appl
    detector_width = 0.03*appl

class SampleEnviGeometry():
    dead_angle =   np.array([20,40,60,75,120,180,250,290,340,350]).reshape(-1,2)
    radius = TasGeometry.sample_stage_radius

class SampleEnviPlan():
    window_sec = []
    radius = TasGeometry.sample_stage_radius

class LimitRange():
    # for spice configuration
    ### softlimit is phhysical value, not motor value
    index = ['m1','m2','s1','s2','a1','a2','s0','mts','sta','dtx']
    low = [17,36,-360,-120,-170,-170,-360,2000,800,600]
    high = [70,140,360,120,170,170,360,3000,2000,2000]
    softlimit = pd.DataFrame(data = [low,high],columns = index,index = ['low','high'])