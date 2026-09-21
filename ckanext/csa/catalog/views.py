"""
Flask views for the data catalogue: governance status updates and the
administrator reports.
"""
from __future__ import annotations

from datetime import date

from flask import Blueprint, Response

import ckan.plugins.toolkit as tk
from ckan.plugins.toolkit import _, h, request

from ckanext.csa.catalog import report
from ckanext.csa.catalog import status as governance

blueprint = Blueprint("csa_catalog", __name__)

REPORT_FORMATS = {
    "csv": "text/csv; charset=utf-8",
    "html": "text/html; charset=utf-8",
}


def _require_sysadmin():
    if not (tk.g.userobj and tk.g.userobj.sysadmin):
        return tk.abort(403, _("Need to be system administrator to administer"))


@blueprint.route("/dataset/<id>/governance-status", methods=["POST"])
def update_governance_status(id):
    """Set or clear a dataset's governance status from its sidebar."""
    context = {"user": tk.g.user}
    try:
        tk.check_access("package_update", context, {"id": id})
    except tk.NotAuthorized:
        return tk.abort(403, _("Unauthorized to update dataset"))

    value = (request.form.get(governance.FIELD_NAME) or "").strip()
    if value and governance.get_status(value) is None:
        return tk.abort(400, _("Invalid governance status."))

    try:
        # ``None`` drops the extra; an empty string would fail choice validation.
        pkg = tk.get_action("package_patch")(
            context, {"id": id, governance.FIELD_NAME: value or None}
        )
    except tk.ObjectNotFound:
        return tk.abort(404, _("Dataset not found"))
    except tk.ValidationError as exc:
        details = "; ".join(f"{key}: {msg}" for key, msg in exc.error_summary.items())
        h.flash_error(_("Could not update the governance status: %s") % details)
        return tk.redirect_to("dataset.read", id=id)

    h.flash_success(_("Governance status updated."))
    return tk.redirect_to("dataset.read", id=pkg["name"])


@blueprint.route("/ckan-admin/reports")
def reports():
    """Administrator landing page for the catalogue reports."""
    _require_sysadmin()
    return tk.render("admin/reports.html", {"statuses": governance.STATUSES})


@blueprint.route("/ckan-admin/reports/status.<fmt>")
def status_report(fmt):
    """The dataset status report as CSV or HTML."""
    _require_sysadmin()
    if fmt not in REPORT_FORMATS:
        return tk.abort(404, _("Unknown report format"))

    lang = h.lang()
    today = date.today().isoformat()
    title = _("Dataset status report")
    site_title = tk.config.get("ckan.site_title") or ""
    subtitle = _("Generated on {date} from {site}").format(date=today, site=site_title)
    headers = report.ReportHeaders(
        title=_("Name of the dataset"),
        status=_("Status"),
        steward=_("Data steward"),
        url=_("URL"),
    )
    rows = report.collect_rows(
        tk.g.user, lang, lambda name: h.url_for("dataset.read", id=name, qualified=True)
    )
    summary = report.summarize(rows, lang, _("Not set"))
    filename = f"dataset-status-report-{today}.{fmt}"

    if fmt == "csv":
        body = report.render_csv(rows, headers)
        disposition = "attachment"
    else:
        body = tk.render(
            "catalog/report_status.html",
            {
                "title": title,
                "subtitle": subtitle,
                "headers": headers,
                "rows": rows,
                "summary": summary,
                "total": len(rows),
            },
        )
        disposition = "inline"

    return Response(
        body,
        mimetype=REPORT_FORMATS[fmt],
        headers={"Content-Disposition": f'{disposition}; filename="{filename}"'},
    )
