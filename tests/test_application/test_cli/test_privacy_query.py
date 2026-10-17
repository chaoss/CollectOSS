# SPDX-License-Identifier: MIT
"""Tests for the privacy query. They use made-up people and an in-memory SQLite
database with the tables attached as the ``data`` schema, so no server is needed."""
import json
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from collectoss.application.privacy import build_report

ADA = "11111111-1111-1111-1111-111111111111"
BOB = "22222222-2222-2222-2222-222222222222"

SCHEMA_SQL = (
    """CREATE TABLE data.contributors (
        cntrb_id TEXT PRIMARY KEY, cntrb_login TEXT, cntrb_email TEXT,
        cntrb_full_name TEXT, cntrb_canonical TEXT, gh_login TEXT, gl_username TEXT)""",
    """CREATE TABLE data.contributors_aliases (
        cntrb_alias_id INTEGER PRIMARY KEY, cntrb_id TEXT, alias_email TEXT, canonical_email TEXT)""",
    """CREATE TABLE data.commits (
        cmt_id INTEGER PRIMARY KEY, repo_id INTEGER, cmt_commit_hash TEXT,
        cmt_author_name TEXT, cmt_author_email TEXT, cmt_author_raw_email TEXT,
        cmt_author_platform_username TEXT, cmt_ght_author_id TEXT,
        cmt_committer_name TEXT, cmt_committer_email TEXT, cmt_committer_raw_email TEXT)""",
    """CREATE TABLE data.message (msg_id INTEGER PRIMARY KEY, cntrb_id TEXT, msg_text TEXT)""",
    """CREATE TABLE data.pull_request_commits (
        pr_cmt_id INTEGER PRIMARY KEY, pr_cmt_author_cntrb_id TEXT, pr_cmt_author_email TEXT)""",
)

ROWS_SQL = (
    f"""INSERT INTO data.contributors VALUES
        ('{ADA}', 'adaex', 'Ada@Example.test', 'Ada Example', 'ada@example.test', 'adaex', NULL),
        ('{BOB}', 'bobby', 'bob@example.test', 'Bob Builder', 'bob@example.test', 'bobby', NULL)""",
    f"""INSERT INTO data.contributors_aliases VALUES
        (1, '{ADA}', 'ada.work@example.test', 'ada@example.test')""",
    # c1: Ada authored, Bob committed. c2: Bob authored, Ada committed (work email).
    # c3: Bob only.
    f"""INSERT INTO data.commits VALUES
        (1, 1, 'c1', 'Ada Example', 'ada@example.test', 'ada@example.test', 'adaex', '{ADA}',
            'Bob Builder', 'bob@example.test', 'bob@example.test'),
        (2, 1, 'c2', 'Bob Builder', 'bob@example.test', 'bob@example.test', 'bobby', '{BOB}',
            'Ada Example', 'ada.work@example.test', 'ada.work@example.test'),
        (3, 1, 'c3', 'Bob Builder', 'bob@example.test', 'bob@example.test', 'bobby', '{BOB}',
            'Bob Builder', 'bob@example.test', 'bob@example.test')""",
    f"""INSERT INTO data.message VALUES (1, '{ADA}', 'hello from ada'), (2, '{BOB}', 'hello from bob')""",
    f"""INSERT INTO data.pull_request_commits VALUES (1, '{ADA}', 'ada@example.test')""",
)


@pytest.fixture
def engine():
    engine = create_engine("sqlite://", poolclass=StaticPool)
    with engine.begin() as conn:
        conn.exec_driver_sql("ATTACH DATABASE ':memory:' AS data")
        for statement in SCHEMA_SQL + ROWS_SQL:
            conn.execute(text(statement))
    return engine


def test_email_resolves_to_other_emails_logins_and_contributor_id(engine):
    found = build_report(engine, "ada@example.test")["identifiers"]
    assert found["contributor_ids"] == [ADA]
    assert found["logins"] == ["adaex"]
    assert "ada.work@example.test" in found["emails"]


def test_matching_ignores_case_and_surrounding_spaces(engine):
    found = build_report(engine, "  ADA@EXAMPLE.TEST ")["identifiers"]
    assert found["contributor_ids"] == [ADA]


def test_an_alias_email_finds_the_same_person(engine):
    found = build_report(engine, "ada.work@example.test")["identifiers"]
    assert found["contributor_ids"] == [ADA]


def test_commits_are_split_by_role_and_hide_the_other_party(engine):
    tables = build_report(engine, "ada@example.test")["tables"]

    authored = tables["commits_as_author"]
    assert [r["cmt_commit_hash"] for r in authored["rows"]] == ["c1"]
    assert not any(key.startswith("cmt_committer") for key in authored["rows"][0])

    committed = tables["commits_as_committer"]
    assert [r["cmt_commit_hash"] for r in committed["rows"]] == ["c2"]
    assert not any(key.startswith("cmt_author") for key in committed["rows"][0])


def test_nothing_about_other_people_appears_in_the_report(engine):
    report = build_report(engine, "ada@example.test")
    assert report["tables"]["contributors"]["count"] == 1
    assert [r["msg_text"] for r in report["tables"]["message"]["rows"]] == ["hello from ada"]
    dumped = json.dumps(report)
    assert "bob@example.test" not in dumped
    assert "Bob Builder" not in dumped
    assert BOB not in dumped


def test_an_unknown_email_gives_an_empty_report(engine):
    report = build_report(engine, "nobody@example.test")
    assert report["identifiers"]["contributor_ids"] == []
    assert report["identifiers"]["emails"] == ["nobody@example.test"]
    assert all(t["count"] == 0 for t in report["tables"].values())


def test_tables_missing_from_the_database_are_reported_as_skipped(engine):
    report = build_report(engine, "ada@example.test")
    assert report["skipped"]["issues"] == "table not found"
    assert "commits_as_author" in report["tables"]


def test_a_wrong_schema_gives_a_clear_error(engine):
    with pytest.raises(LookupError, match="contributors not found"):
        build_report(engine, "ada@example.test", schema_name="augur_data")


@pytest.mark.parametrize("email", ["", "not-an-email", "a@b c"])
def test_a_bad_email_is_rejected(engine, email):
    with pytest.raises(ValueError):
        build_report(engine, email)


def test_a_schema_name_cannot_carry_sql(engine):
    with pytest.raises(ValueError):
        build_report(engine, "ada@example.test", schema_name="data; DROP TABLE x")


def test_the_report_is_plain_json_with_a_report_id(engine):
    report = build_report(engine, "ada@example.test")
    assert uuid.UUID(report["report_id"])
    assert json.loads(json.dumps(report)) == report