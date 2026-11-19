# SPDX-License-Identifier: MIT
"""Guards for the personal-data lookup in collectoss.application.db.lib.

These tests read only the model metadata, so they need no database.
"""
from sqlalchemy import String

from collectoss.application.db import lib
from collectoss.application.db.models.base import Base

# Email-looking columns that are deliberately not searched for a contributor.
# Add a column here only after deciding it does not hold a contributor's personal data.
EXCLUDED = {
    # Not reviewed yet: decide with the maintainers whether these belong in the lookup.
    "data.repo_groups_list_serve.rgls_email",
    "data.chaoss_user.chaoss_email",
    # Accounts of people who registered on this instance (operations.users). A different
    # kind of identity from contributors (no link to contributors.cntrb_id), and the table
    # holds secrets (password hash, session tokens, API keys) that must never be exported.
    # Needs its own design: see the PR discussion.
    "operations.users.email",
}


def _name(column):
    return f"{column.table.fullname}.{column.name}"


def test_every_email_column_is_searched_or_excluded():
    searched = {_name(c) for c in lib._table_columns(lib.PERSONAL_EMAIL_COLUMNS)}
    email_columns = {
        _name(column)
        for table in Base.metadata.tables.values()
        for column in table.columns
        if "email" in column.name.lower() and isinstance(column.type, String)
    }
    unhandled = email_columns - searched - EXCLUDED
    assert not unhandled, (
        f"email columns not covered by the personal-data lookup: {sorted(unhandled)}. "
        "Add them to PERSONAL_EMAIL_COLUMNS in db/lib.py, or to EXCLUDED here with a reason."
    )


def test_foreign_key_walk_finds_the_known_contributor_references():
    id_columns, login_columns = lib.get_contributor_reference_columns()
    ids = {_name(c) for c in id_columns}
    logins = {_name(c) for c in login_columns}

    assert {
        "data.contributors.cntrb_id",
        "data.contributors_aliases.cntrb_id",
        "data.commits.cmt_ght_author_id",
        "data.issues.reporter_id",
        "data.issues.cntrb_id",
        "data.message.cntrb_id",
        "data.pull_requests.pr_augur_contributor_id",
        "data.pull_request_commits.pr_cmt_author_cntrb_id",
    } <= ids
    assert "data.commits.cmt_author_platform_username" in logins


def test_all_searched_columns_are_in_a_schema_we_search():
    # data is the main schema; spdx.creators holds SBOM creator emails
    for group in (
        lib.PERSONAL_EMAIL_COLUMNS,
        lib.PERSONAL_LOGIN_COLUMNS,
        lib.PERSONAL_EMBEDDED_EMAIL_COLUMNS,
    ):
        for column in lib._table_columns(group):
            assert column.table.schema in {"data", "spdx"}, _name(column)


def test_release_author_is_matched_as_an_embedded_email_not_as_a_login():
    # release_author holds "<name>_<email>" or "<name>_<company>", never a bare login
    embedded = {_name(c) for c in lib._table_columns(lib.PERSONAL_EMBEDDED_EMAIL_COLUMNS)}
    logins = {_name(c) for c in lib._table_columns(lib.PERSONAL_LOGIN_COLUMNS)}
    assert "data.releases.release_author" in embedded
    assert "data.releases.release_author" not in logins