#! /usr/bin/env python
#coding=utf-8
#!/usr/bin/env python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 

'''
Attention to BNF SELECTION AND SENSITIVITY PARAMETER 
'''
# parameteric factors:
# BNF code and sensitivity analysis (use ctrl+f to search keyword sensitivity

'''
medicine_sas = pd.read_sas('D:/research/HA_QP/data/medication.sas7bdat', 
                         format = 'sas7bdat',encoding="ISO-8859-1")

medicine_sas.to_csv('D:/research/HA_QP/data/medication_sas2csv.csv', index = False)
'''

p2p = pd.read_csv('match_file.csv')
p2p.drop_duplicates(keep='first',inplace=True)
med = pd.read_csv('D:/research/HA_QP/data/medication_sas2csv.csv')
test = med.loc[0:500]
med = med.dropna(subset=['bnf_no','patient_pssn','presc_duration_day'])
bnf_no_first_two = [i[:3] for i in med['bnf_no']]
med['bnf_no_first_two'] = bnf_no_first_two

from collections import Counter
#a = Counter(list(med['bnf_no']))
Antidepressant_med = med[med['bnf_no_first_two']=='4.3']
#Antidepressant_med = med[med['bnf_no']=='4.3.1']
Antidepressant_drugs = Counter(list(Antidepressant_med['drug_name']))

#---------
ami = Antidepressant_med[Antidepressant_med['patient_pssn'].isin(p2p['patient_pssn'])]
ami = ami[ami['disp_date']<=201012]

print( len(set(ami['patient_pssn'])),len(set(p2p['patient_pssn'])) )

#---dct -----
pssn2pat = dict()
for i in p2p.index:
    pssn2pat[p2p.loc[i, 'patient_pssn']] = p2p.loc[i, 'PATID']
pat2pssn = dict()
for i in p2p.index:
    pat2pssn[p2p.loc[i, 'PATID']] = p2p.loc[i, 'patient_pssn']
 
dementia_code = ['331.0',
                 '290.0',
                 '290.1','290.10','290.11','290.12','290.13',
                 '290.2','290.20','290.21',
                 '290.3',
                 '290.4','290.40','290.41','290.42','290.43',
                 '294.1','294.10','294.11','294.8',
                 '331.1','331.82','331.83']
#%%
#==============TEN YEARS DATA==============
#==========================================
data_10YEARS = pd.read_csv('D:/research/HA_project_and_Embedding/full_data/fulldata.csv', encoding = 'utf-8')
data_10YEARS.columns = ['OBS', 'PATID', 'HOSPITAL', 'AGE', 'SEX', 'DOB', 'DIST_BOA',
       'ADATE', 'DDATE', 'diag_cd_01', 'diag_cd_02', 'diag_cd_03', 'diag_cd_04', 'diag_cd_05',
       'diag_cd_06', 'diag_cd_07', 'diag_cd_08', 'diag_cd_09', 'diag_cd_10', 'diag_cd_11', 'diag_cd_12',
       'diag_cd_13', 'diag_cd_14', 'diag_cd_15', 'TLOS', 'DSTATUS', 'no_code']

##how many older people and the prevalence of the dementia
old =  data_10YEARS[data_10YEARS['PATID'].isin(pat2pssn)] 
old = old[old['AGE']>=65]
print (len(set(old['PATID']) )) #no change because the QP's data is for older people only

#%%
drug_user_lst = [pssn2pat[i] for i in set(ami['patient_pssn'])] #drug_user_lst: PATID

drug_user_TEN_YEARS = data_10YEARS[data_10YEARS['PATID'].isin(drug_user_lst)]  # to jiannan

print (len(set(drug_user_TEN_YEARS['PATID'])))
#drug_user_TEN_YEARS.to_csv('ehr_info.csv') #for jiannan
#========patients who have first-ever dementia in 2008-2010=======

def first_three(xy,cd_0x):
    temp = []
    for i in xy[cd_0x]:
        l = i.strip().split('.')
        temp.append(l[0])
    xy[cd_0x] = temp 
    return xy

