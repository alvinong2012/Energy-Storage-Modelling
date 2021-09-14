#Master Function to dictate charging/discharging---------------------------------------------------------------------------------------------------------------------------
def char_dischar(state, storage, dis_left, char_left,proxy_factor,time_idx):

    error=''
    loss = 0
    leftover = 0
    end_stor = 0

    state_to_fix = state
    
    if dis_left > 0:
        char_or_dis = 'Discharge'
    else:
        char_or_dis = 'Charge'

    #configuration_raw = configuration_raw.loc[(configuration_raw['State']==state_to_fix) &\
                                              #(configuration_raw['Type']==char_or_dis)]

    #configuration = calc_proxy(configuration_raw,storage,proxy_factor,char_or_dis)
    
    configuration  = storage_config(state, storage,dis_left,char_left, proxy_factor)
    
    configuration['New Storage Value']=0
    
    while dis_left + char_left > 0:
        interconnection = 0
        for index,state_to in configuration.iterrows():
            #Collecting State Name
            state_to_send = state_to['Name'][0:3]
            if state_to_send[-1] == " ":
                state_to_send = state_to_send[:-1]
                
            state_to_send_class = getattr(sys.modules[__name__], state_to_send)

            #Collecting storage type
            storage_type = state_to['Name'][len(state_to_send_class.name)+1:]
            storage_eff = getattr(state_to_send_class.eff, storage_type)
            storage_pwr = getattr(state_to_send_class.pwr, storage_type)
            storage_stor = getattr(state_to_send_class.stor, storage_type)
            storage_value = state_to['Storage Value']

            if state_to['Interconnector Capacity'] == 'No':
                stor_cap = storage_pwr
            else:
                inter_cap = state_to['Interconnector Capacity']
                if inter_cap < storage_pwr:
                    stor_cap = inter_cap
                else: 
                    stor_cap = storage_pwr
                interconnection = interconnection + stor_cap


            if char_left > 0:
                charg = charge(char_left, storage_value, storage_eff,\
                                    storage_stor,\
                                    stor_cap,time_idx)
                storage_final = charg[0]
                configuration.loc[index,'New Storage Value'] = storage_final
                char_left = charg[1]
                loss = charg[2]
                error = charg[3]
                    
            else:
                discharg = discharge(dis_left, storage_value, storage_eff,\
                                    stor_cap,time_idx)
                storage_final = discharg[0]
                configuration.loc[index,'New Storage Value'] = storage_final
                dis_left = discharg[1]
                loss = discharg[2]
                error = discharg[3]
                    
            leftover = dis_left + char_left
           
            if leftover == 0:
                break
            
        if leftover > 0:
            end_stor = 1
            break
        else:
            leftover = 0
    
    configuration['New Storage Value'] = np.where(configuration['New Storage Value']==0, \
                                                      configuration['Storage Value'],\
                                                      configuration['New Storage Value'])
    return(configuration,leftover,interconnection,error)
