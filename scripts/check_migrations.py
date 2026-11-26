"""Validate Alembic migration files without requiring a database."""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Iterable

MIGRATION_FILENAME = re.compile(r"^(?P<revision>\d+)_.*\.py$")
DEFAULT_FORBIDDEN_MODULES = ("collectoss.application.db.models",)


def validate_filename(migration: Path) -> list[str]:
    """Validate the migration filename convention."""
    if MIGRATION_FILENAME.fullmatch(migration.name):
        return []
    return [f"{migration.name}: migration filename must use '<number>_<description>.py'"]


def validate_revision_number(migration: Path) -> list[str]:
    """Ensure the numeric filename prefix matches Alembic's revision value."""
    match = MIGRATION_FILENAME.fullmatch(migration.name)
    if not match:
        return []

    try:
        tree = ast.parse(migration.read_text(encoding="utf-8"), filename=str(migration))
    except (SyntaxError, UnicodeDecodeError) as exc:
        return [f"{migration.name}: unable to parse migration: {exc}"]

    revision_value = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "revision"
            for target in node.targets
        ):
            revision_value = node.value
            break
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "revision":
            revision_value = node.value
            break

    if revision_value is None:
        return [f"{migration.name}: migration must define a revision value"]

    try:
        revision = str(ast.literal_eval(revision_value))
    except (ValueError, TypeError):
        return [f"{migration.name}: revision must be a literal string or integer"]

    filename_revision = match.group("revision")
    if revision != filename_revision:
        return [
            f"{migration.name}: filename revision {filename_revision} "
            f"does not match migration revision {revision}"
        ]
    return []


def _module_matches(module: str, forbidden_module: str) -> bool:
    return module == forbidden_module or module.startswith(f"{forbidden_module}.")


def _imports_forbidden_module(node: ast.AST, forbidden_module: str) -> bool:
    if isinstance(node, ast.Import):
        return any(_module_matches(alias.name, forbidden_module) for alias in node.names)

    if isinstance(node, ast.ImportFrom):
        imported_module = node.module or ""
        if _module_matches(imported_module, forbidden_module):
            return True
        return any(
            _module_matches(
                f"{imported_module}.{alias.name}" if imported_module else alias.name,
                forbidden_module,
            )
            for alias in node.names
        )

    return False


def validate_imports(migration: Path, forbidden_modules: Iterable[str]) -> list[str]:
    """Reject imports from or underneath any configured module."""
    forbidden_modules = tuple(forbidden_modules)
    try:
        syntax_tree = ast.parse(
            migration.read_text(encoding="utf-8"),
            filename=str(migration),
        )
    except (SyntaxError, UnicodeDecodeError) as exc:
        return [f"{migration.name}: unable to parse migration: {exc}"]

    errors = []
    for node in ast.walk(syntax_tree):
        for module in forbidden_modules:
            if _imports_forbidden_module(node, module):
                errors.append(
                    f"{migration.name}:{getattr(node, 'lineno', 1)}: "
                    f"migration must not import from {module}"
                )
    return errors


def validate_migration(
    migration: Path,
    forbidden_modules: Iterable[str] = DEFAULT_FORBIDDEN_MODULES,
) -> list[str]:
    """Run every validation rule against one migration file."""
    migration = Path(migration).resolve()
    if not migration.is_file():
        return [f"{migration}: migration file does not exist"]

    errors = validate_filename(migration)
    errors.extend(validate_revision_number(migration))
    errors.extend(validate_imports(migration, forbidden_modules))
    return errors


def validate_migrations(
    migration_files: Iterable[Path],
    forbidden_modules: Iterable[str] = DEFAULT_FORBIDDEN_MODULES,
) -> list[str]:
    """Return validation errors for the supplied migration files."""
    forbidden_modules = tuple(forbidden_modules)
    return [
        error
        for migration_file in migration_files
        for error in validate_migration(Path(migration_file), forbidden_modules)
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "migration_files",
        nargs="+",
        type=Path,
        help="Migration file paths to validate (either relative to the repository root or absolute)",
    )
    parser.add_argument(
        "--forbidden-module",
        action="append",
        dest="forbidden_modules",
        help=(
            "Module that migrations must not import from or underneath; "
            "may be supplied more than once"
        ),
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    migration_files = [
        path if path.is_absolute() else repo_root / path
        for path in args.migration_files
    ]
    forbidden_modules = args.forbidden_modules or list(DEFAULT_FORBIDDEN_MODULES)
    errors = validate_migrations(migration_files, forbidden_modules)
    if errors:
        print("Database migration checks failed:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)

    print(f"Database migration checks passed for {len(migration_files)} provided migration(s).")
