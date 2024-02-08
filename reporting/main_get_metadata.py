# This script uses the API to retrieve the metadata of the datasets of the Open Data Portal.
#
# @author Emiline Filion - Canadian Space Agency
#

import datetime
from datetime import datetime
from pdf_document import pdf_document
import portal_helper
import pandas as pd


# Formats the data type
# Params:
#    data_type : Type of data (string)
#    detailed_data_type : Detailed type of data (string)
def format_data_type(data_type, detailed_data_type):
    
    if len(detailed_data_type) == 0:
        return portal_helper.format_to_readable(data_type)
    if data_type in detailed_data_type:
        return portal_helper.format_to_readable(detailed_data_type)
    return portal_helper.format_to_readable(data_type + ', ' + detailed_data_type)


# Read all datasets from the Open Data Portal
space_df = portal_helper.get_data('https://donnees-data.asc-csa.gc.ca')
print('Number of datasets found in the Open Data Portal: ' + str(len(space_df.index)))

# Save data to Excel
month = str(datetime.now().month)
year = str(datetime.now().year)
excel_filename = "Open Data Portal - Metadata-" + year + "-" + month + ".xlsx"
space_df = space_df.sort_values('metadata_created')

# Extract the metadata (resources column)
print ('Saving the list of data stewards to disk: ' + excel_filename)
#metadata_df = space_df[['title', 'title_translated', 'portal_type', 'format_of_source_data', 'format_of_source_data_details', 'id', 'resources', 'metadata_created', 'metadata_modified', 'metadata_contact', 'data_owner', 'data_steward', 'manager_or_supervisor', 'portal_release_date', 'date_published', 'audience', 'subject', 'keywords', 'directorate', 'division', 'imso_approval', 'jurisdiction', 'language_support', 'license_id', 'license_title', 'notes', 'notes_translated']]
metadata_df = space_df[['title', 'title_translated', 'id', 'notes', 'notes_translated', 'portal_type', 'format_of_source_data', 'format_of_source_data_details', 'resources', 'data_owner', 'data_steward', 'manager_or_supervisor', 'metadata_created', 'metadata_modified', 'portal_release_date', 'date_published', 'audience', 'subject', 'directorate', 'division', 'imso_approval', 'jurisdiction', 'language_support', 'license_id', 'license_title']]
metadata_df = metadata_df.sort_values('title', ascending=False)
metadata_df.to_excel("Open Data Portal - Metadata-" + year + "-" + month + ".xlsx", index=False)

# Create the PDF documents
pdf_doc_en = pdf_document('Open Data Portal - Metadata', 'en')
pdf_doc_fr = pdf_document('Portail des données ouvertes - Métédonnées', 'fr')
pdf_doc_en.createHeader()
pdf_doc_fr.createHeader()

# Add flesh to the bones
pdf_doc_en.addChapter('Scope')
pdf_doc_en.addParagraph('The Open Data Portal provides a reference to various data and information from space-related missions and activities and from corporate publications, peer-reviewed publications, financial reports, audits and evaluations. This document presents the metadata of all the datasets that are part of the Open Data Portal.')
pdf_doc_en.addSeparationBlock()
pdf_doc_en.addSeparationBlock()
pdf_doc_fr.addChapter('Résumé')
pdf_doc_fr.addParagraph('Le portail de données ouvertes de l’Agence spatiale canadienne fournit une référence aux données et informations provenant de missions spatiales, des publications gouvernementales, des publications évaluées par des pairs, des rapports financiers, des audits et des rapports d’évaluations. Ce document présente les métadonnées de tous les ensembles de données qui font partie du portail des données ouvertes.')
pdf_doc_fr.addSeparationBlock()
pdf_doc_fr.addSeparationBlock()

