# -*- coding: utf-8 -*-
import json
import requests
import pandas as pd
import numpy as np
import time

def get_data():
    # Request a list of datasets that have the id csa-asc
    response = requests.get('https://open.canada.ca/data/en/api/3/action/organization_show?id=csa-asc&include_datasets=True') #to change when public
    response.encoding = "utf-8"
    gov_canada_api_datasets = json.loads(response.text)

    assert (gov_canada_api_datasets['success'] == True)

    dataset_ids = []

    for dataset in gov_canada_api_datasets['result']['packages']:
        dataset_ids.append(dataset['id'])

    datasets = []

    print "This will take a few minutes...."

    # Request datasets by their id to get their full metadata
    l=len(dataset_ids)

    i=0
    for dataset_id in dataset_ids:
        if True :
            i+=1
            try :

                response = requests.get('https://open.canada.ca/data/en/api/3/action/package_show?id=' + dataset_id)
                response.encoding = "utf-8"
                gov_canada_api_dataset = json.loads(response.text)
                assert (gov_canada_api_dataset['success'] == True)
                datasets.append(gov_canada_api_dataset)
                print i,'/',l
                time.sleep(1)

            except :
                print('An error occured and this dataset will be skipped!')
                l-=1
                time.sleep(1)

    # Save data that was requested into .json
    # Could be a problem if there is too much data to hold in memory if this script is used on another instance of CKAN
    with open('gov_canada_datasets_raw.json', 'w') as f:
        json.dump(datasets, f)

    print "Success!!"