def HA_formation(data):
    data.columns = ['OBS', 'PATID', 'HOSPITAL', 'AGE', 'SEX', 'DOB', 'DIST_BOA',
       'ADATE', 'DDATE', 'diag_cd_01', 'diag_cd_02', 'diag_cd_03', 'diag_cd_04', 'diag_cd_05',
       'diag_cd_06', 'diag_cd_07', 'diag_cd_08', 'diag_cd_09', 'diag_cd_10', 'diag_cd_11', 'diag_cd_12',
       'diag_cd_13', 'diag_cd_14', 'diag_cd_15', 'TLOS', 'DSTATUS', 'no_code']
    
    # drop nan
    data = data.dropna(subset = ['PATID','AGE','ADATE', 'DDATE','TLOS'])
    
    #admn_year
    temp = data['ADATE']
    admn_year = [int(i[:4]) for i in temp]
    data['admin_year'] = admn_year

    import time
    import datetime
     
    def Caltime(date1,date2):
        date1=time.strptime(date1,"%Y-%m-%d")
        date2=time.strptime(date2,"%Y-%m-%d")
        date1=datetime.datetime(date1[0],date1[1],date1[2])
        date2=datetime.datetime(date2[0],date2[1],date2[2])
        return date2-date1
    #---
    los = []
    for date1, date2 in zip(data['ADATE'],data['DDATE']):
        if date1 == date2: los.append(1)
        else:              los.append( int(str(Caltime(date1,date2)).split('day')[0])+1 )   
    data['TLOS'] = los
    
    #---------fillnan for diagnoses----
    data = data.fillna('nnnulll')
    print ('# of patients',len(set(data['PATID'])))
    print ('# of diseases',len(set(list(data['diag_cd_01'])+list(data['diag_cd_02']))))
    
    #---------diag processing---------
    for j in range(1, 10):
        temp = data['diag_cd_0'+str(j)]
        temp1 = [i[2:-1] for i in temp]
        data['diag_cd_0'+str(j)] = temp1
    
    for j in range(10,16):
        temp = data['diag_cd_'+str(j)]
        temp1 = [i[2:-1] for i in temp]
        data['diag_cd_'+str(j)] = temp1
    
    #---------SEX processing
    temp = data['SEX']
    temp1 = [i[2:-1] for i in temp]
    data['SEX'] = temp1 
     
    #---------DIST_BOA processing
    temp = data['DIST_BOA']
    temp1 = [i[2:-1] for i in temp]
    data['DIST_BOA'] = temp1 

    #---------DSTATUS processing
    temp = data['DSTATUS']
    temp1 = [i[2:-1] for i in temp]
    data['DSTATUS'] = temp1 
    return data

drug_user_info = HA_formation(drug_user_TEN_YEARS)
#--------patients with in 2008-2010--------
drug_user_info_20082010 = drug_user_info[ (drug_user_info['admin_year']>=2008) 
                                         & (drug_user_info['admin_year']<=2010)]

#--sensitivity analysis (excluding death)
#drug_user_info_20082010 = drug_user_info_20082010[drug_user_info_20082010['DSTATUS']=='X']
print (len(set(drug_user_info_20082010['PATID'])))

''' #!!!
mental_illness=[]
for i in range(29000,31901):
    mental_illness.append("%.2f" % (i*0.01))
for i in range(2900,3191):
    mental_illness.append("%.1f" % (i*0.1))
for i in range(290,320):
    mental_illness.append("%.0f" % i)

diag_columns = ['diag_cd_01', 'diag_cd_02', 'diag_cd_03', 'diag_cd_04', 'diag_cd_05',
       'diag_cd_06', 'diag_cd_07', 'diag_cd_08', 'diag_cd_09', 'diag_cd_10', 'diag_cd_11', 'diag_cd_12',
       'diag_cd_13', 'diag_cd_14', 'diag_cd_15']
mental_patient = []
for i in drug_user_info_20082010.index:
    for j in diag_columns:
        if drug_user_info_20082010.loc[i,j] in mental_illness:
            mental_patient.append(drug_user_info_20082010.loc[i,'PATID'])
            break
mental_patient = set(mental_patient) 
print ('# mental patient...',len(mental_patient)) 
print ('all patient',len(set(drug_user_info_20082010['PATID'])))
'''

