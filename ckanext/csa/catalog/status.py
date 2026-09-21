"""
Governance status for catalogue datasets (issue #242).

The status reflects a dataset's governance maturity and trust level. It is
stored in the internal schema's ``governance_status`` scheming field, which is
absent from the public schema and hidden from generic forms and displays. The
catalogue renders it in the "About this record" sidebar and lets users with
update permission change it there.

This module is the single source of truth for the values, labels, colours and
descriptions. The scheming schema carries a copy of the choices for
validation; a unit test keeps the two in sync.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

FIELD_NAME = "governance_status"

LABEL = {"en": "Governance status", "fr": "Statut de gouvernance"}
HELP_TEXT = {
    "en": "Governance maturity and trust level of this dataset. Set from the"
          " dataset page in the data catalogue.",
    "fr": "Niveau de maturité et de confiance de la gouvernance de ce jeu de"
          " données. Défini à partir de la page du jeu de données dans le"
          " catalogue de données.",
}


@dataclass(frozen=True)
class GovernanceStatus:
    value: str
    label: dict[str, str]
    description: dict[str, str]
    #: Bootstrap 3 / WET label variant: default, info, success, warning, danger.
    style: str
    #: Glyphicon name shown before the label.
    icon: str

    def label_for(self, lang: Optional[str]) -> str:
        return self.label.get(lang or "en") or self.label["en"]

    def description_for(self, lang: Optional[str]) -> str:
        return self.description.get(lang or "en") or self.description["en"]

    @property
    def css_class(self) -> str:
        return f"label label-{self.style}"


STATUSES: tuple[GovernanceStatus, ...] = (
    GovernanceStatus(
        value="draft",
        label={"en": "Draft", "fr": "Ébauche"},
        description={
            "en": "Dataset is new or incomplete. Documentation may be partial"
                  " or missing. Ownership or definitions not finalized.",
            "fr": "Le jeu de données est nouveau ou incomplet. La documentation"
                  " peut être partielle ou manquante. La propriété ou les"
                  " définitions ne sont pas finalisées.",
        },
        style="default",
        icon="glyphicon-pencil",
    ),
    GovernanceStatus(
        value="in_review",
        label={"en": "In review", "fr": "En révision"},
        description={
            "en": "Dataset structure exists. Business context and definitions"
                  " are being reviewed. Governance checks (quality, compliance)"
                  " may be in progress.",
            "fr": "La structure du jeu de données existe. Le contexte"
                  " opérationnel et les définitions sont en cours de révision."
                  " Des vérifications de gouvernance (qualité, conformité)"
                  " peuvent être en cours.",
        },
        style="info",
        icon="glyphicon-eye-open",
    ),
    GovernanceStatus(
        value="validated",
        label={"en": "Validated", "fr": "Validé"},
        description={
            "en": "Dataset has been reviewed and approved. Key metadata is"
                  " complete. Owner and steward identified.",
            "fr": "Le jeu de données a été révisé et approuvé. Les métadonnées"
                  " clés sont complètes. Le propriétaire et le responsable des"
                  " données sont identifiés.",
        },
        style="success",
        icon="glyphicon-ok",
    ),
    GovernanceStatus(
        value="paused_from_disposal",
        label={"en": "Paused from disposal", "fr": "Disposition suspendue"},
        description={
            "en": "Dataset is paused from being disposed of. Key metadata is"
                  " complete. Owner and steward identified.",
            "fr": "La disposition du jeu de données est suspendue. Les"
                  " métadonnées clés sont complètes. Le propriétaire et le"
                  " responsable des données sont identifiés.",
        },
        style="warning",
        icon="glyphicon-pause",
    ),
    GovernanceStatus(
        value="deprecated",
        label={"en": "Deprecated", "fr": "Obsolète"},
        description={
            "en": "Dataset should no longer be used. Still documented for"
                  " lineage and audit purposes. Clearly flagged to prevent"
                  " accidental reuse.",
            "fr": "Le jeu de données ne devrait plus être utilisé. Il demeure"
                  " documenté à des fins de traçabilité et d'audit. Clairement"
                  " signalé afin d'éviter toute réutilisation accidentelle.",
        },
        style="danger",
        icon="glyphicon-ban-circle",
    ),
)

BY_VALUE: dict[str, GovernanceStatus] = {s.value: s for s in STATUSES}


def all_statuses() -> tuple[GovernanceStatus, ...]:
    """Template helper: every status, in lifecycle order."""
    return STATUSES


def get_status(value: Any) -> Optional[GovernanceStatus]:
    """Template helper: the status for a stored value, or None if unset/unknown."""
    if not value:
        return None
    return BY_VALUE.get(str(value))


def status_label(value: Any, lang: Optional[str] = None) -> str:
    """The display label for a stored value; empty when unset or unknown."""
    status = get_status(value)
    return status.label_for(lang) if status else ""


def schema_choices() -> list[dict[str, Any]]:
    return [{"value": s.value, "label": dict(s.label)} for s in STATUSES]


def schema_field() -> dict[str, Any]:
    """The scheming field definition that ``ckan_dataset.json`` must contain."""
    return {
        "field_name": FIELD_NAME,
        "label": dict(LABEL),
        "help_text": dict(HELP_TEXT),
        "required": False,
        "form_snippet": None,
        "display_snippet": None,
        "validators": "ignore_missing scheming_choices",
        "choices": schema_choices(),
    }
