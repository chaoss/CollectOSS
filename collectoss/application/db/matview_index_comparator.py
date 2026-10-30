"""Autogenerate comparator for materialized view *index* changes.

``alembic_utils_extended``'s entity comparator detects view definition changes
and renders index creation alongside create/replace ops
(``render_post_create_entity``), but the registry's ``indexes`` list plays no
role in change *detection*: an index-only change produces an empty migration
(confirmed with the fork maintainer for v1.5.0).

This module closes that gap as a separate Alembic comparator — the approach
the maintainer suggested — emitting bare ``CreateIndexOp`` / ``DropIndexOp``
instead of rebuilding the view, so a populated matview keeps its data
(``CREATE INDEX`` on an existing matview is legal; no ``WITH NO DATA`` /
first-refresh-must-be-non-concurrent dance).

Comparison uses structured signatures — ``(name, unique, ordered column
names)`` — the same approach stock Alembic uses for table indexes. Indexes
bearing expressions (anything other than plain column references) compare by
name only: their DB-side rendering (``pg_get_indexdef``) is not reliably
comparable, so a content change to one requires renaming it or a hand-written
migration.

Import this module from the alembic ``env.py`` *after* ``register_entities``
has been called: the entity comparator must be registered first so that, when
a view's definition also changed, its pending CreateOp/ReplaceOp (which
already renders index creation) suppresses this comparator for that view.
Importing the module registers the comparator; there is nothing to call.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass

from alembic.autogenerate import comparators
from alembic.autogenerate.api import AutogenContext
from alembic.operations import ops
from sqlalchemy import Column, text
from sqlalchemy.engine import Connection

from alembic_utils_extended.pg_materialized_view import PGMaterializedView
from alembic_utils_extended.reversible_op import CreateOp, ReplaceOp

from collectoss.application.db.materialized_views import MATERIALIZED_VIEWS, MaterializedView


@dataclass(frozen=True)
class _IndexSig:
    """Comparison signature for one index.

    ``columns`` is ``None`` for expression-bearing indexes, which compare by
    name only (see module docstring).
    """

    name: str
    unique: bool
    columns: tuple[str, ...] | None


_PLAIN_IDENTIFIER = re.compile(r'^"?(\w+)"?$')

# "CREATE [UNIQUE] INDEX name ON [schema.]table USING method (cols) ..."
# (pg_get_indexdef always emits the USING clause)
_COL_LIST = re.compile(r"\bON\s+(?:[\w\"]+\.)?[\w\"]+\s+USING\s+\w+\s*\(", re.IGNORECASE)


def _local_index_sigs(view: MaterializedView) -> dict[str, _IndexSig]:
    """Signatures for a registry view's ``Index`` declarations, by name."""
    sigs: dict[str, _IndexSig] = {}
    for index in view.indexes or []:
        if not index.name:
            raise ValueError(
                f"Unnamed index on materialized view '{view.schema}.{view.signature}'. "
                "All indexes must have a name for autogenerate support."
            )
        columns: list[str] | None = []
        for expr in index.expressions:
            if isinstance(expr, str):
                columns.append(expr.lower())
            elif isinstance(expr, Column):
                columns.append(expr.name.lower())
            else:
                # Expression index: not reliably comparable, name-only.
                columns = None
                break
        sigs[index.name] = _IndexSig(index.name, bool(index.unique), tuple(columns) if columns else None)
    return sigs


def _parse_indexdef_columns(indexdef: str) -> tuple[str, ...] | None:
    """Extract the ordered plain-column names from a ``pg_get_indexdef`` string.

    Returns ``None`` when the index bears expressions (any element that is
    not a plain identifier) or does not parse.
    """
    match = _COL_LIST.search(indexdef)
    if match is None:
        return None

    # Walk from just past the opening paren to its matching close.
    start = match.end()
    depth = 1
    i = start
    while i < len(indexdef) and depth > 0:
        if indexdef[i] == "(":
            depth += 1
        elif indexdef[i] == ")":
            depth -= 1
        i += 1
    col_list = indexdef[start : i - 1]

    # Split on top-level commas only (expressions may contain commas).
    elements: list[str] = []
    buf = ""
    depth = 0
    for char in col_list:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if char == "," and depth == 0:
            elements.append(buf.strip())
            buf = ""
        else:
            buf += char
    if buf.strip():
        elements.append(buf.strip())

    columns: list[str] = []
    for element in elements:
        ident = _PLAIN_IDENTIFIER.match(element)
        if ident is None:
            return None
        columns.append(ident.group(1).lower())
    return tuple(columns)


