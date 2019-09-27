#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 14:32:43 2017

@author: luowei
        principle : 
            database  ---> SQL
            reversible
"""

import pickle
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import pylab as plt 

def write_config(config):
    '''
        config:
            df_path
            exp_number
            roi         : [right,left,bottom,top]
            xadjust     : a*x+b
            yadjust     : a*y+b
            abnormal    :
            merge_check :
            posi_tlr  : Series = pd.Series(index = items_posi)
            items_exp : ['monitor','time','detector']
            items_file: ['numb','pixelFileName','Pt.']
            items_envi: ['temp']
            items_all :
            items_posi :
    '''
    file = open('spice.config','wb')
    pickle.dump(config,file)
    file.close()
# =====================================================================================================
def read_config():
    file = open('spice.config','rb')
    config = pickle.load(file)
    file.close()
    return config
# =====================================================================================================
def filename(numb):
    en = config['exp_number']
    filename = config['df_path'] + 'exp'+str(en)+'/Datafiles/IOP_exp%04i_scan%04i.dat' % (en,numb)
    return filename
# =====================================================================================================
def rawctas(numb):
    '''
        read raw data , nothing change !
        header     : 1-25
        motorname  : 26
        data       : 27 - 
        to be done :  
            add try except
            add pixel data
            add multi index
    '''
    header = {}
    f = open(filename(numb),'r')
    for line in f:
        if '#' in line:
            if 'Pt.' in line:
                motors = line.split()[1:]
                data = pd.DataFrame(index = motors)
            else:
                junk = line.split()
                header[junk[1]] = junk[3:]
        else:
                dataline = line.split()
                ## !!! pixel  is the last one
                #  !!! Pt. is the first one
                dataline[1:-1] = [eval(x) for x in dataline[1:-1]]
                junk_se = pd.Series(dataline,index = motors)
                data[junk_se['Pt.']] = junk_se
    f.close()
    ctasraw = {}
    ctasraw['header'] = header
    ctasraw['motors'] = motors
    # swap axis
    ctasraw['data'] = data.swapaxes(0,1)
    # add detector fluctuate
#    ctasraw['data']['detector_errbar'] = ctasraw['data']['detector'].apply(lambda x : m.sqrt(x))
    # add numb
    ctasraw['data']['numb'] = str(numb)
    # adjust items_file from str to list
    for x in config['items_file']:
        ctasraw['data'][x] = ctasraw['data'][x].apply(lambda x : [x]) 
    return ctasraw
# =====================================================================================================
def anactas(numb):
    '''
        analyse rawdata
            1. find the abnormal point
            2. basic statistics
        output:
            header
            data
            ana :
                mode          :  2axis/3axis
                time          :  mean,std
                temp          :  mean,std
                stemp         :  mean,std
                monitor       :  mean,std
                scan_center   :
                
        to be done:
            add roi
            add pixel data
    '''
    ctasraw = rawctas(numb)
    ctasana = {}
    ctasana['header'] =  ctasraw['header']
    # !!! abnormal check to be done
    ctasana['data'] =  ctasraw['data']
    ctasana['ana'] = anactas_ana(ctasana['data'])
    # roi to be done
    return ctasana
# =====================================================================================================
def anactas_ana(data):
    anactas_ana = {}
    item = ['time','monitor','temp','stemp']
    for x in item:
        anactas_ana[x]  = dict(zip(['mean','std'],[data[x].mean(),data[x].std()]))
    # check axis mode : a2 < 1
    if abs(data['a2'].sum()) < 1:
        anactas_ana['mode'] = '2_axis'
        anactas_ana['scan_center'] = ''
    else:
        anactas_ana['mode'] = '3_axis'
        item = ['h','k','l','e']
        anactas_ana['scan_center'] = dict(zip(item,[data[x].mean() for x in item]))
    return anactas_ana
# =====================================================================================================
def mergectas(numb):
    '''
    data split to :
            posi   :  other                  (equal check)
            exp    :  monitor time detector  (normalize to one)
            file   :  numb pixelFileName Pt.    (list)
    ouput: (like anactas)
        header
        data
        ana
    method :
        merge df one by one
    
    !!! to be done : errbar in x direction during merge process 
    '''
    if type(numb) == int:
        mergectas = anactas(numb)
    else:
        mergectas = {}
        df1 = anactas(numb[0])['data']
        mergectas['header'] = anactas(numb[0])['header']
        for x in numb[1:]:
            df2 = anactas(x)['data']
            df1 = mergedf_ctas(df1,df2)
        mergectas['data'] = df1
        mergectas['ana'] = anactas_ana(df1)
    return mergectas
# =====================================================================================================
def mergedf_ctas(df1,df2):
    '''
    '''
    data = pd.DataFrame()
    for x in df1.index:
        for y in df2.index:
            if seequal_ctas(df1.ix[x],df2.ix[y]) == 1:
                df1.ix[x] = mergese_ctas(df1.ix[x],df2.ix[y])
                df2 = df2.drop(y)
    data = df1.append(df2,ignore_index=True)
    return data
# =====================================================================================================
def mergese_ctas(se1,se2):
    '''
    '''    
    se = pd.Series(index = config['items_all'])
    se[config['items_posi']] = se1[config['items_posi']]
    for x in config['items_envi']:
        se[x] = (se1[x]+se2[x])/2
    for x in config['items_file']:
        junk = se1[x].copy()
        junk.extend(se2[x])
        se[x] = junk
    for x in config['items_exp']:
        se[x] = se1[x]+se2[x]
    return se
# =====================================================================================================
def seequal_ctas(se1,se2):
    seequal_ctas.posi_tlr = 0.03
    seequal_ctas.envi_tlr1 = 0.2
    seequal_ctas.envi_tlr2 = 2
    seequal_ctas.judge = {1:'equal',2:'envi warning',0:'not equal'} 
    posi1 = se1[config['items_posi']]
    posi2 = se2[config['items_posi']]
    envi1 = se1[config['items_envi']]
    envi2 = se2[config['items_envi']]
    dev_posi = abs(posi1 - posi2).sum()
    dev_envi = abs(envi1 - envi2).sum()
    if dev_posi < seequal_ctas.posi_tlr and dev_envi < seequal_ctas.envi_tlr1 :
        judge = 1
    elif dev_posi < seequal_ctas.posi_tlr and seequal_ctas.envi_tlr1 < dev_envi <seequal_ctas.envi_tlr2 :
        judge = 2
    else:
        judge = 0 
    return judge
# =====================================================================================================    
def spice(numb):
    '''
        to be done: introduce seaborn
    '''
    data = mergectas(numb)['data']
    header = mergectas(numb)['header']
    defx = header['def_x'][0]
    xdata = np.array(data[defx].values).astype(dtype = float)
    ydata = np.array(data['detector'].values).astype(dtype = float)
    sigma = np.sqrt(ydata)

# find default p0
 # a: I.I,  b: x[max(y)], c: FMWH, d: bg 
    d = min(ydata)
    b = xdata[ydata == max(ydata)][0]
    junk = abs(ydata-max(ydata)/2)
    xl = xdata[xdata < b][junk[xdata < b] == min(junk[xdata < b])][0]
    xh = xdata[xdata > b][junk[xdata > b] == min(junk[xdata > b])][0]
    c = abs((xh-xl)/2)
    a = abs(c*2*max(ydata))
    e = 0


    popt, pcov = curve_fit(gaussian, xdata, ydata,p0 = [a,b,c,d,e],sigma=sigma)

# how to fix parameter?   fixp
# how to put errbar in the fitting
# where is the output of sigma and chisq
    
    margin = (max(xdata)-min(xdata))/10
    x1 = np.linspace(min(xdata)-margin,max(xdata)+margin,100)
    plt.close()
    plt.plot(xdata,ydata,'r+:',label=defx+' scan')
    plt.plot(x1,gaussian(x1,*popt),'go:',label='fit')  
    plt.legend()  
    plt.show()
# =====================================================================================================    
def gaussian(x,a,b,c,d,e):
    return a*np.exp(-np.power(x-b,2)/(2*np.power(c,2)))+d+e*x
# =====================================================================================================
def exp_para():
#  how to __init__ 
    global config
    config = {}
    config['df_path'] = '/home/luowei/spice_data/'
    config['exp_number'] = 5
    config['roi'] = [1,256,1,256]
    config['xadjust'] = [1,0]
    config['yadjust'] = [1,0]
    config['items_exp'] = ['monitor','time','detector']
    config['items_file'] = ['numb','pixelFileName','Pt.']
    config['items_envi'] = ['temp','stemp']
    junk = config['items_exp'] + config['items_file'] + config['items_envi']
    config['items_all']  = ['Pt.','m1','time','monitor','detector','m2','mts',\
          'mfv','slit1v2','mtx','mty','mgu','mgl','slit1h','slit1h2','slit1v',\
          's2','stx','sty','s1','sgl','sgu','sbl','sbr','sbu','sbd','sta','a2',\
          'abr','abv','atx','aty','a1','agu','agl','dtx','cv1','cv2','q','h','k',\
          'l','ei','ef','e','temp','stemp','stemp_t','temp_t','pixelFileName','numb']
    config['items_posi'] = [x for x in config['items_all'] if x not in junk]
    write_config(config)

# check __name__
if __name__ == '__main__':
    exp_para()

