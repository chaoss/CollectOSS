# SPDX-License-Identifier: MIT
import pytest
import sqlalchemy as s

@pytest.mark.integration
def test_can_query_schema(clean_schema_db):
    """This test uses a fixture to get a clean (empty) database with a valid CollectOSS schema

    It is used as a sanity check to make sure database-backed testing infrastructure is working correctly
    """
    # Simple smoke test to ensure schemas/tables exist and are empty
    with clean_schema_db.connect() as conn:

        count = conn.execute(s.sql.text("SELECT count(*) FROM operations.config")).scalar()
        assert count == 0