for row in metadata_df.index:
    
    # Title
    pdf_doc_en.addChapter(metadata_df['title'][row])
    pdf_doc_fr.addChapter(metadata_df['title'][row])
    
    # Description
    pdf_doc_en.addParagraph('<b>Subject</b>: ' + portal_helper.format_to_readable(str(metadata_df['subject'][row])))
    pdf_doc_fr.addParagraph('<b>Sujet</b>: ' + portal_helper.format_to_readable(str(metadata_df['subject'][row])))
    pdf_doc_en.addParagraph('<b>Langage(s)</b>: ' + portal_helper.format_to_readable(str(metadata_df['language_support'][row])))
    pdf_doc_fr.addParagraph('<b>Langue(s)</b>: ' + portal_helper.format_to_readable(str(metadata_df['language_support'][row])))
    pdf_doc_en.addParagraph('<b>Description</b>: ' + str(metadata_df['notes'][row]))
    pdf_doc_fr.addParagraph('<b>Description</b>: ' + str(metadata_df['notes'][row]))
    pdf_doc_en.addEmptyLine()
    pdf_doc_fr.addEmptyLine()
    
    # Main contact point (data steward + manager)
    pdf_doc_en.addParagraph('<b>Data owner</b>: ' + portal_helper.format_to_readable(str(metadata_df['data_owner'][row]).upper()))
    pdf_doc_fr.addParagraph('<b>Propriétaire des données</b>: ' + portal_helper.format_to_readable(str(metadata_df['data_owner'][row]).upper()))
    pdf_doc_en.addParagraph('<b>Data steward</b>: ' + portal_helper.format_to_readable(str(metadata_df['data_steward'][row])))
    pdf_doc_fr.addParagraph('<b>Responsable des données</b>: ' + portal_helper.format_to_readable( str(metadata_df['data_steward'][row])))
    pdf_doc_en.addParagraph('<b>Manager</b>: ' + portal_helper.format_to_readable(str(metadata_df['manager_or_supervisor'][row])))
    pdf_doc_fr.addParagraph('<b>Superviseur(e)</b>: ' + portal_helper.format_to_readable(str(metadata_df['manager_or_supervisor'][row])))
    pdf_doc_en.addParagraph('<b>Directorate</b>: ' + portal_helper.format_to_readable(str(metadata_df['directorate'][row])))
    pdf_doc_fr.addParagraph('<b>Direction</b>: ' + portal_helper.format_to_readable(str(metadata_df['directorate'][row])))
    pdf_doc_en.addParagraph('<b>Division</b>: ' + portal_helper.format_to_readable(str(metadata_df['division'][row])))
    pdf_doc_fr.addParagraph('<b>Division</b>: ' + portal_helper.format_to_readable(str(metadata_df['division'][row])))

    # Audience
    pdf_doc_en.addParagraph('<b>Audience</b>: ' + portal_helper.format_to_readable(str(metadata_df['audience'][row])))
    pdf_doc_fr.addParagraph('<b>Auditoire</b>: ' + portal_helper.format_to_readable(str(metadata_df['audience'][row])))
    pdf_doc_en.addEmptyLine()
    pdf_doc_fr.addEmptyLine()

    # Type of format
    format = format_data_type(str(metadata_df['format_of_source_data'][row]), str(metadata_df['format_of_source_data_details'][row]))
    pdf_doc_en.addParagraph('<b>Type of data</b>: ' + portal_helper.format_to_readable(str(metadata_df['portal_type'][row])))
    pdf_doc_fr.addParagraph('<b>Type de données</b>: ' + portal_helper.format_to_readable(str(metadata_df['portal_type'][row])))
    pdf_doc_en.addParagraph('<b>Format of data</b>: ' + format)
    pdf_doc_fr.addParagraph('<b>Format(s) des données</b>: ' + format)
    pdf_doc_en.addEmptyLine()
    pdf_doc_fr.addEmptyLine()
    
    # Extra
    pdf_doc_en.addParagraph('<b>IMSO approval</b>: ' + str(metadata_df['imso_approval'][row]))
    pdf_doc_fr.addParagraph('<b>Approbation IMSO</b>: ' + str(metadata_df['imso_approval'][row]))
    pdf_doc_en.addParagraph('<b>Jurisdiction</b>: ' + str(metadata_df['jurisdiction'][row]))
    pdf_doc_fr.addParagraph('<b>Juridiction</b>: ' + str(metadata_df['jurisdiction'][row]))

    # License
    pdf_doc_en.addParagraph('<b>License ID</b>: ' + str(metadata_df['license_id'][row]))
    pdf_doc_fr.addParagraph('<b>Identifiant de la licence</b>: ' + str(metadata_df['license_id'][row]))
    pdf_doc_en.addParagraph('<b>License title</b>: ' + str(metadata_df['license_title'][row]))
    pdf_doc_fr.addParagraph('<b>Nom de la licence</b>: ' + str(metadata_df['license_title'][row]))
    
    # URL
    tmp_link = 'https://donnees-data.asc-csa.gc.ca/en/dataset/' + metadata_df['id'][row]
    pdf_doc_en.addParagraph('<b>URL</b>: <a href=\"' + tmp_link + '\">' + tmp_link + '</a>')
    pdf_doc_fr.addParagraph('<b>Lien</b>: <a href=\"' + tmp_link + '\">' + tmp_link + '</a>')
    
    pdf_doc_en.addSeparationBlock()
    pdf_doc_en.addSeparationBlock()
    pdf_doc_fr.addSeparationBlock()
    pdf_doc_fr.addSeparationBlock()

# Save the PDF document
pdf_doc_en.save()
pdf_doc_fr.save()

# End of script
print("\nThe script ended successfully")
print("Have a nice day!\n")