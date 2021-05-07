from flask import Blueprint

csa = Blueprint('csa', __name__)

def API(self):
    return base.render('content/api.html')

csa.add_url_rule(u'/API')