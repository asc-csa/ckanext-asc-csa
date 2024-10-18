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


# Gets all metadata for all datasets.
# @param portal_url - CSA Open Data Portal URL.
# @return dataframe of all data.
def get_data(portal_url):
    
    # Request a list of datasets for all categories
    # Online reference: https://docs.ckan.org/en/2.9/api/index.html
    print('\nConnecting to the Open Data Portal to retrieve data...\n')
    response = requests.get(portal_url + '/api/action/package_search?fq=&rows=400')
    response.encoding = ENCODING
    datasets = json.loads(response.text)
    
    # Create a pandas dataframe object for easy analysis.
    df = pd.DataFrame(datasets['result']['results'])
    return df


# Gets the information of a specific datatset.
# @param portal_url - CSA Open Data Portal URL.
# @param dataset_id = ID of the dataset.
# @return Information of the datatset.
def get_dataset_info(portal_url, dataset_id):
    
    # Request a list of datasets for all categories
    # Online reference: https://docs.ckan.org/en/2.9/api/index.html
    #print('\nConnecting to the Open Data Portal to retrieve the information of a specific dataset...\n')
    response = requests.get(portal_url + '/api/action/package_show?id='+dataset_id+'&include_tracking=true')
    response.encoding = ENCODING
    dataset = json.loads(response.text)
    return dataset['result']


# Returns the number of unassigned datasets.
# @return The number of unassigned datasets.
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


# Formats a string to a readable value.
# @param content - Input string content.
# @return Formated string.
def format_to_readable(content) :
    
    content = content.replace('_', ' ')
    content = content.replace("[", "")
    content = content.replace("]", "")
    content = content.replace("'", "")
    content = content.replace("nan", "")
    content = content.replace("NAN", "")
    return content