# Matviews cannot have PRIMARY KEYs or table constraints, so — unlike the
# fork's table index comparator — no pg_constraint exclusion is needed.
_DB_INDEX_SQL = text(
    """
    SELECT t.relname AS table_name,
           c.relname AS index_name,
           pg_get_indexdef(i.indexrelid) AS indexdef,
           i.indisunique AS is_unique
    FROM pg_index i
    JOIN pg_class c ON c.oid = i.indexrelid
    JOIN pg_class t ON t.oid = i.indrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = :schema
      AND t.relname = ANY(:view_names)
    """
)


def _db_index_sigs(
    connection: Connection, schema: str, view_names: list[str]
) -> dict[str, dict[str, _IndexSig]]:
    """Live index signatures per view, from ``pg_index`` directly.

    Returns ``{view_name: {index_name: sig}}``. Views absent from the result
    do not exist in the database (the entity comparator handles those).
    """
    rows = connection.execute(_DB_INDEX_SQL, {"schema": schema, "view_names": view_names}).fetchall()

    result: dict[str, dict[str, _IndexSig]] = defaultdict(dict)
    for row in rows:
        result[row.table_name][row.index_name] = _IndexSig(
            name=row.index_name,
            unique=bool(row.is_unique),
            columns=_parse_indexdef_columns(row.indexdef),
        )
    return dict(result)


@comparators.dispatch_for("schema")
def compare_matview_indexes(
    autogen_context: AutogenContext,
    upgrade_ops: ops.UpgradeOps,
    _schemas: list[str | None],
) -> None:
    """Diff registered matview indexes against the live database.

    Emits CreateIndexOp / DropIndexOp for added, removed, renamed, and
    changed indexes. A changed index under a stable name is emitted as a
    drop + create pair. Views with a pending CreateOp/ReplaceOp from the
    entity comparator are skipped: those ops already render index creation
    (see module docstring for the import-order requirement this relies on).
    """
    connection = autogen_context.connection
    if connection is None:
        # Offline autogenerate has no live database to diff against.
        return

    # Views whose create/replace is already pending from the entity
    # comparator — emitting index ops for them here would duplicate the ops
    # its rendering produces.
    pending_entity_views = {
        op.target.signature
        for op in upgrade_ops.ops
        if isinstance(op, (CreateOp, ReplaceOp)) and isinstance(op.target, PGMaterializedView)
    }
    views = [view for view in MATERIALIZED_VIEWS if view.signature not in pending_entity_views]

    by_schema: dict[str, list[MaterializedView]] = defaultdict(list)
    for view in views:
        by_schema[view.schema].append(view)

    for schema, schema_views in by_schema.items():
        db_views = _db_index_sigs(connection, schema, [v.signature for v in schema_views])

        for view in schema_views:
            db_sigs = db_views.get(view.signature)
            if db_sigs is None:
                # View missing from the database and no pending entity op:
                # creating indexes now would fail, so leave it alone.
                continue

            local_sigs = _local_index_sigs(view)

            for name, local in local_sigs.items():
                db = db_sigs.get(name)
                if db is None:
                    # Added (or renamed-to) index.
                    upgrade_ops.ops.append(
                        ops.CreateIndexOp(
                            index_name=name,
                            table_name=view.signature,
                            columns=list(local.columns) if local.columns is not None else [],
                            schema=schema,
                            unique=local.unique,
                        )
                    )
                elif (local.unique, local.columns) != (db.unique, db.columns) and not (
                    local.columns is None or db.columns is None
                ):
                    # Changed under a stable name (unique flag or column
                    # list): CREATE INDEX cannot overwrite, so drop + create.
                    # (If either side is expression-bearing — columns is None
                    # — the comparison above is name-only; skip.)
                    upgrade_ops.ops.append(
                        ops.DropIndexOp(
                            index_name=name,
                            table_name=view.signature,
                            schema=schema,
                            _reverse=ops.CreateIndexOp(
                                index_name=name,
                                table_name=view.signature,
                                columns=list(db.columns),
                                schema=schema,
                                unique=db.unique,
                            ),
                        )
                    )
                    upgrade_ops.ops.append(
                        ops.CreateIndexOp(
                            index_name=name,
                            table_name=view.signature,
                            columns=list(local.columns),
                            schema=schema,
                            unique=local.unique,
                        )
                    )

            for name, db in db_sigs.items():
                if name not in local_sigs:
                    # Removed (or renamed-from) index. Columns are attached
                    # to the reverse op only when parseable, so the
                    # downgrade recreates it faithfully.
                    upgrade_ops.ops.append(
                        ops.DropIndexOp(
                            index_name=name,
                            table_name=view.signature,
                            schema=schema,
                            _reverse=ops.CreateIndexOp(
                                index_name=name,
                                table_name=view.signature,
                                columns=list(db.columns) if db.columns is not None else [],
                                schema=schema,
                                unique=db.unique,
                            )
                            if db.columns is not None
                            else None,
                        )
                    )
