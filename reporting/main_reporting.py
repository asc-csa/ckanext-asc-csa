# This script uses the API to retrieve the statistics of the Open Data Portal.
#
# @author Emiline Filion - Canadian Space Agency
#

import datetime
from datetime import datetime
import data_steward
import portal_helper
import pandas as pd


# Read all datasets from the Open Data Portal
space_df = portal_helper.get_data('https://donnees-data.asc-csa.gc.ca')
print('Number of datasets in the Open Data Portal: ' + str(len(space_df.index)))

# View the values for a column you're interested in.
data_stewards = data_steward.get_data_stewards(space_df)
print('Number of data stewards: ' + str(len(data_stewards)) + '\n')

# Save the array of data stewards to Excel
excel_df = data_steward.get_data_frame_excel_format(data_stewards)
month = str(datetime.now().month)
year = str(datetime.now().year)
excel_filename = "Open Data Portal - list of Data Stewards-" + year + "-" + month + ".xlsx"
print ('Saving the list of data stewards to disk: ' + excel_filename)
excel_df.to_excel(excel_filename, index=False)  
space_df.to_excel("Open Data Portal - List of Datasets-" + year + "-" + month + ".xlsx", index=False)  

# TODO: To send emails
# https://realpython.com/python-send-email/
# https://docs.python.org/3/library/email.examples.html
# https://stackoverflow.com/questions/6270782/how-to-send-an-email-with-python
# https://mailtrap.io/blog/python-send-email/

# End of script
print("\nThe script ended successfully")
print("Have a nice day!")