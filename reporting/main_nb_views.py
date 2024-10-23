# This script uses the API to retrieve the number of views for each dataset of the Open Data Portal.
# The scripts also prints out stats and creates an Excel file.
#
# @author Emiline Filion - Canadian Space Agency
#

import datetime
from datetime import date
from datetime import datetime
import math
import matplotlib.pyplot as plt
import portal_helper
import pandas as pd


# Constants
CSA_OPEN_DATA_PORTAL_URL = 'https://donnees-data.asc-csa.gc.ca'
EXPLODE_PARAM = [0.2, 0.1, 0, 0, 0, 0]
PERCENT_DISPLAY = '%1.0f%%'
OTHERS = 'Others'
GOOD_DATASET_STR = "At least a visit per day"
BAD_DATASET_STR = "Needs marketing - Less than one view per week"
GREAT_NB_VIEWS_GOING_UP_STR = "↗↗↗↗"
REALLY_BAD_NB_VIEWS_GOING_DOWN_STR = "↘↘↘↘"
NB_VIEWS_STABLE_STR = "~"
NB_VIEWS_GOING_UP_STR = "↗"
NB_VIEWS_GOING_DOWN_STR = "↘"
NB_DAYS_PER_YEAR = 365.26
NO_VIEWS_THRESHOLD = 1
GREAT_IMPROVEMENTS_NB_VIEWS_PER_DAY = 1.2
BAD_DEPRECIATION_NB_VIEWS_PER_DAY = -1.0
BUFFER_STABLE_NB_VIEWS_PER_DAY = 0.2
GOOD_RECENT_NB_VIEWS = 40
GOOD_RATIO_THRESHOLD_PER_DAY = 0.96
POOR_RATIO_THRESHOLD_PER_DAY = 0.23

COL_ID = 'id'
COL_TITLE = 'title'
COL_PORTAL_TYPE = 'portal_type'
COL_CREATION_DATE = 'metadata_created'
COL_TOTAL_NB_VIEWS = 'total_nb_views'
COL_RECENT_NB_VIEWS = 'recent_nb_views'
COL_NB_YEARS_PORTAL = 'nb_years_in_portal'
COL_AVG_RECENT_NB_VIEWS_PER_DAY = 'average_recent_nb_views_per_day'
COL_AVG_NB_VIEWS_PER_DAY = 'average_total_nb_views_per_day'
COL_AVG_NB_VIEWS_PER_YEAR = 'average_nb_views_per_year'
COL_LONG_TERM_TREND = 'long_term_trend'
COL_COMMENTS = 'comments'

# Date values
today = datetime.now()
today2 = date.today()
day = str(today.day)
month = str(today.month)
year = str(today.year)


# Evaluates the ratio of views per day.
# @param average_nb_views_per_day - Average number of views per day
# @param recent_nb_views - Recent number of views
# @return String comment
def eval_ratio_views_per_day(average_nb_views_per_day, recent_nb_views):

    average_recent_nb_views_per_day = recent_nb_views / 14
    if (average_nb_views_per_day >= GOOD_RATIO_THRESHOLD_PER_DAY or recent_nb_views >= GOOD_RECENT_NB_VIEWS) and ((average_recent_nb_views_per_day - average_nb_views_per_day) > GREAT_IMPROVEMENTS_NB_VIEWS_PER_DAY):
        average_recent_nb_views_per_day = math.floor(average_recent_nb_views_per_day + 0.5)
        return GOOD_DATASET_STR + ' - Got recently around ' + str(average_recent_nb_views_per_day) + ' views per day'
    if average_nb_views_per_day >= GOOD_RATIO_THRESHOLD_PER_DAY or recent_nb_views >= GOOD_RECENT_NB_VIEWS:
        return GOOD_DATASET_STR
    if average_recent_nb_views_per_day <= POOR_RATIO_THRESHOLD_PER_DAY and average_nb_views_per_day <= POOR_RATIO_THRESHOLD_PER_DAY:
        return BAD_DATASET_STR
    return ""

