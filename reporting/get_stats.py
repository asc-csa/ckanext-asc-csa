# This script uses the API to retrieve the statistics of the Open Data Portal.
#
# @author Emiline Filion - Canadian Space Agency
#

import datetime
from datetime import datetime
import portal_helper
import pandas as pd


# Read all datasets from the Open Data Portal
space_df = portal_helper.get_data('https://donnees-data.asc-csa.gc.ca')
nb_datasets = len(space_df.index)
print('Number of datasets in the Open Data Portal: ' + str(nb_datasets))

# Save the array of data stewards to Excel
month = str(datetime.now().month)
year = str(datetime.now().year)
excel_filename = "Open Data Portal - List of Data Stewards-" + year + "-" + month + ".xlsx"
print ('Saving the list of data stewards to disk: ' + excel_filename)
space_df = space_df.sort_values('metadata_created')
space_df.to_excel("Open Data Portal - List of Datasets-" + year + "-" + month + ".xlsx", index=False)

# Compute stats
nb_info2021 = 0
nb_info2022 = 0
nb_info2023 = 0
nb_info2024 = 0
nb_data2021 = 0
nb_data2022 = 0
nb_data2023 = 0
nb_data2024 = 0
for dataset in space_df.index:
    if '2021' in space_df['metadata_created'][dataset] and space_df['portal_type'][dataset] == 'info':
        nb_info2021 += 1
    if '2022' in space_df['metadata_created'][dataset] and space_df['portal_type'][dataset] == 'info':
        nb_info2022 += 1
    if '2023' in space_df['metadata_created'][dataset] and space_df['portal_type'][dataset] == 'info':
        nb_info2023 += 1
    if '2024' in space_df['metadata_created'][dataset] and space_df['portal_type'][dataset] == 'info':
        nb_info2024 += 1
    if '2021' in space_df['metadata_created'][dataset] and space_df['portal_type'][dataset] == 'data':
        nb_data2021 += 1
    if '2022' in space_df['metadata_created'][dataset] and space_df['portal_type'][dataset] == 'data':
        nb_data2022 += 1
    if '2023' in space_df['metadata_created'][dataset] and space_df['portal_type'][dataset] == 'data':
        nb_data2023 += 1
    if '2024' in space_df['metadata_created'][dataset] and space_df['portal_type'][dataset] == 'data':
        nb_data2024 += 1

# Displat the result
print("\n")
print('**** 2021 ****')
print('info: ' + str(nb_info2021))
print('data: ' + str(nb_data2021))
print("\n")
print('**** 2022 ****')
print('info: ' + str(nb_info2022))
print('data: ' + str(nb_data2022))
print("\n")
print('**** 2023 ****')
print('info: ' + str(nb_info2023))
print('data: ' + str(nb_data2023))
print("\n")
print('**** 2024 ****')
print('info: ' + str(nb_info2024))
print('data: ' + str(nb_data2024))

# End of script
print("\nThe script ended successfully")
print("Have a nice day!\n")