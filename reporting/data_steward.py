# This class describes a data steward.
# Open Data Portal
#
# @author Emiline Filion - Canadian Space Agency
#

import pandas as pd


# Constants
EMAIL_DOMAIN = '@asc-csa.gc.ca'


class data_steward:
    
    def __init__(self, name, manager):
        
        self.name = name
        self.email = name.replace(' ', '.') + EMAIL_DOMAIN
        self.manager = manager
        self.email_supervisor = manager.replace(' ', '.') + EMAIL_DOMAIN
        self.has_left_csa = self.set_has_left_csa()
        self.nb_datasets = 0
        self.datasets = []
        
    def __eq__(self, name):
        return self.name == name
    
    def __repr__(self):
        return '%s' % (self.name)
    
    def add_dataset(self, title):
        self.datasets.append(title)
    
    def get_nb_datasets(self):
        return len(self.datasets)
    
    def set_has_left_csa(self):
        
        if self.name == 'Robert Saint-Jean':
            return 'gone'
        if self.name == 'Nathalie Levesque':
            return 'gone'
        if self.name == 'Denis Laurin':
            return 'gone'
        if self.name == 'Anne Marie LaBreque':
            return 'gone'
        if self.name == 'Renee St-Amant':
            return 'gone'
        if self.name == 'Yves Proulx':
            return 'gone'
        return ''

    def as_dict(self):
        return {'Data Steward': self.name, 
                'Email': self.email, 
                'Has Left CSA': self.has_left_csa,
                'Manager': self.manager,
                'Email Manager': self.self_email_supervisor,
                'Number of datasets': self.nb_datasets,
                'List of Datasets': self.datasets}


'''
Validates the data steward
'''
def validate_data_steward(value, manager, dataset_title, data_stewards):
    try:
        idx = value.find(',')
        if idx > 0:
            value = idx[idx:len(value)] + '.' + value[0:idx]
        if len(value) > 0:
            if value not in data_stewards:
                new_data_steward = data_steward(value, manager)
                new_data_steward.add_dataset(dataset_title)
                data_stewards.append(new_data_steward)
                new_data_steward.nb_datasets += 1
            else:
                for the_data_steward in data_stewards:
                    if the_data_steward.name == value:
                        the_data_steward.nb_datasets += 1
                        the_data_steward.add_dataset(dataset_title)
    except :
        # Nothing to do
        return
        
        
'''
Returns the list of data stewards.
df - dataframe
'''
def get_data_stewards(df):
    
    data_stewards = []
    for ind in df.index:
        validate_data_steward(df['data_steward'][ind], 
                              df['manager_or_supervisor'][ind], 
                              df['title'][ind], 
                              data_stewards)
    return data_stewards


'''
Converts the array of data stewards to the Excel format
data_stewards - Array of <data_steward> objects
'''
def get_data_frame_excel_format(data_stewards):
    
    excel_df = pd.DataFrame([t.__dict__ for t in data_stewards])
    excel_df.rename(columns={'name': 'Data Steward', 
                             'email': 'Email',
                             'has_left_csa': 'Has Left CSA',
                             'manager': 'Manager or Supervisor',
                             'email_supervisor': 'Supervisor Email',
                             'nb_datasets': 'Number of datasets',
                             'datasets': 'List of Datasets'}, inplace=True)
    return excel_df