diag_columns = ['diag_cd_01', 'diag_cd_02', 'diag_cd_03', 'diag_cd_04', 'diag_cd_05',
       'diag_cd_06', 'diag_cd_07', 'diag_cd_08', 'diag_cd_09', 'diag_cd_10', 'diag_cd_11', 'diag_cd_12',
       'diag_cd_13', 'diag_cd_14', 'diag_cd_15']
dementia_patient = []
patient_dementiatype = dict()
for i in drug_user_info_20082010.index:
    for j in diag_columns:
        if drug_user_info_20082010.loc[i,j] in dementia_code:
            
            dementia_patient.append(drug_user_info_20082010.loc[i,'PATID'])
            
            patient_dementiatype[drug_user_info_20082010.loc[i,'PATID']] = drug_user_info_20082010.loc[i,j]
            
            break
dementia_patient = set(dementia_patient)  

#draw distribution of all 4819 dementia codes
dt_distri = Counter(patient_dementiatype.values())
df_distri = pd.DataFrame()
df_distri['codes'], df_distri['count'] = dt_distri.keys(), dt_distri.values()
df_distri = df_distri.sort_values('count', ascending=False)
df_distri.index =range(df_distri.shape[0])
plt.bar(df_distri['codes'], df_distri['count'])


#--------patients with in 2003-2007--------
drug_user_info_20032007 = drug_user_info[ (drug_user_info['admin_year']>=2003) 
                                         & (drug_user_info['admin_year']<=2007)]

pre_dementia_patient = []
for i in drug_user_info_20032007.index:
    for j in diag_columns:
        if drug_user_info_20032007.loc[i,j] in dementia_code:
            pre_dementia_patient.append(drug_user_info_20032007.loc[i,'PATID'])
pre_dementia_patient = set(pre_dementia_patient)        
post_dementia_pat = [i for i in dementia_patient if i not in pre_dementia_patient]

print ('# dementia patient...',len(dementia_patient) , 
       '# pre-dementia patient...', len(dementia_patient)-len(post_dementia_pat),
       '# valable dementia patient (post-dementia)...',len(post_dementia_pat))

#------dict PAT-event day------
PAT_event = dict()
for i in drug_user_info_20082010.index:
    if drug_user_info_20082010.loc[i,'PATID'] in post_dementia_pat:
        if drug_user_info_20082010.loc[i,'PATID'] not in PAT_event:
            for j in diag_columns:
                if drug_user_info_20082010.loc[i,j] in dementia_code:
                    PAT_event[drug_user_info_20082010.loc[i,'PATID']] = \
                    drug_user_info_20082010.loc[i, 'ADATE']
                    break
#---transer to pssn-event
from datetime import datetime
def event_day(strr, basetime): # return a set (start, end), compared with the basetime
    d1 = datetime.strptime(strr, '%Y-%m-%d')
    basetime = datetime.strptime(basetime, '%Y-%m-%d')
    return ( (d1-basetime).days )
print ('test..the event_day for 2010-07-01 is..',event_day('2010-07-01','2008-01-01') )

pssn_event=dict()
for i in PAT_event:
    pssn_event[pat2pssn[i]] = event_day(PAT_event[i],'2008-01-01')

#%%
#----read drug date----
def exposure_period(strr, basetime): # return a set (start, end), compared with the basetime
    d1,d2 = strr.strip().split('-')[0],strr.strip().split('-')[1]
    d1,d2 = datetime.strptime(d1, '%Y/%m/%d'),datetime.strptime(d2, '%Y/%m/%d')
    basetime = datetime.strptime(basetime, '%Y/%m/%d')
    return (( (d1-basetime).days, (d2-basetime).days  ))
print ('test..the exposure_period for 2010/07/01-2010/07/30 is..',exposure_period('2010/07/01-2010/07/30', '2008/01/01') )

drug_date = pd.read_csv('D:/research/HA_QP/jiannan/exposure_period_v2.csv')
drug_date = drug_date.dropna()
print (len(set(drug_date['patient_pssn'])))

