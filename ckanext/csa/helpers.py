# -*- coding: utf-8 -*-
from ckan.model import Package
import unicodedata
from ckan.plugins.toolkit import _
from ckan.plugins.toolkit import h
from os import path


def get_license(license_id):
    return Package.get_license_register().get(license_id)


def normalize_strip_accents(s):
    """
    utility function to help with sorting our French strings
    """
    if isinstance(s, str):
        return s
    if not s:
        s = ""
    s = unicodedata.normalize("NFD", s)
    return s.encode("ascii", "ignore").decode("ascii").lower()


def get_translated_t(data_dict, field):
    """
    customized version of core get_translated helper that also looks
    for machine translated values (e.g. en-t-fr and fr-t-en)

    Returns translated_text, is_machine_translated (True/False)
    """
    language = h.lang()
    try:
        return data_dict[field + "_translated"][language], False
    except KeyError:
        if field + "_translated" in data_dict:
            for l in data_dict[field + "_translated"]:
                if l.startswith(language + "-t-"):
                    return data_dict[field + "_translated"][l], True
        val = data_dict.get(field, "")
        return (_(val) if val and isinstance(val, str) else val), False


def header_embeds_exists():
    """check whether the files exists"""
    # return path.dirname(path.realpath(__file__))
    return path.exists(
        path.dirname(path.realpath(__file__)) + "/templates/header_embeds.html"
    )


def footer_embeds_exists():
    """check whether the files exists"""
    # return path.dirname(path.realpath(__file__))
    return path.exists(
        path.dirname(path.realpath(__file__)) + "/templates/footer_embeds.html"
    )


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
