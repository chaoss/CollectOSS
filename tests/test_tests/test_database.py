# SPDX-License-Identifier: MIT
import pytest
import sqlalchemy as s


def test_can_query_schema(new_blank_db):
    # Simple smoke test to ensure schemas/tables exist and are empty
    with new_blank_db.connect() as conn:

        count = conn.execute(s.sql.text("SELECT count(*) FROM augur_operations.config")).scalar()
        assert count == 0
