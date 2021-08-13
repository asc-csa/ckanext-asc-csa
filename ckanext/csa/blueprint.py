from flask import Blueprint, redirect, request
import ckan.plugins.toolkit as toolkit

csa = Blueprint('csa', __name__)

redirect_urls = {
    '/': '/dataset',
    }

def API():
    return toolkit.render('content/api.html')

def redirect_url():
    print('redirecting')
    print(request.path)
    return redirect(redirect_urls[request.path], 301)
    # return redirect('http://google.ca', 301)

# def send_to_dataset():
#     print('trying to redirect')
#     return redirect('/dataset')

def get_blueprints():
    return [csa]

print('REDIRECT URLS')
for url in redirect_urls:
    print(url)
    csa.add_url_rule(url, url, redirect_url)

csa.add_url_rule('/API', '/API', view_func=API)