#------dict pssn-exposure_period------
a=[]
duration_invalid = []
pssn_exposure_period = dict()
for i in drug_date.index:
    j = drug_date.loc[i,'period']
    j = j.split(';')
    a.append(j)
    for k in j:
        try:
            exposure_period(k,'2010/12/31')
        except:
            print (k) 
            k='2011/01/31-2011/02/28'            
        key = drug_date.loc[i,'patient_pssn']
        
        if ((exposure_period(k,'2010/12/31')[1]<0) and (exposure_period(k,'2008/01/01')[0]>0) and (pssn2pat[key] in post_dementia_pat)):    
            if key in pssn_exposure_period:
                pssn_exposure_period[key].append(exposure_period(k,'2008/01/01'))
            else:
                pssn_exposure_period[key]=[]
                pssn_exposure_period[key].append(exposure_period(k,'2008/01/01'))
        else: duration_invalid.append(key)
#%%
#-----intersection
intersection = list(set(pssn_exposure_period.keys()).intersection(set(pssn_event.keys())))
for i in duration_invalid:
    if i in intersection: 
        intersection.remove(i)
#give the intersection to jiannan
#get back patients with duration >= 7  
rmv = []
duration_greater_seven = pd.read_csv('../jiannan/pssn_select.csv') 
for i in intersection:
    if i not in duration_greater_seven.values.flatten(): 
        rmv.append(i)
for i in rmv: intersection.remove(i)   
   
day_20080101 = 0
day_20101231 = event_day('2010-12-31','2008-01-01')
first_treatment_period_start, first_treatment_period_end = dict(), dict()
before_first_treatment_start, before_first_treatment_end = dict(), dict()
period_fu1_start, period_fu1_end = dict(), dict()
period_fu2_start, period_fu2_end = dict(), dict()
washout_start, washout_end = dict(), dict()
washout = dict()
subsequent_treatment = dict()

overlap=[]
for pssn in intersection:
    if len(pssn_exposure_period[pssn])>=2:
        if pssn_exposure_period[pssn][1][0]-pssn_exposure_period[pssn][0][1] <= 50: 
            overlap.append(pssn)   
                    
for i in overlap: intersection.remove(i)
print ('# individuals...', len(intersection))
for pssn in intersection:
    
    first_treatment_period_start[pssn] = pssn_exposure_period[pssn][0][0]
    
    first_treatment_period_end[pssn] = pssn_exposure_period[pssn][0][1]+0
    if first_treatment_period_end[pssn] > day_20101231: first_treatment_period_end[pssn] = day_20101231
    
    #---subsequent--
    if len(pssn_exposure_period[pssn])>1:
        for p in pssn_exposure_period[pssn][1:]:
            if pssn in subsequent_treatment:
                subsequent_treatment[pssn].append(p)
            else:
                subsequent_treatment[pssn] = []
                subsequent_treatment[pssn].append(p)
        
    before_first_treatment_end[pssn] = pssn_exposure_period[pssn][0][0]
    
    before_first_treatment_start[pssn] = pssn_exposure_period[pssn][0][0]-50
    if before_first_treatment_start[pssn] < 0: before_first_treatment_start[pssn] = 0
    
    period_fu2_start[pssn], period_fu2_end[pssn] = pssn_exposure_period[pssn][0][0]-90, pssn_exposure_period[pssn][0][0]-60
    period_fu1_start[pssn], period_fu1_end[pssn] = pssn_exposure_period[pssn][0][0]-60, pssn_exposure_period[pssn][0][0]-30
    if period_fu2_start[pssn] < 0: period_fu2_start[pssn] = 0 
    if period_fu2_end[pssn] < 0:   period_fu2_end[pssn] = 0  
    if period_fu1_start[pssn] < 0: period_fu1_start[pssn] = 0
    if period_fu1_end[pssn] < 0:   period_fu1_end[pssn] = 0
    
    #---washout--
    #for p in pssn_exposure_period[pssn]:
        #if pssn in washout:
            #washout[pssn].append(p)
        #else:
            #washout[pssn] = []
            #washout[pssn].append(p)
    
    washout_start[pssn],washout_end[pssn] = pssn_exposure_period[pssn][0][1], pssn_exposure_period[pssn][0][1]+50  
    if washout_end[pssn] > day_20101231: washout_end[pssn] = day_20101231
    
