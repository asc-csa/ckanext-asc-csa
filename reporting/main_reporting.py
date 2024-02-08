# This script uses the API to retrieve the data stewards from the Open Data Portal.
#
# @author Emiline Filion - Canadian Space Agency
#

import datetime
from datetime import datetime
import data_steward
import email_message
import portal_helper
import pandas as pd


# Read all datasets from the Open Data Portal
space_df = portal_helper.get_data('https://donnees-data.asc-csa.gc.ca')
nb_datasets = len(space_df.index)
print('Number of datasets in the Open Data Portal: ' + str(nb_datasets))
nb_unassigned_datasets = portal_helper.get_nb_unassigned_datasets(space_df)
percent_assigned = nb_unassigned_datasets * 100 / nb_datasets
print('Number of datasets that do not have a data steward assigned: ' + str(nb_unassigned_datasets) + ' --> ' + str(percent_assigned) + '%')

# View the values for a column you're interested in.
data_stewards = data_steward.get_data_stewards(space_df)
print('Number of distinct data stewards: ' + str(len(data_stewards)) + '\n')

# Save the array of data stewards to Excel
excel_df = data_steward.get_data_frame_excel_format(data_stewards)
month = str(datetime.now().month)
year = str(datetime.now().year)
excel_filename = "Open Data Portal - List of Data Stewards-" + year + "-" + month + ".xlsx"
print ('Saving the list of data stewards to disk: ' + excel_filename)
excel_df.to_excel(excel_filename, index=False)  
space_df.to_excel("Open Data Portal - List of Datasets-" + year + "-" + month + ".xlsx", index=False)  

# Send email to data stewards
print ('\nDo you want to send email to data stewards?')
send_email_response = input("Yes (Y), No (N) ")
send_email_response = send_email_response.lower()
if send_email_response == 'y' or send_email_response == 'yes':
    
    print ('\nWARNING: The script is going to send email to all data stewards.')
    print ('Are you sure you want to continue?')
    send_email_response = input("Yes (Y), No (N) ")
    send_email_response = send_email_response.lower()
    if send_email_response == 'y' or send_email_response == 'yes':
        print('\nSending emails...')
        for ind in excel_df.index:
            msg = email_message.email_message(excel_df['Email'][ind], excel_df['Supervisor Email'][ind], "[Portail des données ouvertes / Open Data Portal] Demande de révision / Review request")
            msg.send_email(msg.generate_body(excel_df['Data Steward'][ind], excel_df['Number of Datasets'][ind], excel_df['List of Datasets'][ind], excel_df['List of Dataset IDs'][ind]))
    
# End of script
print("\nThe script ended successfully")
print("Have a nice day!")