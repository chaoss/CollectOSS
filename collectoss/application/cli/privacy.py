# SPDX-License-Identifier: MIT
"""
CollectOSS commands for finding the personal data an instance holds about a person.

Running the script:
Query command: collectoss privacy query <email> [--output report.json]
"""
import json
import os

import click

from collectoss.application.cli import (
    test_connection,
    test_db_connection,
    with_database,
    DatabaseContext,
)
from collectoss.application.privacy import DEFAULT_SCHEMA, build_report


@click.group("privacy", short_help="Find the personal data held about a person")
@click.pass_context
def cli(ctx):
    ctx.obj = DatabaseContext()


@cli.command("query")
@click.argument("email")
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False),
    help="Write the JSON report to this file instead of stdout. "
    "A new file is created readable by its owner only.",
)
@click.option(
    "--schema",
    default=DEFAULT_SCHEMA,
    show_default=True,
    help="Database schema that holds the CollectOSS tables.",
)
@test_connection
@test_db_connection
@with_database
@click.pass_context
def query(ctx, email, output, schema):
    """Report the personal data held about the person with this EMAIL.

    The email is expanded to the person's other emails, logins and contributor
    ids, and every matching row is returned as JSON. Nothing is changed.
    """
    try:
        report = build_report(ctx.obj.engine, email, schema)
    except (ValueError, LookupError) as error:
        raise click.ClickException(str(error))

    body = json.dumps(report, indent=2)
    if output:
        descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as report_file:
            report_file.write(body)
        click.echo(f"Report written to {output}", err=True)
    else:
        click.echo(body)

    # The summary goes to stderr so that stdout stays valid JSON.
    for name, found in report["tables"].items():
        if found["count"]:
            click.echo(f"  {name}: {found['count']} row(s)", err=True)