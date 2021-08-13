
# CSA Open Data and Information Portal (CKAN)  
The intent of this project was to develop and support the continuous evolution of a web-based data and information Portal for CSA data and information assets. This is a key element in the CSA's fulfillment of the Directive on Open Government (2013), the Roadmap for Open Science (2020), as well as the CSA Data Strategy.

The live version of the site is available at https://donnees-data.asc-csa.gc.ca/dataset.

Key Portal features include the ability to:
 -Search the dataset registry.
 -Ensure metadata quality with a custom metadata schema and associated automated validator functions.
 -Implement and monitor a strict governance strategy.
 -Harvest data and metadata from external sources (including the open.canada.ca CKAN Portal) using https://github.com/asc-csa/ckan-gov-canada-harvester-master.
 -Interact with the site through a robust API.
 -Explore and analyze data in your browser, without the need to download the data and use complex software. This greatly decreases the barrier to entry.

 This project's guiding vision is to maximize access to data and information produced by and/or supported by the Canadian Space Agency.


# Introduction  
This project extends the default Comprehensive Knowledge Archive Network (CKAN) portal. The document outlines how to install everything required to implement these custom CSA features (including installing ckanext-asc-csa). It should serve as a high-level guide to any who works on the development of the CSA CKAN Portal in the future.

This document is structured in 2 main sections:  
- Installation and deployment  
- Development notes  

The "Installation and deployment" section of this document is a step-by-step guide on how to install a source install of CKAN and extend it further with CSA-developed features.  

The "Development notes" section of this document goes into specifics about each developed feature of CKAN. It was originally meant as a "write as you go" document so at times it may seem a bit unclear.

There is a short guide that might be of importance called "Directory Structures" near the bottom of the document which may be useful if you want to get up and running fast.  

"Useful commands" details a series of common tasks which can be run from the terminal.  

#  Installation and deployment  
This is the section on how to install and deploy CKAN.    

