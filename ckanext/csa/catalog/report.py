"""
Dataset status report for administrators (issue #245).

One row per dataset: name, governance status, data steward and URL, rendered
as CSV or a standalone HTML document. The row collection talks to CKAN;
status labels and defaults come from the active catalogue schema.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Iterator, Mapping, Optional, Sequence

from ckanext.scheming.helpers import scheming_language_text

from ckanext.csa.catalog import status as governance

#: Rows fetched per package_search call.
CHUNK_SIZE = 1000


@dataclass(frozen=True)
class StatusReportRow:
    title: str
    status: str
    status_label: str
    steward: str
    url: str


@dataclass(frozen=True)
class ReportHeaders:
    title: str
    status: str
    steward: str
    url: str

    def as_list(self) -> list[str]:
        return [self.title, self.status, self.steward, self.url]


def dataset_title(pkg: Mapping[str, Any], lang: Optional[str]) -> str:
    """The dataset title in ``lang``, falling back like the theme does."""
    translated = pkg.get("title_translated")
    if isinstance(translated, dict):
        for candidate in (lang, "en", "fr"):
            if candidate and translated.get(candidate):
                return str(translated[candidate])
    return str(pkg.get("title") or pkg.get("name") or "")


def row_from_package(
    pkg: Mapping[str, Any],
    lang: Optional[str],
    url_for_dataset: Callable[[str], str],
) -> StatusReportRow:
    choice = governance.get_status(pkg.get(governance.FIELD_NAME))
    value = choice["value"] if choice else pkg.get(governance.FIELD_NAME)
    return StatusReportRow(
        title=dataset_title(pkg, lang),
        status=str(value),
        status_label=scheming_language_text(choice["label"], lang) if choice else "",
        steward=str(pkg.get("data_steward") or "").strip(),
        url=url_for_dataset(str(pkg.get("name") or pkg.get("id") or "")),
    )


def sort_rows(rows: Iterable[StatusReportRow]) -> list[StatusReportRow]:
    return sorted(rows, key=lambda r: (r.title.casefold(), r.url))


def iter_packages(username: str, chunk_size: Optional[int] = None) -> Iterator[dict[str, Any]]:
    """Every active dataset the user can see, including private ones."""
    import ckan.plugins.toolkit as tk

    chunk_size = chunk_size or CHUNK_SIZE
    offset = 0
    while True:
        response = tk.get_action("package_search")(
            {"user": username},
            {
                "q": "*:*",
                "facet": False,
                "include_private": True,
                "sort": "metadata_modified desc",
                "start": offset,
                "rows": chunk_size,
            },
        )
        results = response.get("results", [])
        yield from results
        if len(results) < chunk_size:
            break
        offset += chunk_size


def collect_rows(
    username: str,
    lang: Optional[str],
    url_for_dataset: Callable[[str], str],
    chunk_size: Optional[int] = None,
) -> list[StatusReportRow]:
    return sort_rows(
        row_from_package(pkg, lang, url_for_dataset)
        for pkg in iter_packages(username, chunk_size)
    )


def summarize(rows: Iterable[StatusReportRow], lang: Optional[str], unset_label: str) -> list[tuple[str, int]]:
    """(label, count) per status in lifecycle order, then datasets with none."""
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.status] = counts.get(row.status, 0) + 1
    summary = [
        (scheming_language_text(choice["label"], lang), counts.pop(choice["value"], 0))
        for choice in governance.all_statuses()
    ]
    unset = sum(counts.values())
    if unset:
        summary.append((unset_label, unset))
    return summary


def render_csv(rows: Sequence[StatusReportRow], headers: ReportHeaders) -> str:
    """CSV text with a BOM so spreadsheets open the accents correctly."""
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(headers.as_list())
    for row in rows:
        writer.writerow([row.title, row.status_label, row.steward, row.url])
    return "﻿" + out.getvalue()