#Function to create configuration of storage-------------------------------------------------------------------------------------------------------------------------------
def storage_config(state, storage,dis_left,char_left, proxy_factor):
        #proxy_score = %eff of storage / fullness %
    
    proxy_score = pd.DataFrame({'Name':[],'Efficiency':[],'% Fullness':[],'Interconnector Capacity':[],\
                                'Storage Value':[]})

    state_to_fix = state

    stateus_maximus = [NSW, QLD, VIC ,TAS ,SA]

    for stateus in stateus_maximus:
        max_stor = 0
        if stateus.name_long == state_to_fix:

            cols = [stateus.name + ' fly', stateus.name + ' batt', stateus.name + ' phes',\
                    stateus.name + ' caes', stateus.name + ' hyd']
            
            for idx,stortus in enumerate(cols):
                stor_value = storage[stortus].iloc[-1]
                max_stor = getattr(stateus.stor, stortus[len(stateus.name)+1:])
                stor_perc = stor_value/max_stor
                stor_eff = getattr(stateus.eff, stortus[len(stateus.name)+1:])
                to_append = [stortus, stor_eff,stor_perc,'No',stor_value]
                to_series = pd.Series(to_append,index=proxy_score.columns)
                proxy_score = proxy_score.append(to_series,ignore_index=True)

            if dis_left > 0 :
                inter_possibility = inter_raw.loc[(inter_raw['From'] == state_to_fix)]
                state_to = inter_possibility['To'].unique()
            else:
                inter_possibility = inter_raw.loc[(inter_raw['To'] == state_to_fix)]
                state_to = inter_possibility['From'].unique()

            for stateus_again in stateus_maximus:
                
                if stateus_again.name_long in state_to:

                    cols = [stateus_again.name + ' fly', stateus_again.name + ' batt', stateus_again.name + ' phes',\
                    stateus_again.name + ' caes', stateus_again.name + ' hyd']
                                        
                    if dis_left > 0:
                        inter_cap = inter_possibility.loc[inter_possibility['To']==stateus_again.name_long,\
                                                          'Nominal Capacity'].sum()
                        
                    else:
                        inter_cap = inter_possibility.loc[inter_possibility['From']==stateus_again.name_long,\
                                                          'Nominal Capacity'].sum()
    
                            
                    for stortus in cols:
                        max_stor = storage[stortus].iloc[-1] + max_stor

                    for idx,stortus in enumerate(cols):
                        stor_value = storage[stortus].iloc[-1]
                        max_stor = getattr(stateus_again.stor, stortus[len(stateus_again.name)+1:])
                        stor_perc = stor_value/max_stor
                        stor_eff = getattr(stateus_again.eff, stortus[len(stateus_again.name)+1:])
                        to_append = [stortus, stor_eff,stor_perc,inter_cap,stor_value]
                        to_series = pd.Series(to_append,index=proxy_score.columns)
                        proxy_score = proxy_score.append(to_series,ignore_index=True)

    
    if dis_left > 0 :
        proxy_score['Proxy Score'] = np.where(proxy_score['Interconnector Capacity'] == 'No',\
                                              proxy_score['Efficiency']*proxy_score['% Fullness']*proxy_factor,\
                                              proxy_score['Efficiency']*proxy_score['% Fullness'])
    else:
        proxy_score['Proxy Score'] = np.where(proxy_score['Interconnector Capacity'] == 'No',\
                                              (proxy_score['Efficiency']/proxy_score['% Fullness'])*proxy_factor,\
                                              proxy_score['Efficiency']/proxy_score['% Fullness'])
        
    inter = proxy_score[proxy_score['Interconnector Capacity'] != 'No']
    inter_state = []

    for name in inter['Name'].unique():
        inter_state.append(name[:3])
    unique_inter_state = list(set(inter_state))

    for name in unique_inter_state:
        target_row = [row for row in inter['Name'] if name in row]
        to_remove_inter = inter[inter['Name'].isin(target_row)]
        max_proxy_score = to_remove_inter['Proxy Score'].max()
        to_remove_inter = to_remove_inter[to_remove_inter['Proxy Score'] != max_proxy_score]
        
        to_remove_inter_lst = list(to_remove_inter['Name'])

        proxy_score=proxy_score[~proxy_score['Name'].isin(to_remove_inter_lst)]
    
    
    return(proxy_score.sort_values(['Proxy Score'],ascending=False))
#Function to decide state from index number--------------------------------------------------------------------------------------------------------------------------------
def decide_state_r(state):
    
    if state == 'New South Wales':
        index = 0
    elif state == 'Queensland':
        index = 1
    elif state == 'Victoria':
        index = 2
    elif state == 'Tasmania':
        index = 3
    elif state == 'South Australia':
        index = 4
    return(index)
#Function to decide index from state---------------------------------------------------------------------------------------------------------------------------------------
def decide_state(index):
    if index == 0:
        #Run NSW's Interconnector
        p = 'New South Wales'
    elif index == 1:
        #Run QLD's Interconnector
        p = 'Queensland'
    elif index == 2:
        #Run VIC's Interconnector
        p = 'Victoria'
    elif index == 3:
        #Run VIC's Interconnector
        p = 'Tasmania'
    elif index == 4:
        #Run VIC's Interconnector
        p = 'South Australia'
    return(p)
#Function containing discharge algorithem----------------------------------------------------------------------------------------------------------------------------------
def discharge(discharge_amt, stor_amt, stor_eff, stor_cap, time_idx):
    
    loss = 0
    
    #print('Discharge Amount: %d, Storage Amount: %d, Storage Eff: %f, Storage Pwr Capacity: %d' %(discharge_amt,stor_amt, stor_eff , stor_cap))
    
    pwr_cap = stor_cap *time_idx
    error = ''
    
    if pwr_cap < discharge_amt: # CASE 1: If Power capacity DOES NOT meet discharge requirements--------------------
        total_discharged = pwr_cap
        
        if stor_amt < total_discharged: # CASE 1A: If Storage level DOES NOT meet discharge requirements------------
            total_discharged = stor_amt
            new_stor_amt = 0
            discharge_leftover = discharge_amt- (total_discharged * (stor_eff))
            error = 'Power and Storage Capacity DOES NOT meet discharge requirements'
        
        else: #CASE 1B: If Storage level DOES meet discharge requirements-------------------------------------------
            new_stor_amt = stor_amt - total_discharged
            discharge_leftover = discharge_amt - (total_discharged * (stor_eff))
            error = 'Only Power Capacity DOES NOT meets discharge requirements'
                                                 
    else: #CASE 2: If Power Capacity DOES meet discharge requirements-----------------------------------------------
        total_discharge = discharge_amt
        
        if stor_amt < total_discharge: #CASE 2A: If Storage Level DOES NOT meet discharge requirements--------------
            total_discharge = stor_amt
            new_stor_amt = 0
            discharge_leftover = discharge_amt- (total_discharge * (stor_eff))
            error = 'Only Storage Capacity DOES NOT meets discahrge requirements'
            
        else: #CASE 2B: If Storage Level DOES meet discharge requirements-------------------------------------------
            discharge_leftover = 0
            new_stor_amt = stor_amt - discharge_amt
   
    return([new_stor_amt, discharge_leftover,loss,error])