# Evaluates the long-term trend.
# @param average_total_nb_views_per_day - Average number of views per day (total).
# @param average_recent_nb_views_per_day - Average number of views per day (recent).
# @return Trend as a string.
def eval_trend(average_total_nb_views_per_day, average_recent_nb_views_per_day):

    delta_avg = abs(average_total_nb_views_per_day - average_recent_nb_views_per_day)
    if (average_recent_nb_views_per_day - average_total_nb_views_per_day) >= GREAT_IMPROVEMENTS_NB_VIEWS_PER_DAY:
        return GREAT_NB_VIEWS_GOING_UP_STR
    if (average_recent_nb_views_per_day - average_total_nb_views_per_day) <= BAD_DEPRECIATION_NB_VIEWS_PER_DAY:
        return REALLY_BAD_NB_VIEWS_GOING_DOWN_STR
    if delta_avg <= BUFFER_STABLE_NB_VIEWS_PER_DAY:
        return NB_VIEWS_STABLE_STR
    if (average_recent_nb_views_per_day > average_total_nb_views_per_day):
        return NB_VIEWS_GOING_UP_STR
    if average_recent_nb_views_per_day < average_total_nb_views_per_day:
        return NB_VIEWS_GOING_DOWN_STR
    return ''


# Read the list datasets from the Open Data Portal
metadata_df = portal_helper.get_data(CSA_OPEN_DATA_PORTAL_URL)
metadata_df = metadata_df.sort_values(COL_TITLE, ascending=False)
print('Number of datasets found in the Open Data Portal: ' + str(len(metadata_df.index)))

# Get the number of views for each dataset
nb_recent_views = 0
nb_total_views = 0
views_df = pd.DataFrame(columns=[COL_ID, COL_TITLE, COL_PORTAL_TYPE, COL_CREATION_DATE, COL_TOTAL_NB_VIEWS, COL_RECENT_NB_VIEWS, COL_NB_YEARS_PORTAL, COL_AVG_NB_VIEWS_PER_YEAR, COL_AVG_NB_VIEWS_PER_DAY, COL_AVG_RECENT_NB_VIEWS_PER_DAY, COL_LONG_TERM_TREND, COL_COMMENTS])
print('Getting the number of views... (takes one or two minutes)')
for row in metadata_df.index:
    
    # Get the number of views for each dataset
    dataset = portal_helper.get_dataset_info(CSA_OPEN_DATA_PORTAL_URL, metadata_df[COL_ID][row])
    created_date = str(dataset[COL_CREATION_DATE]).split('T')[0]
    date_delta = today2 - datetime.strptime(created_date, "%Y-%m-%d").date()
    average_per_day = dataset['tracking_summary']['total'] / date_delta.days
    average_recent_per_day = dataset['tracking_summary']['recent'] / 14
    views_df.loc[len(views_df)] = [metadata_df[COL_ID][row], dataset[COL_TITLE], dataset[COL_PORTAL_TYPE], created_date, dataset['tracking_summary']['total'], dataset['tracking_summary']['recent'], portal_helper.trunc_floating_value(date_delta.days/NB_DAYS_PER_YEAR), math.floor(((average_per_day*NB_DAYS_PER_YEAR)) + 0.5), portal_helper.trunc_floating_value(average_per_day), portal_helper.trunc_floating_value(average_recent_per_day), eval_trend(average_per_day, average_recent_per_day), eval_ratio_views_per_day(average_per_day, dataset['tracking_summary']['recent'])]
    nb_recent_views = nb_recent_views + dataset['tracking_summary']['recent']
    nb_total_views = nb_total_views + dataset['tracking_summary']['total']

# Save data to disk
excel_filename = "Open Data Portal - Number of Views-" + year + "-" + month + "-" + day + ".xlsx"
print('Number of views on the CSA Open Data Portal for the last 2 weeks: ' + str(nb_recent_views))
print ('Saving the number of views to disk: ' + excel_filename)
views_df = views_df.sort_values(COL_TOTAL_NB_VIEWS, ascending=False)
views_df.to_excel(excel_filename, index=False)

# Print conventions
print('\nNOTE: The number of views in the last 2 weeks corresponds to 14 days.')
print('The total number of views is all of its tracked views (including recent ones).')
print('Repeatedly visiting the same page does not increase the page\’s view count.')
print('Page view counting is limited to one view per user per page per day.\n')

