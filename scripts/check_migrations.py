"""Validate newly changed Alembic migrations without requiring a database."""

from __future__ import annotations

import argparse
import ast
import re
import shutil
import subprocess  # nosec B404 - the command is fixed and all arguments are validated.
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

MIGRATIONS_DIR = Path("collectoss/application/schema/alembic/versions")
MIGRATION_FILENAME = re.compile(r"^(?P<revision>\d+)_.*\.py$")
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
DATABASE_MODELS_MODULE = "collectoss.application.db.models"
DATABASE_MODULE = "collectoss.application.db"


def get_changed_migration_files(base: str, head: str, repo_root: Path) -> list[Path]:
    """Return added or modified top-level Alembic migration files in a PR diff."""
    if not COMMIT_SHA.fullmatch(base) or not COMMIT_SHA.fullmatch(head):
        raise ValueError("base and head must be full 40-character commit SHAs")

    git_executable = shutil.which("git")
    if git_executable is not None:
        git_executable = str(Path(git_executable).resolve())
    if git_executable is None:
        raise RuntimeError("Git executable was not found on PATH")

    result = subprocess.run(  # nosec B603 - absolute executable, validated SHAs, fixed arguments, no shell.
        [
            git_executable,
            "diff",
            "--name-only",
            "--diff-filter=ACMRT",
            f"{base}...{head}",
        ],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    migrations_dir = MIGRATIONS_DIR.as_posix()
    changed_files = []
    for filename in result.stdout.splitlines():
        path = Path(filename)
        if (
            path.parent.as_posix() == migrations_dir
            and path.suffix == ".py"
            and path.name != "__init__.py"
        ):
            changed_files.append(repo_root / path)
    return changed_files


def _imports_database_models(node: ast.AST) -> bool:
    if isinstance(node, ast.Import):
        return any(
            alias.name == DATABASE_MODELS_MODULE
            or alias.name.startswith(f"{DATABASE_MODELS_MODULE}.")
            for alias in node.names
        )

    if isinstance(node, ast.ImportFrom):
        module = node.module or ""
        if module == DATABASE_MODELS_MODULE or module.startswith(f"{DATABASE_MODELS_MODULE}."):
            return True
        return module == DATABASE_MODULE and any(
            alias.name == "models" or alias.name.startswith("models.")
            for alias in node.names
        )

    return False


def validate_migrations(migrations_dir: Path, changed_files: Iterable[Path]) -> list[str]:
    """Return validation errors for changed migrations only."""
    migrations_dir = Path(migrations_dir).resolve()
    all_migrations = sorted(
        path for path in migrations_dir.glob("*.py") if path.name != "__init__.py"
    )
    changed_migrations = []
    errors = []

    for changed_file in changed_files:
        path = Path(changed_file).resolve()
        if path.parent != migrations_dir or path.suffix != ".py" or not path.is_file():
            continue
        changed_migrations.append(path)
        if not MIGRATION_FILENAME.match(path.name):
            errors.append(
                f"{path.name}: migration filename must use '<number>_<description>.py'"
            )

    revisions: dict[str, list[Path]] = defaultdict(list)
    for migration in all_migrations:
        match = MIGRATION_FILENAME.match(migration.name)
        if match:
            revisions[match.group("revision")].append(migration)

    changed_revisions = {
        match.group("revision")
        for path in changed_migrations
        if (match := MIGRATION_FILENAME.match(path.name))
    }
    for revision in sorted(changed_revisions):
        duplicates = revisions[revision]
        if len(duplicates) > 1:
            names = ", ".join(path.name for path in duplicates)
            errors.append(f"migration revision {revision} is duplicated: {names}")

    for migration in changed_migrations:
        try:
            syntax_tree = ast.parse(migration.read_text(encoding="utf-8"), filename=str(migration))
        except (SyntaxError, UnicodeDecodeError) as exc:
            errors.append(f"{migration.name}: unable to parse migration: {exc}")
            continue

        for node in ast.walk(syntax_tree):
            if _imports_database_models(node):
                errors.append(
                    f"{migration.name}:{getattr(node, 'lineno', 1)}: "
                    "migration must not import from collectoss.application.db.models"
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="Pull request base commit SHA")
    parser.add_argument("--head", required=True, help="Pull request head commit SHA")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    migrations_dir = repo_root / MIGRATIONS_DIR
    changed_files = get_changed_migration_files(args.base, args.head, repo_root)
    if not changed_files:
        print("No changed Alembic migration files found; skipping migration checks.")
        return 0

    errors = validate_migrations(migrations_dir, changed_files)
    if errors:
        print("Database migration checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Database migration checks passed for {len(changed_files)} changed migration(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
