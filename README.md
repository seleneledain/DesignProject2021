# Design Project 2021

by Maxwell Bergström, Sélène Ledain 

date: June 2021


## Project Description

This repository contains the scripts used for the Design Project 2021 "Machine Learning pour l’énergétique des bâtiments sur outil SIG" in collaboration between EPFL and Idiap.

Please refer to the Report for reference.

---

## Required settings
The following scripts are .ipynb (Jupyter Notebooks) files and must be opened with an appropriate program in order to be read and executed.

For 'main_create_xml.ipynb' there is need of CitySim Pro which is distributed by Kaemco. Please visit http://www.kaemco.ch/download.php for further information.


---
## File list
* scrapper.ipynb
* main_create_xml.ipynb
* SATOM_data.ipynb
* SATOM_linear_annual.ipynb
* SATOM_linear_timeseries.ipynb
* SATOM_randomforest_annual.ipynb
* SATOM_randomforest_timeseries.ipynb
* SATOM_randomforest_annual_tuned.ipynb
* SATOM_randomforest_timeseries_tuned.ipynb
* geometry_processor_db_2021.py
* AllData_TH.tsv
* Aigle_MeteoSchweiz_2019.cli
* Aigle_MeteoSchweiz_2019_v2.cli
* Martigny.cli
* Martigny_to_3D.cli

* Report 
    
(Additional informative files)
* Meteo_data.ipynb
* Time_data.ipynb

---

## File descriptions

### scrapper.ipynb
For a list of EGIDs, will scrap from RegBL (https://map.geo.admin.ch) the period of construction (GBAUP).
Based on a series of hypothesis, standard types of composites for the walls, roofs, floors and ground are created depending on the period of construction. 
Based off the GBAUP, each building is attributed certain composites. 

The script then connects to a PostgreSQL database containing a CityDB structure and its EnergyADE. 

For more about CityDB, refer to:
    https://www.3dcitydb.org/3dcitydb/
    https://github.com/gioagu/3dcitydb_metadata_module
    https://github.com/gioagu/3dcitydb_energy_ade
as well as the report in documentation for details on installation and setup.
    

Informations on the composites are stored in panda dataframes nrg8_construction, nrg8_layer, nrg8_layer_component and nrg8_material. The links between the buildings and the composites are stored in nrg8_cityobj_to_constr. 
These tables are then directly stored in the PostgreSQL database.


### main_create_xml.ipynb
Creates the XML file for launching simulations on CitySim. This file calls auxiliary functions from the 'geometry_processor_db_2021.py' file which must be called from the same folder. The XML also requires a climate file to add climatic conditions to the simumation. This file is 'Martigny.cli'.

The script downloads geometries in the PostgreSQL (Design Project 2020 database) and creates an enevelope for each of the geometries. The composites of the buildings are listed (from Design Project 2021 database). Only buildings containing at least a floor, roof and wall are kept. Each building with its geometry as well as physical properties, occupancy type (default values), activity type (default values), are written in the XML.

The script also calls CitySim in an executable version is found in the same folder. In practice, the simulation was done on another computer and therefore the last part of the script simply reads results from a tsv file (AllData_TH.tsv).
The results are read by the script and generated into an appropriate table before being inserted into the PostgreSQL database (under citydb.nrg8_time_series).

The timeesereies for each building is stored, as well as annual energy demands.


### SATOM_data.ipynb
Collects mesurements from the SATOM network which are stored in the satom schema in the Design Project 2021 PostgreSQL database.
Measurements are grouped by building, and buildings are linked to thee Energy ADE strucuturee with the gmlid.
The timeseries for the buildings is calculated by computing the difference in cumulative energy between 2 consecutive measurements. The total annual demand is also computed for each building.
Both the timeseries and the annual data are in the citydb.nrg8_time_series table in the Design Project 2021 PostgreSQL database.  


### SATOM_linear_annual.ipynb
Contains the linear regression model trained on the SATOM annual data to predict annual energy demands. Uses the climatic file 'Aigle_MetoSchwiez_2019_v2.cli'.

### SATOM_linear_timeseries.ipynb
Contains the linear regression model trained on the SATOM timeseries data to predict energy demands at different times. Uses the climatic file 'Aigle_MetoSchwiez_2019_v2.cli'.

### SATOM_randfomforest_annual.ipynb
Contains Random Forest model to predict annual energy demand on SATOM annual data. Uses the climatic file 'Aigle_MetoSchwiez_2019_v2.cli'.

### SATOM_randomforest_timeseries_tuned.ipynb
Contains Random Forest model with hyperparameter tuning to predict energy demand at different timesteps on SATOM data. Uses the climatic file 'Aigle_MetoSchwiez_2019_v2.cli'.

### SATOM_randfomforest_annual_tuned.ipynb
Contains Random Forest model with hyperparameter tuning to predict annual energy demand on SATOM annual data. Uses the climatic file 'Aigle_MetoSchwiez_2019_v2.cli'.

### SATOM_randomforest_timeseries.ipynb
Contains Random Forest model to predict energy demand at different timesteps on SATOM data. Uses the climatic file 'Aigle_MetoSchwiez_2019_v2.cli'.

###  geometry_processor_db_2021.py
Auxiliary functions for the 'main_create_xml.ipynb'. In particular, allows to calculate geometric features and write the xml.

###  AllData_TH.tsv
TSV table containing results of CitySim simulation using the XML and climate file 'Martigny.cli'

###  Aigle_MeteoSchweiz_2019.cli
Climate file for Aigle in 2019.

###  Aigle_MeteoSchweiz_2019.cli
Same file as 'Aigle_MetoSchwiez_2019.cli' but formatted to be read properly by the scripts.

###  Martigny.cli
Climate file for Martigny in 2019.

###  Martigny_to_3D.xml
XML file generated by 'main_create_xml.ipynb' and used by CitySim.  

###  Meteo_data.ipynb
This script is not intended to be run. Instead it shows how meteorological data were prepared for the machine learning models.

### Time_data.ipynb
This script is not intended to be run. Instead it shows how timeseries data were prepared for the machine learning models.