#---count for every period-----
count_1,count_2,count_3,count_4, count_fu2,count_fu1,count_washout  = 0,0,0,0,0,0,0
patient_days_1,patient_days_2,patient_days_3,patient_days_4 = 0,0,0,0
patient_days_fu1,patient_days_fu2 = 0,0
patient_days_washout = 0 

aa=[]

for pssn in intersection:

    #----------patient-days---------
    period_washout = washout_end[pssn]-washout_start[pssn]
    patient_days_washout+=period_washout
    
    #for i in washout[pssn]:
        #washout_end = i[1]+50
        #if washout_end > day_20101231: washout_end = day_20101231
        #period_washout = washout_end-i[1]
        #patient_days_washout += period_washout
    
    period_fu2 = period_fu2_end[pssn] - period_fu2_start[pssn]
    patient_days_fu2 += period_fu2
    
    period_fu1 = period_fu1_end[pssn] - period_fu1_start[pssn]
    patient_days_fu1 += period_fu1

    period_1 = before_first_treatment_end[pssn]-before_first_treatment_start[pssn]
    patient_days_1 += period_1
    
    period_2 = first_treatment_period_end[pssn]-first_treatment_period_start[pssn]
    patient_days_2 += period_2
    
    period_3 = 0
    if pssn in subsequent_treatment:
        for i in subsequent_treatment[pssn]:
            period_3 = i[1]-i[0]
            patient_days_3 += period_3
    
    period_4 = event_day('2010-12-31','2008-01-01')-period_1-period_2-period_3-period_washout
    patient_days_4 += period_4 
    
    #---------count----------
    baseline_indicator = True
    '''
    if ( (pssn_event[pssn]>period_fu2_start[pssn]) and \
        (pssn_event[pssn]<=period_fu2_end[pssn])): 
        count_fu2+=1
        baseline_indicator = False
         
    if ( (pssn_event[pssn]>period_fu1_start[pssn]) and \
        (pssn_event[pssn]<=period_fu1_end[pssn])): 
        count_fu1+=1
        baseline_indicator = False
        
    '''
    overlap_test=0
    #---washout--
    if ( (pssn_event[pssn] > washout_start[pssn]) and \
        (pssn_event[pssn] <= washout_end[pssn]) ): 
        count_washout+=1
        baseline_indicator = False
        overlap_test=overlap_test+1
    

    #for i in washout[pssn]:
        #washout_end = i[1]+50
        #if washout_end > day_20101231: washout_end = day_20101231
        #if ( (pssn_event[pssn]>i[1]) and (pssn_event[pssn]<=washout_end) ):
            #count_washout+=1
            #baseline_indicator = False      
            #overlap_test=overlap_test+1
        
    if ( (pssn_event[pssn]>before_first_treatment_start[pssn]) and \
        (pssn_event[pssn]<=before_first_treatment_end[pssn]) ): 
        count_1+=1
        baseline_indicator = False
        overlap_test=overlap_test+1
        
    if ((pssn_event[pssn]>first_treatment_period_start[pssn]) and \
        (pssn_event[pssn]<=first_treatment_period_end[pssn])):       
        count_2+=1
        baseline_indicator = False
        overlap_test=overlap_test+1
        aa.append(pssn)
    
    if pssn in subsequent_treatment:
        for i in subsequent_treatment[pssn]:
            if ( (pssn_event[pssn]>i[0]) and (pssn_event[pssn]<=i[1]) ):  
                count_3+=1
                baseline_indicator = False
                overlap_test+=1
                aa.append(pssn)
           
    if overlap_test>=2: print(pssn)
    
    if baseline_indicator:
        count_4+=1

