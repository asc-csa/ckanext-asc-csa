# This class represents email.
# Open Data Portal
#
# @author Emiline Filion - Canadian Space Agency
#

import smtplib
from email.message import EmailMessage


# Constants
SMTP_DOMAIN = 'smtp.com'
PORT_NUMBER = 21
FROM_ADDRESS = 'no-reply@gmail.com'


class email_message:
    
    # Constructor.
    # @param to - to email address.
    # @param cc - cc email address.
    # @param subject - Subject of the email.
    def __init__(self, to, cc, subject):
        
        self.to_address = to
        self.cc_address = cc
        self.subject = subject
    
    # Generates the body of the email.
    # @param person_name - Name of the person.
    # @param nb_datasets - Number of datasets.
    # @param array_datasets - List of datasets.
    # @param array_dataset_ids - IDs of the datasets
    # @return Body of the email.
    def generate_body(self, person_name, nb_datasets, array_datasets, array_dataset_ids):
        
        # Extract the first name
        idx = person_name.find(' ')
        first_name = person_name[0: idx]
        
        # Split the datasets
        msg_datasets = ''
        idx = 0
        for edataset in array_datasets:
            msg_datasets += '<li><a href="https://donnees-data.asc-csa.gc.ca/dataset/' + array_dataset_ids[idx] +'">' + edataset + '</a></li>'
            idx += 1
        
        # Build the body
        return '<p>Bonjour ' + first_name + ',</p><i><small>[English follows]</small></i><br>Selon nos données du portail des données ouvertes, vous êtes l\'intendant des jeux de données suivants:<br><br><ul>' + msg_datasets + '</ul><p>Pouvez-vous confirmer que vous continuez d\'être la personne ressource pour les ensembles de données mentionnés ci-dessus? Si vous n\'êtes plus l\'intendant des ensembles de données ci-dessus, veuillez nous référer à la nouvelle personne ressource.<p>Bien à vous,<br><br><b>Équipe des données et technologies émergentes, GI-TI<br>Centre d’expertise en numérique</b><br><center>__________________________________________________________</center><p>Hi ' + first_name + ',</p><i><small>[Le français précède]</small></i><br>According to our records on the Open Data Portal, you are one of the data stewards for the following datasets:<br><br><ul>' + msg_datasets + '</ul><p>We are reaching out to ask if you could confirm that you continue to be the main contact person for the aforementioned datasets. If you are no longer the data steward of the datasets above, please refer us to the new contact person.<p>Regards,<br><br><b>Data and Emerging Technologies Team, IM-IT<br>Digital Centre of Expertise</b>'
    
    # Sends the email.
    # @param body - Body of the email.
    def send_email(self, body):
        
        # Create a text/plain message
        print('Email ' + self.to_address + '...')
        msg = EmailMessage()
        msg.set_content(body, subtype='html')
        msg['Subject'] = self.subject
        msg['From'] = FROM_ADDRESS
        msg['To'] = self.to_address
        msg['Cc'] = self.cc_address
        
        # Send the message via our own SMTP server
        s = smtplib.SMTP(SMTP_DOMAIN)
        s.port = PORT_NUMBER
        s.send_message(msg)
        s.quit()
        print('email sent successfully')
