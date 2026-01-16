
# Portail de données et information ouvertes de l'ASC (CKAN)  
L'objectif de ce projet était de développer et de soutenir l'évolution continue d'un portail Web pour les données et les informations de l'ASC. Il s'agit d'un élément clé de la réalisation par l'ASC de la Directive sur le gouvernement ouvert (2013), de la Feuille de route pour la science ouverte (2020), ainsi que de la Stratégie de données de l'ASC.

Vous pouvez accéder au portail en direct au https://donnees-data.asc-csa.gc.ca/fr/dataset.

Les éléments clés du portail incluent la possibilité de :
 - Faire une recherche dans le registre des jeux de données.
 - Assurer la qualité des métadonnées avec un schéma de métadonnées personnalisé et des fonctions de validation automatisées.
 - Mettre en œuvre et contrôler une stratégie de gouvernance stricte.
 - Récolter des données et des métadonnées de sources externes (y compris le portail CKAN open.canada.ca) en utilisant https://github.com/asc-csa/ckan-gov-canada-harvester-master.
 - Interagir avec le site grâce à une API robuste.
 - Explorer et analyser les données dans votre navigateur, sans avoir à télécharger les données et à utiliser un logiciel complexe. Cela rend les données beaucoup plus accessibles.

 La vision qui guide ce projet est de maximiser l'accès aux données et aux informations produites par et/ou soutenues par l'Agence spatiale canadienne.

