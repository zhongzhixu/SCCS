# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 19:56:12 2020

@author: 89276
"""

#! /usr/bin/env python
#coding=utf-8
#!/usr/bin/env python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 

#%%
#========patients who have first-ever dementia in 2008-2010=======
#=================================================================
dementia_code = ['331.0',
                 '290.0',
                 '290.1','290.10','290.11','290.12','290.13',
                 '290.2','290.20','290.21',
                 '290.3',
                 '290.4','290.40','290.41','290.42','290.43',
                 '294.1','294.10','294.11','294.8',
                 '331.1','331.82','331.83']
depression_code = ['296.0', '296.1', '296.2', '296.3', '296.4', '296.90'
                   '300.4','309.0','309.28','311']

p2p = pd.read_csv('match_file.csv')
p2p.drop_duplicates(keep='first',inplace=True)
pat2pssn = dict()
for i in p2p.index:
    pat2pssn[p2p.loc[i, 'PATID']] = p2p.loc[i, 'patient_pssn']
#%%
#---------for statistics
#-----------------------No. of older people with dementia
data_10YEARS_reformat = pd.read_csv('D:/research/POISONING/reformat_10years_ehr.csv', encoding = 'utf-8')
available_data = data_10YEARS_reformat[data_10YEARS_reformat['PATID'].isin(pat2pssn)]

three_year_data = available_data[ (available_data['admin_year']>=2008) ] 

three_year_older_data = three_year_data[ (three_year_data['AGE']>=65) ]  #basically no need, as QP's data is for older

three_year_older_data.index = range(three_year_older_data.shape[0])

three_year_older_data['index'] = range(three_year_older_data.shape[0])

three_year_older_data=data_10YEARS_reformat

idx = 0
dtp = []
col1, col2, col3, col4, col5 = three_year_older_data['diag_cd_01'],three_year_older_data['diag_cd_02'], three_year_older_data['diag_cd_03'], three_year_older_data['diag_cd_04'],three_year_older_data['diag_cd_05']
for a,b,c,d,e in zip(col1.values, col2.values, col3.values, col4.values, col5.values):
    if ((a in dementia_code) or( b in dementia_code) or (c in dementia_code) or (d in dementia_code) or (e in dementia_code)):
        dtp.append(idx)
    idx = idx +1
    
dt_records = three_year_older_data[three_year_older_data['index'].isin(dtp)]

print('No. of dementia individuals in total:', len(set(dt_records['PATID'])))
#%%
#---------------------No. of older people with FIRST LIFETIME dementia
five_year_data = available_data[ (available_data['admin_year']>=2003) &  (available_data['admin_year']<=2007)] 
five_year_older_data = five_year_data[ (five_year_data['AGE']>=65) ] 
five_year_older_data.index = range(five_year_older_data.shape[0])
five_year_older_data['index'] = range(five_year_older_data.shape[0])


idx = 0
dtp = []
col1, col2, col3, col4, col5 = five_year_older_data['diag_cd_01'],five_year_older_data['diag_cd_02'], five_year_older_data['diag_cd_03'], five_year_older_data['diag_cd_04'],five_year_older_data['diag_cd_05']
for a,b,c,d,e in zip(col1.values, col2.values, col3.values, col4.values, col5.values):
    if ((a in dementia_code) or( b in dementia_code) or (c in dementia_code) or (d in dementia_code) or (e in dementia_code)):
        dtp.append(idx)
    idx = idx +1
    
dt_records_fiveyears = five_year_older_data[five_year_older_data['index'].isin(dtp)]

print('No. of dementia individuals in total:', len(set(dt_records_fiveyears['PATID'])))
intersect = list( set(dt_records_fiveyears['PATID']).intersection(set(dt_records['PATID'])) )

#%%
#---------for statistics
#-----------------------No. of older people with depression
data_10YEARS_reformat = pd.read_csv('D:/research/POISONING/reformat_10years_ehr.csv', encoding = 'utf-8')
available_data = data_10YEARS_reformat[data_10YEARS_reformat['PATID'].isin(pat2pssn)]

three_year_data = available_data[ (available_data['admin_year']>=2008) ] 

three_year_older_data = three_year_data[ (three_year_data['AGE']>=65) ]  #basically no need, as QP's data is for older

three_year_older_data.index = range(three_year_older_data.shape[0])

three_year_older_data['index'] = range(three_year_older_data.shape[0])


idx = 0
dtp = []
col1, col2, col3, col4, col5 = three_year_older_data['diag_cd_01'],three_year_older_data['diag_cd_02'], three_year_older_data['diag_cd_03'], three_year_older_data['diag_cd_04'],three_year_older_data['diag_cd_05']
for a,b,c,d,e in zip(col1.values, col2.values, col3.values, col4.values, col5.values):
    if ((a in depression_code) or( b in depression_code) or (c in depression_code) or (d in depression_code) or (e in depression_code)):
        dtp.append(idx)
    idx = idx +1
    
depression_records = three_year_older_data[three_year_older_data['index'].isin(dtp)]

print('No. of depression individuals in total:', len(set(depression_records['PATID'])))

#%%
#---------for statistics
#-----------------------No. of older people with depression and dementia

idx = 0
dtp = []
col1, col2, col3, col4, col5 = depression_records['diag_cd_01'],depression_records['diag_cd_02'], depression_records['diag_cd_03'], depression_records['diag_cd_04'],depression_records['diag_cd_05']
for a,b,c,d,e in zip(col1.values, col2.values, col3.values, col4.values, col5.values):
    if ((a in dementia_code) or( b in dementia_code) or (c in dementia_code) or (d in dementia_code) or (e in dementia_code)):
        dtp.append(idx)
    idx = idx +1
    
depression_dementia_records = three_year_older_data[three_year_older_data['index'].isin(dtp)]

print('No. of dementia individuals in total:', len(set(depression_dementia_records['PATID'])))







































