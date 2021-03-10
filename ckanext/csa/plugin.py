# -*- coding: utf-8 -*-
import ckan.plugins as p
import ckan.plugins.toolkit as tk
import json
import os
import inspect

from paste.reloader import watch_file
from ckan.common import config
from ckan.common import request
from ckan.lib.plugins import DefaultTranslation
from pylons.i18n import _
from ckanext.csa import helpers
from ckanext.csa import loader


import ckan.lib.base as base
import routes.mapper
# class _CsaMixin(object):
#     """
#     Store single plugin instances in class variable

#     """

#     instance = None
#     _field_descriptions = None

#     def load_field_descriptions(self, config):
#         field_descriptions = config.get('csa.field_descriptions').split()
#         _CsaMixin._presets = {}
#         for f in reversed(field_descriptions):
#             for pp in _loadschema(f)['presets']:
#         _field_descriptions



# def load_field_description_module_path(url):
#     """
#     Given a path like "ckanext.spatialx:spatialx_schema.json"
#     find the second part relative to the import path of the first
#     """
#     print url
#     module, file_name = url.split(':', 1)
#     try:
#         # __import__ has an odd signature
#         m = __import__(module, fromlist=[''])
#     except ImportError:
#         return
#     p = os.path.join(os.path.dirname(inspect.getfile(m)), file_name)
#     if os.path.exists(p):
#         watch_file(p)
#         # print loader.load(open(p))
#         return loader.load(open(p))

