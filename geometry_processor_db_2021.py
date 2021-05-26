# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 16:39:36 2019

@author: Roberto
@editor: Sélèn & Maxwell
"""

import numpy as np
import geopandas as gpd
import shapely.geometry as shp
import multiprocessing
# To avoid pandas warnings
import warnings
warnings.filterwarnings('ignore')



def eg_run(buildings_df):
    df_length = len(buildings_df)
    envelope = gpd.GeoDataFrame(columns=['egid', 'geometry', 'class_id'])
    # Create as many processes as there are CPUs on the machine - 1
    num_processes = min(multiprocessing.cpu_count()-1, df_length)
    # Calculate the chunk size as an integer
    chunk_size = int(np.ceil(df_length/num_processes))
    # Divide the df in chunks
    chunks = [buildings_df.iloc[buildings_df.index[i:i + chunk_size]] for i in range(0, df_length, chunk_size)]
    # Create a pool of processes
    pool = multiprocessing.Pool(processes=num_processes)
    # Apply the function to the chunks and combine the results in a single df
    for result in pool.starmap(envelope_generator, [(i, buildings_df) for i in chunks]):
        envelope = envelope.append(result, ignore_index = True)
    pool.close()
    pool.join()
    return envelope

def buildings_xml(df_chunk, envelope, occupancy_df):
    text = ''
    for r in df_chunk.index:
        if df_chunk.index[-1] == len(df_chunk)-1:
            print('printing progress: ' + str(100*r/df_chunk.index[-1]) + '%')
        egid = df_chunk["egid"].loc[r]
        ssid = df_chunk["ssid"].loc[r]
        occupancy_type = df_chunk["occupancytype"].loc[r]
        #height = df_chunk["height"].loc[r]
        gross_volume = df_chunk["calc_vol"].loc[r]
        n_people = df_chunk["n_people"].loc[r]
        #n_floors = int(df_chunk["n_floors"].loc[r])
        #ventilation_coeff = occupancy_df["ventilation_coeff"].loc[occupancy_type-1]
        nat_ventilation_coeff = occupancy_df["nat_ventilation_coeff"].loc[occupancy_type-1] #valeur par défaut
        #ventilation_rate = occupancy_df["ventilation_rate"].loc[occupancy_type-1]*ventilation_coeff*(n_floors/height)
        infiltration_rate = 1.01*nat_ventilation_coeff 
        #ventilation = max(ventilation_rate, infiltration_rate)
        ventilation = infiltration_rate
        surfaces_df = envelope.loc[envelope['egid'] == egid]
        if occupancy_type == 1:
            dhwtype = 1
        else:
            dhwtype = 2

        #if egid > 250325:
        text = text + '<Building id="' + str(ssid) + '" key="' + str(egid) + '" Vi="' + str(gross_volume) + '" Ninf="' + str(ventilation) + '" Tmin="21.0" Tmax="26.0" BlindsLambda="0.0170000009" BlindsIrradianceCutOff="300.0" Simulate="true">\n'
        #else:
         #   text = text + '<Building id="' + str(ssid) + '" key="' + '" Vi="' + str(gross_volume) + '" Ninf="' + str(ventilation) + '" Tmin="21.0" Tmax="26.0" BlindsLambda="0.0170000009" BlindsIrradianceCutOff="300.0" Simulate="false">\n'

        text = text + '<HeatTank V="50.0" phi="200.0" rho="1000.0" Cp="4180.0" Tmin="20.0" Tmax="35.0" Tcritical="90.0"/>\n'
        text = text + '<DHWTank V="0.2" phi="2.5" rho="1000.0" Cp="4180.0" Tmin="50.0" Tmax="70.0" Tcritical="90.0" Tinlet="5.0"/>\n'
        text = text + '<CoolTank V="20.0" phi="20.0" rho="1000.0" Cp="4180.0" Tmin="5.0" Tmax="20.0"/>\n'
        text = text + '<HeatSource beginDay="288" endDay="135">\n'
        text = text + '<Boiler name = "boiler1" Pmax="500000" eta_th="0.96"/>\n'
        text = text + '</HeatSource>\n'
        text = text + '<Zone id="' + str(r) + '" volume="' + str(gross_volume*0.8) + '" Psi="0.2" groundFloor="true">\n'
        text = text + '<Occupants n="'+ str(n_people) + '" type ="' + str(occupancy_type) + '" Stochastic="true" ActivityType="1" DHWType="' + str(dhwtype) + '"/>\n'
        for r1 in surfaces_df.index:
            surface = surfaces_df["geometry"].loc[r1]
            class_id = surfaces_df["class_id"].loc[r1]
            #glazing_ratio = surfaces_df["glazing_ratio"].loc[r1]
            composite_id = surfaces_df["composite_id"].loc[r1]
            if class_id == 34:
                text = text + '<Wall id="' + str(r1) + '" type="'+ str(int(composite_id)) +'" ShortWaveReflectance="0.2" GlazingRatio="0.174" GlazingGValue="0.47" GlazingUValue="3.3" OpenableRatio="0.5">\n'
                v = 0
                for n in range(len(surface.exterior.coords)-1):
                    text = text + '<V' + str(v) +' x="' + str(surface.exterior.coords[n][0]) + '" y="' + str(surface.exterior.coords[n][1]) + '" z="' + str(surface.exterior.coords[n][2]) + '"/>\n'
                    v = v + 1
                text = text + '</Wall>\n'
            elif class_id == 35:
                text = text + '<Floor id="' + str(r1) + '" type="'+ str(int(composite_id)) +'">\n'
                v = 0
                for n in range(len(surface.exterior.coords)-1):
                    text = text + '<V' + str(v) +' x="' + str(surface.exterior.coords[n][0]) + '" y="' + str(surface.exterior.coords[n][1]) + '" z="' + str(surface.exterior.coords[n][2]) + '"/>\n'
                    v = v + 1
                text = text + "</Floor>\n"
            elif class_id == 33:
                text = text + '<Roof id="' + str(r1) + '" type="'+ str(int(composite_id)) +'" ShortWaveReflectance="0.2" GlazingRatio="0.0" GlazingGValue="0.7" GlazingUValue="1.4" OpenableRatio="0.0">\n'
                v = 0
                for n in range(len(surface.exterior.coords)-1):
                    text = text + '<V' + str(v) +' x="' + str(surface.exterior.coords[n][0]) + '" y="' + str(surface.exterior.coords[n][1]) + '" z="' + str(surface.exterior.coords[n][2]) + '"/>\n'
                    v = v + 1
                text = text + '</Roof>\n'
        text = text + '</Zone>\n'
        text = text + '</Building>\n'
    return text
       
    
def bx_run(buildings_df, envelope, occupancy_df):
    df_length = len(buildings_df)
    # Create as many processes as there are CPUs on the machine
    num_processes = min(multiprocessing.cpu_count()-1, df_length)
    # Calculate the chunk size as an integer
    chunk_size = int(np.ceil(df_length/num_processes))
    # Divide the df in chunks
    chunks = [buildings_df.loc[buildings_df.index[i:i + chunk_size]] for i in range(0, df_length, chunk_size)] #problem is on  chunk size!!! 
    # Create a pool of processes
    pool = multiprocessing.Pool(processes=num_processes)   
    # Apply the function to the chunks and combine the results in a single variable
    text = ''
    for result in pool.starmap(buildings_xml, [(i, envelope, occupancy_df) for i in chunks]):
        text = text + result    
    pool.close()
    pool.join()
    return text