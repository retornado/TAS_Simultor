# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 00:48:44 2017

@author: luowei
"""
import numpy as np
import pandas as pd
import TasPara as cc
import SciTas as st
import TasLimit as tl
import TasSimulate as ts

def tag2df(tag='tas'):
    # expand or update to which point
    if tag == 'tas':
        df_exp = cc.TasStatus.tas_status
    elif tag == 'tas_temp':
        df_exp = cc.TasStatus_temp.tas_status
    elif tag == 'qe':
        df_exp = cc.TasQe.tas_qe
    elif tag == 'qe_temp':
        df_exp = cc.TasQe_temp.tas_qe
    return df_exp
    
def df_expand(df_var,tag = 'tas'):
    # input : points vary
    # ouput : expand to points which can plot
    df_exp = tag2df(tag)
    for x in df_exp.index:
        if x not in df_var.columns:
            df_var[x] = df_exp[x]
    return df_var

def se_expand(se_var,tag = 'tas'):
    # input : points vary
    # ouput : expand to points which can plot
    se_exp = tag2df(tag)
    for x in se_exp.index:
        if x not in se_var.index:
            se_var[x] = se_exp[x]
    return se_var

def update_status(se,tag = 'tas'):
    # update status record
    if not se.isnull().any():
        df_exp = tag2df(tag)
        for x in se.index :
            if x in df_exp.index:
                df_exp[x] = se[x]
        return df_exp
    else:
        return se
        
def ctas_config_adjust(se):
    if not se.isnull().any():
        config = cc.TasConfig.tas_config
        se.m1 = se.m1*config.m
        se.m2 = se.m2*config.m
        se.a1 = se.a1*config.a
        se.a2 = se.a2*config.a
    
#######################################################################################################
# scan 
class tas_scan():
    def __init__(self,*args):   
        # get variables
        self.df_var(*args)
        # prepare order_text for Exception 
        self.order_text()
        if self.isqscan == True:
            self.tas_qscan()
            update_status(self.points.ix[self.npoint-1],tag = 'qe')
        else:
            self.tas_mscan()
        self.points['order'] = self.order        
        update_status(self.points.ix[self.npoint-1],tag = 'tas')
        # generate data for plot
        self.data_plot = ts.scictas_to_plot_df(self.points)
        self.data_plot.name = self.order


    def df_var(self,*args):
        # get variables
        # recogonize the scan type
        nmotor = len(args)/4    
        df = pd.DataFrame()
        indexq = cc.TasQe.tas_qe.index
        self.isqscan = False
        for x in range(nmotor):
            if args[4*x] in indexq:
                self.isqscan = True
            df[args[4*x]] = np.linspace(args[4*x+1],args[4*x+2],args[4*x+3]) 
        self.df_var = df
        self.args = args
        self.npoint = len(df)

    def tas_mscan(self):
        self.points = df_expand(self.df_var,tag = 'tas')
        self.points = tl.TasLimit_df(self.points)
        self.points['qe_limit'] = 1


    def tas_qscan(self):
        # expand to qe point
        df = df_expand(self.df_var,tag = 'qe')
        # if mode =3 s0 can add in
        # prepare tas point
        df2 = pd.DataFrame()
        for x in range(self.npoint):
            # translate to tas
            junk = st.Scisoft(df.ix[x])
            now_ctas = junk.tas
            # adjust to tas configuration
            ctas_config_adjust(now_ctas)
            df2 = df2.append(now_ctas,ignore_index=True)
        df = df.combine_first(df2)
        # add mts ...
        self.points = df_expand(df,tag = 'tas')
    def order_text(self):
        junk = 'tas_scan('
        for x in self.args:
            junk = junk + str(x) + ','
        self.order = junk[:-1]+')'
    
#######################################################################################################           
# move 
class tas_move():
    def __init__(self,*args):
        self.se_var(*args)
        self.order_text()
        if self.isqmove == True:
            self.tas_qmove()
            update_status(self.points,tag = 'qe')
        else:
            self.tas_mmove()
        self.points['order'] = self.order
        update_status(self.points,tag = 'tas')
        self.data_plot = ts.scictas_to_plot(self.points)
        self.data_plot.name = self.order
    
    def se_var(self,*args):
        # translate the order to point vary
        # recogonize the scan type : qmove or mmove
        nmotor = len(args)/2    
        se = pd.Series()
        indexq = cc.TasQe.tas_qe.index
        self.isqmove = False
        for x in range(nmotor):
            if args[2*x] in indexq:
                self.isqmove = True
            se[args[2*x]] = args[2*x+1]
        self.se_var = se
        self.args = args
    
    def tas_mmove(self):
        self.points = se_expand(self.se_var,tag = 'tas')
        self.points = tl.TasLimit(self.points).point
        self.points['qe_limit'] = 1

    def tas_qmove(self):
        # expand to qe point
        se = se_expand(self.se_var,tag = 'qe')
        # translate qe to tas
        now_ctas = st.Scisoft(se).tas
        # add mts ...
        now_ctas = se_expand(now_ctas,tag='tas')
        # adjust to tas configuration
        ctas_config_adjust(now_ctas)
        # add to points
        self.points = se.append(now_ctas)
    
    def order_text(self):
        junk = 'tas_move('
        for x in self.args:
            junk = junk + str(x) + ','
        self.order = junk[:-1]+')'

#######################################################################################################
class orderlist():
    # realize the order list function
    def __init__(self,filename):
        self.file = filename
        self.read_file_to_orderlist()
        self.read_orderlist_to_points()
        
    def read_file_to_orderlist(self,order_eval_filename = './orderlist'):
        f = open(self.file,'r')
        self.order_eval_filename = order_eval_filename
        fw = open(order_eval_filename,'w')
        for line in f:
            if '#' not in line:
                junk = text_to_order(line)+'\n'
                fw.writelines(junk)                
        f.close()
        fw.close()
        
    def read_orderlist_to_points(self,pointslist_name = './points_list'):
        f = open(self.order_eval_filename,'r')
        self.pointslist_name = pointslist_name
        fw = open(pointslist_name,'w')
        import pandas as pd
        points = pd.DataFrame()
        for line in f:
            junk = eval(line).points
            junk['order'] = line[:-1]
            points = points.append(junk,ignore_index=True)
        fw.writelines("%s" % (points))
        self.points = points
        self.data_plot = ts.scictas_to_plot_df(points)
        self.data_plot.name = self.file

        f.close()
        fw.close()  
        


def text_to_order(text):
    # change text to string application to eval()
    strs = text.strip().split()
    passby = 0
    if strs[0] == 'scan':
        junk = 'tas_scan('
    elif strs[0] == 'mv':
        junk = 'tas_move('
    elif strs[0] == 'file':
        junk = 'ts.Numb_to_points('
    elif strs[0] == 'orderfile':
        junk = 'orderlist('
    else:
        junk = text
        passby = 1
    if passby == 0:
        for x in strs[1:]:
            try:
                # file
                junk = junk + str(eval(x)) + ','
            except:
                # orderfile,scan,move
                junk = junk + '\''+x+'\','
        junk = junk[:-1] + ')'
    return junk 

# parameter change
def modechange(mode):
    cc.ModeChoice.mode = mode
    
 