#Function containing charge algorithem-------------------------------------------------------------------------------------------------------------------------------------
def charge(charge_amt, stor_amt , stor_eff, chargemax, stor_cap, time_idx):
    
    loss = 0
    
   #print('Charge Amount: %d, Storage Amount: %d, Storage Eff: %f, Storage Max: %d, Storage Pwr Capacity: %d' %(charge_amt, stor_amt , stor_eff, chargemax, stor_cap))
    pwr_cap = stor_cap * time_idx
    error=""
    
    if pwr_cap < charge_amt: # CASE 1: If Power capacity DOES NOT meet charge requirements--------------------
        total_charged = pwr_cap
        
        if stor_amt + total_charged > chargemax: # CASE 1A: If Storage level DOES NOT meet charge requirements------------
            total_charged = chargemax - stor_amt
            new_stor_amt = chargemax
            charge_leftover = charge_amt - (total_charged * (1+(1-stor_eff)))
            error = 'Power and Storage Capacity DOES NOT meet charge requirements'
        
        else: #CASE 1B: If Storage level DOES meet charge requirements-------------------------------------------
            new_stor_amt = stor_amt + total_charged
            charge_leftover = charge_amt - (total_charged * (1+(1-stor_eff)))
            error = 'Only Power Capacity DOES NOT meets charge requirements'
                                                 
    else: #CASE 2: If Power Capacity DOES meet charge requirements-----------------------------------------------
        total_charged = charge_amt
        
        if stor_amt + total_charged > chargemax: #CASE 2A: If Storage Level DOES NOT meet charge requirements--------------
            total_charged = chargemax - stor_amt
            new_stor_amt = chargemax
            charge_leftover = charge_amt - (total_charged * (1+(1-stor_eff)))
            error = 'Only Storage Capacity DOES NOT meets charge requirements'
            
        else: #CASE 2B: If Storage Level DOES meet charge requirements-------------------------------------------
            charge_leftover = 0
            new_stor_amt = stor_amt + charge_amt
    
    
    return([new_stor_amt, charge_leftover, loss,error])

#Importing Libraries-------------------------------------------------------------------------------------------------------------------------------------------------------
import numpy as np
import pandas as pd
import sys

#Defining Constants--------------------------------------------------------------------------------------------------------------------------------------------------------
storage_factor = 1
power_factor = 1
proxy_factor = 1.5

fly_eff = 0.9
batt_eff = 0.9
phes_eff = 0.8
caes_eff = 0.5
hyd_eff = 0.3
re_factor = 1
time_idx = 0.5

Y = pd.DataFrame()
renewable_generation = pd.DataFrame()

#States Classes-------------------------------------------------------------------------------------------------------------------------------------------------------------
class NSW:
    
    class eff:
        fly = fly_eff
        batt = batt_eff
        phes = phes_eff
        caes = caes_eff
        hyd = hyd_eff
        pass
    class pwr:
        fly = 4000*power_factor #MW
        batt = 6000*power_factor #MW
        phes = 17000*power_factor #MW
        caes = 17000*power_factor #MW
        hyd = 50000*power_factor #MW
        pass
    class stor:
        fly = 500*1000*storage_factor #MWh
        batt = 3200*1000*storage_factor  #MWh
        phes = 4000*1000*storage_factor  #MWh
        caes = 4000*1000*storage_factor  #MWh
        hyd = 2000*1000*storage_factor  #MWh
        pass   

    init_stor_factor = 1

    re_multiplier = 9.3*re_factor
    
    name = 'NSW'
    
    name_long = 'New South Wales'
    
    pass