#pssn_event[28047732]
#pssn_exposure_period[28047732]
print ("patient_days...",patient_days_1,patient_days_2,patient_days_washout,patient_days_3,patient_days_4)
print ("# of event...",count_fu2, count_fu1, count_1,count_2,count_washout,count_3,count_4)
print ("coarse risk ratio...",
       #round(count_fu2/patient_days_fu2*1000,2),round(count_fu1/patient_days_fu1*1000,2),
       round(count_1/patient_days_1*1000,2),round(count_2/patient_days_2*1000,2),round(count_washout/patient_days_washout*1000,2),
       round(count_3/patient_days_3*1000,2),round(count_4/patient_days_4*1000,2))
#'At first, later higher'
# after ensure the first onset of dementia is considered, the subsequent period becomes low 
#%%
import math
obs_start,obs_end,first_treatment_start,first_treatment_end,eventdate = [],[],[],[],[]
second_treatment_start,second_treatment_end = [],[]
third_treatment_start,third_treatment_end = [],[]
case_id = []
a = 1
for pssn in intersection:
    '''    
    #-----sensitivity analysis (excluding exposure period < 30)
    exposure_1 = first_treatment_period_end[pssn]-first_treatment_period_start[pssn]
    exposure_sub = 0
    if pssn in subsequent_treatment:
        for i in subsequent_treatment[pssn]:
            exposure_sub = i[1]-i[0]
    if exposure_1+exposure_sub < 30: continue 
    '''
    
    case_id.append(a)
    a = a + 1
    obs_start.append(0)
    obs_end.append(day_20101231)

    eventdate.append(pssn_event[pssn]) 
    
    first_treatment_start.append(first_treatment_period_start[pssn])
    first_treatment_end.append(first_treatment_period_end[pssn])
    
    #second treatment
    if len(pssn_exposure_period[pssn])>=2:
        second_treatment_start.append(pssn_exposure_period[pssn][1][0])
        second_treatment_end.append(pssn_exposure_period[pssn][1][1])
    else:
        second_treatment_start.append(math.nan)
        second_treatment_end.append(math.nan)
    
    #third treatment
    if len(pssn_exposure_period[pssn])>=3:
        third_treatment_start.append(pssn_exposure_period[pssn][2][0])
        third_treatment_end.append(pssn_exposure_period[pssn][2][1])
    else:
        third_treatment_start.append(math.nan)
        third_treatment_end.append(math.nan)
    
nonparameter_sccs = pd.DataFrame(columns=['obs_start','obs_end','first_treatment_start',
                                          'first_treatment_end','eventdate']) 

nonparameter_sccs['case_id'] = case_id 
nonparameter_sccs['obs_start'] = obs_start 
nonparameter_sccs['obs_end'] = obs_end 
nonparameter_sccs['eventdate'] = eventdate 

nonparameter_sccs['first_treatment_start'] = first_treatment_start 
nonparameter_sccs['first_treatment_end'] = first_treatment_end 

nonparameter_sccs['second_treatment_start'],nonparameter_sccs['second_treatment_end'] = second_treatment_start,second_treatment_end 

nonparameter_sccs['third_treatment_start'],nonparameter_sccs['third_treatment_end'] = third_treatment_start, third_treatment_end

nonparameter_sccs.to_csv('nonparameter_sccs.csv', index=False)    

nonparameter_sccs.dropna()


#%%
# to jiannan
import pickle
def save_obj(obj, name ):
    with open('./to_jiannan/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open('./to_jiannan/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)
    
    
#ehr    
eligible_patient_lst = [pssn2pat[i] for i in intersection] #drug_user_lst: PATID
eligible_patient_ehr = data_10YEARS[data_10YEARS['PATID'].isin(eligible_patient_lst)]  # to jiannan        
eligible_patient_ehr.to_csv('./to_jiannan/patient_ehr.csv', index=False)    
    
#PAT-EVENT
save_obj(PAT_event, 'PAT_event')  


import scipy.stats as st
a = [0.951,0.948,0.952,0.960,0.947,0.939,0.944,0.962,0.925]
a1 = st.t.interval(0.95, len(a)-1, loc=np.mean(a), scale=st.sem(a))
a2 = np.mean(a)
np.std(a, ddof = 1)
print (a1[1]-a2, a2-a1[0])