# Rename title that are too long, which is going to make our pie charts much better
views_df.loc[views_df[COL_TITLE] == 'Radarsat Constellation Mission (RCM) Data', COL_TITLE] = 'RCM'
views_df.loc[views_df[COL_TITLE] == 'MOPITT - Measurements of Pollution in the Troposphere', COL_TITLE] = 'MOPITT'
views_df.loc[views_df[COL_TITLE] == 'Atmospheric Chemistry Experiment (ACE) on SCISAT', COL_TITLE] = 'SCISAT'
views_df.loc[views_df[COL_TITLE] == 'RADARSAT-1 Archive', COL_TITLE] = 'RADARSAT-1'
views_df.loc[views_df[COL_TITLE] == 'NEOSSAT - Astronomy Data', COL_TITLE] = 'NEOSSAT'
views_df.loc[views_df[COL_TITLE] == 'Ionosphere images from Alouette satellites', COL_TITLE] = 'Alouette'
views_df.loc[views_df[COL_TITLE] == 'Alpha Particle X-Ray Spectrometer (APXS) Carried on Board the Curiosity Rover', COL_TITLE] = 'APXS'
views_df.loc[views_df[COL_TITLE] == 'The Geospace Observatory (GO) Canada Initiative', COL_TITLE] = 'GO Canada'
views_df.loc[views_df[COL_TITLE] == 'THEMIS Mission (Time History of Events and Macroscale Interactions during Substorms)', COL_TITLE] = 'THEMIS'
views_df.loc[views_df[COL_TITLE] == 'CARISMA Magnetometer Network', COL_TITLE] = 'CARISMA'
views_df.loc[views_df[COL_TITLE] == 'CASSIOPE Satellite Data on Earth’s Space Environment', COL_TITLE] = 'CASSIOPE'
views_df.loc[views_df[COL_TITLE] == 'Canadian Planetary Emulation Terrain 3D Mapping Dataset: CSA Mars Emulation Terrain (MET)', COL_TITLE] = 'Terrain 3D'
views_df.loc[views_df[COL_TITLE] == 'BRITE Constellation', COL_TITLE] = 'BRITE'
views_df.loc[views_df[COL_TITLE] == 'RADARSAT-1 - Heatmap of processed archived images', COL_TITLE] = 'R1 Heatmap'
views_df.loc[views_df[COL_TITLE] == 'Advanced MOST Science Archive (AMSA)', COL_TITLE] = 'AMSA'
views_df.loc[views_df[COL_TITLE] == 'Meteorological Station (MET) of the Phoenix Mission', COL_TITLE] = 'Phoenix MET'
views_df.loc[views_df[COL_TITLE] == 'OSIRIS - Optical Spectrograph and InfraRed Imaging System', COL_TITLE] = 'OSIRIS'
views_df.loc[views_df[COL_TITLE] == 'Lunar Exploration Analogue Deployment (LEAD) - Rover Data', COL_TITLE] = 'LEAD'
views_df.loc[views_df[COL_TITLE] == 'Canadian Space Agency (CSA) peer-reviewed publications list', COL_TITLE] = 'CSA Pub List'
views_df.loc[views_df[COL_TITLE] == 'Evaluation of the European Space Agency Contribution Program of the Canadian Space Agency', COL_TITLE] = 'Eval ESA-CSA'

# Top 5 - Recent views
print('\nTOP 5 (last 2 weeks)')
views_df = views_df.sort_values(COL_RECENT_NB_VIEWS, ascending=False)
top5_df = views_df[:5].copy()
top5_df = top5_df.drop(columns=[COL_ID, COL_PORTAL_TYPE, COL_CREATION_DATE, COL_TOTAL_NB_VIEWS, COL_NB_YEARS_PORTAL, COL_AVG_NB_VIEWS_PER_DAY, COL_AVG_RECENT_NB_VIEWS_PER_DAY, COL_AVG_NB_VIEWS_PER_YEAR, COL_LONG_TERM_TREND, COL_COMMENTS])
for row in top5_df.index:
    print(' - ' + top5_df[COL_TITLE][row])
    nb_recent_views = nb_recent_views - top5_df[COL_RECENT_NB_VIEWS][row]
