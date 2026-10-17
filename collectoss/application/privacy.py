# SPDX-License-Identifier: MIT
"""Find the personal data a CollectOSS instance holds about one person.

Starting from an email address, resolve the identifiers that can be linked to
that person (other emails, platform logins, contributor ids), then report the
rows in each table that carry one of them. This module is read-only: it never
changes the database.

``cntrb_id`` is only an internal join key here. It is derived from the platform
user id, so it counts as personal data itself and is reported as such.
"""
import re
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import bindparam, inspect, text

DEFAULT_SCHEMA = "data"

LIMITATIONS = (
    "Identifiers are expanded once from the email given: contributors and aliases "
    "that share it, plus their other emails and logins. Longer alias chains are not followed.",
    "Matching is by email, platform login and contributor id. Names alone are not matched.",
    "Free text (message bodies, issue and pull request text) is returned for rows linked "
    "to the person but is not searched for mentions of them.",
    "A row linked to the person can carry another person's contributor id in a different "
    "column (for example both sides of an issue). Only commits are trimmed to the queried "
    "person's own columns so far.",
)

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+$")


@dataclass(frozen=True)
class Source:
    """One place personal data can live, and how a row is tied to a person."""

    name: str  # label used in the report
    table: str
    ids: Tuple[str, ...] = ()  # columns holding a contributor id
    emails: Tuple[str, ...] = ()  # columns holding an email address
    logins: Tuple[str, ...] = ()  # columns holding a platform login
    # Columns to return. None means every column. Used to keep another
    # person's details out of a row, e.g. the committer of a commit the
    # queried person authored.
    columns: Optional[Tuple[str, ...]] = None


_COMMIT_KEYS = ("cmt_id", "repo_id", "cmt_commit_hash")

SOURCES: Tuple[Source, ...] = (
    Source(
        "contributors",
        "contributors",
        ids=("cntrb_id",),
        emails=("cntrb_email", "cntrb_canonical"),
        logins=("cntrb_login", "gh_login", "gl_username"),
    ),
    Source(
        "contributors_aliases",
        "contributors_aliases",
        ids=("cntrb_id",),
        emails=("alias_email", "canonical_email"),
    ),
    Source(
        "commits_as_author",
        "commits",
        ids=("cmt_ght_author_id",),
        emails=("cmt_author_email", "cmt_author_raw_email"),
        logins=("cmt_author_platform_username",),
        columns=_COMMIT_KEYS
        + (
            "cmt_author_name",
            "cmt_author_email",
            "cmt_author_raw_email",
            "cmt_author_affiliation",
            "cmt_author_platform_username",
            "cmt_author_date",
            "cmt_author_timestamp",
            "cmt_ght_author_id",
        ),
    ),
    Source(
        "commits_as_committer",
        "commits",
        emails=("cmt_committer_email", "cmt_committer_raw_email"),
        columns=_COMMIT_KEYS
        + (
            "cmt_committer_name",
            "cmt_committer_email",
            "cmt_committer_raw_email",
            "cmt_committer_affiliation",
            "cmt_committer_date",
            "cmt_committer_timestamp",
        ),
    ),
    Source(
        "pull_request_commits",
        "pull_request_commits",
        ids=("pr_cmt_author_cntrb_id",),
        emails=("pr_cmt_author_email",),
    ),
    Source("unresolved_commit_emails", "unresolved_commit_emails", emails=("email",)),
    Source("contributor_repo", "contributor_repo", ids=("cntrb_id",)),
    Source("issues", "issues", ids=("cntrb_id", "reporter_id")),
    Source("issue_assignees", "issue_assignees", ids=("cntrb_id",)),
    Source("issue_events", "issue_events", ids=("cntrb_id",)),
    Source("message", "message", ids=("cntrb_id",)),
    Source("pull_requests", "pull_requests", ids=("pr_augur_contributor_id",)),
    Source("pull_request_assignees", "pull_request_assignees", ids=("contrib_id",)),
    Source("pull_request_events", "pull_request_events", ids=("cntrb_id",)),
    Source("pull_request_meta", "pull_request_meta", ids=("cntrb_id",)),
    Source("pull_request_repo", "pull_request_repo", ids=("pr_cntrb_id",)),
    Source("pull_request_reviewers", "pull_request_reviewers", ids=("cntrb_id",)),
    Source("pull_request_reviews", "pull_request_reviews", ids=("cntrb_id",)),
)


@dataclass(frozen=True)
class Identifiers:
    """Everything the query could link to the person who was asked about."""

    emails: Tuple[str, ...]
    logins: Tuple[str, ...]
    contributor_ids: Tuple[str, ...]

    def as_dict(self) -> Dict[str, List[str]]:
        return {
            "emails": list(self.emails),
            "logins": list(self.logins),
            "contributor_ids": list(self.contributor_ids),
        }


def normalize_email(email: str) -> str:
    email = (email or "").strip().lower()
    if not _EMAIL.match(email):
        raise ValueError("expected an email address such as name@example.com")
    return email


