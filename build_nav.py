#!/usr/bin/env python3
"""
build_nav.py
------------
Génère la section nav: de mkdocs.yml à partir des 4 SOMMAIRE.md.
Remplace uniquement la section nav:, préserve le reste du fichier.

Usage :
    python build_nav.py
"""

import os
import re

DOCS_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
MKDOCS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mkdocs.yml")

# Ordre d'affichage et labels des sections de navigation
SECTIONS = [
    ("accords-interprofessionnels", "Accords interprofessionnels"),
    ("accords-groupe",              "Accords de groupe"),
    ("las-fr",                      "Thales LAS France"),
    ("las-rungis-toulouse",         "LAS Rungis-Toulouse"),
]

# Caractères YAML nécessitant des guillemets
_YAML_SPECIAL = set(':\'"{[],&#*?|-<>=!%@`')


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def yaml_quote(s: str) -> str:
    """Entoure la valeur de guillemets doubles si nécessaire pour YAML."""
    if any(c in _YAML_SPECIAL for c in s):
        return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
    return s


def strip_bold(text: str) -> str:
    return re.sub(r'\*\*(.+?)\*\*', r'\1', text).strip()


def parse_table_rows(content: str) -> list[list[str]]:
    """Retourne toutes les lignes d'un tableau markdown (sans séparateurs)."""
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


def extract_md_link(cell: str) -> str | None:
    m = re.search(r'\[.*?\]\(([^)]+\.md)\)', cell)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Construction de la nav pour une section
# ---------------------------------------------------------------------------

def build_section_nav(folder: str, section_label: str) -> list[str]:
    sommaire_path = os.path.join(DOCS_DIR, folder, "SOMMAIRE.md")
    if not os.path.exists(sommaire_path):
        print(f"  [WARN] SOMMAIRE.md introuvable : {sommaire_path}")
        return []

    with open(sommaire_path, encoding="utf-8") as f:
        content = f.read()

    all_rows = parse_table_rows(content)
    if len(all_rows) < 2:
        return []

    # Grouper par catégorie (héritage des cellules vides)
    categories: dict[str, list[tuple[str, str]]] = {}
    cat_order: list[str] = []
    last_cat = ""

    for row in all_rows[1:]:       # skip header row
        while len(row) < 5:
            row.append("")
        cat   = strip_bold(row[0])
        titre = row[1].strip()
        doc   = row[3]

        if cat:
            last_cat = cat
        else:
            cat = last_cat

        md_rel = extract_md_link(doc)
        if not md_rel or not titre:
            continue

        if cat not in categories:
            categories[cat] = []
            cat_order.append(cat)
        categories[cat].append((titre, f"{folder}/{md_rel}"))

    # Sérialiser en YAML (2 espaces par niveau de base = section top-level)
    lines: list[str] = []
    lines.append(f"  - {yaml_quote(section_label)}:")
    lines.append(f"      - Sommaire: {folder}/SOMMAIRE.md")

    for cat in cat_order:
        lines.append(f"      - {yaml_quote(cat)}:")
        for titre, path in categories[cat]:
            lines.append(f"          - {yaml_quote(titre)}: {path}")

    return lines


# ---------------------------------------------------------------------------
# Construction de la nav complète
# ---------------------------------------------------------------------------

def build_nav() -> str:
    lines = ["nav:"]
    lines.append("  - Accueil: index.md")

    for folder, label in SECTIONS:
        lines.append("")
        lines.extend(build_section_nav(folder, label))

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def main():
    with open(MKDOCS_PATH, encoding="utf-8") as f:
        original = f.read()

    # Remplace tout à partir de "nav:" jusqu'à la fin du fichier
    nav_match = re.search(r'^nav:.*', original, flags=re.MULTILINE | re.DOTALL)
    before = original[: nav_match.start()] if nav_match else original.rstrip() + "\n\n"

    new_content = before + build_nav()

    with open(MKDOCS_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    # Compte les entrées générées
    total = sum(len(v) for _, v in [(f, build_section_nav(f, l)) for f, l in SECTIONS])
    print(f"  ✓ mkdocs.yml mis à jour ({sum(1 for l in new_content.splitlines() if l.strip().startswith('- ') and '.md' in l)} entrées dans nav:)")


if __name__ == "__main__":
    main()
