
-----------------
Portail des données ouvertes - Rapport des gestionnaires de données (English follows)
-----------------

Ce répertoire contient les scripts Python requis pour dresser la liste des gestionnaires de données et pour les modifier au besoin.

=============
Prérequis
=============

Vous avez besoin d'un environnement Python pour exécuter les scripts sur votre ordinateur tel que Spyder ou PyCharm. Aucune version spécifique n'est requise.

=============
Exécution
=============

Veuillez suivre les étapes suivantes pour obtenir la liste des gestionnaires de données :

1. Ouvrez le fichier data_steward.py. Définissez la constante EMAIL_DOMAIN.

2. Ouvrez le fichier email_message.py. Définissez les constantes SMTP_DOMAIN, PORT_NUMBER et FROM_ADDRESS.

3. Ouvrez le fichier main_reporting.py.

4. Exécutez main_reporting.py dans votre environnement de développement (Spyder ou PyCharm).

5. Suivez le résultat de l'exécution. Le script génère un fichier Excel.

6. Ouvrez le fichier Excel produit. Il contient tous les ensembles de données du portail des données ouvertes.

Suivez ces étapes pour mettre à jour les gestionnaires de données :

ATTENTION : Soyez vigilant avant d'exécuter cette partie. Cela modifie le portail des données ouvertes.

1. Ouvrez update_data_steward.py. Définissez API_KEY avec votre propre clé. Vous ne pouvez pas mettre à jour le portail si vous n'en avez pas.

2. Exécutez update_data_steward.py dans votre environnement de développement (Spyder ou PyCharm).

3. Suivez le résultat de l'exécution. Le script met à jour le portail Open Data.




------------
Open Data Portal - Reporting Data Stewards (le français précède)
------------

This folder contains the Python scripts required to list the data stewards and to modify them if required.

=============
Requirements
=============

You need Python environment to execute the scripts on your computer such as Spyder or PyCharm. No specific version of Python is required.

=============
Execution
=============

Follow these steps to get the list of data stewards:

1. Open data_steward.py. Set the EMAIL_DOMAIN.

2. Open email_message.py. Set the SMTP_DOMAIN, PORT_NUMBER and FROM_ADDRESS.

3. Open main_reporting.py.

4. Execute main_reporting.py in your development environment (e.g. Spyder or PyCharm).

5. Follow the output of the execution. The script outputs an Excel spreadsheet.

6. Open the spreadsheet. It contains all the datasets of the Open Data Portal.


Follow these steps to update the data stewards:

WARMING: Be careful before running this part. It updates the Open Data Portal.

1. Open update_data_steward.py. Set the API_KEY with your own key. You cannot update the portal if you do not have one.

2. Execute update_data_steward.py in your development environment (e.g. Spyder or PyCharm).

3. Follow the output of the execution. The script updates the Open Data Portal.