If you are not currently running Linux, you will need to create a virtual machine using a software such as [VirtualBox](https://www.virtualbox.org/). Configure this VM to run Ubuntu 20.04 LTS. You can find additional instructions on how to do this [here](https://www.wikihow.com/Install-Ubuntu-on-VirtualBox).  

## What is CKAN  
CKAN, is the world's leading Open Source data portal platform. More information about CKAN can be found on their website:  
[ckan](https://ckan.org)  

Documentation for CKAN can be difficult to get into, but overall is very well done. There is also a really helpful [gitter chat](https://gitter.im/ckan/chat) for CKAN developers. Below you can find documentation on the installation process to get the source version of CKAN along with the extensions that support CSA features. The installation process can take a long time (4-6 hours), particularly if this is your first time working on a project like this.

## Installing CKAN from package

Copied with some modifications from: [https://docs.ckan.org/en/2.9/maintaining/installing/install-from-package.html](https://docs.ckan.org/en/2.9/maintaining/installing/install-from-package.html)  

This section describes how to install CKAN from package. This is the quickest and easiest way to install CKAN, but it requires Ubuntu 18.04 (Python 2) or 20.04 (Python 3 or Python 2) 64-bit. If you’re not using any of these Ubuntu versions, or if you’re installing CKAN for development, you should follow Installing CKAN from source instead.

At the end of the installation process you will end up with two running web applications, CKAN itself and the DataPusher, a separate service for automatically importing data to CKAN’s DataStore extension. Additionally, there will be a process running the worker for running Background jobs. All these processes will be managed by Supervisor.

For Python 3 installations, the minimum Python version required is 3.6.

* Ubuntu 20.04 includes Python 3.8 as part of its distribution
* Ubuntu 18.04 includes Python 3.6 as part of its distribution

Host ports requirements:

|Service  |Port  |Used for
|:--|:--|:--|
|NGINX	|80	|Proxy
|uWSGI	|8080	|Web Server
|uWSGI	|8800	|DataPusher
|Solr/Jetty	|8983	|Search
|PostgreSQL	|5432	|Database
|Redis	|6379	|Search

###  1. Install the CKAN package
On your Ubuntu system, open a terminal and run these commands to install CKAN:

1.  Update Ubuntu’s package index:

	```
    sudo apt update
	```
2.  Install the Ubuntu packages that CKAN requires (and ‘git’, to enable you to install CKAN extensions):
	```
	sudo apt install -y libpq5 redis-server nginx supervisor
	```

3.  Download the CKAN package:

	On Ubuntu 20.04, for Python 3 (recommended):
	```
	wget https://packaging.ckan.org/python-ckan_2.9-py3-focal_amd64.deb
	```  

4.  Install the CKAN package:

     On Ubuntu 20.04, for Python 3:
     ```
     sudo dpkg -i python-ckan_2.9-py3-focal_amd64.deb
     ```

###  2. Install and configure PostgreSQL
Install PostgreSQL, running this command in a terminal:
```
sudo apt install -y postgresql
```
If you are facing a problem in case postgresql is not running, execute the command
```
sudo  service  postgresql  start
```
Check that PostgreSQL was installed correctly by listing the existing databases:
```
sudo -u postgres psql -l
```
Check that the encoding of databases is  `UTF8`, if not you might find issues later on with internationalization. Since changing the encoding of PostgreSQL may mean deleting existing databases, it is suggested that this is fixed before continuing with the CKAN install.

Next you’ll need to create a database user if one doesn’t already exist. Create a new PostgreSQL user called ckan_default, and enter a password for the user when prompted. You’ll need this password later, for this guide we will use the password 'Alouette1CSA':
```
sudo -u postgres createuser -S -D -R -P ckan_default
```
Create a new PostgreSQL database, called ckan_default, owned by the database user you just created:
```
sudo -u postgres createdb -O ckan_default ckan_default -E utf-8
```
Edit the [sqlalchemy.url](https://docs.ckan.org/en/2.9/maintaining/configuration.html#sqlalchemy-url) option in your [CKAN configuration file](https://docs.ckan.org/en/2.9/maintaining/configuration.html#config-file) (/etc/ckan/default/ckan.ini) file and set the correct password, database and database user.
```
sqlalchemy.url = postgresql://ckan_default:Alouette1CSA@localhost/ckan_default
```

###  3. Install and configure Solr
Install Solr, running this command in a terminal:
```
sudo apt install -y solr-tomcat
```
CKAN uses [Solr](https://lucene.apache.org/solr/) as its search platform, and uses a customized Solr schema file that takes into account CKAN’s specific search needs. Now that we have CKAN installed, we need to install and configure Solr.

Change the default port Tomcat runs on (8080) to the one expected by CKAN. To do so change the following line in the  `/etc/tomcat9/server.xml`  file (`tomcat8`  in older Ubuntu versions):

From:
```
<Connector port="8080" protocol="HTTP/1.1"
```
To:
```
<Connector port="8983" protocol="HTTP/1.1"
```
1.  Replace the default  `schema.xml`  file with a symlink to the CKAN schema file included in the sources.
    ```
    sudo mv /etc/solr/conf/schema.xml /etc/solr/conf/schema.xml.bak
    sudo ln -s /usr/lib/ckan/default/src/ckan/ckan/config/solr/schema.xml /etc/solr/conf/schema.xml
    ```

2.  Now restart Solr (use  `tomcat8`  on older Ubuntu versions):
    ```
    sudo service tomcat9 restart
    ```
3.  Check that Solr is running by opening  [http://localhost:8983/solr/](http://localhost:8983/solr/)
4.  Finally, change the  [solr_url](https://docs.ckan.org/en/2.9/maintaining/configuration.html#solr-url)  setting in your  [CKAN configuration file](https://docs.ckan.org/en/2.9/maintaining/configuration.html#config-file)  (/etc/ckan/default/ckan.ini) to point to your Solr server, for example:
	```    
	solr_url=http://127.0.0.1:8983/solr
	```
###  4. Install CKAN into a Python virtual environment
1.  Edit the  [CKAN configuration file](https://docs.ckan.org/en/2.9/maintaining/configuration.html#config-file)  (/etc/ckan/default/ckan.ini) to set up the following options:

	**site_id**
    Each CKAN site should have a unique  `site_id`, if only running this CKAN instance use:
    > ckan.site_id = default

    **site_url**
    Provide the site’s URL. For example:
    >
    > ckan.site_url = http://localhost:5000

	But use whatever you plan to use for either your production or development environment.

2.  Initialize your CKAN database by running this command in a terminal:

    >sudo ckan db init
###  5. Start the Web Server and restart Nginx  
Reload the Supervisor daemon so the new processes are picked up:

>sudo supervisorctl reload

After a few seconds run the following command to check the status of the processes:

>sudo supervisorctl status

You should see three processes running without errors:
```
ckan-datapusher:ckan-datapusher-00   RUNNING   pid 1963, uptime 0:00:12
ckan-uwsgi:ckan-uwsgi-00             RUNNING   pid 1964, uptime 0:00:12
ckan-worker:ckan-worker-00           RUNNING   pid 1965, uptime 0:00:12
```
If some of the processes report an error, make sure you’ve run all the previous steps and check the logs located in  `/var/log/ckan`  for more details.

Restart Nginx by running this command:

>sudo service nginx restart

You can now test the install by going to [http://localhost:5000](http://localhost:5000/), if it loads CKAN you have done everything right up to this point.
###  6. DataStore and DataPusher  
#### 1. Enable the plugin[](https://docs.ckan.org/en/2.9/maintaining/datastore.html#enable-the-plugin "Permalink to this headline")

Add the  `datastore`  plugin to your CKAN config file (leave the other plugins, add datastore to the end):
```
ckan.plugins = datastore
```
#### 2. Set up the database
*Make sure that you follow the steps in [Set Permissions](https://docs.ckan.org/en/2.9/maintaining/datastore.html#set-permissions) below correctly. Wrong settings could lead to serious security issues.*

The DataStore requires a separate PostgreSQL database to save the DataStore resources to.

List existing databases:

>sudo -u postgres psql -l

Check that the encoding of databases is  `UTF8`, if not internationalization may be a problem. Since changing the encoding of PostgreSQL may mean deleting existing databases, it is suggested that this is fixed before continuing with the datastore setup.
#### Create users and databases
Create a database_user called datastore_default. This user will be given read-only access to your DataStore database in the  [Set Permissions](https://docs.ckan.org/en/2.9/maintaining/datastore.html#set-permissions)  step below, when prompted for a password enter 'Canada1Alouette':

>sudo -u postgres createuser -S -D -R -P -l datastore_default

Create the database (owned by ckan_default), which we’ll call datastore_default:

>sudo -u postgres createdb -O ckan_default datastore_default -E utf-8

#### Set URLs
Now, uncomment the  [ckan.datastore.write_url](https://docs.ckan.org/en/2.9/maintaining/configuration.html#ckan-datastore-write-url)  and  [ckan.datastore.read_url](https://docs.ckan.org/en/2.9/maintaining/configuration.html#ckan-datastore-read-url)  lines in your CKAN config file and edit them if necessary, for example:

>ckan.datastore.write_url = postgresql://ckan_default:Alouette1CSA@localhost/datastore_default
>ckan.datastore.read_url = postgresql://datastore_default:Canada1Alouette@localhost/datastore_default

If you didn't use the recommended passwords replace  `Alouette1CSA` and `Canada1Alouette` with the passwords you used.
#### Set permissions
Once the DataStore database and the users are created, the permissions on the DataStore and CKAN database have to be set. CKAN provides a ckan command to help you correctly set these permissions.

If you are able to use the  `psql`  command to connect to your database as a superuser, you can use the  `datastore  set-permissions`  command to emit the appropriate SQL to set the permissions.

For example, if you can connect to your database server as the  `postgres`  superuser using:

>sudo -u postgres psql

Then you can use this connection to set the permissions:

> ckan -c /etc/ckan/default/ckan.ini datastore set-permissions | sudo -u postgres psql --set ON_ERROR_STOP=1

**Note:**
If you performed a package install, you will need to replace all references to ‘ckan -c /etc/ckan/default/ckan.ini …’ with ‘sudo ckan …’ and provide the path to the config file, e.g.:

>sudo ckan datastore set-permissions | sudo -u postgres psql --set ON_ERROR_STOP=1

If you can’t use the  `psql`  command in this way, you can simply copy and paste the output of:

> ckan -c /etc/ckan/default/ckan.ini datastore set-permissions

into a PostgreSQL superuser console.
### 3. Test the set-up
(https://docs.ckan.org/en/2.9/maintaining/datastore.html#test-the-set-up "Permalink to this headline")

The DataStore is now set-up. To test the set-up, (re)start CKAN and run the following command to list all DataStore resources:

>curl -X GET "http://127.0.0.1:5000/api/3/action/datastore_search?resource_id=_table_metadata"

This should return a JSON page without errors.

To test the whether the set-up allows writing, you can create a new DataStore resource. To do so, run the following command:

>curl -X POST http://127.0.0.1:5000/api/3/action/datastore_create -H "Authorization: {YOUR-API-KEY}" -d '{"resource": {"package_id": "{PACKAGE-ID}"}, "fields": [ {"id": "a"}, {"id": "b"} ], "records": [ { "a": 1, "b": "xyz"}, {"a": 2, "b": "zzz"} ]}'

Replace  `{YOUR-API-KEY}`  with a valid API key and  `{PACKAGE-ID}`  with the id of an existing CKAN dataset.

A table named after the resource id should have been created on your DataStore database. Visiting this URL should return a response from the DataStore with the records inserted above:

>http://127.0.0.1:5000/api/3/action/datastore_search?resource_id={RESOURCE_ID}

Replace  `{RESOURCE-ID}`  with the resource id that was returned as part of the response of the previous API call.

You can now delete the DataStore table with:

>curl -X POST http://127.0.0.1:5000/api/3/action/datastore_delete -H "Authorization: {YOUR-API-KEY}" -d '{"resource_id": "{RESOURCE-ID}"}'

To find out more about the DataStore API, see  [The DataStore API](https://docs.ckan.org/en/2.9/maintaining/datastore.html#the-datastore-api).

##  Extending CKAN with CSA Features  
The sections above set up a vanilla version of CKAN with the datastore and datapusher. To extend CKAN to contain developed features for the CSA follow the steps below.  

###  1. Installing Extensions  
To install Scheming, Fluent, and CSA extensions you will need git to clone the necessary files into the CKAN extensions directory. Git should have been installed in the above steps. If the CKAN server is running, turn the server off with `CTRL C`.  

Before starting make sure that the python virtual environment included with CKAN is running.  
```
. /usr/lib/ckan/default/bin/activate
```
Now navigate to CKAN's extension directory  
```  
cd /usr/lib/ckan/default/src  
```  
Clone the scheming repository into the directory  
  ```  
 git clone https://github.com/asc-csa/ckanext-asc-csa-scheming  
 ```  
Clone the fluent extension into the directory  
  ```  
 git clone https://github.com/ckan/ckanext-fluent.git
 ```  
Clone the CSA extension into the directory  
 ```   
git clone https://github.com/asc-csa/ckanext-asc-csa
```  

In CKAN's configuration file (`/etc/ckan/default/ckan.ini`) edit to include these settings. Some of these settings will exist others will not and must be added. Make sure that the settings are above the logging configuration settings or they will not be parsed.  

```  
ckan.plugins = stats text_view image_view recline_view csa scheming_datasets fluent datastore  

## Scheming Settings  

scheming.dataset_schemas = ckanext.csa:ckan_dataset.json  
 ckanext.csa:info.json ckanext.csa:doc.json  
scheming.presets = ckanext.csa:presets.json  
 ckanext.fluent:presets.json  
licenses_group_url = http://{ip of CKAN instance}/licenses.json  

# Example: licenses_group_url = http://127.0.0.1:5000/licenses.json  

ckan.locale_default = en  
ckan.locale_order = en fr  
ckan.locales_offered = en fr  
```  

Before continuing you should build each extension. You should be in the ckan src directory, if not execute:  
```
cd /usr/lib/ckan/default/src  
```
Enter into each extension directory and build the extension  
```
 cd ckanext-asc-csa-scheming
 pip install -r requirements.txt
 python setup.py develop
 cd ..  
 cd ckanext-fluent  
 python setup.py develop
 cd ..     
 cd ckanext-asc-csa  
 python setup.py develop
 cd ..  
```
###  2. Modify `schema.xml` File for Custom CKAN Search  
Copy the contents of the `schema.xml` file from the CSA extension into the original `schema.xml` file.  

```  
cp /usr/lib/ckan/default/src/ckanext-asc-csa/ckanext/csa/conf/solr/schema.xml /usr/lib/ckan/default/src/ckan/ckan/config/solr/schema.xml  
```  
You can also do this manually by copy and pasting the contents of the `schema.xml` file from ckanext-asc-csa into the specified file location above.  

Restart jetty after editing the `schema.xml` file  

For Ubuntu 20.04:  
```
sudo service nginx restart  
```
3. Test the extensions  
Restart the CKAN server and access the site from a browser. CSA features should now be present on the page.  
```  
sudo supervisorctl stop all  
```  

## Setting Up Your Installation

You will now want to create a sysadmin user and possibly import organizations to facilitate your work. This section is optional but will guide you through that process.

```
ckan -c /etc/ckan/default/ckan.ini sysadmin add seanh email=seanh@localhost name=seanh
```
where seanh will be replace by your username. You can find more instruction on
https://docs.ckan.org/en/2.9/maintaining/getting-started.html#create-admin-user

Once done, you will need to manually copy the file transitional_orgs.json from the ckanext-csa extension to the directory containing the ckan.ini file. Once in this directory, open a command prompt and use the following commands :
```  
. /usr/lib/ckan/default/bin/activate  
ckanapi load organizations -I transitional_orgs.jsonl
```  


In the ckan.ini file, add
```
ckan.storage_path = /var/lib/ckan/default
```
and execute the commands
```
paster --plugin=ckan datastore set-permissions -c /etc/ckan/default/ckan.ini
```

### Core File Replacement
There are a few features that had to be modified to meet accessibility and translation requirements. There was not a clear way to override the functionality to 2 files needed to be modified. You will need to replace these 2 files with the modified ones:
 - pagination.py
   - From the `ckan/lib` folder within the `ckanext-asc-csa extension` copy `pagination.py` into `/usr/lib/ckan/default/src/ckan/ckan/lib/`
 - reline.js
   - From the `reclinejs` folder within the `ckanext-asc-csa extension` copy `recline.js` into `/usr/lib/ckan/default/src/ckan/ckanext/reclineview/theme/public/vendor/recline/`


### Setting Up the Datapusher

The datapusher doesn't require any modification as it runs along ckan and not inside it. You can follow the steps onthe project's github page for this step.
https://github.com/ckan/datapusher

*Note: it is a good idea to install datapusher in a different environment (virtual or otherwise) than the one you used for CKAN. This is because they require different versions of various python libraries. If you install the datapusher requirements in your CKAN directory, you will probably temporarily break your CKAN installation. If you have done this, do not fret - it is an easy fix. Just reinstall your CKAN requirements.txt in that virtual environment and restart the datapusher setup process in a different environment.

##  Deploying a Source Install  
After installing source, follow this guide to deploy it to a production server.  
[https://docs.ckan.org/en/2.9/maintaining/installing/deployment.html](https://docs.ckan.org/en/2.9/maintaining/installing/deployment.html)  

Notes:  

Apache log files can be found in var/log/apache2.  
There has been permission denied errors on /tmp/default/sessions from the wsgi. A temporary solution is to execute the command:  
```
sudo chmod -R 777 /tmp  
```
#  Development Notes  

## Introduction to Development Notes  

Where above was a guide to install CKAN, below are the notes I have taken to communicate the progress that has been made so far.  

## Directory Structure and Specific Files of ckanext-asc-csa  
 - /installation guide - contains this document in the most updated form
 - /ckanext/csa - contains most of the code that adds CSA features to CKAN
 - /ckanext/csa/templates - contains most of the code that deals with what is rendered on the front end in terms of html
 - /ckanext/csa/fanstatic - contains the css and js files that are customized and added on top of what CKAN provides by default.
 - /ckanext/csa/presets.json - contains some presets that are used as scheming fields found in ckan_datasets.json
 - /ckanext/csa/ckan_datasets.json - contains the scheming fields on the CKAN instance
 - /ckanext/csa/plugin.py - contains the plugin class that uses [CKAN's plugin interface](https://docs.ckan.org/en/2.8/extensions/plugin-interfaces.html) to customize and [extend features](https://docs.ckan.org/en/2.8/extensions/tutorial.html)
 - /ckanext/csa/helpers.py - contains [helper functions](https://docs.ckan.org/en/2.8/theming/templates.html#adding-your-own-template-helper-functions) that are used in templates
 - /ckanext/csa/public - contains publicly available files that can be shown statically, in specific it contains the favicon, logo, and licenses.json file
 - /ckanext/csa/conf/solr/schema.xml - contains the modified schema that implements bilingual search and facetted search
 -

##  Harvesters  
Harvesting data from other sources is an important part of the CSA's implementation of CKAN. Currently CSA CKAN has scripts written to harvest data from DIIDS (Data and Information Inventory and Disclosure System) and the [Government of Canada Open Data Portal](https://open.canada.ca/en/open-data).  

On a new install of CKAN these harvesters should be used to populate the datasets with datasets from DIIDS and Government of Canada Open Data.  

Harvesting scripts will need an API key found in an administrator account on the CKAN user account page. The ip of the CKAN instance should also be included in these scripts. By default the ip included in the scripts should work with the development install of CKAN.  

###  Harvesting Data from Government of Canada Open Data  

https://github.com/asc-csa/ckan-gov-canada-harvester-master


###  Harvesting Data from DIIDS (Internal Only)
Harvesting data from DIIDS can be done from an external computer/server. It is done through HTTP API requests. This is quite similar to the Government of Canada harvester but instead of taking the files from a GET request, it takes data from a source csv file downloaded from DIIDS. Please see the "Unicode Problems" section of this document to ensure the CSV is in the correct format. That would include save as in notepad to UTF-8. Take a look at that section below.  

Creating Datasets with DIIDS may fail with this extension in it's current state because of new validators that have been put on the forms. In specific there are some fields that are required that would not be found from DIIDS only found in Government of Canada Open Data Portal. This was not dealt with earlier because there wasn't a way to know which fields would be needed later, so it was easiest just to keep everything the same before someone with the domain knowledge would author a guide on what metadata fields to use.  

Git clone this file and follow the readme for instructions.  
[https://gccode.ssc-spc.gc.ca/csa-data-centre-of-expertise/ckan-didds-harvester](https://gccode.ssc-spc.gc.ca/csa-data-centre-of-expertise/ckan-didds-harvester)  


##  Integration with Other Platforms (Query for Data)  
Querying CKAN from other applications can be done in two different ways. The first and most simple is to do a url download request like found below:  
https://stackabuse.com/download-files-with-python/  

The other option would be to use CKAN's API for tabular data. API reference for the datastore can be found online at this link:   
https://docs.ckan.org/en/2.8/maintaining/datastore.html#the-datastore-api  

Although there could be some limitation with the datastore API especially when trying to query for tens of thousands of rows. After discussions for stand alone applications such as individual satellite visualizations it may be best just to download/cache the file on the server/machine that is running the application.  


## Bilingual facets  
Facets are controlled by ckanext-asc-csa by using the IFacets interface in plugins.py. Here facets_dict is updated to include more facets. In addition to updating the interface multiple templates had to be created to account for the French and English versions of each of the facet values. The main problem here was that the facet would display the value instead of the localized label for each selection. This problem was solved by customizing templates to show the label of the correct language to the user of the website. The templates can be found in this repository (ckanext-asc-csa).  

These templates were created to accomplish this task:  
 - ckanext/csa/templates/package/search.html
 - ckanext/csa/templates/snippets/facet_list.html  
 - ckanext/csa/templates/snippets/dataset_facets.html  
 - ckanext/csa/templates/macros/csa_read.html  

In addition to editing the templates, for subject and keywords it was a special case because these are multivalued and also contain French and English versions. To solve this problem first as part of the IPackageController interface before_index had to be configured   
```  
def before_index(self, pkg_dict):  
 kw = json.loads(pkg_dict.get('extras_keywords', '{}')) pkg_dict['keywords_en'] = kw.get('en', []) pkg_dict['keywords_fr'] = kw.get('fr', []) pkg_dict['subject'] = json.loads(pkg_dict.get('subject', '[]')) return pkg_dict
```  

After defining a before_index function to modify the dataset/package dictionary before SOLR indexing, I manually specified a multivalued field in schema.xml  
```
<field name= "keywords_en" type="string" indexed="true" stored="true" multiValued="true"/>  
<field name= "keywords_fr" type="string" indexed="true" stored="true" multiValued="true"/>  
<field name="subject" type="string" indexed="true" stored="true" multiValued="true"/>  
```  
Once modified, the SOLR server must be reindexed manually from the virtual environment where CKAN is installed.  

`ckan -c /etc/ckan/default/ckan.ini search-index rebuild`

Facets for the organization page have not been fully integrated with the new facet functionality because that page should removed because the organization structure should be abstracted away from the user. If not the facets can be implemented by changing the template files to render language specific values.  


## Bilingual Metadata Display on Search Page  
This was a simple fix, and was done by creating snippets/package_item.html and creating some helper functions in helpers.py to display the correct version of the text by calling h.lang().  

## Translating Internationalized Strings  
To translate the UI strings first you must mark the string as being translatable within the Python or Jinja code. Then you must custom create a .po file with those manual translations. CKAN provides a [great guide](https://docs.ckan.org/en/2.8/extensions/translating-extensions.html) to implement this. String translations English to French were taken from GC Canada, located [here](https://github.com/open-data/ckanext-canada/blob/master/ckanext/canada/i18n/fr/LC_MESSAGES/canada.po).  

##  Bilingual Search Engine  
After customizing fields to include French and English support, content search was not working as expected. Simple searches of whole titles were not displaying any datasets.   

I reached out to Ian Ward (CKAN Development Team Member also GC Public Servant) to ask for some advice on how to solve this problem, his reply is below.  
Notes from Ian Ward:  

> You'll need a solr schema with en/fr text fields and a bunch of  
> copyFields for each field in your schema kind of like  
> https://github.com/open-data/ogc_search/blob/master/ogc_search/open_data/solr/schema.xml#L572 (NB: this is not a ckan schema so you won't be able to use it  
> directly) and a before_index that stores all language text separately  
> so it can be picked up by these copyFields then you need to override  
> ckan's search so it will use the correct field for search based on the  
> user's language Bonus point for doing this in a reusable way that  
> could be incorporated into ckan/scheming themselves. That's always  
> harder than hacking something together quickly of course  

CKAN search uses [SOLR](https://lucene.apache.org/solr/guide/6_6/index.html) for content discovery. The file "schema.xml" specifies the settings for the search schema. It can be found in this path "/usr/lib/ckan/default/src/ckan/ckan/config/solr/schema.xml". A modified copy that includes the changes is included within ckanext-asc-csa. It was first good to learn how a solr search works ([Analyzers, Tokenizers, and Filters](https://lucene.apache.org/solr/guide/6_6/understanding-analyzers-tokenizers-and-filters.html)).   

CKAN package search logic can be found on [github](https://github.com/ckan/ckan/blob/master/ckan/logic/action/get.py#L1705).  

To remedy search I custom defined new a new field type in schema.xml which uses a special process on French text

After defining the new field I modified my before_index to extract from pkg_dict the terms I wanted to include within the search index, in this case being notes_fr, title_fr. Next I added multi-valued res_name_fr. I had to parse through the source code of CKAN to determine where the query was being executed. The code for that can be found [here](https://github.com/ckan/ckan/blob/master/ckan/lib/search/query.py#L253). To debug the code I added in some print statements that are included in this snippet of code.   
```  
 conn = make_connection(decode_dates=False) log.debug('Package query: %r' % query) print query try: solr_response = conn.search(**query) for result in solr_response: print result
```  
CKAN uses a library called [pysolr](https://github.com/django-haystack/pysolr) to interface with Solr, it was useful to take a look at some of the documentation for how CKAN does a query.  

After I was able to view the query I realized I had to change the 'qf' search parameter to specify that I wanted to weight the French fields higher when searching when CKAN is set to French. CKAN uses DisMax to do searches, documentation for that is [here](https://lucene.apache.org/solr/guide/6_6/the-dismax-query-parser.html#TheDisMaxQueryParser-Theqf_QueryFields_Parameter) this link also helps you to understand what 'qf' does.  

**Important note:** when doing development of search you will need to restart the SOLR server and reindex the the current packages. How to do this is found in terminal commands in the the Tips and Tricks section of this document.  


# Authors  
- Cooper Ang - Initial development of CSA CKAN in 4 month long internship  
- Jenisha Patel - Started the CSA CKAN project in initial 1 week long pilot
- Patrick Baral - In a 4 month long internship
- Jonathan Beaulieu-Emond - In a 3 month long internship
- Natasha Fee - DCoE Data Scientist
- Canadian Space Agency (Data Center Centre of Expertise) - Supported project with resources

# Acknowledgements  
- Étienne Low-Décarie - Supervisor of project
- Wasiq Mohammad - Technical mentor
