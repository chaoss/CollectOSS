# SPDX-License-Identifier: MIT
import pytest
import sqlalchemy as s

@pytest.mark.integration
def test_can_query_schema(clean_db):
    # Simple smoke test to ensure schemas/tables exist and are empty
    with clean_db.connect() as conn:

        count = conn.execute(s.sql.text("SELECT count(*) FROM augur_operations.config")).scalar()
        assert count == 0
