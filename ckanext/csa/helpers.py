# -*- coding: utf-8 -*-
import json
from ckan.model import Package
import ckan.model as model
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


SPOTLIGHT_KEY = "ckanext.csa.spotlight"
COMMUNITY_SPOTLIGHT_KEY = "ckanext.csa.community_spotlight"

DEFAULT_SPOTLIGHT = [
    {
        "title": {"en": "Flood Mapping",
                  "fr": "Cartographie des inondations"},
        "url": {"en": "#", "fr": "#"},
        "image": "/images/splash/sp-bg-4.jpg",
        "text": {
            "en": "Canadian federal, provincial and territorial government"
                  " geospatial data providers collaborate to provide tools and"
                  " resources to help Canadians plan and prepare for floods.",
            "fr": "Les fournisseurs de données géospatiales des gouvernements"
                  " fédéral, provinciaux et territoriaux du Canada collaborent"
                  " pour offrir des outils et des ressources afin d'aider les"
                  " Canadiens à planifier et à se préparer aux inondations.",
        },
    },
    {
        "title": {"en": "GeoAI", "fr": "GéoIA"},
        "url": {"en": "#", "fr": "#"},
        "image": "/csa-org.jpg",
        "text": {
            "en": "Discover the GeoAI Data Series, the time enabled geospatial"
                  " features created using artificial intelligence (AI).",
            "fr": "Découvrez la série de données GéoIA, les entités géospatiales"
                  " temporelles créées à l'aide de l'intelligence artificielle"
                  " (IA).",
        },
    },
    {
        "title": {"en": "Canadian Hydrospatial Network",
                  "fr": "Réseau hydrospatial canadien"},
        "url": {"en": "#", "fr": "#"},
        "image": "/images/splash/sp-bg-4.jpg",
        "text": {
            "en": "Discover Canada's new, higher-resolution hydrographic"
                  " network. The network enables geospatial analyses to model"
                  " surface water flow.",
            "fr": "Découvrez le nouveau réseau hydrographique du Canada à plus"
                  " haute résolution. Le réseau permet des analyses géospatiales"
                  " pour modéliser l'écoulement des eaux de surface.",
        },
    },
]

DEFAULT_COMMUNITY_SPOTLIGHT = []


def csa_bilingual_text(value):
    """Return the current-language string from a bilingual spotlight field.

    Accepts a plain string (legacy items) or a {"en": ..., "fr": ...} dict.
    Falls back to any populated language so a page is never blank.
    """
    if isinstance(value, dict):
        lang = h.lang()
        return (value.get(lang) or value.get("en") or value.get("fr")
                or next((v for v in value.values() if v), ""))
    return value or ""


def csa_bilingual_get(value, lang):
    """Return the stored value for one language (used by the admin form).

    A legacy plain string is treated as the English value.
    """
    if isinstance(value, dict):
        return value.get(lang, "")
    return (value or "") if lang == "en" else ""


def _load_spotlight(key, default):
    raw = model.get_system_info(key)
    if not raw:
        return default
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return default
    return data if isinstance(data, list) else default


def csa_spotlight():
    """Items for the home page 'In the Spotlight' section."""
    return _load_spotlight(SPOTLIGHT_KEY, DEFAULT_SPOTLIGHT)


def csa_community_spotlight():
    """Items for the home page 'Community Spotlight' section."""
    return _load_spotlight(COMMUNITY_SPOTLIGHT_KEY, DEFAULT_COMMUNITY_SPOTLIGHT)


def save_spotlight(items):
    model.set_system_info(SPOTLIGHT_KEY, json.dumps(items))


def save_community_spotlight(items):
    model.set_system_info(COMMUNITY_SPOTLIGHT_KEY, json.dumps(items))
