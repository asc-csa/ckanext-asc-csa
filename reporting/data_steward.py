# This class describes a data steward.
# Open Data Portal
#
# @author Emiline Filion - Canadian Space Agency
#

import pandas as pd


# Constants
EMAIL_DOMAIN = '@asc-csa.gc.ca'


class data_steward:

    # Constructor.
    # @param name - Name of the data steward.
    # @param manager - Name of the manager.
    def __init__(self, name, manager):
        
        self.name = name
        self.email = name.replace(' ', '.').replace('é', 'e').replace('è', 'e').lower() + EMAIL_DOMAIN
        self.has_left_csa = self.set_has_left_csa()
        self.manager = manager
        self.email_supervisor = manager.replace(' ', '.').replace('é', 'e').replace('è', 'e').lower() + EMAIL_DOMAIN
        self.nb_datasets = 0
        self.dataset_titles = []
        self.dataset_ids = []
    
    # Equal method.
    # @param name - Name of the data steward.
    # @return True if the data steward is the same. False otherwise.
    def __eq__(self, name):
        return self.name == name
    
    # Returns the self representation.
    # @return Name of the data steward.
    def __repr__(self):
        return '%s' % (self.name)
    
    # Assigns a dataset to the data steward.
    # @param title - Title of the dataset.
    # @param idf - Dataframe.
    def add_dataset(self, title, idf):
        self.dataset_titles.append(title)
        self.dataset_ids.append(idf)
    
    # Returns the number of datasets that the data steward is responsible of.
    # @return Number of datasets.
    def get_nb_datasets(self):
        return len(self.dataset_titles)
    
    # Indicates if the data steward has left the CSA.
    # @return True if the data steward has left the CSA. False otherwise.
    def set_has_left_csa(self):
        
        if self.name == 'Robert Saint-Jean' or self.name == 'Nathalie Levesque' or self.name == 'Denis Laurin' or self.name == 'Anne Marie LaBreque' or self.name == 'Renee St-Amant' or self.name == 'Yves Proulx':
            return 'Has left CSA'
        elif self.name == 'Nancy Vezina' or self.name == 'Karl Saad' or self.name == 'David Haight' or self.name == 'Victoria Hipkin' or self.name == 'Jonathan Lajoie':
            return 'Works on another project'
        else :
            return ''

    # Converts the data steward to a data dictionary.
    # @return Data dictionary.
    def as_dict(self):
        return {'Data Steward': self.name, 
                'Email': self.email, 
                'Has Left CSA': self.has_left_csa,
                'Manager': self.manager,
                'Email Manager': self.self_email_supervisor,
                'Number of datasets': self.nb_datasets,
                'List of Datasets': self.dataset_titles}


# Validates the data steward.
# @param value - Name of the data steward.
# @param manager - Name of the manager.
# @param idf - Dataframe.
# @param dataset_title - Title of the dataset.
# @param data_stewards - List of data stewards.
def validate_data_steward(value, manager, idf, dataset_title, data_stewards):
    try:
        idx = value.find(',')
        if idx > 0:
            value = idx[idx:len(value)] + '.' + value[0:idx]
        if len(value) > 0:
            if value not in data_stewards:
                new_data_steward = data_steward(value, manager)
                new_data_steward.add_dataset(dataset_title, idf)
                data_stewards.append(new_data_steward)
                new_data_steward.nb_datasets += 1
            else:
                for the_data_steward in data_stewards:
                    if the_data_steward.name == value:
                        the_data_steward.nb_datasets += 1
                        the_data_steward.add_dataset(dataset_title, idf)
    except :
        # Nothing to do
        return
        
        

# Returns the list of data stewards.
# @param df - dataframe.
# @return List of data stewards.
def get_data_stewards(df):
    
    data_stewards = []
    for ind in df.index:
        
        validate_data_steward(df['data_steward'][ind], 
                              df['manager_or_supervisor'][ind], 
                              df['name'][ind], 
                              df['title'][ind], 
                              data_stewards)
    return data_stewards



# Converts the array of data stewards to the Excel format
# @param data_stewards - Array of <data_steward> objects.
# @return Array of data stewards to the Excel format.
def get_data_frame_excel_format(data_stewards):
    
    excel_df = pd.DataFrame([t.__dict__ for t in data_stewards])
    excel_df.rename(columns={'name': 'Data Steward', 
                             'email': 'Email',
                             'has_left_csa': 'Departure Notes',
                             'manager': 'Manager or Supervisor',
                             'email_supervisor': 'Supervisor Email',
                             'nb_datasets': 'Number of Datasets',
                             'dataset_titles': 'List of Datasets',
                             'dataset_ids': 'List of Dataset IDs'}, inplace=True)
    return excel_df
