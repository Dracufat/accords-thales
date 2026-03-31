#!/usr/bin/env python3
"""
build_zip.py
------------
Construit un fichier ZIP contenant :
  - docs/index.md
  - tous les fichiers .md des accords actifs (référencés dans les SOMMAIRE.md)

Les accords révolus (REVOLUS.md) sont exclus.

Usage :
    python build_zip.py [output.zip]

Par défaut le ZIP est écrit dans : accords-thales.zip
"""

import os
import re
import sys
import zipfile

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR   = os.path.join(BASE_DIR, "docs")
INDEX_PATH = os.path.join(DOCS_DIR, "index.md")

SOURCES = [
    ("accords-groupe",              "Accord Groupe"),
    ("las-fr",                      "LAS France"),
    ("las-rungis-toulouse",         "LAS Rungis - Toulouse"),
    ("accords-interprofessionnels", "Accord Interprofessionnel"),
]


def parse_table_rows(content: str) -> list[list[str]]:
    rows = []
    for line in content.splitlines():
        line = line.strip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        if re.fullmatch(r'[\|\s\-:]+', line):
            continue
        cells = [c.strip() for c in line[1:-1].split("|")]
        rows.append(cells)
    return rows


def extract_link_target(cell: str) -> str | None:
    m = re.search(r'\[.*?\]\(([^)]+)\)', cell)
    return m.group(1) if m else None


def collect_active_md_paths() -> list[tuple[str, str]]:
    """
    Retourne une liste de (chemin_absolu, chemin_dans_zip) pour chaque
    fichier .md d'accord actif.
    """
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()

    for folder, _ in SOURCES:
        sommaire_path = os.path.join(DOCS_DIR, folder, "SOMMAIRE.md")
        if not os.path.exists(sommaire_path):
            print(f"  [WARN] SOMMAIRE.md introuvable : {sommaire_path}", file=sys.stderr)
            continue

        with open(sommaire_path, encoding="utf-8") as f:
            content = f.read()

        all_rows = parse_table_rows(content)
        for row in all_rows[1:]:          # skip header
            while len(row) < 5:
                row.append("")
            doc_cell = row[3]
            md_rel = extract_link_target(doc_cell)
            if not md_rel or not md_rel.endswith(".md"):
                continue

            abs_path = os.path.join(DOCS_DIR, folder, md_rel)
            zip_path = os.path.join("docs", folder, md_rel)   # chemin dans le ZIP

            if abs_path in seen:
                continue
            seen.add(abs_path)

            if os.path.exists(abs_path):
                entries.append((abs_path, zip_path))
            else:
                print(f"  [WARN] Fichier introuvable : {abs_path}", file=sys.stderr)

    return entries


def main():
    output_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE_DIR, "accords-thales.zip")

    if not os.path.exists(INDEX_PATH):
        print(f"[ERREUR] index.md introuvable : {INDEX_PATH}", file=sys.stderr)
        sys.exit(1)

    entries = collect_active_md_paths()

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # index.md à la racine du ZIP
        zf.write(INDEX_PATH, os.path.join("docs", "index.md"))

        for abs_path, zip_path in entries:
            zf.write(abs_path, zip_path)

    total = 1 + len(entries)
    print(f"  ✓ {output_path} — {total} fichiers ({len(entries)} accords + index.md)")


if __name__ == "__main__":
    main()
