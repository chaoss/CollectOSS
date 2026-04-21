"""Generate a Graphviz .dot file from SQLAlchemy models."""
import sys
from collectoss.application.db.models.base import Base
import collectoss.application.db.models.augur_data
import collectoss.application.db.models.augur_operations
import collectoss.application.db.models.spdx

SCHEMA_STYLES = {
    "augur_data": {"header_bg": "#4A90D9", "header_font": "white", "border": "#4A90D9"},
    "augur_operations": {"header_bg": "#E67E22", "header_font": "white", "border": "#E67E22"},
    "spdx": {"header_bg": "#27AE60", "header_font": "white", "border": "#27AE60"},
    None: {"header_bg": "#AAAAAA", "header_font": "white", "border": "#AAAAAA"},
}


def generate_dot(metadata, schema_filter=None):
    tables = {}
    for table_name, table in sorted(metadata.tables.items()):
        if schema_filter and table.schema != schema_filter:
            continue
        tables[table_name] = table

    lines = [
        'digraph schema {',
        '    graph [',
        '        rankdir=LR,',
        '        overlap=false,',
        '        splines=ortho,',
        '        sep="+25,25",',
        '        nodesep=0.8,',
        '        ranksep=1.5,',
        '        fontsize=10,',
        '        pad=0.5',
        '    ];',
        '    node [shape=plaintext, fontsize=9];',
        '    edge [arrowhead=crow, arrowtail=none, dir=both, color="#666666"];',
        '',
    ]

    # Group tables into subgraphs by schema for better clustering
    by_schema = {}
    for table_name, table in tables.items():
        by_schema.setdefault(table.schema, []).append((table_name, table))

    for schema, schema_tables in sorted(by_schema.items(), key=lambda x: x[0] or ""):
        style = SCHEMA_STYLES.get(schema, SCHEMA_STYLES[None])
        lines.append(f'    subgraph "cluster_{schema or "default"}" {{')
        lines.append(f'        label="{schema or "default"}";')
        lines.append(f'        style=dashed;')
        lines.append(f'        color="{style["border"]}";')
        lines.append(f'        fontsize=14;')
        lines.append(f'        fontcolor="{style["border"]}";')
        lines.append('')

        for table_name, table in schema_tables:
            pk_cols = {col.name for col in table.primary_key.columns}
            fk_cols = {fk.parent.name for fk in table.foreign_keys}

            label_rows = []
            for col in table.columns:
                markers = []
                if col.name in pk_cols:
                    markers.append("PK")
                if col.name in fk_cols:
                    markers.append("FK")
                prefix = f'<FONT COLOR="#888888">[{",".join(markers)}]</FONT> ' if markers else ""
                label_rows.append(
                    f'<TR><TD ALIGN="LEFT" PORT="{col.name}">'
                    f"{prefix}{col.name} : "
                    f'<FONT COLOR="#888888">{col.type}</FONT></TD></TR>'
                )

            rows_str = "".join(label_rows)
            display_name = table_name.split(".")[-1] if "." in table_name else table_name
            label = (
                f'<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" COLOR="{style["border"]}">'
                f'<TR><TD BGCOLOR="{style["header_bg"]}">'
                f'<FONT COLOR="{style["header_font"]}"><B>{display_name}</B></FONT>'
                f"</TD></TR>"
                f"{rows_str}</TABLE>>"
            )
            safe_name = table_name.replace(".", "__")
            lines.append(f'        "{safe_name}" [label={label}];')

        lines.append("    }")
        lines.append("")

    seen = set()
    for table_name, table in tables.items():
        for fk in table.foreign_keys:
            target_fullname = fk.column.table.fullname
            if target_fullname not in tables:
                continue
            src = table_name.replace(".", "__")
            dst = target_fullname.replace(".", "__")
            edge = (src, fk.parent.name, dst, fk.column.name)
            if edge not in seen:
                seen.add(edge)
                lines.append(
                    f'    "{src}":{fk.parent.name} -> '
                    f'"{dst}":{fk.column.name};'
                )

    lines.append("}")
    return "\n".join(lines)


if __name__ == "__main__":
    schema_filter = sys.argv[1] if len(sys.argv) > 1 else None
    print(generate_dot(Base.metadata, schema_filter=schema_filter))