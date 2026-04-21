"""Generate a Graphviz .dot file from SQLAlchemy models."""
from collectoss.application.db.models.base import Base
import collectoss.application.db.models.augur_data
import collectoss.application.db.models.augur_operations
import collectoss.application.db.models.spdx


def generate_dot(metadata):
    lines = [
        'digraph schema {',
        '    rankdir=LR;',
        '    node [shape=plaintext, fontsize=10];',
        '    edge [arrowhead=crow, arrowtail=none, dir=both];',
        '',
    ]

    for table_name, table in sorted(metadata.tables.items()):
        pk_cols = {col.name for col in table.primary_key.columns}
        fk_cols = {fk.parent.name for fk in table.foreign_keys}

        label_rows = []
        for col in table.columns:
            markers = []
            if col.name in pk_cols:
                markers.append("PK")
            if col.name in fk_cols:
                markers.append("FK")
            prefix = f"[{','.join(markers)}] " if markers else ""
            label_rows.append(
                f'<TR><TD ALIGN="LEFT" PORT="{col.name}">'
                f'{prefix}{col.name} : {col.type}</TD></TR>'
            )

        rows_str = "".join(label_rows)
        label = (
            f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0">'
            f'<TR><TD BGCOLOR="lightblue"><B>{table_name}</B></TD></TR>'
            f'{rows_str}</TABLE>>'
        )
        safe_name = table_name.replace(".", "__")
        lines.append(f'    "{safe_name}" [label={label}];')

    lines.append('')

    seen = set()
    for table_name, table in metadata.tables.items():
        for fk in table.foreign_keys:
            src = table_name.replace(".", "__")
            dst = fk.column.table.fullname.replace(".", "__")
            edge = (src, fk.parent.name, dst, fk.column.name)
            if edge not in seen:
                seen.add(edge)
                lines.append(
                    f'    "{src}":{fk.parent.name} -> '
                    f'"{dst}":{fk.column.name};'
                )

    lines.append('}')
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate_dot(Base.metadata))



    # dnf install graphviz
    # uv run ./generate_dot.py > schema.dot
    # uv run dot -Tsvg schema.dot -o schema.svg
