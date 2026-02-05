# CSA Open Data Portal Installation Guide

## Minimum System Requirements

- Ubuntu 24.04 LTS
- Solr 9.x
- Python 3.12 or later
- PostgreSQL 17.6 or later (with PostGIS extension)
- Redis 6.x or later
- Git
- 4GB RAM minimum (8GB recommended)
- 20GB disk space


## Prerequisites Installation

### 1. Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev \
    build-essential libxml2-dev libxslt1-dev zlib1g-dev \
    libffi-dev libpq-dev git redis-server \
    libgeos-dev proj-bin libproj-dev

### Install Java
sudo apt update
sudo apt install default-jdk
java -version
```
### 2. Install PostgreSQL 17

Ubuntu 24.04 does not include PostgreSQL 17 by default. Add the official PostgreSQL repository:
```bash
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt install -y postgresql-17 postgresql-17-postgis-3
```

### 3. Create PostgreSQL User and Database

```bash
sudo -u postgres psql
```

In the PostgreSQL shell:

```sql
CREATE USER ckan_default WITH PASSWORD 'your_password_here';
CREATE DATABASE ckan_default OWNER ckan_default ENCODING 'UTF8';
\c ckan_default
GRANT ALL PRIVILEGES ON DATABASE ckan_default TO ckan_default;
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
\q
```


## Solr 9 Installation

```bash
cd /opt
sudo wget https://archive.apache.org/dist/solr/solr/9.4.0/solr-9.4.0.tgz
sudo tar xzf solr-9.4.0.tgz
sudo solr-9.4.0/bin/install_solr_service.sh solr-9.4.0.tgz
```


## CKAN Installation

### 1. Create CKAN Directory Structure

```bash
sudo mkdir -p /usr/lib/ckan/default
sudo mkdir -p /etc/ckan/default
sudo mkdir -p /var/lib/ckan/default/storage
sudo chown -R $USER:$USER /usr/lib/ckan /etc/ckan /var/lib/ckan
```

### 2. Create Virtual Environment

```bash
python3.12 -m venv /usr/lib/ckan/default
source /usr/lib/ckan/default/bin/activate
pip install --upgrade pip setuptools wheel
```

### 3. Install CKAN 2.11 from Git

```bash
pip install -e 'git+https://github.com/ckan/ckan.git@ckan-2.11.0#egg=ckan[requirements]'
```

### 4. Install the CSA Extension and Dependencies

```bash
cd /usr/lib/ckan/default/src
git clone https://github.com/asc-csa/ckanext-asc-csa.git
OR
git clone --branch cleanups --single-branch https://github.com/asc-csa/ckanext-asc-csa.git
cd ckanext-asc-csa
pip install -r requirements.txt
pip install -e .
```


## CKAN Configuration

### 1. Generate CKAN Configuration File

```bash
ckan generate config /etc/ckan/default/ckan.ini
```

### 2. Edit CKAN Configuration

Edit `/etc/ckan/default/ckan.ini` and update the following settings:

```ini
## Database Settings
sqlalchemy.url = postgresql://ckan_default:your_password_here@localhost:5432/ckan_default

## Site Settings
ckan.site_url = http://localhost:5000
ckan.site_id = default

## Storage Path
ckan.storage_path = /var/lib/ckan/default/storage

## Solr Settings
solr_url = http://127.0.0.1:8983/solr/ckan

## Redis Settings
ckan.redis.url = redis://localhost:6379/0

## Plugins
ckan.plugins = stats text_view image_view webpage_view recline_view
               fluent scheming_datasets scheming_organizations scheming_groups
               pdf_view geo_view geojson_view wmts_view shp_view
               xloader spatial_metadata spatial_query
               officedocs_view bulk similar_datasets csa

## Scheming Configuration
scheming.dataset_schemas = ckanext.csa:csa_dataset.yaml
scheming.organization_schemas = ckanext.csa:csa_organization.yaml
scheming.group_schemas = ckanext.csa:csa_group.yaml
scheming.presets = ckanext.scheming:presets.json
                   ckanext.fluent:presets.json
                   ckanext.csa:presets.json

## Locales
ckan.locale_default = en
ckan.locales_offered = en fr

## XLoader Settings
ckanext.xloader.jobs_db.uri = postgresql://ckan_default:your_password_here@localhost/ckan_default

## Spatial Settings
ckanext.spatial.search_backend = solr-bbox
ckanext.spatial.common_map.type = custom
ckanext.spatial.common_map.custom_url = https://maps-cartes.services.geo.ca/server2_serveur2/rest/services/BaseMaps/CBMT_CBCT_GEOM_3857/MapServer/tile/{z}/{y}/{x}
```

### 3. Configure Solr

Create a new Solr core for CKAN:

```bash
sudo -u solr /opt/solr/bin/solr create -c ckan
```

Copy the CSA-specific Solr configuration files:

```bash
sudo cp /usr/lib/ckan/default/src/ckanext-asc-csa/my_conf/schema.xml /var/solr/data/ckan/conf/
sudo cp /usr/lib/ckan/default/src/ckanext-asc-csa/my_conf/solrconfig.xml /var/solr/data/ckan/conf/
sudo cp -r /usr/lib/ckan/default/src/ckanext-asc-csa/my_conf/lang /var/solr/data/ckan/conf/
sudo cp /usr/lib/ckan/default/src/ckanext-asc-csa/my_conf/*.txt /var/solr/data/ckan/conf/
sudo chown -R solr:solr /var/solr/data/ckan
```

Restart Solr to apply changes:

```bash
sudo systemctl restart solr
```

### 4. Initialize the CKAN Database

```bash
source /usr/lib/ckan/default/bin/activate
ckan -c /etc/ckan/default/ckan.ini db init
```

### 5. Create System Administrator

```bash
ckan -c /etc/ckan/default/ckan.ini sysadmin add admin email=admin@example.com
```


## Running CKAN

### Development Mode

```bash
source /usr/lib/ckan/default/bin/activate
ckan -c /etc/ckan/default/ckan.ini run
```

The portal will be available at `http://localhost:5000`. There are no datasets at this point.

### Background Jobs (XLoader)

In a separate terminal, start the background job worker for XLoader:

```bash
source /usr/lib/ckan/default/bin/activate
ckan -c /etc/ckan/default/ckan.ini jobs worker
```


## Post-Installation

### 1. Create an Organization

Log in as the admin user and create at least one organization before adding datasets.

### 2. Rebuild Search Index

If you have imported existing data:

```bash
source /usr/lib/ckan/default/bin/activate
ckan -c /etc/ckan/default/ckan.ini search-index rebuild
```


## Troubleshooting

### Solr Connection Issues

Verify Solr is running:

```bash
sudo systemctl status solr
curl http://localhost:8983/solr/ckan/admin/ping
```

### Database Connection Issues

Verify PostgreSQL is running and accepting connections:

```bash
sudo systemctl status postgresql
psql -U ckan_default -d ckan_default -c "SELECT 1;"
OR
psql -h localhost -U ckan_default -d ckan_default -c "SELECT 1;"
```

### Plugin Loading Errors

Check that all extensions are installed correctly:

```bash
source /usr/lib/ckan/default/bin/activate
pip list | grep ckanext
```
