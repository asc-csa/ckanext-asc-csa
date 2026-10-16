import json
import logging
from datetime import date, datetime, timezone
from urllib.parse import quote
from zoneinfo import ZoneInfo

from jinja2 import Environment, select_autoescape
from sqlalchemy import text

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk
from ckan import model
from ckan.common import ugettext, ungettext
from ckan.lib import jinja_extensions, mailer
from ckan.logic.validators import email_validator

log = logging.getLogger(__name__)
TASK_TYPE = "csa_catalog_retention"


def retention_date(value):
    try:
        parsed = date.fromisoformat(value)
        if parsed.isoformat() != value:
            raise ValueError
    except (TypeError, ValueError):
        raise tk.Invalid(tk._("Use a date in YYYY-MM-DD format."))
    return value


def retention_end(key, data, errors, context):
    end = retention_date(data[key])
    start = data.get(key[:-1] + ("retention_start_date",))
    if not start or start is tk.missing:
        raise tk.Invalid(tk._("A retention start date is required."))
    start = retention_date(start)
    if end < start:
        raise tk.Invalid(tk._("Retention end date must not precede the start date."))


def settings(require_mail=False):
    options = {
        "timezone": ZoneInfo(tk.config.get("ckanext.csa.retention.timezone", "UTC")),
        "fallback": tk.config.get("ckanext.csa.retention.fallback_email", "").strip(),
    }
    if options["fallback"]:
        email_validator(options["fallback"], {})
    if require_mail:
        if not options["fallback"]:
            raise ValueError("Configure retention fallback_email first.")
        if not tk.config.get("smtp.server") or not tk.config.get("smtp.mail_from"):
            raise ValueError("Configure smtp.server and smtp.mail_from first.")
    return options


def is_due(pkg, today):
    if pkg.get("state") != "active" or pkg.get("governance_status") == "paused_from_disposal":
        return False
    start, end = pkg.get("retention_start_date"), pkg.get("retention_end_date")
    if not start or not end:
        return False
    try:
        start, end = retention_date(start), retention_date(end)
    except tk.Invalid:
        log.warning("Invalid retention dates for dataset %s", pkg["id"])
        return False
    return start <= end < today.isoformat()


def recipients(pkg, options):
    steward = (pkg.get("data_steward_email") or "").strip() or options["fallback"]
    admins = model.Session.query(model.User.email).filter_by(
        sysadmin=True, state=model.State.ACTIVE).order_by(model.User.id).all()
    admin_emails = [email.strip() for email, in admins if email and email.strip()]
    addresses = list(dict.fromkeys([steward, *admin_emails]))
    for address in addresses:
        if not address:
            raise ValueError("No steward email or configured fallback for dataset " + pkg["id"])
        email_validator(address, {})
    return addresses


def candidate_ids(today):
    expired = (
        model.Session.query(model.Package.id)
        .join(model.PackageExtra, model.PackageExtra.package_id == model.Package.id)
        .filter(model.Package.state == "active", model.PackageExtra.state == "active",
                model.PackageExtra.key == "retention_end_date",
                model.PackageExtra.value < today.isoformat())
    )
    pending = model.Session.query(model.TaskStatus.entity_id).filter_by(
        task_type=TASK_TYPE, key="expiry", state="pending")
    return [row[0] for row in expired.union(pending).order_by(None).all()]


def task_for(package_id):
    try:
        return tk.get_action("task_status_show")({"ignore_auth": True}, {
            "entity_id": package_id, "task_type": TASK_TYPE, "key": "expiry",
        })
    except tk.ObjectNotFound:
        return None


def save_task(package_id, payload, state="pending", task=None):
    data = {
        "entity_id": package_id, "entity_type": "package", "task_type": TASK_TYPE,
        "key": "expiry", "value": json.dumps(payload), "state": state,
        "last_updated": datetime.now(timezone.utc).isoformat(), "error": "",
    }
    if task:
        data["id"] = task["id"]
    return tk.get_action("task_status_update")({"ignore_auth": True}, data)


