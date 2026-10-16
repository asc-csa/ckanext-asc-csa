"""Regression coverage for reporting datasets without a governance status."""
import json
from pathlib import Path

from ckanext.csa.catalog import report, status


def test_reports_count_unset_datasets_as_draft(monkeypatch):
    schema = json.loads((Path(status.__file__).parent / "ckan_dataset.json").read_text())
    monkeypatch.setattr(status, "scheming_get_dataset_schema", lambda _: schema)
    packages = [
        {},
        {"governance_status": None},
        {"governance_status": ""},
        {"governance_status": "validated"},
    ]
    rows = [report.row_from_package(pkg, "en", lambda name: name) for pkg in packages]

    assert [row.status_label for row in rows] == ["Draft", "Draft", "Draft", "Validated"]
    summary = dict(report.summarize(rows, "en", "Not set"))
    assert summary["Draft"] == 3
    assert summary["Validated"] == 1
    assert "Not set" not in summary