# Introduction  
Ce projet étend le portail du "Comprehensive Knowledge Archive Network" (CKAN). Ce document décrit comment installer tout ce qui est nécessaire pour mettre en œuvre ces fonctionnalités CSA personnalisées (y compris l'installation de ckanext-asc-csa). Il devrait servir de guide de haut niveau à tous ceux qui travailleront sur le développement du portail CKAN de l'ASC.

Ce document est structuré en deux parties principales.   
 - Installation et déploiement  
 - Notes de développement    

La section "Installation et déploiement" de ce document vous guidera étape par étape sur la façon d'installer une version source de CKAN et de l'étendre avec les fonctionnalités développées par l'ASC.  

La section "Notes de développement" de ce document donne des détails sur chaque fonctionnalité CKAN développée par l'ASC.  

Un petit guide intitulé "Structures de répertoire", situé vers le bas du document, peut s'avérer utile si vous souhaitez être rapidement opérationnel.   

"Commandes utiles" peut vous aider à réaliser une série de tâches courantes qui peuvent être exécutées à partir du terminal.

#  Installation et déploiement  
Voici la section sur l'installation et le déploiement de CKAN.     


Si vous n'utilisez pas Linux actuellement, vous devrez créer une machine virtuelle à l'aide d'un logiciel tel que [VirtualBox] (https://www.virtualbox.org/). Configurez cette VM pour exécuter Ubuntu 20.04 LTS. Vous trouverez des instructions supplémentaires sur la façon de procéder [ici] (https://docs.oracle.com/cd/E26217_01/E35193/html/qs-create-vm.html).  


## Qu'est-ce que CKAN
CKAN est la première plateforme de portail de données Open Source au monde. Vous trouverez de plus amples informations sur CKAN sur leur site web :   
[ckan](https://ckan.org)(en anglais seulement)  

La documentation de CKAN peut être difficile à consulter, mais elle est globalement très bien faite. Il existe également un [gitter chat] (https://gitter.im/ckan/chat) très utile pour les développeurs de CKAN. Vous trouverez ci-dessous de la documentation sur le processus d'installation pour obtenir la version source de CKAN ainsi que les extensions qui supportent les fonctionnalités de CSA. Le processus d'installation peut prendre beaucoup de temps (4 à 6 heures), surtout si c'est la première fois que vous travaillez sur un tel projet.


## Installation de CKAN à partir du package

Adapté de [https://docs.ckan.org/en/2.9/maintaining/installing/install-from-package.html](https://docs.ckan.org/en/2.9/maintaining/installing/install-from-package.html)  

Cette section décrit comment installer CKAN à partir du package. C'est la façon la plus rapide et la plus facile d'installer CKAN, mais elle nécessite Ubuntu 18.04 (Python 2) ou 20.04 (Python 3 ou Python 2) 64 bits. Si vous n'utilisez pas l'une de ces versions d'Ubuntu, ou si vous installez CKAN pour le développement, vous devriez plutôt suivre Installer CKAN à partir des sources.

À la fin du processus d'installation, vous vous retrouverez avec deux applications web en cours d'exécution, CKAN lui-même et le DataPusher, un service distinct pour l'importation automatique de données dans l'extension DataStore de CKAN. En outre, il y aura un processus exécutant le worker pour l'exécution des travaux en arrière-plan. Tous ces processus seront gérés par Supervisor.

Pour les installations Python 3, la version minimale de Python requise est 3.6.

* Ubuntu 20.04 inclut Python 3.8 dans sa distribution.
* Ubuntu 18.04 inclut Python 3.6 dans sa distribution.

Exigences des ports hôtes :

|Service  |Port  |Utilisé pour
|:--|:--|:--|
|NGINX	|80	|Proxy
|uWSGI	|8080	|Serveur web
|uWSGI	|8801	|DataPusher
|Solr/Jetty	|8983	|Recherche
|PostgreSQL	|5432	|Base de données
|CKAN	|5000	|Application web
|Redis	|6379	|Recherche

###  1. Installer le package CKAN
Sur votre système Ubuntu, ouvrez un terminal et exécutez ces commandes pour installer CKAN :

1.  Mise à jour de l'index des packages d'Ubuntu :

	```
    sudo apt update
	```
2.  Installez les packages Ubuntu dont CKAN a besoin (et 'git', pour vous permettre d'installer les extensions CKAN) :
	```
	sudo apt install -y libpq5 redis-server nginx supervisor
	```

3.  Téléchargez le package CKAN :

	Sur Ubuntu 20.04, pour Python 3 (recommandé) :
	```
	wget https://packaging.ckan.org/python-ckan_2.9-py3-focal_amd64.deb
	```  

4.  Téléchargez ce package additionnel dont CKAN a besoin :

	```
	sudo apt-get install python3-disutils
	```

5.  Installez le package CKAN :

     Sur Ubuntu 20.04, pour Python 3 (recommandé) :
     ```
     sudo dpkg -i python-ckan_2.9-py3-focal_amd64.deb
     ```

###  2. Installer et configurer PostgreSQL
Installez PostgreSQL, en exécutant cette commande dans un terminal :
```
sudo apt install -y postgresql
```
Si vous rencontrez un problème dans le cas où PostgreSQL n'est pas en cours d'exécution, exécutez la commande :

```
sudo  service  postgresql  start
```
Vérifiez que PostgreSQL a été installé correctement en regardant les bases de données existantes :
```
sudo -u postgres psql -l
```
Vérifiez que l'encodage des bases de données est `UTF8`, sinon vous pourriez rencontrer des problèmes plus tard avec l'internationalisation. Comme le changement de l'encodage de PostgreSQL peut signifier la suppression de bases de données existantes, il est suggéré que cela soit corrigé avant de continuer l'installation de CKAN.

Ensuite, vous devrez créer un utilisateur de base de données s'il n'en existe pas déjà un. Créez un nouvel utilisateur PostgreSQL appelé ckan_default, et entrez un mot de passe pour l'utilisateur lorsque vous y êtes invité. Vous aurez besoin de ce mot de passe plus tard. Pour ce guide, nous utiliserons le mot de passe 'Alouette1CSA' :
```
sudo -u postgres createuser -S -D -R -P ckan_default
```
Créez une nouvelle base de données PostgreSQL, appelée ckan_default, appartenant à l'utilisateur de base de données que vous venez de créer :
```
sudo -u postgres createdb -O ckan_default ckan_default -E utf-8
```
Modifier l'option [sqlalchemy.url](https://docs.ckan.org/en/2.9/maintaining/configuration.html#sqlalchemy-url) dans votre [fichier de configuration CKAN ](https://docs.ckan.org/en/2.9/maintaining/configuration.html#config-file) (/etc/ckan/default/ckan.ini) et définir le mot de passe, la base de données et l'utilisateur de la base de données.
```
sqlalchemy.url = postgresql://ckan_default:Alouette1CSA@localhost/ckan_default
```

###  3. Installer et configurer Solr
Installez Solr, en exécutant cette commande dans un terminal :
```
sudo apt install -y solr-tomcat
```
CKAN utilise [Solr](https://lucene.apache.org/solr/) et utilise un fichier de schéma Solr personnalisé qui prend en compte les besoins de recherche spécifiques de CKAN. Maintenant que nous avons installé CKAN, nous devons installer et configurer Solr.

Changez le port par défaut sur lequel Tomcat fonctionne (8080) pour celui attendu par CKAN. Pour ce faire, changez la ligne suivante dans le fichier `/etc/tomcat9/server.xml` (`tomcat8` dans les anciennes versions d'Ubuntu) :

De:
```
<Connector port="8080" protocol="HTTP/1.1"
```
A:
```
<Connector port="8983" protocol="HTTP/1.1"
```
1.  Remplacer le fichier défaut `schema.xml` par un lien symbolique vers le fichier de schéma CKAN inclus dans les sources.
    ```
    sudo mv /etc/solr/conf/schema.xml /etc/solr/conf/schema.xml.bak
    sudo ln -s /usr/lib/ckan/default/src/ckan/ckan/config/solr/schema.xml /etc/solr/conf/schema.xml
    ```

2. Maintenant, redémarrez Solr (utilisez `tomcat8` sur les anciennes versions d'Ubuntu) :
    ```
    sudo service tomcat9 restart
    ```
3.  Vérifiez que Solr est en cours d'exécution au [http://localhost:8983/solr/](http://localhost:8983/solr/)
4.  Enfin, modifiez le paramètre [solr_url](https://docs.ckan.org/en/2.9/maintaining/configuration.html#solr-url) dans votre [fichier de configuration CKAN](https://docs.ckan.org/en/2.9/maintaining/configuration.html#config-file)  (/etc/ckan/default/ckan.ini) pour pointer vers votre serveur Solr, par exemple :
	```    
	solr_url=http://127.0.0.1:8983/solr
	```
###  4. Installer CKAN dans un environnement virtuel Python
1.  Modifier le [fichier de configuration CKAN](https://docs.ckan.org/en/2.9/maintaining/configuration.html#config-file)  (/etc/ckan/default/ckan.ini) de la manière suivante :

	**site_id**
    Chaque site CKAN devrait avoir  `site_id` unique. Si vous n'en avez qu'une, utiliser :
    > ckan.site_id = default

    **site_url**
    Indiquez l'URL du site. Par exemple :
    >
    > ckan.site_url = http://localhost:5000

	Mais utilisez ce que vous prévoyez d'utiliser pour votre environnement de production ou de développement.

2.  Initialisez votre base de données CKAN en exécutant cette commande dans un terminal :

    >sudo ckan db init
###  5. Démarrez le serveur Web et redémarrez Nginx
Relancez le daemon Supervisor pour que les nouveaux processus soient pris en compte :

>sudo supervisorctl reload

Après quelques secondes, exécutez la commande suivante pour vérifier l'état des processus :

>sudo supervisorctl status

Vous devriez voir trois processus s'exécuter sans erreur :
```
ckan-datapusher:ckan-datapusher-00   RUNNING   pid 1963, uptime 0:00:12
ckan-uwsgi:ckan-uwsgi-00             RUNNING   pid 1964, uptime 0:00:12
ckan-worker:ckan-worker-00           RUNNING   pid 1965, uptime 0:00:12
```
Si l'un des processus rapporte une erreur, assurez-vous d'avoir exécuté toutes les étapes précédentes et vérifiez les journaux situés dans `/var/log/ckan` pour plus de détails.

Relancer Nginx en exécutant cette commande :

>sudo service nginx restart

Lancer l'environnement virtuel en exécutant cette commande :

>. /usr/lib/ckan/default/bin/activate

Puis, lancer CKAN en exécutant cette commande : 

>ckan -c /etc/ckan/default/ckan.ini run

Vous pouvez maintenant tester l'installation en allant sur [http://localhost:5000](http://localhost:5000/), s'il affiche CKAN vous avez tout fait correctement jusqu'à ce point.

###  6. DataStore et DataPusher  
#### 1. Activer le plugin[](https://docs.ckan.org/en/2.9/maintaining/datastore.html#enable-the-plugin "Permalink to this headline")

Ajouter le plugin `datastore`  a votre fichier config pour CKAN (laissez les autres plugins, ajoutez datastore à la fin):
```
ckan.plugins = datastore
```
#### 2. Configurer la base de données
*Assurez-vous que vous suivez correctement les étapes de [Set Permissions] (https://docs.ckan.org/en/2.9/maintaining/datastore.html#set-permissions) ci-dessous. Des paramètres incorrects peuvent entraîner de graves problèmes de sécurité.*

Le DataStore nécessite une base de données PostgreSQL séparée pour y enregistrer les ressources du DataStore.

Liste des bases de données existantes :

>sudo -u postgres psql -l

Vérifiez que l'encodage des bases de données est `UTF8`, sinon l'internationalisation peut être un problème. Puisque changer l'encodage de PostgreSQL peut signifier supprimer des bases de données existantes, il est suggéré que cela soit corrigé avant de continuer avec la configuration du datastore.

#### Créer des utilisateurs et les bases de données
Créez un utilisateur de base de données appelé datastore_default. Cet utilisateur recevra seulement un accès de lecture à votre base de données DataStore dans l'étape [Set Permissions](https://docs.ckan.org/en/2.9/maintaining/datastore.html#set-permissions) ci-dessous, lorsque vous êtes invité à saisir un mot de passe, entrez 'Canada1Alouette' :

>sudo -u postgres createuser -S -D -R -P -l datastore_default

Créer la base de données (appartenant à ckan_default), que nous appellerons datastore_default :

>sudo -u postgres createdb -O ckan_default datastore_default -E utf-8

#### Définir les URL
Maintenant, décommentez  les lignes [ckan.datastore.write_url](https://docs.ckan.org/en/2.9/maintaining/configuration.html#ckan-datastore-write-url)  et [ckan.datastore.read_url](https://docs.ckan.org/en/2.9/maintaining/configuration.html#ckan-datastore-read-url)  dans votre fichier de config CKAN. Modifiez-les si nécessaire, par exemple :

>ckan.datastore.write_url = postgresql://ckan_default:Alouette1CSA@localhost/datastore_default
>ckan.datastore.read_url = postgresql://datastore_default:Canada1Alouette@localhost/datastore_default

Si vous n'avez pas utilisé les mots de passe recommandés, remplacez `Alouette1CSA` et `Canada1Alouette` par les mots de passe que vous avez utilisés.

#### Définir les autorisations
Une fois que la base de données DataStore et les utilisateurs sont créés, les permissions sur la base de données DataStore et CKAN doivent être définies. CKAN fournit une commande ckan pour vous aider à définir correctement ces permissions.

Si vous êtes capable d'utiliser la commande `psql` pour vous connecter à votre base de données en tant que super-utilisateur, vous pouvez utiliser la commande `datastore set-permissions` pour émettre le SQL approprié pour définir les permissions.

Par exemple, si vous pouvez vous connecter à votre serveur de base de données en tant que superutilisateur `postgres` en utilisant :

>sudo -u postgres psql

Vous pouvez ensuite utiliser cette connexion pour définir les autorisations :

> ckan -c /etc/ckan/default/ckan.ini datastore set-permissions | sudo -u postgres psql --set ON_ERROR_STOP=1

**Note:**
Si vous avez effectué une installation par package, vous devrez remplacer toutes les références à 'ckan -c /etc/ckan/default/ckan.ini ...' par 'sudo ckan ...' et fournir le chemin vers le fichier de configuration, par exemple :

>sudo ckan datastore set-permissions | sudo -u postgres psql --set ON_ERROR_STOP=1

Si vous ne pouvez pas utiliser la commande `psql` de cette manière, vous pouvez simplement copier et coller la sortie de :

> ckan -c /etc/ckan/default/ckan.ini datastore set-permissions

dans une console de super-utilisateur PostgreSQL.
### 3. Testez l'installation
(https://docs.ckan.org/en/2.9/maintaining/datastore.html#test-the-set-up "Permalink to this headline")

Le DataStore est maintenant configuré. Pour tester la configuration (re)lancez CKAN et exécutez la commande suivante pour lister toutes les ressources du DataStore :
>curl -X GET "http://127.0.0.1:5000/api/3/action/datastore_search?resource_id=_table_metadata"

Ceci devrait retourner une page JSON sans erreur.

Pour tester si la configuration permet l'écriture, vous pouvez créer une nouvelle ressource DataStore. Pour ce faire, exécutez la commande suivante :

>curl -X POST http://127.0.0.1:5000/api/3/action/datastore_create -H "Authorization: {YOUR-API-KEY}" -d '{"resource": {"package_id": "{PACKAGE-ID}"}, "fields": [ {"id": "a"}, {"id": "b"} ], "records": [ { "a": 1, "b": "xyz"}, {"a": 2, "b": "zzz"} ]}'

Remplacer `{YOUR-API-KEY}`  avex une une clé API valide et  `{PACKAGE-ID}`  avec l'id d'un jeu de données CKAN existant.

Une table portant le nom de l'identifiant de la ressource doit avoir été créée dans votre base de données DataStore. La visite de cette URL devrait renvoyer une réponse du DataStore avec les enregistrements insérés ci-dessus :

>http://127.0.0.1:5000/api/3/action/datastore_search?resource_id={RESOURCE_ID}

Remplacez `{RESOURCE-ID}` par l'identifiant de la ressource qui a été renvoyé dans la réponse de l'appel d'API précédent.

Vous pouvez maintenant supprimer la table DataStore avec

>curl -X POST http://127.0.0.1:5000/api/3/action/datastore_delete -H "Authorization: {YOUR-API-KEY}" -d '{"resource_id": "{RESOURCE-ID}"}'

Pour en savoir plus sur l'API du DataStore, voir [The DataStore API](https://docs.ckan.org/en/2.9/maintaining/datastore.html#the-datastore-api).

##  Extension de CKAN avec des fonctionnalités CSA
Les sections ci-dessus ont configuré une version vanille de CKAN avec le datastore et le datapusher. Pour étendre CKAN afin de contenir les fonctionnalités développées pour l'ASC, suivez les étapes ci-dessous.   

###  1. Installation des extensions  
Pour installer les extensions Scheming, Fluent et CSA, vous aurez besoin de git pour cloner les fichiers nécessaires dans le répertoire des extensions CKAN. Git devrait avoir été installé dans les étapes précédentes. Si le serveur CKAN est en cours d'exécution, éteignez le serveur avec `CTRL C`.  

Avant de commencer, assurez-vous que l'environnement virtuel python fourni avec CKAN est en cours d'exécution.
```
. /usr/lib/ckan/default/bin/activate
```
Maintenant, naviguez vers le répertoire d'extension de CKAN   
```  
cd /usr/lib/ckan/default/src  
```  
Clonez le projet ckanext-asc-csa-scheming dans ce répertoire :  
  ```  
 git clone https://github.com/asc-csa/ckanext-asc-csa-scheming  
 ```  
Clonez le projet fluent dans ce répertoire :  
  ```  
 git clone https://github.com/ckan/ckanext-fluent.git
 ```  
Clonez le projet ckanext-asc-csa dans ce répertoire :  
 ```   
git clone https://github.com/asc-csa/ckanext-asc-csa
```  

Dans le fichier de configuration de CKAN (`/etc/ckan/default/ckan.ini`) éditez pour inclure ces paramètres. Certains de ces paramètres existent déjà, d'autres non et doivent être ajoutés. Assurez-vous que les paramètres sont au-dessus des paramètres de configuration de la journalisation/logging ou ils ne seront pas analysés.  

```  
ckan.plugins = stats text_view image_view recline_view csa scheming_datasets fluent datastore  

## Scheming Settings  

scheming.dataset_schemas = ckanext.scheming:ckan_dataset.json  
 ckanext.csa:info.json ckanext.csa:doc.json  
scheming.presets = ckanext.scheming:presets.json  
 ckanext.fluent:presets.json  
licenses_group_url = file:///usr/lib/ckan/default/src/ckanext-asc-csa/ckanext/csa/public/licenses.json

ckan.locale_default = en  
ckan.locale_order = en fr  
ckan.locales_offered = en fr  
```  

Avant de continuer, vous devez construire chaque extension. Vous devriez être dans le répertoire ckan src, sinon exécutez :  
```
cd /usr/lib/ckan/default/src  
```
Entrez dans chaque répertoire d'extension et construisez l'extension   
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
###  2. Modifier le fichier `schema.xml` pour une recherche CKAN personnalisée   
Copiez le contenu du fichier `schema.xml` de l'extension CSA dans le fichier `schema.xml` original.
```  
cp /usr/lib/ckan/default/src/ckanext-asc-csa/misc/schema.xml /usr/lib/ckan/default/src/ckan/ckan/config/solr/schema.xml  
```  
Vous pouvez aussi le faire manuellement en copiant et collant le contenu du fichier `schema.xml` de ckanext-asc-csa dans l'emplacement spécifié ci-dessus.   

Relancez Jetty après avoir modifié le fichier `schema.xml`.

Pour Ubuntu 20.04:  
```
sudo service nginx restart  
```
3. Testez les extensions
Redémarrez le serveur CKAN et accédez au site à partir d'un navigateur. Les fonctionnalités CSA devraient maintenant être présentes sur la page.   
```  
sudo supervisorctl stop all  
```  

## Configuration de votre installation

Vous allez maintenant vouloir créer un utilisateur sysadmin et éventuellement importer des organisations pour faciliter votre travail. Cette section est facultative, mais vous guidera dans ce processus.

```
ckan -c /etc/ckan/default/ckan.ini sysadmin add seanh email=seanh@localhost name=seanh
```
où seanh sera remplacé par votre nom d'utilisateur. Vous pouvez trouver plus d'instructions sur
https://docs.ckan.org/en/2.9/maintaining/getting-started.html#create-admin-user

Une fois fait, vous devrez copier manuellement le fichier misc/transitional_orgs.json de l'extension ckanext-csa dans le répertoire contenant le fichier ckan.ini. Une fois dans ce répertoire, ouvrez une invite de commande et utilisez les commandes suivantes :
```  
. /usr/lib/ckan/default/bin/activate  
ckanapi load organizations -I misc/transitional_orgs.jsonl
```  


Dans ckan.ini file, ajoutez
```
ckan.storage_path = /var/lib/ckan/default
```
et exécutez les commandes (désuet - ce n'est pas obligatoire)
```
paster --plugin=ckan datastore set-permissions -c /etc/ckan/default/ckan.ini
```

### Remplacement de fichiers de base
Quelques fonctionnalités ont dû être modifiées pour répondre aux exigences d'accessibilité et de traduction. Il n'y avait pas de moyen clair de faire ces changements sans avoir besoin de modifier 2 fichiers du project CKAN de base. Vous devrez remplacer ces 2 fichiers par les fichiers modifiés :
 - pagination.py
   - Dans le dossier `ckan/lib` dans `ckanext-asc-csa extension` copier `pagination.py` dans `/usr/lib/ckan/default/src/ckan/ckan/lib/`
 - reline.js
   - Dans le dossier `reclinejs` dans `ckanext-asc-csa extension` copier `recline.js` dans `/usr/lib/ckan/default/src/ckan/ckanext/reclineview/theme/public/vendor/recline/`


### Configuration du Datapusher

Le datapusher n'a pas besoin d'être modifié car il fonctionne avec ckan et non à l'intérieur. Vous pouvez suivre les étapes sur la page github du projet pour cette étape. https://github.com/ckan/datapusher

*Note : c'est une bonne idée d'installer datapusher dans un environnement (virtuel ou autre) différent de celui que vous avez utilisé pour CKAN. Cela est dû au fait qu'ils nécessitent des versions différentes de diverses bibliothèques python. Si vous installez les exigences de datapusher dans votre répertoire CKAN, vous allez probablement casser temporairement votre installation CKAN. Si c'est le cas, ne vous inquiétez pas, la solution est simple. Réinstallez simplement votre CKAN requirements.txt dans cet environnement virtuel et redémarrez le processus d'installation de datapusher dans un autre environnement.

##  Déploiement d'une installation source   
Après avoir installé la source, suivez ce guide pour la déployer sur un serveur de production.   
[https://docs.ckan.org/en/2.9/maintaining/installing/deployment.html](https://docs.ckan.org/en/2.9/maintaining/installing/deployment.html)  

Notes:  

Les fichiers journaux d'Apache se trouvent dans var/log/apache2.  
Il y a eu des erreurs de permission refusée sur /tmp/default/sessions à partir du wsgi. Une solution temporaire est d'exécuter la commande :    
```
sudo chmod -R 777 /tmp  
```
#  Notes de développement  

## Introduction aux notes de développement    

Ci-dessus était un guide pour installer CKAN, ci-dessous sont les notes que j'ai prises pour communiquer les étapes qui ont été franchies jusqu'à présent.  

## Structure du répertoire et fichiers spécifiques de ckanext-asc-csa
 - /installation guide - contiens ce document dans sa version la plus récente
 - /ckanext/csa - contient la plupart du code qui ajoute les fonctionnalités ASC à CKAN.
 - /ckanext/csa/templates - contient la plupart du code qui traite de ce qui est affiché sur le front-end en termes de html.
 - /ckanext/csa/fanstatic - contient les fichiers css et js qui sont personnalisés et ajoutés en plus de ce que CKAN fournit par défaut.
 - /ckanext/csa/plugin.py - contient le plugin qui utilise [CKAN's plugin interface](https://docs.ckan.org/en/2.8/extensions/plugin-interfaces.html) pour personnaliser et étendre to [étendre les fonctionnalités](https://docs.ckan.org/en/2.8/extensions/tutorial.html)
 - /ckanext/csa/public - contient des fichiers accessibles au public qui peuvent être affichés de manière statique. Il contient notamment le favicon, le logo et le fichier licenses.json.
 - /misc/schema.xml - contient le schéma modifié qui implémente la recherche bilingue et la recherche à facettes
 -

##  Harvesters  
La collecte de données à partir d'autres sources est une partie importante de la mise en œuvre du CKAN par l'ASC. Actuellement, le CKAN de l'ASC a des scripts écrits pour récolter des données de DIIDS (Data and Information Inventory and Disclosure System) et du [Portail de données ouvertes du gouvernement du Canada] (https://open.canada.ca/en/open-data).  

Lors d'une nouvelle installation de CKAN, ces moissonneurs doivent être utilisés pour alimenter les jeux de données avec des jeux de données provenant de DIIDS et des données ouvertes du gouvernement du Canada.  

Les scripts de moissonnage auront besoin d'une clé API trouvée dans un compte administrateur sur la page du compte utilisateur CKAN. L'adresse IP de l'instance CKAN doit également être incluse dans ces scripts. Par défaut, l'adresse IP incluse dans les scripts devrait fonctionner avec l'installation de développement de CKAN.  


###  Récolte de données à partir des données ouvertes du gouvernement du Canada  

https://github.com/asc-csa/ckan-gov-canada-harvester-master


###  Récolte de données à partir de DIIDS (interne seulement)
La récolte des données de DIIDS peut se faire à partir d'un ordinateur/serveur externe. Cela se fait par le biais de requêtes HTTP API. C'est assez similaire au moissonneur du gouvernement du Canada, mais au lieu de prendre les fichiers à partir d'une requête GET, il prend les données à partir d'un fichier csv source téléchargé à partir de DIIDS. Veuillez consulter la section "Problèmes d'Unicode" de ce document pour vous assurer que le CSV est dans le bon format. Cela inclut l'enregistrement sous dans le bloc-notes en UTF-8. Jetez un coup d'œil à cette section ci-dessous.  

La création d'ensembles de données avec DIIDS peut échouer avec cette extension dans son état actuel en raison des nouveaux validateurs qui ont été mis sur les formulaires. En particulier, il y a certains champs qui sont requis et qui ne seraient pas trouvés dans DIIDS mais seulement dans le portail de données ouvertes du gouvernement du Canada. Cela n'a pas été traité plus tôt parce qu'il n'y avait aucun moyen de savoir quels champs seraient nécessaires plus tard, il était donc plus facile de tout garder en l'état avant que quelqu'un avec la connaissance du domaine ne rédige un guide sur les champs de métadonnées à utiliser.  

Git clonez ce fichier et suivez le readme pour les instructions.  
[https://gccode.ssc-spc.gc.ca/csa-data-centre-of-expertise/ckan-didds-harvester](https://gccode.ssc-spc.gc.ca/csa-data-centre-of-expertise/ckan-didds-harvester)  


##  Intégration avec d'autres plateformes (Query for Data)
L'interrogation de CKAN à partir d'autres applications peut se faire de deux manières différentes. La première et la plus simple est de faire une demande de téléchargement d'url comme ci-dessous :   
https://stackabuse.com/download-files-with-python/  

L'autre option serait d'utiliser l'API de CKAN pour les données tabulaires. La référence API pour le datastore peut être trouvée en ligne à ce lien :   
https://docs.ckan.org/en/2.8/maintaining/datastore.html#the-datastore-api  

Bien qu'il puisse y avoir quelques limitations avec l'API de la base de données, notamment lorsqu'on essaie d'interroger des dizaines de milliers de lignes. Après discussion, pour les applications autonomes telles que les visualisations de satellites individuels, il peut être préférable de simplement télécharger/cacher le fichier sur le serveur/machine qui exécute l'application.   


## Facets bilingues
Les facets sont contrôlés par ckanext-asc-csa en utilisant l'interface IFacets dans plugins.py. Ici facets_dict est mis à jour pour inclure plus de facettes. En plus de la mise à jour de l'interface, plusieurs modèles ont dû être créés pour tenir compte des versions française et anglaise de chacune des valeurs des facettes. Le principal problème était que la facette affichait la valeur au lieu de l'étiquette localisée pour chaque sélection. Ce problème a été résolu en personnalisant les modèles pour afficher l'étiquette de la langue correcte à l'utilisateur du site web. Les modèles peuvent être trouvés dans ce dépôt (ckanext-asc-csa).  


Ces modèles ont été créés pour accomplir cette tâche :   
 - ckanext/csa/templates/package/search.html
 - ckanext/csa/templates/snippets/facet_list.html  
 - ckanext/csa/templates/snippets/dataset_facets.html  
 - ckanext/csa/templates/macros/csa_read.html  

Outre l'édition des modèles, pour le sujet et les mots-clés, il s'agissait d'un cas particulier car ceux-ci sont multivalués et contiennent également des versions française et anglaise. Pour résoudre ce problème, il fallait d'abord configurer l'interface before_index dans le cadre de l'interface IPackageController    
```  
def before_index(self, pkg_dict):  
 kw = json.loads(pkg_dict.get('extras_keywords', '{}')) pkg_dict['keywords_en'] = kw.get('en', []) pkg_dict['keywords_fr'] = kw.get('fr', []) pkg_dict['subject'] = json.loads(pkg_dict.get('subject', '[]')) return pkg_dict
```  

Après avoir défini une fonction before_index pour modifier le dictionnaire de l'ensemble de données/package avant l'indexation par le SOLR, j'ai spécifié manuellement un champ multivalué dans schema.xml   
```
<field name= "keywords_en" type="string" indexed="true" stored="true" multiValued="true"/>  
<field name= "keywords_fr" type="string" indexed="true" stored="true" multiValued="true"/>  
<field name="subject" type="string" indexed="true" stored="true" multiValued="true"/>  
```  
Une fois modifié, le serveur SOLR doit être réindexé manuellement à partir de l'environnement virtuel où CKAN est installé.  


`ckan -c /etc/ckan/default/ckan.ini search-index rebuild`

Les facettes pour la page de l'organisation n'ont pas été complètement intégrées à la nouvelle fonctionnalité des facettes parce que cette page devrait être supprimée car la structure de l'organisation devrait être abstraite pour l'utilisateur. Si ce n'est pas le cas, les facettes peuvent être mises en œuvre en modifiant les fichiers de modèle pour rendre les valeurs spécifiques à la langue.   


## Affichage des métadonnées bilingues sur la page de recherche   
Il s'agissait d'une correction simple, réalisée en créant snippets/package_item.html et en créant quelques fonctions d'aide dans helpers.py pour afficher la version correcte du texte en appelant h.lang().


## Traduction de strings internationalisés  
Pour traduire les chaînes de l'interface utilisateur, vous devez d'abord marquer la chaîne comme étant traduisible dans le code Python ou Jinja. Ensuite, vous devez créer un fichier .po personnalisé avec ces traductions manuelles. CKAN fournit un [excellent guide] (https://docs.ckan.org/en/2.8/extensions/translating-extensions.html) pour mettre en œuvre cette procédure. Les traductions des chaînes de l'anglais au français proviennent de GC Canada, situé [ici](https://github.com/open-data/ckanext-canada/blob/master/ckanext/canada/i18n/fr/LC_MESSAGES/canada.po).  


##  Moteur de recherche bilingue    
Après avoir personnalisé les champs pour inclure le support du français et de l'anglais, la recherche de contenu ne fonctionnait pas comme prévu. Les recherches simples de titres entiers n'affichaient aucun ensemble de données.   

J'ai contacté Ian Ward (membre de l'équipe de développement de CKAN et fonctionnaire du GC) pour lui demander des conseils sur la façon de résoudre ce problème. Sa réponse est ci-dessous.  
Notes de Ian Ward :  

> You'll need a solr schema with en/fr text fields and a bunch of  
> copyFields for each field in your schema kind of like  
> https://github.com/open-data/ogc_search/blob/master/ogc_search/open_data/solr/schema.xml#L572 (NB: this is not a ckan schema so you won't be able to use it  
> directly) and a before_index that stores all language text separately  
> so it can be picked up by these copyFields then you need to override  
> ckan's search so it will use the correct field for search based on the  
> user's language Bonus point for doing this in a reusable way that  
> could be incorporated into ckan/scheming themselves. That's always  
> harder than hacking something together quickly of course  

Le moteur de recherche CKAN utilise [SOLR] (https://lucene.apache.org/solr/guide/6_6/index.html) pour la recherche de contenu. Le fichier "schema.xml" spécifie les paramètres du schéma de recherche. Il peut être trouvé dans ce chemin "/usr/lib/ckan/default/src/ckan/ckan/config/solr/schema.xml". Une copie modifiée qui inclut les changements est incluse dans ckanext-asc-csa. Il a d'abord été bon d'apprendre comment fonctionne une recherche solr ([Analyseurs, Tokenizers, et Filtres](https://lucene.apache.org/solr/guide/6_6/understanding-analyzers-tokenizers-and-filters.html)).   

La logique de recherche des paquets CKAN peut être trouvée sur [github](https://github.com/ckan/ckan/blob/master/ckan/logic/action/get.py#L1705).  

Pour remédier à la recherche, j'ai défini un nouveau type de champ dans schema.xml qui utilise un traitement spécial sur le texte français.

Après avoir défini le nouveau champ, j'ai modifié mon before_index pour extraire de pkg_dict les termes que je voulais inclure dans l'index de recherche, dans ce cas, notes_fr, title_fr. Ensuite, j'ai ajouté le champ multivalué res_name_fr. J'ai dû analyser le code source de CKAN pour déterminer où la requête était exécutée. Le code pour cela peut être trouvé [ici] (https://github.com/ckan/ckan/blob/master/ckan/lib/search/query.py#L253). Pour déboguer le code, j'ai ajouté quelques instructions d'impression qui sont incluses dans cet extrait de code.   
```  
 conn = make_connection(decode_dates=False) log.debug('Package query: %r' % query) print query try: solr_response = conn.search(**query) for result in solr_response: print result
```  
CKAN utilise une bibliothèque appelée [pysolr] (https://github.com/django-haystack/pysolr) pour s'interfacer avec Solr. Il était utile de jeter un coup d'œil à la documentation sur la façon dont CKAN effectue une requête.  

Après avoir pu visualiser la requête, j'ai réalisé que je devais modifier le paramètre de recherche "qf" pour spécifier que je voulais donner plus de poids aux champs français lors de la recherche lorsque CKAN est réglé sur le français. CKAN utilise DisMax pour effectuer des recherches. La documentation à ce sujet se trouve [ici] (https://lucene.apache.org/solr/guide/6_6/the-dismax-query-parser.html#TheDisMaxQueryParser-Theqf_QueryFields_Parameter). Ce lien vous aidera également à comprendre ce que fait 'qf'.  

**Note importante : lors du développement de la recherche, vous devez redémarrer le serveur SOLR et réindexer les paquets actuels. Vous trouverez la marche à suivre dans les commandes terminales de la section Conseils et astuces de ce document.  


# Authors  
- Cooper Ang - Développement initial du CSA CKAN au cours d'un stage de 4 mois
- Jenisha Patel - Lancement du projet CSA CKAN dans le cadre d'un projet pilote d'une semaine.
- Patrick Baral - Dans le cadre d'un stage de 4 mois
- Jonathan Beaulieu-Emond - Dans le cadre d'un stage de 3 mois
- Natasha Fee - Scientifique des données au CED
- Agence spatiale canadienne (Centre d’expertise en données) - Support du projet avec des ressources

# Remerciements  
- Étienne Low-Décarie - Supervisor of project
- Wasiq Mohammad - Mentorat technique