class QLD:
    class eff:
        fly = fly_eff
        batt = batt_eff
        phes = phes_eff
        caes = caes_eff
        hyd = hyd_eff
        pass
    class pwr:
        fly = 6000*power_factor #MW
        batt = 6000*power_factor #MW
        phes = 17000*power_factor #MW
        caes = 17000*power_factor #MW
        hyd = 50000*power_factor #MW
        pass
    class stor:
        fly = 500*1000*storage_factor  #MWh
        batt = 1200*1000*storage_factor  #MWh
        phes = 3000*1000*storage_factor  #MWh
        caes = 3000*1000*storage_factor  #MWh
        hyd = 3000*1000*storage_factor  #MWh
        pass   

    init_stor_factor = 0.6

    re_multiplier = 8.6*re_factor
    
    name = 'QLD'
    
    name_long = 'Queensland'
    
    pass

class VIC:
    class eff:
        fly = fly_eff
        batt = batt_eff
        phes = phes_eff
        caes = caes_eff
        hyd = hyd_eff
        pass
    class pwr:
        fly = 2000*power_factor #MW
        batt = 10000*power_factor #MW
        phes = 20000*power_factor #MW
        caes = 20000*power_factor #MW
        hyd = 20000*power_factor #MW
        pass
    class stor:
        fly = 500*1000*storage_factor  #MWh
        batt = 600*1000*storage_factor  #MWh
        phes = 3000*1000*storage_factor  #MWh
        caes = 3000*1000*storage_factor  #MWh
        hyd = 2000*1000*storage_factor  #MWh
        pass   

    init_stor_factor = 0.65

    re_multiplier = 5*re_factor
    
    name = 'VIC'
    
    name_long = 'Victoria'
    
    pass

class TAS:
    class eff:
        fly = fly_eff
        batt = batt_eff
        phes = phes_eff
        caes = caes_eff
        hyd = hyd_eff
        pass
    class pwr:
        fly =1000*power_factor #MW
        batt = 5000*power_factor #MW
        phes = 15000*power_factor #MW
        caes = 15000*power_factor #MW
        hyd = 15000*power_factor #MW
        pass
    class stor:
        fly = 500*1000*storage_factor  #MWh
        batt = 600*1000*storage_factor  #MWh
        phes = 2000*1000*storage_factor  #MWh
        caes = 2000*1000*storage_factor  #MWh
        hyd = 2000*1000*storage_factor  #MWh
        pass

    init_stor_factor = 0.65

    re_multiplier = 7.3*re_factor
    
    name = 'TAS'
    name_long = 'Tasmania'
    
    pass

class SA:
    class eff:
        fly = fly_eff
        batt = batt_eff
        phes = phes_eff
        caes = caes_eff
        hyd = hyd_eff
        pass
    class pwr:
        fly = 200*power_factor  #MW
        batt = 1000*power_factor #MW
        phes = 2000*power_factor #MW
        caes = 2000*power_factor #MW
        hyd = 2000*power_factor #MW
        pass
    class stor:
        fly = 300*1000*storage_factor  #MWh
        batt = 400*1000*storage_factor  #MWh
        phes = 1200*1000*storage_factor  #MWh
        caes = 1000*1000*storage_factor  #MWh
        hyd = 1000*1000*storage_factor  #MWh
        pass   

    init_stor_factor = 0.55

    re_multiplier = 1.8*re_factor
    
    name = 'SA'
    
    name_long = 'South Australia'
    
    pass

#Loading Input Files-------------------------------------------------------------------------------------------------------------------------------------------------------------
file_loading = False
while file_loading != True:
    xls = pd.ExcelFile('Raw_Data.xlsx')
    inter_raw = pd.read_excel(xls, 'Interconnector Raw')
    Demand = pd.read_excel(xls, 'Scheduled Demand')
    NSW_TGen = pd.read_excel(xls, 'NSW Fuels')
    QLD_TGen = pd.read_excel(xls, 'QLD Fuels')
    VIC_TGen = pd.read_excel(xls, 'VIC Fuels')
    TAS_TGen = pd.read_excel(xls, 'Tas Fuels')
    SA_TGen = pd.read_excel(xls, 'SA Fuels')

    inter_raw['Nominal Capacity'] = inter_raw['Nominal Capacity'].str.replace('MW','')
    inter_raw['Nominal Capacity'] = pd.to_numeric(inter_raw['Nominal Capacity'] )
    file_loading = True