top5_df.loc[len(top5_df)] = [OTHERS, nb_recent_views]
plt.pie(top5_df[COL_RECENT_NB_VIEWS], labels = top5_df[COL_TITLE], explode=EXPLODE_PARAM, shadow = True, autopct=PERCENT_DISPLAY)
plt.savefig("Top 5 - Most Popular Datasets (last 2 weeks)-" + year + "-" + month + "-" + day + ".png")
plt.show()

# Top 5 - Forever
print('\nTOP 5 (all time)')
views_df = views_df.sort_values(COL_TOTAL_NB_VIEWS, ascending=False)
top5_df = views_df[:5].copy()
top5_df = top5_df.drop(columns=[COL_ID, COL_PORTAL_TYPE, COL_CREATION_DATE, COL_RECENT_NB_VIEWS, COL_NB_YEARS_PORTAL, COL_AVG_NB_VIEWS_PER_DAY, COL_AVG_RECENT_NB_VIEWS_PER_DAY, COL_AVG_NB_VIEWS_PER_YEAR, COL_LONG_TERM_TREND, COL_COMMENTS])
for row in top5_df.index:
    print(' - ' + top5_df[COL_TITLE][row])
    nb_total_views = nb_total_views - top5_df[COL_TOTAL_NB_VIEWS][row]
top5_df.loc[len(top5_df)] = [OTHERS, nb_total_views]
plt.pie(top5_df[COL_TOTAL_NB_VIEWS], labels = top5_df[COL_TITLE], explode=EXPLODE_PARAM, shadow = True, autopct=PERCENT_DISPLAY)
plt.savefig("Top 5 - Most Popular Datasets (all time)-" + year + "-" + month + "-" + day + ".png")
plt.show()

# Histogram having both number of views
top20_df = views_df[:20].copy()
top20_df.plot(x="title", y=["total_nb_views", "recent_nb_views"], xlabel='Number of views', ylabel="Datasets", legend=['All time', 'Last 2 weeks'], color=["blue","fuchsia"], kind="barh") 
plt.savefig("Top 20 - Most Popular Datasets-" + year + "-" + month + "-" + day + ".png")
plt.show()

# Ratio between the number of views versus creation date
print('\nTOP 20 (best ratio - Number of views / day)')
views_df = views_df.sort_values(COL_AVG_NB_VIEWS_PER_DAY, ascending=False)
top20_df = views_df[:20].copy()
top20_df = top20_df.drop(columns=[COL_ID, COL_PORTAL_TYPE, COL_CREATION_DATE, COL_RECENT_NB_VIEWS, COL_TOTAL_NB_VIEWS, COL_NB_YEARS_PORTAL, COL_AVG_NB_VIEWS_PER_YEAR, COL_LONG_TERM_TREND, COL_COMMENTS])
for row in top20_df.index:
    print(' - ' + top20_df[COL_TITLE][row])

# Datasets without any views (last 2 weeks)
print('\nDatasets without any views (last 2 weeks)')
views_df = views_df.sort_values(COL_TITLE, ascending=False)
nb_datasets_without_views = 0
for row in views_df.index:
    if views_df[COL_RECENT_NB_VIEWS][row] <= NO_VIEWS_THRESHOLD:
        print(' - ' + views_df[COL_TITLE][row])
        nb_datasets_without_views = nb_datasets_without_views + 1
if nb_datasets_without_views == 0:
    print('There are no datasets without any views. All ' + str(len(metadata_df.index)) + ' datasets have been visited over the last 2 weeks.')

# Datasets having a low average of views per day
print('\nDatasets having a low average of views per day')
views_df = views_df.sort_values(COL_TITLE, ascending=True)
for row in views_df.index:
    if views_df[COL_COMMENTS][row] == BAD_DATASET_STR:
        print(' - ' + views_df[COL_TITLE][row])

# End of script
print("\nThe script ended successfully")
print("Have a nice day!\n")
