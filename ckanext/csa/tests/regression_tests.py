# Regression tests
#
# Regression tests verify that new code changes have not broken existing features or introduced new bugs. 
# If any tests fail, it indicates a potential regression that needs to be investigated and fixed. 
# Regression testing helps maintain the stability and reliability of software over time, especially in fast-paced development environments where frequent code changes are common. 
# 
# IMPORTANT:
# It is recommended to run the regression tests after bug fixes, new feature additions, or code updates to the CSA Open Data Portal.
# 
# Execution: Simply run this file. It contains everthing it needs.
#
# @author Emiline Filion - Canadian Space Agency
#

import json
import requests
import os
import pandas as pd
import unittest


# Constants
ENCODING = "utf-8"
MIN_NB_PUBLIC_DATASETS = 153
CSA_OPEN_DATA_PORTAL = 'https://donnees-data.asc-csa.gc.ca'
datasets_df = pd.DataFrame()


class csa_portal_regression_tests(unittest.TestCase):

    # Gets all metadata for all datasets.
    # @param portal_url - CSA Open Data Portal URL.
    # @return dataframe of all data.
    def __get_data(self, portal_url):
        
        # Request a list of datasets for all categories
        # Online reference: https://docs.ckan.org/en/2.9/api/index.html
        print('Connecting to the Open Data Portal to retrieve data... (takes around a minute)')
        response = requests.get(portal_url + '/api/action/package_search?fq=&rows=400')
        response.encoding = ENCODING
        datasets = json.loads(response.text)
        
        # Create a pandas dataframe object for easy analysis.
        df = pd.DataFrame(datasets['result']['results'])
        return df


    def test_nb_public_datasets(self):

        # Read all datasets from the Open Data Portal
        global datasets_df
        print("\nTEST_START: test_nb_public_datasets()")
        if len(datasets_df) == 0:
            datasets_df = self.__get_data(CSA_OPEN_DATA_PORTAL)
        print('Number of datasets found in the Open Data Portal: ' + str(len(datasets_df.index)))

        # Make the number of public datasets is correct
        self.assertTrue(len(datasets_df.index) >= MIN_NB_PUBLIC_DATASETS)


    def test_format_of_datasets(self):

        # Read all datasets from the Open Data Portal
        global datasets_df
        print("\nTEST_START: test_format_of_datasets()")
        if len(datasets_df) == 0:
            datasets_df = self.__get_data(CSA_OPEN_DATA_PORTAL)

        # Make sure the format is correct
        try:
            metadata_df = datasets_df[['title', 'title_translated', 'id', 'notes', 'notes_translated', 'portal_type', 'format_of_source_data', 'format_of_source_data_details', 'resources', 'data_owner', 'data_steward', 'manager_or_supervisor', 'metadata_created', 'metadata_modified', 'portal_release_date', 'date_published', 'audience', 'subject', 'directorate', 'division', 'imso_approval', 'jurisdiction', 'language_support', 'license_id', 'license_title']]
            metadata_df = metadata_df.sort_values('title', ascending=True)
            for row in metadata_df.index:
                self.assertTrue(len(str(metadata_df['id'][row])) > 7)
                self.assertTrue(len(str(metadata_df['title'][row])) > 4)
                self.assertTrue(len(str(metadata_df['title_translated'][row])) > 4)
                self.assertTrue(len(str(metadata_df['notes'][row])) > 10)
                self.assertTrue(len(str(metadata_df['notes_translated'][row])) > 10)
            print("The format of the datasets is correct.")
        except:
            self.fail("The format of the dataset has changed and is now incorrect.")


    def test_solr_schema(self):

        # Make sure the SOLR schema is at appropriate place
        self.assertTrue(os.path.exists("../conf/solr/schema.xml"))


    def test_license(self):

        # Make sure the license is there
        self.assertTrue(os.path.exists("../../../LICENSE"))
        self.assertTrue(os.path.exists("../public/GCWeb/Licence-fr.txt"))
        self.assertTrue(os.path.exists("../public/GCWeb/License-en.txt"))

        # Validate the content (English)
        en_licence_file = open("../public/GCWeb/License-en.txt")
        en_licence = str(en_licence_file.read())
        self.assertTrue("MIT License" in en_licence)
        self.assertTrue("Web Experience Toolkit (WET) - Terms and Conditions of Use" in en_licence)
        self.assertTrue("Government of Canada" in en_licence)
        self.assertTrue("Permission is hereby granted, free of charge, to any person obtaining a copy of this software" in en_licence)

        # Validate the content (French)
        fr_licence_file = open("../public/GCWeb/Licence-fr.txt")
        fr_licence = str(fr_licence_file.read())
        self.assertTrue("Licence MIT" in fr_licence)
        self.assertTrue("BOEW" in fr_licence)
        self.assertTrue("Gouvernement du Canada" in fr_licence)
        self.assertTrue("obtenir gratuitement une copie " in fr_licence)


    def test_translation_module(self):

        # Make sure the translation module is there
        self.assertTrue(os.path.exists("../i18n/ckanext-csa.pot"))
        self.assertTrue(os.path.exists("../i18n/fr/LC_MESSAGES/ckanext-csa.mo"))
        self.assertTrue(os.path.exists("../i18n/fr/LC_MESSAGES/ckanext-csa.po"))
        self.assertTrue(os.path.exists("../public/GCWeb/css/ie8-theme.css"))
        self.assertTrue(os.path.exists("../public/GCWeb/css/ie8-theme.min.css"))
        self.assertTrue(os.path.exists("../public/GCWeb/css/ie8-theme-srv.css"))
        self.assertTrue(os.path.exists("../public/GCWeb/css/ie8-theme-srv.min.css"))
        self.assertTrue(os.path.exists("../public/GCWeb/css/ie8-wet-boew.css"))
        self.assertTrue(os.path.exists("../public/GCWeb/css/ie8-wet-boew.min.css"))


    def test_fanstatic(self):

        # Make sure the fantastic stuffs are there
        self.assertTrue(os.path.exists("../fanstatic/csa_field_descriptions.css"))
        self.assertTrue(os.path.exists("../fanstatic/extra.css"))
        self.assertTrue(os.path.exists("../fanstatic/csa_field_descriptions.js"))
        self.assertTrue(os.path.exists("../fanstatic/webassets.yml"))


    def test_libraries(self):

        # Validate required modules & librairies
        self.assertTrue(os.path.exists("../../../requirements.txt"))
        self.assertTrue(os.path.exists("../../../dev-requirements.txt"))
        self.assertTrue(os.path.exists("../../../setup.cfg"))


    def test_data(self):

        # Read all datasets from the Open Data Portal
        global datasets_df
        print("\nTEST_START: test_data()")
        if len(datasets_df) == 0:
            datasets_df = self.__get_data(CSA_OPEN_DATA_PORTAL)

        # Validation
        try:
            metadata_df = datasets_df[['title', 'title_translated', 'id', 'notes', 'notes_translated', 'portal_type', 'format_of_source_data', 'format_of_source_data_details', 'resources', 'data_owner', 'data_steward', 'manager_or_supervisor', 'metadata_created', 'metadata_modified', 'portal_release_date', 'date_published', 'audience', 'subject', 'directorate', 'division', 'imso_approval', 'jurisdiction', 'language_support', 'license_id', 'license_title']]
            metadata_df = metadata_df.sort_values('title', ascending=True)
    
            # Let's look for "Evaluation Summary Space Astronomy Missions and Planetary Missions Programs"
            for row in metadata_df.index:
                if str(metadata_df['title'][row]) == "Evaluation Summary Space Astronomy Missions and Planetary Missions Programs":

                    # Validate the description
                    self.assertTrue("Conducted in 2017 in response to the Treasury Board of Canada Secretariat" in str(metadata_df['notes'][row]))
                    self.assertTrue("Conducted in 2017 in response to the Treasury Board of Canada Secretariat" in str(metadata_df['notes_translated'][row]))
                    self.assertTrue("Politique sur les résultats (2016) du Conseil du Trésor." in str(metadata_df['notes_translated'][row]))

                    # Validate the basic
                    self.assertTrue("08b13a1d-98fd-4374-b131-931116a15709" in str(metadata_df['id'][row]))
                    self.assertTrue("info" in str(metadata_df['portal_type'][row]))
                    self.assertTrue("['government_and_politics', 'science_and_technology']" in str(metadata_df['subject'][row]))
                    self.assertTrue("['general_public', 'government', 'scientists']" in str(metadata_df['audience'][row]))

                    # Validate the license
                    self.assertTrue("ca-ogl-lgo" in str(metadata_df['license_id'][row]))
                    self.assertTrue("Open Government Licence - Canada" in str(metadata_df['license_title'][row]))
                    self.assertTrue("federal" in str(metadata_df['jurisdiction'][row]))
                    self.assertTrue("true" in str(metadata_df['imso_approval'][row]))
                    self.assertTrue("csa" in str(metadata_df['data_owner'][row]))

                    # Validate resources
                    tmp_resources = str(metadata_df['resources'][row])
                    self.assertTrue("Evaluation Summary Space Astronomy Missions and Planetary Missions Programs" in tmp_resources)
                    self.assertTrue("Sommaire de l'évaluation des programmes de missions d'astronomie spatiale et de missions planétaires" in tmp_resources)
                    self.assertTrue("'format': 'HTML'" in tmp_resources)
                    self.assertTrue("'format': 'PDF'" in tmp_resources)
                    break

        except:
            self.fail("The format of the dataset has changed and is now incorrect.")


    def test_wet(self):

        # Make sure the WET is good
        self.assertTrue(os.path.exists("../public/csa_theme.css"))
        self.assertTrue(os.path.exists("../public/csa-asc.png"))
        self.assertTrue(os.path.exists("../public/favicon.ico"))
        self.assertTrue(os.path.exists("../public/jquery.min.js"))
        self.assertTrue(os.path.exists("../public/images/favicon.ico"))
        self.assertTrue(os.path.exists("../public/GCWeb/package.json"))
        self.assertTrue(os.path.exists("../public/wet-boew/payload.json"))
        self.assertTrue(os.path.exists("../public/GCWeb/assets/sig-blk-en.png"))
        self.assertTrue(os.path.exists("../public/GCWeb/assets/sig-blk-fr.png"))
        self.assertTrue(os.path.exists("../public/GCWeb/assets/wmms-blk.png"))
        self.assertTrue(os.path.exists("../public/GCWeb/assets/wmms-spl.png"))
        self.assertTrue(os.path.exists("../public/GCWeb/css/theme.css"))
        self.assertTrue(os.path.exists("../public/GCWeb/css/theme.min.css"))
        self.assertTrue(os.path.exists("../public/GCWeb/js/theme.js"))
        self.assertTrue(os.path.exists("../public/GCWeb/js/theme.min.js"))
        self.assertTrue(os.path.exists("../public/wet-boew/js/wet-boew.js"))
        self.assertTrue(os.path.exists("../public/wet-boew/js/wet-boew.min.js"))
        self.assertTrue(os.path.exists("../public/wet-boew/js/wet-boew.min.js.map"))
        self.assertTrue(os.path.exists("../public/GCWeb/css/wet-boew.css"))
        self.assertTrue(os.path.exists("../public/GCWeb/css/wet-boew.min.css"))
        self.assertTrue(os.path.exists("../public/GCWeb/css/wet-boew-overrides.css"))
        self.assertTrue(os.path.exists("../public/GCWeb/css/wet-boew-overrides.min.css"))

        # Validate templates

        
if __name__ == '__main__':
    unittest.main()
