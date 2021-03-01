# -*- coding: utf-8 -*-
import json
import requests
import pandas as pd
import numpy as np
import time


def get_data():
    # Demander une liste des ensembles de données qui ont le id csa-asc
    # Request a list of datasets that have the id csa-asc
    response = requests.get('https://open.canada.ca/data/en/api/3/action/organization_show?id=csa-asc&include_datasets=True')
    response.encoding = "utf-8"
    gov_canada_api_datasets = json.loads(response.text)

    assert (gov_canada_api_datasets['success'] == True)

    dataset_ids = []

    for dataset in gov_canada_api_datasets['result']['packages']:
        dataset_ids.append(dataset['id'])

    datasets = []

    print("Cela prendra quelques minutes.... | This will take a few minutes....")

    # Demander les ensembles de données par leur identifiant pour obtenir leurs métadonnées complètes
    # Request datasets by their id to get their full metadata
    l=len(dataset_ids)

    i=0
    for dataset_id in dataset_ids:
        if True :
            i+=1
            try :

                response = requests.get("https://open.canada.ca/data/en/api/3/action/package_show?id=" + dataset_id)
                response.encoding = "utf-8"
                gov_canada_api_dataset = json.loads(response.text)
                assert (gov_canada_api_dataset['success'] == True)
                datasets.append(gov_canada_api_dataset)
                print(i,'/',l)
                time.sleep(1)

            except :
                print("Une erreur s'est produite et cet ensemble de données sera ignoré ! | An error occurred and this dataset will be skipped!")
                l-=1
                time.sleep(1)

    # Sauvegarder les données demandées dans un fichier .json
    # Save the data that was requested into a .json file
    with open('gov_canada_datasets_raw.json', 'w') as f:
        json.dump(datasets, f)

    print("Succès ! | Success!")