class CsaPlugin(p.SingletonPlugin, DefaultTranslation):
    # p.implements(p.IDatasetForm)
    p.implements(p.IConfigurer)
    p.implements(p.IPackageController)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IFacets)
    p.implements(p.ITranslation)
    p.implements(p.IRoutes)

    instance = None
    _field_descriptions = None

    @classmethod
    def _store_instance(cls, self):
        CsaPlugin.instance = self

    def _load_field_descriptions(self, config):
        """
        Loads field descriptions from a json file, and stores it in the CsaPlugin object
        *used for JS field_descriptions
        """
        if self._field_descriptions is not None:
            return
        CsaPlugin._field_descriptions = {}
        file = "ckanext.csa:field_descriptions.json"
        for p in self._load_files(file)['descriptions']:
            CsaPlugin._field_descriptions[p['field_name']] = p['description']

    def _load_files(self, url):
        """
        Given a path like "ckanext.csa:test.json"
        find the second part relative to the import path of the first
        *used for JS field_descriptions
        """
        module, file_name = url.split(':', 1)
        try:
            # __import__ has an odd signature
            m = __import__(module, fromlist=[''])
        except ImportError:
            return
        p = os.path.join(os.path.dirname(inspect.getfile(m)), file_name)
        if os.path.exists(p):
            watch_file(p)
            return loader.load(open(p))

    #IpackageController
    def before_search(self, search_params):
        u'''Extensions will receive a dictionary with the query parameters,
        and should return a modified (or not) version of it.
        '''
        query_fields = ''
        # get current language
        try:
            current_lang = request.environ['CKAN_LANG']
        except TypeError as err:
            if err.message == ('No object (name: request) has been registered '
                               'for this thread'):
                current_lang = 'en'
            else:
                raise
        except KeyError:
            current_lang = 'en'

        # Dismax search term for French
        if current_lang == 'fr':
            query_fields = 'title_fr^8 text_french^4 title^2 text'
        # code below to potentially search equal parameters English, although currently defaults to CKAN core search
        # else if current_lang == 'en':
        #     query_fields = 'title^8 text^4 title_fr^2 text_french'

        if query_fields:
            search_params['qf'] = query_fields


        return search_params

    def after_search(self, search_results, search_params):
        return search_results



    #Before index runs before SOLR does an index/reindex
    #SOLR can be reindexed with the command 'search-index rebuild -r'
    #Must also edit schema.xml for these changes to help

    #Implements bilingual searching
    def before_index(self, pkg_dict):

        pkg_dict['subject'] = json.loads(pkg_dict.get('subject', '[]'))
        pkg_dict['project'] = json.loads(pkg_dict.get('project', '[]'))

        kw = json.loads(pkg_dict.get('extras_keywords', '{}'))
        pkg_dict['keywords_en'] = kw.get('en', [])
        pkg_dict['keywords_fr'] = kw.get('fr', [])



        notes = json.loads(pkg_dict.get('extras_notes_translated', '{}'))
        pkg_dict['notes_en'] = notes.get('en', u'')
        pkg_dict['notes_fr'] = notes.get('fr', u'')

        titles = json.loads(pkg_dict.get('title_translated', '{}'))
        pkg_dict['title_fr'] = titles.get('fr', u'')
        pkg_dict['title_string'] = titles.get('en', u'')

        validated_data_dict = json.loads(pkg_dict.get('validated_data_dict'))
        res_name_fr = []
        if validated_data_dict:
            resources = validated_data_dict.get('resources')
            for resource in resources:
                res_name_fr_temp = resource.get('name_translated', {}).get('fr')
                if res_name_fr_temp:
                    res_name_fr.append(res_name_fr_temp)
        pkg_dict['res_name_fr'] = res_name_fr

        return pkg_dict

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




    # IConfigurer
    def update_config(self, config_):
        # Add template and resource directories to access custom html/css files
        # Further documentation available in the CKAN official documentation
        tk.add_template_directory(config_, 'templates')
        tk.add_public_directory(config_, 'public')
        tk.add_resource('fanstatic', 'csa')
        self._load_field_descriptions('test')
        self._store_instance(self)

    def get_helpers(self):
        # Helpers for templates
        # Taken from helpers.py file
        return {
            'csa_normalize_strip_accents': helpers.normalize_strip_accents,
            'get_license': helpers.get_license,
            'csa_get_translated_t': helpers.get_translated_t,
            'csa_get_field_descriptions': helpers.csa_get_field_descriptions,
            'csa_get_field_description': helpers.csa_get_field_description,
            'get_translated_t' : helpers.get_translated_t,
            'header_embeds_exists' : helpers.header_embeds_exists,
            'footer_embeds_exists' : helpers.footer_embeds_exists,
            }


    # IFacets
    # Implements custom facetting

    def dataset_facets(self, facets_dict, package_type):
        # facets_dict['division'] = p.toolkit._('Division')
        facets_dict.update({
            'portal_type': _('Data or information'),
            'collection': _('Collection type'),
            'science_admin': _('Science or management'),
            'keywords_en': _('Keywords'),
            'keywords_fr': _('Keywords'),
            'keywords': _('Keywords'),
            'project': _('CSA Science category'),
            'res_format': _('Format'),
            'frequency': _('Maintenance and update frequency'),
            'topic_category': _('Topic categories'),
            'spatial_representation_type': _('Spatial representation type'),
            'fgp_viewer': _('Map viewer'),
            'ready_to_publish': _('Record status'),
            'imso_approval': _('IMSO approval'),
            'jurisdiction': _('Jurisdiction'),
            })
        facets_dict['vocab_project'] = tk._('Project')
        return facets_dict

    def group_facets(self, facets_dict, group_type, package_type):
        facets_dict.update({
            'portal_type': _('Portal type'),
            'collection': _('Collection type'),
            'science_admin': _('Data category'),
            'keywords_en': _('Keywords'),
            'keywords_fr': _('Keywords'),
            'keywords': _('Keywords'),
            'subject': _('Subject'),
            'res_format': _('Format'),
            'res_type': _('Resource type'),
            'frequency': _('Maintenance and update frequency'),
            'topic_category': _('Topic Categories'),
            'spatial_representation_type': _('Spatial representation type'),
            'fgp_viewer': _('Map viewer'),
            'ready_to_publish': _('Record status'),
            'imso_approval': _('IMSO approval'),
            'jurisdiction': _('Jurisdiction'),
            })
        return facets_dict

    def organization_facets(self, facets_dict, organization_type, package_type):
        facets_dict.update({
            'portal_type': _('Portal type'),
            'collection': _('Collection type'),
            'science_admin': _('Data category'),
            'keywords_en': _('Keywords'),
            'keywords_fr': _('Keywords'),
            'keywords': _('Keywords'),
            'subject': _('Subject'),
            'res_format': _('Format'),
            'res_type': _('Resource type'),
            'frequency': _('Maintenance and update frequency'),
            'topic_category': _('Topic categories'),
            'spatial_representation_type': _('Spatial representation type'),
            'fgp_viewer': _('Map viewer'),
            'ready_to_publish': _('Record status'),
            'imso_approval': _('IMSO approval'),
            'jurisdiction': _('Jurisdiction'),
            })
        return facets_dict

    #IRoutesl
    def before_map(self, route_map):
        # Redirect home to datasets instead


        route_map.redirect('/', '/dataset')
        with routes.mapper.SubMapper(route_map,controller='ckanext.csa.plugin:CSAController') as m:
                 m.connect('API', '/API', action='API')
        # Attempt to remove /user functionality and rename to different subdomain
        # m.redirect('/hgljkdhfsqhjfhgaslkhjfkjusadh', '/user')
        # m.redirect('/user', '/dataset')
        return route_map

    def after_map(self, m):
        return m


class CSAController(base.BaseController):

    def API(self):
        return base.render('content/api.html')
