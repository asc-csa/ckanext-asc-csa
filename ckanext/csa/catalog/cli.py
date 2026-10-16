from datetime import datetime
from zoneinfo import ZoneInfoNotFoundError

import click
import ckan.plugins.toolkit as tk

from ckanext.csa.catalog import retention


@click.group(name="csa-catalog")
def catalog():
    """Internal catalogue maintenance."""


@catalog.command(name="expire")
@click.option("--dry-run", is_flag=True, help="List expired datasets and pending emails without changing anything.")
def expire(dry_run):
    """Queue retention processing."""
    try:
        options = retention.settings(require_mail=not dry_run)
        if dry_run:
            today = datetime.now(options["timezone"]).date()
            count = 0
            for package_id in retention.candidate_ids(today):
                try:
                    pkg = tk.get_action("package_show")({"ignore_auth": True}, {"id": package_id})
                except tk.ObjectNotFound:
                    click.echo(f"Cancel notification for missing dataset: {package_id}")
                    count += 1
                    continue
                if retention.is_due(pkg, today):
                    addresses = retention.recipients(pkg, options)
                    click.echo(f"Expire {pkg['name']} ({pkg['retention_end_date']}): {', '.join(addresses)}")
                    count += 1
                elif pkg["state"] == "deleted":
                    click.echo(f"Retry notification: {pkg['name']}")
                    count += 1
            if not count:
                click.echo("No retention work found.")
            return
        job = tk.enqueue_job(retention.expire_datasets, title="Catalogue retention", rq_kwargs={"timeout": 3600})
        click.echo(f"Queued retention job {job.id}")
    except (ValueError, tk.Invalid, ZoneInfoNotFoundError) as exc:
        raise click.ClickException(str(exc)) from exc
