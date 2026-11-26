import tempfile
import unittest
from pathlib import Path

import pytest

from scripts.check_migrations import (
    validate_filename,
    validate_imports,
    validate_migration,
    validate_migrations,
    validate_revision_number,
)

pytestmark = pytest.mark.unit


class MigrationChecksTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.migrations_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_migration(self, filename, content="revision = '1'\n"):
        path = self.migrations_dir / filename
        path.write_text(content, encoding="utf-8")
        return path

    def test_accepts_valid_migration(self):
        migration = self.write_migration(
            "2_add_table.py",
            "from alembic import op\nrevision = '2'\n",
        )
        self.assertEqual(validate_migration(migration), [])

    def test_rejects_unrecognized_filename(self):
        migration = self.write_migration("add_table.py")
        errors = validate_filename(migration)
        self.assertEqual(len(errors), 1)
        self.assertIn("<number>_<description>.py", errors[0])

    def test_accepts_numeric_revision_filename(self):
        migration = self.write_migration("12_add_table.py", "revision = 12\n")
        self.assertEqual(validate_filename(migration), [])
        self.assertEqual(validate_revision_number(migration), [])

    def test_rejects_filename_revision_mismatch(self):
        migration = self.write_migration("12_add_table.py", "revision = '11'\n")
        errors = validate_revision_number(migration)
        self.assertEqual(len(errors), 1)
        self.assertIn("does not match migration revision 11", errors[0])

    def test_requires_revision_assignment(self):
        migration = self.write_migration("12_add_table.py", "down_revision = None\n")
        self.assertIn("must define a revision value", validate_revision_number(migration)[0])

    def test_rejects_non_literal_revision(self):
        migration = self.write_migration("12_add_table.py", "revision = make_revision()\n")
        self.assertIn("must be a literal", validate_revision_number(migration)[0])

    def test_rejects_direct_forbidden_import(self):
        migration = self.write_migration(
            "3_add_table.py",
            "from collectoss.application.db.models import Repo\n",
        )
        errors = validate_imports(migration, ["collectoss.application.db.models"])
        self.assertEqual(len(errors), 1)

    def test_rejects_nested_forbidden_import(self):
        migration = self.write_migration(
            "4_add_table.py",
            "import collectoss.application.db.models.internal\n",
        )
        self.assertEqual(
            len(validate_imports(migration, ["collectoss.application.db.models"])),
            1,
        )

    def test_rejects_imported_forbidden_submodule(self):
        migration = self.write_migration(
            "5_add_table.py",
            "from collectoss.application.db import models\n",
        )
        self.assertEqual(
            len(validate_imports(migration, ["collectoss.application.db.models"])),
            1,
        )

    def test_supports_multiple_configured_modules(self):
        migration = self.write_migration(
            "6_add_table.py",
            "from collectoss.application.tasks.worker import run\n",
        )
        self.assertEqual(
            len(validate_imports(migration, iter([
                "collectoss.application.db.models",
                "collectoss.application.tasks",
            ]))),
            1,
        )

    def test_ignores_comments_and_strings(self):
        migration = self.write_migration(
            "7_add_table.py",
            "# from collectoss.application.db.models import Repo\n"
            "description = 'collectoss.application.db.models.Repo'\n",
        )
        self.assertEqual(validate_imports(migration, ["collectoss.application.db.models"]), [])

    def test_reports_syntax_errors(self):
        migration = self.write_migration("8_add_table.py", "def broken(:\n")
        errors = validate_imports(migration, ["collectoss.application.db.models"])
        self.assertEqual(len(errors), 1)
        self.assertIn("unable to parse migration", errors[0])

    def test_reports_invalid_utf8(self):
        migration = self.migrations_dir / "9_add_table.py"
        migration.write_bytes(bytes([255]))
        errors = validate_imports(migration, ["collectoss.application.db.models"])
        self.assertEqual(len(errors), 1)
        self.assertIn("unable to parse migration", errors[0])

    def test_reports_missing_file(self):
        missing = self.migrations_dir / "10_missing.py"
        errors = validate_migration(missing)
        self.assertEqual(len(errors), 1)
        self.assertIn("does not exist", errors[0])

    def test_validates_multiple_changed_files(self):
        valid = self.write_migration("11_add_table.py", "revision = '11'\n")
        invalid = self.write_migration(
            "12_add_table.py",
            "revision = '12'\nfrom collectoss.application.db.models import Repo\n",
        )
        errors = validate_migrations([valid, invalid])
        self.assertEqual(len(errors), 1)
        self.assertIn("12_add_table.py", errors[0])


if __name__ == "__main__":
    unittest.main()
