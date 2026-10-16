from copy import deepcopy
from datetime import date
from unittest.mock import Mock

import pytest

from ckanext.csa.catalog import retention

TODAY = date(2026, 10, 16)
OPTIONS = {"fallback": "det@example.org"}


@pytest.fixture
def catalogue(monkeypatch):
    pkg = {
        "id": "dataset-id", "name": "example", "title": "Example", "state": "active",
        "retention_start_date": "2020-01-01", "retention_end_date": "2026-10-15",
        "governance_status": "validated", "data_steward_email": "steward@example.org",
    }
    saved = {}
    deleted = Mock()
    sent = Mock()

    def show(context, data):
        return deepcopy(pkg)

    def task_show(context, data):
        if not saved:
            raise retention.tk.ObjectNotFound()
        return deepcopy(saved)

    def task_save(context, data):
        saved.update(deepcopy(data), id="task-id")
        return deepcopy(saved)

    def delete(context, data):
        deleted(data["id"])
        pkg["state"] = "deleted"

    def mail(*args, **kwargs):
        assert pkg["state"] == "deleted"
        sent(args[1])

    actions = {"package_show": show, "package_delete": delete,
               "task_status_show": task_show, "task_status_update": task_save}
    monkeypatch.setattr(retention.tk, "get_action", actions.__getitem__)
    monkeypatch.setattr(retention.tk, "config", {"ckan.site_url": "https://catalogue.example.org"})
    monkeypatch.setattr(retention.jinja_extensions, "get_jinja_env_options", lambda: {})
    monkeypatch.setattr(retention, "Environment", Mock())
    session = Mock()
    session.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [
        ("admin@example.org",), (None,), (" ",), (" admin@example.org ",),
    ]
    monkeypatch.setattr(retention.model, "Session", session)
    monkeypatch.setattr(retention.mailer, "mail_recipient", mail)
    return pkg, saved, deleted, sent, actions


def test_expiry_deletes_once_and_preserves_status(catalogue):
    pkg, saved, deleted, sent, _ = catalogue
    for _ in range(2):
        retention.process_dataset(pkg["id"], TODAY, OPTIONS, {})
    deleted.assert_called_once_with(pkg["id"])
    assert pkg["governance_status"] == "validated"
    assert [call.args[0] for call in sent.call_args_list] == ["steward@example.org", "admin@example.org"]
    assert saved["state"] == "complete"


def test_failed_email_retries_only_unsent_recipients(catalogue):
    pkg, saved, deleted, sent, _ = catalogue
    sent.side_effect = [None, RuntimeError("SMTP unavailable"), None]
    with pytest.raises(RuntimeError, match="SMTP unavailable"):
        retention.process_dataset(pkg["id"], TODAY, OPTIONS, {})
    assert saved["state"] == "pending"
    retention.process_dataset(pkg["id"], TODAY, OPTIONS, {})
    deleted.assert_called_once()
    assert [call.args[0] for call in sent.call_args_list] == [
        "steward@example.org", "admin@example.org", "admin@example.org"]
    assert saved["state"] == "complete"


def test_failed_deletion_does_not_send_mail_and_can_retry(catalogue):
    pkg, saved, deleted, sent, _ = catalogue
    deleted.side_effect = RuntimeError("Delete failed")
    with pytest.raises(RuntimeError, match="Delete failed"):
        retention.process_dataset(pkg["id"], TODAY, OPTIONS, {})
    sent.assert_not_called()
    assert saved["state"] == "pending"
    deleted.side_effect = None
    retention.process_dataset(pkg["id"], TODAY, OPTIONS, {})
    assert pkg["state"] == "deleted"
    assert saved["state"] == "complete"


@pytest.mark.parametrize("change", [
    {"retention_end_date": "2026-10-16"},
    {"retention_end_date": "2027-01-01"},
    {"retention_end_date": ""},
    {"retention_start_date": ""},
    {"governance_status": "paused_from_disposal"},
])
def test_unexpired_or_held_datasets_are_untouched(catalogue, change):
    pkg, saved, deleted, sent, _ = catalogue
    pkg.update(change)
    retention.process_dataset(pkg["id"], TODAY, OPTIONS, {})
    deleted.assert_not_called()
    sent.assert_not_called()
    assert not saved


@pytest.mark.parametrize("change", [
    {"retention_end_date": "2027-01-01"},
    {"data_steward_email": "new-steward@example.org"},
    {"governance_status": "paused_from_disposal"},
])
def test_metadata_changed_during_processing_prevents_deletion(catalogue, change):
    pkg, saved, deleted, sent, actions = catalogue
    save = actions["task_status_update"]

    def postpone(context, data):
        pkg.update(change)
        return save(context, data)

    actions["task_status_update"] = postpone
    retention.process_dataset(pkg["id"], TODAY, OPTIONS, {})
    deleted.assert_not_called()
    sent.assert_not_called()
    assert saved["state"] == "cancelled"


def test_missing_steward_uses_fallback_without_duplicate_mail(catalogue):
    pkg, _, _, sent, _ = catalogue
    pkg["data_steward_email"] = ""
    options = {"fallback": "admin@example.org"}
    retention.process_dataset(pkg["id"], TODAY, options, {})
    sent.assert_called_once_with("admin@example.org")


def test_retention_dates_reject_invalid_format_and_reversed_range():
    for value in ["2026-02-30", "2026-10-16T12:00:00", "16/10/2026"]:
        with pytest.raises(retention.tk.Invalid):
            retention.retention_date(value)
    with pytest.raises(retention.tk.Invalid):
        retention.retention_end(("retention_end_date",), {
            ("retention_start_date",): "2026-10-16", ("retention_end_date",): "2026-10-15",
        }, {}, {})