#Data Pre-processing of raw data-------------------------------------------------------------------------------------------------------------------------------------------------------------
data_preprocessing = False
while data_preprocessing != True:
    NSW_R_Gen = NSW_TGen[['Time-ending','Rooftop PV','Solar','Wind']]
    QLD_R_Gen = QLD_TGen[['Time-ending','Rooftop PV','Solar','Wind']]
    VIC_R_Gen = VIC_TGen[['Time-ending','Rooftop PV','Solar','Wind']]
    TAS_R_Gen = TAS_TGen[['Time-ending','Rooftop PV','Solar','Wind']]
    SA_R_Gen = SA_TGen[['Time-ending','Rooftop PV','Solar','Wind']]

    NSW_Demand = Demand[['NSW1 Scheduled Demand']]
    QLD_Demand = Demand[['QLD1 Scheduled Demand']]
    VIC_Demand = Demand[['VIC1 Scheduled Demand']]
    TAS_Demand = Demand[['TAS1 Scheduled Demand']]
    SA_Demand = Demand[['SA1 Scheduled Demand']]

    NSW_info1 = pd.concat([NSW_R_Gen,NSW_Demand],axis = 1)
    NSW_info1.rename(columns={'NSW1 Scheduled Demand': 'Demand'},inplace = True)
    NSW_info1['re_multi'] = NSW.re_multiplier

    QLD_info1 = pd.concat([QLD_R_Gen,QLD_Demand],axis = 1)
    QLD_info1.rename(columns={'QLD1 Scheduled Demand': 'Demand'},inplace = True)
    QLD_info1['re_multi'] = QLD.re_multiplier

    TAS_info1 = pd.concat([TAS_R_Gen,TAS_Demand],axis = 1)
    TAS_info1.rename(columns={'TAS1 Scheduled Demand': 'Demand'},inplace = True)
    TAS_info1['re_multi'] = TAS.re_multiplier

    SA_info1 = pd.concat([SA_R_Gen,SA_Demand],axis = 1)
    SA_info1.rename(columns={'SA1 Scheduled Demand': 'Demand'},inplace = True)
    SA_info1['re_multi'] = SA.re_multiplier

    VIC_info1 = pd.concat([VIC_R_Gen,VIC_Demand],axis = 1)
    VIC_info1.rename(columns={'VIC1 Scheduled Demand': 'Demand'},inplace = True)
    VIC_info1['re_multi'] = VIC.re_multiplier
    
    input_type = ''

    X = [NSW_info1, QLD_info1, VIC_info1, TAS_info1, SA_info1]
    Y = pd.DataFrame()
    for item in X:
        if str(item) == str(NSW_info1):
            name = 'NSW'
        elif str(item) == str(QLD_info1):
            name = 'QLD'
        elif str(item) == str(VIC_info1):
            name = 'VIC'
        elif str(item) == str(TAS_info1):
            name = 'TAS'
        elif str(item) == str(SA_info1):
            name = 'SA'
            
        for states_col in item.columns:
            if states_col == 'Time-ending':
                continue
            process_array = item[states_col]
            
            if input_type == 'half':
                x = ((process_array + process_array.shift(-1)))[::2]
                time_idx = 1
            else: 
                x = process_array
                time_idx = 0.5
            Y[name +' ' + states_col] = x

    data_preprocessing = True

#Determining Total Discharge and Charge Required per time interval and storing it in dataframe (States)----------------------------------------------------------------------------
creating_states = False
while creating_states !=True:
    X = [NSW, QLD, VIC, TAS, SA]
    states = pd.DataFrame()

    #Calculating charge/discharge requirement
    for item in X:
        state_name = item.name
        total_renewable = (Y[state_name + ' Rooftop PV'] + Y[state_name +' Solar'] +\
                        Y[state_name +' Wind'])*Y[state_name +' re_multi']
        states[state_name+ ' To_Re']= total_renewable
        Y[state_name+ ' To_Re'] = total_renewable
        states[state_name+' Charge(MWh)'] = np.where(Y[state_name+' Demand']<Y[state_name+' To_Re'], \
                                                    Y[state_name+' To_Re']-Y[state_name+' Demand'],0)
        states[state_name+' Discharge(MWh)'] = np.where(Y[state_name+' Demand']<Y[state_name+' To_Re'],\
                                                        0, Y[state_name+' Demand']-Y[state_name+' To_Re'])
        renewable_generation[state_name + ' Solar'] = Y[state_name +' Solar']
        renewable_generation[state_name + ' Wind'] = Y[state_name +' Wind']
    
    #Adding blank line of zeros as the first row
    makezeros = [0]*len(states.columns)
    b_series = pd.DataFrame(makezeros, index = states.columns)
    states = pd.concat([b_series.T,states]).reset_index(drop=True)
    
    creating_states = True

