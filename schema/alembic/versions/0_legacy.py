"""Goodbye, .sql migrations

Revision ID: 73ebe53353af
Revises:
Create Date: 2022-05-14 18:22:34.335494
"""
from alembic import op
import sqlalchemy as sa
from pathlib import Path
from glob import glob
import logging
from sqlalchemy.sql import text
from sqlalchemy.exc import ProgrammingError
import re

# revision identifiers, used by Alembic.
revision = "0"
down_revision = None
branch_labels = None
depends_on = None

logger = logging.getLogger("alembic.runtime.migration")

def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    # thanks Claudiu and KetZoomer - https://stackoverflow.com/a/16090640
    return [int(text) if text.isdigit() else text.lower()
            for text in _nsre.split(s)]


def upgrade():
    # try:
    with op.get_context().autocommit_block():
        try:
            version_rows = op.execute(
                """SELECT "value"::int FROM augur_settings WHERE setting = 'augur_data_version'"""
            )
            augur_version = int(version_rows[0][0])
            logger.info(f"Currently on legacy migration version {augur_version}")
        except:
            # database has never been created
            augur_version = 79
            logger.info(f"New database, will run all legacy migrations")
    legacy_folder = Path(__file__).parent / "legacy"
    relevant_legacy_migrations = filter(
       lambda x: int(str(x.name).split(".")[0]) > augur_version,
       legacy_folder.glob("*.sql"),
    )
    ordered_legacy_migrations = list(
        sorted(
            (f.name for f in relevant_legacy_migrations),
            key=natural_sort_key,
        )
    )
    for legacy_migration_filename in ordered_legacy_migrations:
        legacy_migration_file_path = legacy_folder / legacy_migration_filename
        with legacy_migration_file_path.open() as legacy_migration_file:
            logger.info(f"Running legacy migration {legacy_migration_filename}")
            op.execute(legacy_migration_file.read())


def downgrade():
    op.execute(
        text(
            """
            DROP SCHEMA IF EXISTS augur_data CASCADE;
            DROP SCHEMA IF EXISTS augur_operations CASCADE;
            DROP SCHEMA IF EXISTS spdx CASCADE;
            DROP SCHEMA IF EXISTS toss_specific CASCADE;
            """
        )
    )
