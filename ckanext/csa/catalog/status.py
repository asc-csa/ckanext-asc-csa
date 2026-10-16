"""Governance status choices and defaults from the active catalogue schema."""
from ckan.plugins import toolkit as tk
from ckanext.scheming.helpers import (
    scheming_field_by_name,
    scheming_get_dataset_schema,
)
from ckanext.scheming.validation import scheming_validator

FIELD_NAME = "governance_status"


def status_field():
    schema = scheming_get_dataset_schema("dataset")
    return scheming_field_by_name(schema["dataset_fields"], FIELD_NAME)


@scheming_validator
def default_status(field, schema):
    """Apply the field's default during dataset creation."""
    return tk.get_validator("default")(field["default"])


def all_statuses():
    return status_field()["choices"]


def get_status(value):
    """Return the schema choice, using the field default when unset."""
    field = status_field()
    value = value or field["default"]
    return next((choice for choice in field["choices"] if choice["value"] == value), None)
