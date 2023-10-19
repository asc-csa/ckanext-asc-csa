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
    datasets= json.loads(response.text)
    
    # Create a pandas dataframe object for easy analysis.
    df = pd.DataFrame(datasets['result']['results'])
    return df
