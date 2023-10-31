# This file contains generic functions for the Open Data Portal.
#
# @author Emiline Filion - Canadian Space Agency
#

# -*- coding: utf-8 -*-
import json
import requests
import pandas as pd

# Constants
ENCODING = "utf-8"


'''
get_data
Gets all metadata for all datasets
'''
def get_data(portal_url):
    
    # Request a list of datasets for all categories
    print('\nConnecting to the Open Data Portal to retrieve data...\n')
    response = requests.get(portal_url + '/api/action/package_search?fq=&rows=400')
    response.encoding = ENCODING
    datasets = json.loads(response.text)
    
    # Create a pandas dataframe object for easy analysis.
    df = pd.DataFrame(datasets['result']['results'])
    return df


'''
get_nb_unassigned_datasets
Returns the number of unassigned datasets
'''
def get_nb_unassigned_datasets(df):
    
    nb_unassigned_datasets = 0
    for ind in df.index:
        
        try:
            supervisor = df['manager_or_supervisor'][ind]
            if len(supervisor) > 0:
                # Nothing to do
                continue
            else:
                nb_unassigned_datasets += 1
        except :
            nb_unassigned_datasets += 1
    
    return nb_unassigned_datasets