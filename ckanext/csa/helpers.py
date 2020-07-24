# -*- coding: utf-8 -*-
from ckan.model import User, Package, Activity
import unicodedata
from pylons.i18n import _
from ckantoolkit import h



def get_license(license_id):
    return Package.get_license_register().get(license_id)

def normalize_strip_accents(s):
    """
    utility function to help with sorting our French strings
    """
    if isinstance(s, str):
        return s
    if not s:
        s = u''
    s = unicodedata.normalize('NFD', s)
    return s.encode('ascii', 'ignore').decode('ascii').lower()

def get_translated_t(data_dict, field):
    '''
    customized version of core get_translated helper that also looks
    for machine translated values (e.g. en-t-fr and fr-t-en)

    Returns translated_text, is_machine_translated (True/False)
    '''
    language = h.lang()
    try:
        return data_dict[field+'_translated'][language], False
    except KeyError:
        if field+'_translated' in data_dict:
            for l in data_dict[field+'_translated']:
                if l.startswith(language + '-t-'):
                    return data_dict[field+'_translated'][l], True
        val = data_dict.get(field, '')
        return (_(val) if val and isinstance(val, basestring) else val), False


def csa_get_field_descriptions():
    """
    Gets field descriptions stored in a CsaPlugin object if initialized
    """
    from ckanext.csa.plugin import CsaPlugin as p
    if p.instance:
        return p._field_descriptions

def csa_get_field_description(field_name):
    """
    Gets field description provided a field name
    """
    field_descriptions = csa_get_field_descriptions()
    if field_descriptions:
        return field_descriptions.get(field_name)
    