def _ident(name: str) -> str:
    """Quote an identifier that is about to be placed in SQL text."""
    if not _IDENTIFIER.match(name):
        raise ValueError(f"invalid SQL identifier: {name!r}")
    return f'"{name}"'


def _table(schema: str, table: str) -> str:
    return f"{_ident(schema)}.{_ident(table)}"


def _lowered(values) -> set:
    return {str(v).strip().lower() for v in values if v is not None and str(v).strip()}


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (Decimal, uuid.UUID)):
        return str(value)
    if isinstance(value, (bytes, memoryview)):
        return bytes(value).hex()
    return str(value)


def resolve_identifiers(db_conn, sqla_insp, schema: str, email: str) -> Identifiers:
    """Link an email to contributor ids, other emails and logins."""
    if not sqla_insp.has_table("contributors", schema=schema):
        raise LookupError(
            f"table {schema}.contributors not found; "
            "check that the schema name is right and the database is migrated"
        )
    contributors = _table(schema, "contributors")
    has_aliases = sqla_insp.has_table("contributors_aliases", schema=schema)
    aliases = _table(schema, "contributors_aliases")

    ids = {
        str(row[0])
        for row in db_conn.execute(
            text(
                f"SELECT cntrb_id FROM {contributors} "
                "WHERE lower(cntrb_email) = :e OR lower(cntrb_canonical) = :e"
            ),
            {"e": email},
        )
        if row[0] is not None
    }
    if has_aliases:
        ids |= {
            str(row[0])
            for row in db_conn.execute(
                text(
                    f"SELECT cntrb_id FROM {aliases} "
                    "WHERE lower(alias_email) = :e OR lower(canonical_email) = :e"
                ),
                {"e": email},
            )
            if row[0] is not None
        }

    emails, logins = {email}, set()
    if ids:
        by_id = bindparam("ids", expanding=True)
        rows = db_conn.execute(
            text(
                "SELECT cntrb_email, cntrb_canonical, cntrb_login, gh_login, gl_username "
                f"FROM {contributors} WHERE cntrb_id IN :ids"
            ).bindparams(by_id),
            {"ids": sorted(ids)},
        )
        for row in rows:
            emails |= _lowered(row[0:2])
            logins |= _lowered(row[2:5])
        if has_aliases:
            rows = db_conn.execute(
                text(
                    f"SELECT alias_email, canonical_email FROM {aliases} WHERE cntrb_id IN :ids"
                ).bindparams(bindparam("ids", expanding=True)),
                {"ids": sorted(ids)},
            )
            for row in rows:
                emails |= _lowered(row[0:2])

    return Identifiers(tuple(sorted(emails)), tuple(sorted(logins)), tuple(sorted(ids)))


def _search_source(db_conn, sqla_insp, schema_name: str, source: Source, found: Identifiers):
    """Return (rows, reason). reason is set when the source could not be searched."""
    if not sqla_insp.has_table(source.table, schema_name):
        return None, "table not found"
    present = {c["name"] for c in sqla_insp.get_columns(source.table, schema_name)}

    clauses, params = [], {}
    for column in source.ids:
        if column in present and found.contributor_ids:
            clauses.append(f"{_ident(column)} IN :ids")
            params["ids"] = list(found.contributor_ids)
    for column in source.emails:
        if column in present and found.emails:
            clauses.append(f"lower({_ident(column)}) IN :emails")
            params["emails"] = list(found.emails)
    for column in source.logins:
        if column in present and found.logins:
            clauses.append(f"lower({_ident(column)}) IN :logins")
            params["logins"] = list(found.logins)
    if not clauses:
        return [], None

    if source.columns is None:
        select = "*"
    else:
        chosen = [c for c in source.columns if c in present]
        if not chosen:
            return None, "none of the columns to report exist"
        select = ", ".join(_ident(c) for c in chosen)

    statement = text(
        f"SELECT {select} FROM {_table(schema_name, source.table)} WHERE " + " OR ".join(clauses)
    ).bindparams(*[bindparam(name, expanding=True) for name in params])
    result = db_conn.execute(statement, params)
    return [{k: _jsonable(v) for k, v in row.items()} for row in result.mappings()], None


def build_report(engine, email: str, schema_name: str = DEFAULT_SCHEMA) -> Dict[str, Any]:
    """Collect everything the database holds about the person with this email."""
    email = normalize_email(email)
    _ident(schema_name)  # rejects anything that is not a plain schema name

    tables: Dict[str, Any] = {}
    skipped: Dict[str, str] = {}
    with engine.connect() as conn:
        insp = inspect(conn)
        found = resolve_identifiers(conn, insp, schema_name, email)
        for source in SOURCES:
            rows, reason = _search_source(conn, insp, schema_name, source, found)
            if reason:
                skipped[source.name] = reason
                continue
            tables[source.name] = {
                "table": f"{schema_name}.{source.table}",
                "count": len(rows),
                "rows": rows,
            }

    return {
        "report_id": str(uuid.uuid4()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "query": {"email": email, "schema": schema_name},
        "identifiers": found.as_dict(),
        "tables": tables,
        "skipped": skipped,
        "limitations": list(LIMITATIONS),
    }