# This script update the data steward of the Open Data Portal.
# Open Data Portal
#
# @author Emiline Filion - Canadian Space Agency
#

import ckanapi
import pandas as pd

# Constants
CKAN_URL = 'https://donnees-data.asc-csa.gc.ca/'
API_KEY = 'a**********************************7'


# Connect to the Open Data Portal
print('\nConnecting to the Open Data Portal...')
ckan = ckanapi.RemoteCKAN(CKAN_URL, apikey=API_KEY)
print('Connected')

# Open the Excel file that contains the list of all datasets & data stewards
print('\nOpening the Excel file that contains the list of all datasets & data stewards...')
all_data = pd.read_excel('U:\\Projects\\Space Data\\Open Data Portal\\reporting\\Open Data Portal - List of Data Stewards.xlsx')
print('Found ' + str(len(all_data.index)) + ' datasets\n')
# http://livelink/livelink/llisapi.dll?func=ll&objId=210183504&objAction=viewheader


if 'test' not in CKAN_URL:
    print ('\nWARNING: You are connected to the production Open Data Portal.\nDo you want to continue?')
    response = input("Yes (Y), No (N) ")
    response = response.lower()
    if response == 'n' or response == 'no':
        exit()
    
# Loop for each dataset
print('\nUpdating the Open Data Portal (data steward)...')
nbUpdatedDatasets = 0
for row in all_data.index:
    
    # Get the dataset from the Open Data Portal
    try:
        dataset_id = all_data['id'][row]
        dataset = ckan.action.package_show(id=dataset_id)
    except :
        # Not found (invalid ID) --> Skip it
        print('\n' + all_data['title'][row] + ' was skipped because the ID was not found in the data portal. ID=' + dataset_id)
        continue

    # Get the title of the dataset to update
    dataset_name = dataset['title']
    data_steward = dataset['data_steward']
    data_manager = dataset['manager_or_supervisor']
    new_data_steward = all_data['data_steward'][row]
    new_manager = all_data['manager_or_supervisor'][row]
    
    if data_steward != new_data_steward or data_manager != new_manager:
    
        print('\n---- ' + dataset_name + ' ----')
        print('The current data steward is ' + data_steward + '. It should be ' + new_data_steward + '.')
        print('The current data manager is ' + data_manager + '. It should be ' + new_manager + '.')
        
        # Update the package's title and tags
        dataset['data_steward'] = new_data_steward
        dataset['manager_or_supervisor'] = new_manager
        
        
        # Update the package on CKAN
        nbUpdatedDatasets = nbUpdatedDatasets + 1
        ckan.action.package_update(**dataset)

print('\nA total of ' + str(nbUpdatedDatasets) + ' datasets out of ' + str(len(all_data.index)) + ' were updated.')
print('The other ones were already good.')
print("\nHave a nice day!")