#Creating dataframes and setting up for the main simulation------------------------------------------------------------------------------------------------------------------------------------
setup = False
while setup != True:
    all_storage_raw= pd.DataFrame({'NSW fly' : [] , 'NSW batt':[], \
                                'NSW phes' : [], 'NSW caes' : [],\
                                'NSW hyd' : [], 'NSW Interconnector/s' : [],\
                                    'QLD fly' : [] , 'QLD batt':[], \
                                'QLD phes' : [], 'QLD caes' : [],\
                                'QLD hyd' : [], 'QLD Interconnector/s' : [],\
                                    'VIC fly' : [] , 'VIC batt':[], \
                                'VIC phes' : [], 'VIC caes' : [],\
                                'VIC hyd' : [], 'VIC Interconnector/s' : [],\
                                    'TAS fly' : [] , 'TAS batt':[], \
                                'TAS phes' : [], 'TAS caes' : [],\
                                'TAS hyd' : [], 'TAS Interconnector/s' : [],\
                                    'SA fly' : [] , 'SA batt':[], \
                                'SA phes' : [], 'SA caes' : [],\
                                'SA hyd' : [], 'SA Interconnector/s' : []})
    storage_inter = all_storage_raw.copy()
    initial_factor = []

    for columns in storage_inter:
        storage_type = columns[4:]
        state_to_send = columns[0:3]
        
        if state_to_send[2:3] == " ":
            state_to_send = columns[0:2]
            storage_type = columns[3:]
            
        if storage_type == 'Interconnector/s':
            stor_init_amt = 0
            
        else:
            state_to_send_class = getattr(sys.modules[__name__], state_to_send)
            stor_stor = getattr(state_to_send_class.stor, storage_type)
            init_factor = state_to_send_class.init_stor_factor
            stor_init_amt = stor_stor*init_factor
        
        initial_factor.append(stor_init_amt)
    a_series = pd.Series(initial_factor,index=storage_inter.columns)
    storage_inter = storage_inter.append(a_series,ignore_index=True)

    setup = True

#Main Simulation-------------------------------------------------------------------------------------------------------------------------------------------------------------
simulation = False
while simulation != True:
    #Setting up for main simulation
    states2 = states.copy()
    total_len = len(states2)
    end = 0
    storage = storage_inter.copy()
    #Running Main Simulation--------------------------------------------------------------------------------
    hold = [NSW,QLD,VIC,TAS,SA] # 1 = NSW, 2 = QLD, 3 = VIC, 4 = TAS, 5 = SA

    for index, row in states2.iterrows():
        temp_storage = pd.DataFrame(storage.iloc[-1]).T 
        print("I'm still going. Be Patient. I'm at %d/%d"%(index,total_len))
        if index == 0:
            continue
        
        for index_state ,item in enumerate(hold):
                    
            target_state = [col for col in states2.columns if item.name in col]
            char_left = row[target_state[1]]
            dis_left = row[target_state[2]]
            reference_idx = char_dischar(item.name_long,temp_storage,dis_left,char_left, proxy_factor,time_idx)
            configuration = reference_idx[0]        
            leftover = reference_idx[1]
            error_term = reference_idx[3]
            #storing interconnection values
            #interconnection_cap = reference_idx[2]
            #state_to_interconnect = item.name
            #temp_storage[state_to_interconnect + ' Interconnector/s'] = interconnection_cap
                    
            for idx, config in configuration.iterrows():
                reference = config['Name']
                temp_storage[reference] = config['New Storage Value']
        
            if leftover>0:
                
                if char_left > 0:
                    print('charge leftover (%f) detected in %s' %(leftover, item.name_long))
                    #print(leftover)
                    thingo = item.name+' Interconnector/s'
                    temp_storage[thingo] = leftover
                elif dis_left>0:
                    print('The Simulation Failed at %s due to %s'%(item.name_long, error_term))
                    end = 1
                    break
                
        if end == 1:
            break

        storage = storage.append(temp_storage).reset_index(drop=True)

    state_to_fix = [NSW, QLD, VIC ,TAS ,SA]
    stor_info = pd.DataFrame({'No.':['Efficiency (%)', 'Power Capacity (MW)', 'Storage Capacity (MWh)', 'Renewable Factor']})

    for states_app in state_to_fix:
        
        parameters = [states_app.eff, states_app.pwr, states_app.stor, states_app.re_multiplier]
        cols = [states_app.name + ' Flywheels', states_app.name + ' Batt', states_app.name + ' PHES',\
                    states_app.name + ' CAES', states_app.name + ' Hydrogen', states_app.name + ' Renewable Factor']
        state_storage = pd.DataFrame()
        
        for parameter in parameters:
            
            if parameter == states_app.re_multiplier:
                to_append = [0, 0, 0, 0, 0, states_app.re_multiplier]
            else:
                to_append = [parameter.fly, parameter.batt, parameter.phes, parameter.caes, parameter.hyd,0]
            
                    
            if parameter == states_app.stor:
                maxstor = sum(to_append)  
                
            a_series = pd.Series(to_append, index=cols)
            state_storage = state_storage.append(a_series, ignore_index=True, sort=False)
            state_storage = state_storage.reindex(cols, axis=1)
        
        stor_info = pd.concat([stor_info, state_storage], axis=1)
        
    stor_info.set_index('No.', inplace = True)
    simulation = True
    x = NSW_TGen['Time-ending']
    storage['TimeDate'] = x
    storage = storage.set_index('TimeDate')

