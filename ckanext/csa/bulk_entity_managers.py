"""Custom entity managers for ckanext-bulk with ckanext-scheming integration."""
from __future__ import annotations

import logging
from typing import Any

import ckan.plugins.toolkit as tk
from ckanext.bulk.entity_managers.dataset import DatasetEntityManager
from ckanext.bulk.entity_managers import base
from ckanext.bulk import const

log = logging.getLogger(__name__)


class SchemingDatasetEntityManager(DatasetEntityManager):
    """
    Custom DatasetEntityManager that integrates with ckanext-scheming.

    This manager extends the default DatasetEntityManager to provide:
    - Schema-aware field detection with proper labels
    - Support for choice fields with label-to-value translation
    - Bilingual label support (EN/FR)
    - Automatic filtering by label OR value
    """

    entity_type = "dataset"

    @classmethod
    def get_fields(cls) -> list[base.FieldItem]:
        """
        Get fields for datasets, enriched with scheming schema information.

        Returns field items with proper labels from the scheming schema when available.
        """
        if fields := cls.get_fields_from_redis():
            return fields

        try:
            from ckanext.scheming import helpers as scheming_helpers

            schema = scheming_helpers.scheming_get_dataset_schema(cls.entity_type)

            if schema and 'dataset_fields' in schema:
                fields = cls._get_fields_from_schema(schema)
                cls.cache_fields_to_redis(fields)
                return fields
        except (ImportError, AttributeError) as e:
            log.warning(f"Could not load scheming schema: {e}. Falling back to default field detection.")

        return super().get_fields()

    @classmethod
    def _get_fields_from_schema(cls, schema: dict[str, Any]) -> list[base.FieldItem]:
        """
        Extract fields from a scheming schema with proper labels.

        Args:
            schema: The scheming dataset schema

        Returns:
            List of FieldItem objects with proper labels
        """
        from ckanext.scheming import helpers as scheming_helpers

        fields = []

        for field_def in schema['dataset_fields']:
            field_name = field_def.get('field_name')

            if not field_name:
                continue

            label = field_def.get('label', field_name)
            if isinstance(label, dict):
                label_text = label.get('en', label.get('fr', field_name))
            else:
                label_text = scheming_helpers.scheming_language_text(label) if label else field_name

            fields.append(
                base.FieldItem(
                    value=field_name,
                    text=label_text
                )
            )

        return fields

    @classmethod
    def search_entities_by_filters(
        cls, filters: list[base.FilterItem], global_operator: str = const.GLOBAL_AND
    ) -> list[dict[str, Any]]:
        """
        Search entities by filters with automatic label-to-value translation.

        This method extends the parent implementation to automatically convert
        choice field labels to their internal values before searching.

        Example:
            Filter: {'field': 'geographic_region', 'operator': 'is', 'value': 'Canada'}
            Translates to: {'field': 'geographic_region', 'operator': 'is', 'value': '0'}

        Args:
            filters: List of filter items
            global_operator: AND or OR operator

        Returns:
            List of matching entities
        """
        log.info(f"Bulk: Searching with {len(filters)} filter(s) using {global_operator}")

        translated_filters = []
        for filter_item in filters:
            field_name = filter_item['field']
            original_value = filter_item['value']

            translated_value = cls._translate_filter_value(field_name, original_value)

            if translated_value != original_value:
                log.info(
                    f"Bulk: Translated filter value for '{field_name}': "
                    f"'{original_value}' → '{translated_value}'"
                )

            translated_filters.append({
                'field': field_name,
                'operator': filter_item['operator'],
                'value': translated_value
            })

        log.debug(f"Bulk: Final filters for search: {translated_filters}")
        return super().search_entities_by_filters(translated_filters, global_operator)

    @classmethod
    def _translate_filter_value(cls, field_name: str, value: str) -> str:
        """
        Translate a filter value from label to internal value if it's a choice field.

        Args:
            field_name: The name of the field
            value: The user-provided value (might be a label or internal value)

        Returns:
            The internal value if translation succeeded, otherwise the original value
        """
        if not value:
            return value

        choices = cls.get_field_choices(field_name)
        if not choices:
            return value

        log.debug(f"Bulk: Field '{field_name}' has {len(choices)} choices")

        for choice in choices:
            if choice['value'] == value:
                log.debug(f"Bulk: Value '{value}' matched internal value directly")
                return value

        value_lower = value.lower()
        for choice in choices:
            if choice['label'].lower() == value_lower:
                log.debug(
                    f"Bulk: Value '{value}' matched label '{choice['label']}' → '{choice['value']}'"
                )
                return choice['value']

        for choice in choices:
            if value_lower in choice['label'].lower():
                log.info(
                    f"Bulk: Value '{value}' partially matched label '{choice['label']}' → '{choice['value']}'"
                )
                return choice['value']

        log.warning(
            f"Bulk: Could not translate value '{value}' for field '{field_name}'. "
            f"Using original value. Available choices: {[c['label'] for c in choices[:5]]}"
        )
        return value

    @classmethod
    def get_field_choices(cls, field_name: str) -> list[dict[str, str]] | None:
        """
        Get the choices for a specific field from the scheming schema.

        Args:
            field_name: The name of the field

        Returns:
            List of choice dictionaries with 'value' and 'label' keys, or None if no choices
        """
        try:
            from ckanext.scheming import helpers as scheming_helpers

            schema = scheming_helpers.scheming_get_dataset_schema(cls.entity_type)
            if not schema or 'dataset_fields' not in schema:
                return None

            field_def = scheming_helpers.scheming_field_by_name(
                schema['dataset_fields'],
                field_name
            )

            if not field_def:
                return None

            choices = scheming_helpers.scheming_field_choices(field_def)
            if not choices:
                return None

            result = []
            for choice in choices:
                value = choice.get('value', '')
                label = choice.get('label', value)

                if isinstance(label, dict):
                    label_text = label.get('en', label.get('fr', value))
                else:
                    label_text = scheming_helpers.scheming_language_text(label) if label else value

                result.append({
                    'value': str(value),
                    'label': label_text
                })

            return result

        except (ImportError, AttributeError) as e:
            log.warning(f"Could not get choices for field {field_name}: {e}")
            return None