def notify(package_id, task):
    payload = json.loads(task["value"])
    site = tk.config["ckan.site_url"].rstrip("/")
    extra_vars = {
        "title": payload["title"], "package_id": package_id,
        "end_date": payload["end_date"],
        "dataset_url": f"{site}/dataset/{quote(payload['name'], safe='')}",
        "site_title": tk.config.get("ckan.site_title"), "site_url": site,
    }
    options = jinja_extensions.get_jinja_env_options()
    options["autoescape"] = select_autoescape(disabled_extensions=("txt",), default=True)
    env = Environment(**options)
    env.install_gettext_callables(ugettext, ungettext)
    body = env.get_template("emails/retention_expired.txt").render(extra_vars)
    body_html = env.get_template("emails/retention_expired.html").render(extra_vars)
    for address in payload["recipients"]:
        if address in payload["sent"]:
            continue
        mailer.mail_recipient(address, address, "Dataset retention expired / Fin de conservation",
                              body, body_html=body_html)
        payload["sent"].append(address)
        task = save_task(package_id, payload, task=task)
    save_task(package_id, payload, state="complete", task=task)


def process_dataset(package_id, today, options, context):
    task = task_for(package_id)
    try:
        pkg = tk.get_action("package_show")(dict(context), {"id": package_id})
    except tk.ObjectNotFound:
        if task and task["state"] == "pending":
            save_task(package_id, json.loads(task["value"]), state="cancelled", task=task)
        return

    if pkg["state"] == "deleted":
        if task and task["state"] == "pending":
            notify(package_id, task)
        return
    if not is_due(pkg, today):
        if task and task["state"] == "pending":
            save_task(package_id, json.loads(task["value"]), state="cancelled", task=task)
        return

    payload = {
        "title": pkg.get("title") or pkg["name"], "name": pkg["name"],
        "end_date": pkg["retention_end_date"], "recipients": recipients(pkg, options), "sent": [],
    }
    task = save_task(package_id, payload, task=task)
    # Serialize against dataset edits and recheck after persisting the notification.
    model.Session.query(model.Package).filter_by(id=package_id).with_for_update().one()
    model.Session.expire_all()
    current = tk.get_action("package_show")(dict(context), {"id": package_id})
    if (not is_due(current, today)
            or current["retention_end_date"] != payload["end_date"]
            or recipients(current, options) != payload["recipients"]):
        model.Session.rollback()
        save_task(package_id, payload, state="cancelled", task=task)
        return
    tk.get_action("package_delete")(dict(context), {"id": package_id})
    log.info("Retention expired: dataset %s moved to trash", package_id)
    notify(package_id, task)


def expire_datasets():
    if not plugins.plugin_loaded("csa_catalog"):
        raise RuntimeError("Retention processing requires csa_catalog.")
    options = settings(require_mail=True)
    today = datetime.now(options["timezone"]).date()
    # A session lock survives the commits made by CKAN actions.
    with model.meta.engine.connect() as connection:
        locked = connection.execute(text("SELECT pg_try_advisory_lock(hashtext(:key))"),
                                    {"key": TASK_TYPE}).scalar()
        if not locked:
            log.info("Retention processing is already running")
            return
        try:
            user = tk.get_action("get_site_user")({"ignore_auth": True}, {})
            context = {"user": user["name"], "ignore_auth": True}
            failed = []
            for package_id in candidate_ids(today):
                try:
                    process_dataset(package_id, today, options, context)
                except Exception:
                    model.Session.rollback()
                    failed.append(package_id)
                    log.exception("Retention processing failed for dataset %s", package_id)
            if failed:
                raise RuntimeError(f"Retention failed for {len(failed)} dataset(s); the next run will retry.")
        finally:
            connection.execute(text("SELECT pg_advisory_unlock(hashtext(:key))"), {"key": TASK_TYPE})
