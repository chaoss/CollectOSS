import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_migrations import get_changed_migration_files, validate_migrations


class GetChangedMigrationFilesTests(unittest.TestCase):
    BASE_SHA = "a" * 40
    HEAD_SHA = "b" * 40

    @patch("scripts.check_migrations.subprocess.run")
    def test_rejects_non_commit_refs_before_running_git(self, run):
        for base, head in (
            ("main", self.HEAD_SHA),
            (self.BASE_SHA, "--upload-pack=malicious"),
            ("a" * 39, self.HEAD_SHA),
        ):
            with self.subTest(base=base, head=head):
                with self.assertRaisesRegex(ValueError, "full 40-character commit SHAs"):
                    get_changed_migration_files(base, head, Path("/repo"))

        run.assert_not_called()

    @patch("scripts.check_migrations.shutil.which", return_value=None)
    @patch("scripts.check_migrations.subprocess.run")
    def test_fails_clearly_when_git_is_unavailable(self, run, which):
        with self.assertRaisesRegex(RuntimeError, "Git executable was not found"):
            get_changed_migration_files(self.BASE_SHA, self.HEAD_SHA, Path("/repo"))

        which.assert_called_once_with("git")
        run.assert_not_called()

    @patch("scripts.check_migrations.subprocess.run")
    @patch("scripts.check_migrations.shutil.which", return_value="relative/git")
    def test_uses_absolute_git_path_and_only_returns_migration_files(self, which, run):
        run.return_value.stdout = (
            "collectoss/application/schema/alembic/versions/12_add_table.py\n"
            "scripts/check_migrations.py\n"
            "collectoss/application/schema/alembic/versions/__init__.py\n"
            "collectoss/application/schema/alembic/versions/nested/13_other.py\n"
        )

        changed = get_changed_migration_files(self.BASE_SHA, self.HEAD_SHA, Path("/repo"))

        self.assertEqual(
            changed,
            [Path("/repo/collectoss/application/schema/alembic/versions/12_add_table.py")],
        )
        which.assert_called_once_with("git")
        run.assert_called_once_with(
            [
                str(Path("relative/git").resolve()),
                "diff",
                "--name-only",
                "--diff-filter=ACMRT",
                f"{self.BASE_SHA}...{self.HEAD_SHA}",
            ],
            cwd=Path("/repo"),
            check=True,
            capture_output=True,
            text=True,
        )


class ValidateMigrationsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.migrations_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_migration(self, filename, content="revision = '1'\n"):
        path = self.migrations_dir / filename
        path.write_text(content, encoding="utf-8")
        return path

    def test_accepts_unique_revision_without_model_imports(self):
        changed = self.write_migration("2_add_table.py", "from alembic import op\nrevision = '2'\n")
        self.write_migration("1_initial.py")

        self.assertEqual(validate_migrations(self.migrations_dir, [changed]), [])

    def test_rejects_duplicate_revision_number(self):
        changed = self.write_migration("2_add_table.py")
        self.write_migration("2_add_index.py")

        errors = validate_migrations(self.migrations_dir, [changed])

        self.assertEqual(len(errors), 1)
        self.assertIn("migration revision 2 is duplicated", errors[0])

    def test_rejects_direct_database_model_imports(self):
        changed = self.write_migration(
            "3_add_table.py",
            "from collectoss.application.db.models import Repo\nrevision = '3'\n",
        )

        errors = validate_migrations(self.migrations_dir, [changed])

        self.assertEqual(len(errors), 1)
        self.assertIn("must not import from collectoss.application.db.models", errors[0])

    def test_rejects_models_imported_from_database_package(self):
        changed = self.write_migration(
            "4_add_table.py",
            "from collectoss.application.db import models\nrevision = '4'\n",
        )

        errors = validate_migrations(self.migrations_dir, [changed])

        self.assertEqual(len(errors), 1)
        self.assertIn("must not import from collectoss.application.db.models", errors[0])

    def test_ignores_model_imports_in_unchanged_migrations(self):
        changed = self.write_migration("5_add_table.py")
        self.write_migration(
            "1_legacy.py",
            "from collectoss.application.db.models import Repo\nrevision = '1'\n",
        )

        self.assertEqual(validate_migrations(self.migrations_dir, [changed]), [])

    def test_rejects_unrecognized_migration_filename(self):
        changed = self.write_migration("add_table.py")

        errors = validate_migrations(self.migrations_dir, [changed])

        self.assertEqual(len(errors), 1)
        self.assertIn("<number>_<description>.py", errors[0])

    def test_ignores_model_names_in_comments_and_strings(self):
        changed = self.write_migration(
            "6_add_table.py",
            "# from collectoss.application.db.models import Repo\n"
            "description = 'collectoss.application.db.models.Repo'\nrevision = '6'\n",
        )

        self.assertEqual(validate_migrations(self.migrations_dir, [changed]), [])


if __name__ == "__main__":
    unittest.main()
