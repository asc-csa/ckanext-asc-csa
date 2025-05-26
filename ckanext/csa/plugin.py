import ckan.plugins as p
import ckan.plugins.toolkit as tk
import json
import os
import inspect

from ckan.lib.plugins import DefaultTranslation
from ckan.plugins.toolkit import _, request
from ckanext.csa import helpers, loader, validators


import routes.mapper


class CsaPlugin(p.SingletonPlugin, DefaultTranslation):
    p.implements(p.IConfigurer)
    p.implements(p.IPackageController)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IFacets)
    p.implements(p.ITranslation)
    p.implements(p.IBlueprint)
    p.implements(p.IRoutes)
    p.implements(p.IValidators)

    _field_descriptions = None

    def _load_field_descriptions(self, config):
        """
        Loads field descriptions from a json file, and stores it in the CsaPlugin object
        *used for JS field_descriptions
        """
        if self._field_descriptions is not None:
            return
        CsaPlugin._field_descriptions = {}
        file = "ckanext.csa:field_descriptions.json"
        for preset in self._load_files(file)["descriptions"]:
            CsaPlugin._field_descriptions[preset["field_name"]] = preset["description"]

    def _load_files(self, url):
        """
        Given a path like "ckanext.csa:test.json"
        find the second part relative to the import path of the first
        *used for JS field_descriptions
        """
        module, file_name = url.split(":", 1)
        try:
            # __import__ has an odd signature
            m = __import__(module, fromlist=[""])
        except ImportError:
            return
        p = os.path.join(os.path.dirname(inspect.getfile(m)), file_name)
        if os.path.exists(p):
            # watch_file(p)
            return loader.load(open(p))

    # IpackageController
    def before_search(self, search_params):
        """Extensions will receive a dictionary with the query parameters,
        and should return a modified (or not) version of it.
        """
        query_fields = ""
        # get current language
        try:
            current_lang = request.environ["CKAN_LANG"]
        except TypeError as err:
            if err.message == (
                "No object (name: request) has been registered " "for this thread"
            ):
                current_lang = "en"
            else:
                raise
        except (KeyError, RuntimeError):
            current_lang = "en"

        # Dismax search term for French
        if current_lang == "fr":
            query_fields = "title_fr^8 text_french^4 title^2 text"
        # code below to potentially search equal parameters English, although currently defaults to CKAN core search
        # else if current_lang == 'en':
        #     query_fields = 'title^8 text^4 title_fr^2 text_french'

        if query_fields:
            search_params["qf"] = query_fields

        return search_params

    def after_search(self, search_results, data_dict):
        return search_results

    # Implements bilingual searching
    def before_index(self, pkg_dict):
        pkg_dict["subject"] = json.loads(pkg_dict.get("subject", "[]"))
        pkg_dict["project"] = json.loads(pkg_dict.get("project", "[]"))

        kw = json.loads(pkg_dict.get("extras_keywords", "{}"))
        pkg_dict["keywords_en"] = kw.get("en", [])
        pkg_dict["keywords_fr"] = kw.get("fr", [])

        notes = json.loads(pkg_dict.get("extras_notes_translated", "{}"))
        pkg_dict["notes_en"] = notes.get("en", "")
        pkg_dict["notes_fr"] = notes.get("fr", "")

        titles = json.loads(pkg_dict.get("title_translated", "{}"))
        pkg_dict["title_fr"] = titles.get("fr", "")
        pkg_dict["title_string"] = titles.get("en", "")

        validated_data_dict = json.loads(pkg_dict.get("validated_data_dict"))
        res_name_fr = []
        if validated_data_dict:
            resources = validated_data_dict.get("resources")
            for resource in resources:
                res_name_fr_temp = resource.get("name_translated", {}).get("fr")
                if res_name_fr_temp:
                    res_name_fr.append(res_name_fr_temp)
        pkg_dict["res_name_fr"] = res_name_fr

        return pkg_dict

    # IConfigurer
    def update_config(self, config_):
        # Add template and resource directories to access custom html/css files
        # Further documentation available in the CKAN official documentation
        tk.add_template_directory(config_, "templates")
        tk.add_public_directory(config_, "public")
        tk.add_resource("fanstatic", "csa")
        self._load_field_descriptions("test")

    def get_helpers(self):
        # Helpers for templates
        # Taken from helpers.py file
        return {
            "csa_normalize_strip_accents": helpers.normalize_strip_accents,
            "get_license": helpers.get_license,
            "csa_get_translated_t": helpers.get_translated_t,
            "csa_get_field_descriptions": helpers.csa_get_field_descriptions,
            "csa_get_field_description": helpers.csa_get_field_description,
            "get_translated_t": helpers.get_translated_t,
            "header_embeds_exists": helpers.header_embeds_exists,
            "footer_embeds_exists": helpers.footer_embeds_exists,
        }

    # IFacets

    def dataset_facets(self, facets_dict, package_type):
        # facets_dict['division'] = p.toolkit._('Division')
        facets_dict.update(
            {
                "portal_type": _("Data or information"),
                "collection": _("Collection type"),
                "science_admin": _("Science or management"),
                "keywords_en": _("Keywords"),
                "keywords_fr": _("Keywords"),
                "keywords": _("Keywords"),
                "project": _("CSA Science category"),
                "res_format": _("Format"),
                "frequency": _("Maintenance and update frequency"),
                "topic_category": _("Topic categories"),
                "spatial_representation_type": _("Spatial representation type"),
                "fgp_viewer": _("Map viewer"),
                "ready_to_publish": _("Record status"),
                "imso_approval": _("IMSO approval"),
                "jurisdiction": _("Jurisdiction"),
            }
        )
        facets_dict["vocab_project"] = tk._("Project")
        return facets_dict

    def group_facets(self, facets_dict, group_type, package_type):
        facets_dict.update(
            {
                "portal_type": _("Portal type"),
                "collection": _("Collection type"),
                "science_admin": _("Data category"),
                "keywords_en": _("Keywords"),
                "keywords_fr": _("Keywords"),
                "keywords": _("Keywords"),
                "subject": _("Subject"),
                "res_format": _("Format"),
                "res_type": _("Resource type"),
                "frequency": _("Maintenance and update frequency"),
                "topic_category": _("Topic Categories"),
                "spatial_representation_type": _("Spatial representation type"),
                "fgp_viewer": _("Map viewer"),
                "ready_to_publish": _("Record status"),
                "imso_approval": _("IMSO approval"),
                "jurisdiction": _("Jurisdiction"),
            }
        )
        return facets_dict

    def organization_facets(self, facets_dict, organization_type, package_type):
        facets_dict.update(
            {
                "portal_type": _("Portal type"),
                "collection": _("Collection type"),
                "science_admin": _("Data category"),
                "keywords_en": _("Keywords"),
                "keywords_fr": _("Keywords"),
                "keywords": _("Keywords"),
                "subject": _("Subject"),
                "res_format": _("Format"),
                "res_type": _("Resource type"),
                "frequency": _("Maintenance and update frequency"),
                "topic_category": _("Topic categories"),
                "spatial_representation_type": _("Spatial representation type"),
                "fgp_viewer": _("Map viewer"),
                "ready_to_publish": _("Record status"),
                "imso_approval": _("IMSO approval"),
                "jurisdiction": _("Jurisdiction"),
            }
        )
        return facets_dict

    # IRoutesl
    def before_map(self, route_map):
        route_map.redirect("/", "/dataset")
        with routes.mapper.SubMapper(
            route_map, controller="ckanext.csa.plugin:CSAController"
        ) as m:
            m.connect("API", "/API", action="API")

        return route_map

    # IValidators

    def get_validators(self):
        """
        Returns a dictionary of custom validators.
        """
        return {
            'canada_validate_generate_uuid':
                validators.canada_validate_generate_uuid,
            'canada_tags': validators.canada_tags,
            'geojson_validator': validators.geojson_validator,
            'email_validator': validators.email_validator,
            'canada_copy_from_org_name':
                validators.canada_copy_from_org_name,
            'canada_non_related_required':
                validators.canada_non_related_required,
            'if_empty_set_to':
                validators.if_empty_set_to,
        }

    # Unused interfaces, but required by the plugin system.

    def before_view(self, pkg_dict):
        return pkg_dict

    def read(self, entity):
        return entity

    def create(self, entity):
        return entity

    def edit(self, entity):
        return entity

    def delete(self, entity):
        return entity

    def after_create(self, context, pkg_dict):
        return pkg_dict

    def after_update(self, context, pkg_dict):
        return pkg_dict

    def after_delete(self, context, pkg_dict):
        return pkg_dict

    def after_show(self, context, pkg_dict):
        return pkg_dict