#Main Cost Estimate Generation-------------------------------------------------------------------------------------------------------------------------------------------------------------
cost_estimate = False
while cost_estimate != True:
    #Generating Cost Estimates
    cost_xls = pd.ExcelFile('Cost Estimates for Importing.xlsx')
    cost_storage = pd.read_excel(cost_xls, 'Storage')
    cost_generation = pd.read_excel(cost_xls, 'Generation')

    #Calculating Energy Generation
    LCOE = pd.DataFrame()
    Solar_LCOE = cost_generation.loc['LCOE ($AUD/kWh)']['Residential/Commercial Solar'] * 1000 #$AUD/MWh
    Wind_LCOE = cost_generation.loc['LCOE ($AUD/kWh)']['Wind'] * 1000 #$AUD/MWh


    for states in X:
        target_state = [col for col in renewable_generation.columns if states.name in col]
        solar_state = [col for col in target_state if 'Solar' in col]
        wind_state = [col for col in target_state if 'Wind' in col]
        Solar_Cost = renewable_generation[solar_state] * Solar_LCOE
        Wind_Cost = renewable_generation[wind_state] * Wind_LCOE
        LCOE[solar_state] = Solar_Cost
        LCOE[wind_state] = Wind_Cost

    #Calculating Energy Storage 
    cost_storage = cost_storage.set_index('Index')
    states = [NSW, QLD, VIC, TAS, SA]
    states_name = [NSW.name,QLD.name,VIC.name,TAS.name,SA.name]
    storage_name = ['Flywheel', 'Batt', 'CAES', 'PHES', 'Hydrogen']

    ##Time Frame Calc
    print(storage)
    start_date = storage.index[0]
    end_date = storage.index[-1]
    num_year = ((end_date.year - start_date.year) * 12 + (end_date.month - start_date.month))/12

    ## CAPEX
    capex_df = pd.DataFrame()


    for col in stor_info:
        state = col[:3]
        if state == 'SA ':
            state = col[:2]
        if 'Flywheels' in col:
            static_cost_MW = cost_storage.loc['Investment Cost ($AUD/MW)']['fly']
            state_cost_MW = (static_cost_MW*stor_info.loc['Power Capacity (MW)'][col])/1e9
            
            static_cost_MWh = cost_storage.loc['Investment Cost ($AUD/MWh)']['fly']
            state_cost_MWh = (static_cost_MWh*stor_info.loc['Storage Capacity (MWh)'][col])/1e9
                
            capex = ((state_cost_MW + state_cost_MWh)/cost_storage.loc['Lifetime (years)']['fly'])*num_year
            capex_df[state + ' fly'] = [capex]
        elif 'Batt' in col:
            static_cost_MW = cost_storage.loc['Investment Cost ($AUD/MW)']['batt']
            state_cost_MW = (static_cost_MW*stor_info.loc['Power Capacity (MW)'][col])/1e9
            
            static_cost_MWh = cost_storage.loc['Investment Cost ($AUD/MWh)']['batt']
            state_cost_MWh = (static_cost_MWh*stor_info.loc['Storage Capacity (MWh)'][col])/1e9
            
            capex = ((state_cost_MW + state_cost_MWh)/cost_storage.loc['Lifetime (years)']['batt'])*num_year
            capex_df[state + ' batt'] = [capex]
            
        elif 'PHES' in col:
            static_cost_MW = cost_storage.loc['Investment Cost ($AUD/MW)']['phes']
            state_cost_MW = (static_cost_MW*stor_info.loc['Power Capacity (MW)'][col])/1e9
            
            static_cost_MWh = cost_storage.loc['Investment Cost ($AUD/MWh)']['phes']
            state_cost_MWh = (static_cost_MWh*stor_info.loc['Storage Capacity (MWh)'][col])/1e9
            
            capex = ((state_cost_MW + state_cost_MWh)/cost_storage.loc['Lifetime (years)']['phes'])*num_year
            capex_df[state + ' phes'] = [capex]
            
        elif 'CAES' in col:
            static_cost_MW = cost_storage.loc['Investment Cost ($AUD/MW)']['caes']
            state_cost_MW = (static_cost_MW*stor_info.loc['Power Capacity (MW)'][col])/1e9
            
            static_cost_MWh = cost_storage.loc['Investment Cost ($AUD/MWh)']['caes']
            state_cost_MWh = (static_cost_MWh*stor_info.loc['Storage Capacity (MWh)'][col])/1e9
            
            capex = ((state_cost_MW + state_cost_MWh)/cost_storage.loc['Lifetime (years)']['caes'])*num_year
            capex_df[state + ' caes'] = [capex]
            
        elif 'Hyd' in col:
            static_cost_MW = cost_storage.loc['Investment Cost ($AUD/MW)']['hyd']
            state_cost_MW = (static_cost_MW*stor_info.loc['Power Capacity (MW)'][col])/1e9
            
            static_cost_MWh = cost_storage.loc['Investment Cost ($AUD/MWh)']['hyd']
            state_cost_MWh = (static_cost_MWh*stor_info.loc['Storage Capacity (MWh)'][col])/1e9
            
            capex = ((state_cost_MW + state_cost_MWh)/cost_storage.loc['Lifetime (years)']['hyd'])*num_year
            capex_df[state + ' hyd'] = [capex]

    capex_df['Index'] = 'Capex'
    capex_df=capex_df.set_index('Index')
    capex_df = capex_df.T

    ##OPEX
    variable_cost_df = pd.DataFrame()
    fixed_cost_df = pd.DataFrame()
    for col in storage:
        storage_col_name = col[4:]
        if col[:2] == 'SA':
            storage_col_name = col[3:]
        if storage_col_name == 'Interconnector/s':
            continue
        
        act_var_cost = cost_storage.loc['Variable O&M Cost ($AUD/MWh)'][storage_col_name]
        act_fixed_cost = cost_storage.loc['Fixed O&M Cost ($AUD/MWh-1/2hr)'][storage_col_name]
        variable_cost_df[col] = storage[col]*act_var_cost
        fixed_cost_df[col] = storage[col]*act_fixed_cost

    total_sum_cost = pd.DataFrame({'Capex ($ Billion AUD)': capex_df['Capex'],\
                                    'Variable Cost ($ Billion AUD)':variable_cost_df.sum(axis = 0)/1e9,\
                                'Fixed Cost ($ Billion AUD)':fixed_cost_df.sum(axis = 0)/1e9}) 

    total_sum_cost_fin = pd.DataFrame()
    total_sum_cost_fin['Storage Cost ($ Billion AUD)'] = total_sum_cost.sum(axis=1)

    #Generating Final Cost Estimates
    fin_table = pd.DataFrame()
    for x in states:
        target_row = [row for row in total_sum_cost_fin.index if x.name in row]
        target_df = total_sum_cost_fin.loc[target_row,:]
        storage_cost = target_df.sum(axis = 0)
        fin_table[x.name] = storage_cost
    fin_table = fin_table.T

    gen_cost = []
    for x in states:
        target_col = [col for col in LCOE.columns if x.name in col]
        target_df = LCOE.loc[:,target_col]
        generation_cost = target_df.sum(axis = 0).sum()/1e9
        #fin_table[x.name] = generation_cost
        gen_cost.append(generation_cost)
    fin_table['Generation Cost ($ Billion AUD)'] =  gen_cost

    ttl_dmd=[]
    for x in states:
        target_col = [col for col in Demand.columns if x.name in col]
        target_df = Demand.loc[:,target_col]
        total_demand = target_df.sum(axis = 0)
        ttl_dmd.append(total_demand[0])
    fin_table['Total Energy to Demand (MWh)'] = ttl_dmd

    fin_table['LCOE ($AUD/MWh)'] = ((fin_table['Storage Cost ($ Billion AUD)']*1e9)+\
                                    (fin_table['Generation Cost ($ Billion AUD)']*1e9))/\
                            (fin_table['Total Energy to Demand (MWh)'])

    cost_estimate = True

#Exporting Information to JSON-------------------------------------------------------------------------------------------------------------------------------------------------------------
exporting = False
while exporting != True:
    stor_info.to_json('Run 2 - Inputs.json',orient='columns')     
    storage.to_json('Run 2 - Results.json',orient='columns',date_unit='s', date_format='iso')
    fin_table.to_json('Run 2 - Cost.json',orient='columns')
    exporting = True