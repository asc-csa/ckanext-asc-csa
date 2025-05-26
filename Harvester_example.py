# -*- coding: utf-8 -*-
import json
import requests
import pandas as pd

"""
Tips/Astuces

Dans la terminologie CKAN, un package/dataset est une liste comme celle-ci : https://donnees-data.asc-csa.gc.ca/dataset/02969436-8c0b-4e6e-ad40-781cdb43cf24. Chaque élément que vous pouvez télécharger ou auquel vous pouvez accéder sur une page d'ensemble de données est une ressource.
In CKAN terminology, a package/dataset is a listing like this: https://donnees-data.asc-csa.gc.ca/dataset/02969436-8c0b-4e6e-ad40-781cdb43cf24. Every item that you can download or access on a dataset page is a resource.

Obtenez des listes formatées en JSON de tous les ensembles de données.
Get JSON-formatted lists of all datasets
    https://donnees-data.asc-csa.gc.ca/api/3/action/package_list

Obtenez une représentation JSON complète d'un ensemble de données ou d'une ressource.
Get a full JSON representation of a dataset or resource.
    https://donnees-data.asc-csa.gc.ca/api/3/action/package_show?id=02969436-8c0b-4e6e-ad40-781cdb43cf24

Recherche de jeux de données ou de ressources correspondant à une requête.
Search for dataset or resources matching a query.
    https://donnees-data.asc-csa.gc.ca/api/3/action/package_search?q=astronomy

Get an activity stream of recently changed datasets on the site.
Obtenez un profil d'activité des ensembles de données récemment modifiés sur le site.
    https://donnees-data.asc-csa.gc.ca/api/3/action/recently_changed_packages_activity_list
"""


"""
Exemple/Example: get_data
Obtenir toutes les métadonnées pour les ensembles de données où project = project_cat. Les options disponibles sont les suivantes :
Get all metadata for datasets where project = project_cat. Options include:

    Valeur/Value
    'atmospheric_sci'   : Science atmosphérique/Atmospheric science
    'earth_observation' : Observation terrestre/Earth observation
    'life_sciences'     : Science de la vie/Life sciences
    'space_astronomy'   : Astronomie spatiale/Space astronomy
    'space_environment' : Environnement spatiale/météo spatiale/ Space environment/Space weather
    'space_exploration' : Exploration spatiale/Space exploration
    'telemetry'         : Télémétrie/Telemetry

Pour plus d'informations sur les métadonnées utilisées dans ce portail, voir:
For more information about the metadata used in this portal, see:
    https://github.com/asc-csa/ckanext-asc-csa-scheming/blob/master/ckanext/scheming/ckan_dataset.json
    https://github.com/asc-csa/ckanext-asc-csa-scheming/blob/python3/ckanext/scheming/presets.json.
"""


def get_data(project_cat):
    # Demander une liste des ensembles de données dans la catégorie de votre choix.
    # Request a list of datasets in the category of your choice.
    response = requests.get(
        "https://donnees-data.asc-csa.gc.ca/api/action/package_search?fq=project:"
        + project_cat
    )
    response.encoding = "utf-8"
    datasets = json.loads(response.text)

    # Créez un objet dataframe de pandas pour faciliter l'analyse.
    # Create a pandas dataframe object for easy analysis.
    df = pd.DataFrame(datasets["result"]["results"])

    # Sauvegarder les données demandées dans un fichier .json
    # Save the data that was requested into a .json file
    with open("%s_datasets_raw.json" % project_cat, "w") as f:
        json.dump(datasets, f)

    print("Succès ! | Success!")
    return df


# Appliquer la fonction/Apply the function
space_df = get_data("space_astronomy")
print(space_df)

# Obtenir tous les noms de colonnes/Get all of the column names
for col in space_df.columns:
    print(col)

# Visualisez les valeurs d'une colonne qui vous intéresse.
# View the values for a column you're interested in.
print(space_df["title"])

# Visualisez les valeurs d'une colonne qui vous intéresse si elle contient un objet dictionnaire avec des valeurs anglais-français.# View the values for a column you're interested in.
# View the values for a column you're interested in if it contains a dictionnary object with values in english and french.

print(space_df["title_translated"].apply(pd.Series))
