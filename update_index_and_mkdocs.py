#!/usr/bin/env python3
"""
update_index_and_mkdocs.py
--------------------------
Script unique qui effectue deux opérations :

  1. Met à jour docs/index.md avec :
       - Le tableau détaillé de tous les accords actifs (avec comptage de tokens)
       - Le récapitulatif par type d'accord
       - Le tableau des accords révolus

  2. Régénère la section nav: de mkdocs.yml à partir des 4 SOMMAIRE.md.

Usage :
    python update_index_and_mkdocs.py

Dépendances optionnelles :
    pip install tiktoken   → comptage précis (cl100k_base / GPT-4)
    Sans tiktoken          → approximation : len(texte) // 4
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR    = os.path.join(BASE_DIR, "docs")
INDEX_PATH  = os.path.join(DOCS_DIR, "index.md")
MKDOCS_PATH = os.path.join(BASE_DIR, "mkdocs.yml")

# Ordre et labels pour les tableaux index.md
SOURCES = [
    ("accords-groupe",              "Accord Groupe"),
    ("las-fr",                      "LAS France"),
    ("las-rungis-toulouse",         "LAS Rungis - Toulouse"),
    ("accords-interprofessionnels", "Accord Interprofessionnel"),
]

# Ordre et labels pour la navigation mkdocs.yml (ordre différent)
SECTIONS = [
    ("accords-interprofessionnels", "Accords interprofessionnels"),
    ("accords-groupe",              "Accords de groupe"),
    ("las-fr",                      "Thales LAS France"),
    ("las-rungis-toulouse",         "LAS Rungis-Toulouse"),
]

# Marqueurs pour la mise à jour idempotente d'index.md
SECTION_MARKER = "\n\n---\n\n## Sommaire global\n\n"
REVOLUS_MARKER = "\n\n---\n\n## Accords révolus\n\n"

# Caractères YAML nécessitant des guillemets
_YAML_SPECIAL = set(':\'"{[],&#*?|-<>=!%@`')


# ===========================================================================
# Utilitaires partagés
# ===========================================================================

def parse_table_rows(content: str) -> list[list[str]]:
    """Extrait toutes les lignes d'un tableau markdown (sans séparateurs)."""
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


def strip_bold(text: str) -> str:
    return re.sub(r'\*\*(.+?)\*\*', r'\1', text).strip()


# ===========================================================================
# Section 1 — Mise à jour de docs/index.md
# ===========================================================================

def count_tokens(text: str) -> int:
    """Compte les tokens avec tiktoken si disponible, sinon approximation."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except ImportError:
        return max(1, len(text) // 4)


def extract_link_target(cell: str) -> str | None:
    """Extrait la cible d'un lien markdown `[texte](cible)` ou None."""
    m = re.search(r'\[.*?\]\(([^)]+)\)', cell)
    return m.group(1) if m else None


def _prefix_link(cell: str, folder: str) -> str:
    """Préfixe les liens relatifs dans une cellule markdown avec le dossier."""
    return re.sub(
        r'\[([^\]]*)\]\((?!https?://)([^)]+)\)',
        lambda m: f"[{m.group(1)}]({folder}/{m.group(2)})",
        cell
    )


def collect_data() -> tuple[list[dict], dict[str, int], dict[str, int]]:
    """
    Parcourt tous les SOMMAIRE.md et retourne :
      - rows   : liste de dicts avec les champs de chaque ligne
      - totals : dict label → total tokens (+ clé "**Total**" pour le grand total)
      - counts : dict label → nombre d'accords
    """
    rows = []
    totals: dict[str, int] = {}

    for folder, label in SOURCES:
        sommaire_path = os.path.join(DOCS_DIR, folder, "SOMMAIRE.md")
        if not os.path.exists(sommaire_path):
            print(f"  [WARN] SOMMAIRE.md introuvable : {sommaire_path}", file=sys.stderr)
            continue

        with open(sommaire_path, encoding="utf-8") as f:
            content = f.read()

        all_rows = parse_table_rows(content)
        if len(all_rows) < 2:
            continue

        last_categorie = ""
        type_total = 0

        for row in all_rows[1:]:
            while len(row) < 5:
                row.append("")
            categorie, titre, date, doc_cell, pdf_cell = row[0], row[1], row[2], row[3], row[4]

            if categorie:
                last_categorie = categorie
            else:
                categorie = last_categorie

            tokens_val: int | None = None
            tokens_str = "—"
            md_rel = extract_link_target(doc_cell)
            if md_rel and md_rel.endswith(".md"):
                md_path = os.path.join(DOCS_DIR, folder, md_rel)
                if os.path.exists(md_path):
                    with open(md_path, encoding="utf-8") as f:
                        md_text = f.read()
                    tokens_val = count_tokens(md_text)
                    tokens_str = str(tokens_val)
                    type_total += tokens_val
                else:
                    tokens_str = "N/A"

            rows.append({
                "label":      label,
                "folder":     folder,
                "categorie":  categorie,
                "titre":      titre,
                "date":       date,
                "doc":        doc_cell,
                "pdf":        pdf_cell,
                "tokens_str": tokens_str,
                "tokens_val": tokens_val,
            })

        totals[label] = type_total

    totals["**Total**"] = sum(totals.values())
    counts = {label: 0 for _, label in SOURCES}
    for row in rows:
        counts[row["label"]] = counts.get(row["label"], 0) + 1
    counts["**Total**"] = sum(v for k, v in counts.items() if k != "**Total**")
    return rows, totals, counts


def build_summary_table(totals: dict[str, int], counts: dict[str, int]) -> str:
    """Tableau récapitulatif accords + tokens par type + grand total."""
    lines = [
        "| Type d'accord | Nombre d'accords | Nombre de tokens |",
        "|---|---:|---:|",
    ]
    grand_total = totals.pop("**Total**", 0)
    grand_count = counts.pop("**Total**", 0)
    for label, total in totals.items():
        count = counts.get(label, 0)
        lines.append(f"| {label} | {count} | {total:,} |".replace(",", "\u202f"))
    lines.append(f"| **Total** | **{grand_count}** | **{grand_total:,}** |".replace(",", "\u202f"))
    totals["**Total**"] = grand_total  # restore
    counts["**Total**"] = grand_count  # restore
    return "\n".join(lines)


def build_detail_table(rows: list[dict]) -> str:
    """Tableau détaillé de tous les accords."""
    lines = [
        "| Type d'accord | Catégorie | Titre | Date | Document | PDF | Tokens |",
        "|---|---|---|---|---|---|---:|",
    ]
    for r in rows:
        doc = _prefix_link(r["doc"], r["folder"])
        pdf = _prefix_link(r["pdf"], r["folder"])
        lines.append(
            f"| {r['label']} | {r['categorie']} | {r['titre']} | {r['date']}"
            f" | {doc} | {pdf} | {r['tokens_str']} |"
        )
    return "\n".join(lines)


def collect_revolus_data() -> list[dict]:
    """Parcourt tous les REVOLUS.md et retourne la liste des accords révolus."""
    rows = []
    for folder, label in SOURCES:
        revolus_path = os.path.join(DOCS_DIR, folder, "REVOLUS.md")
        if not os.path.exists(revolus_path):
            continue

        with open(revolus_path, encoding="utf-8") as f:
            content = f.read()

        all_rows = parse_table_rows(content)
        if len(all_rows) < 2:
            continue

        last_categorie = ""
        for row in all_rows[1:]:
            while len(row) < 5:
                row.append("")
            categorie, titre, date, doc_cell, pdf_cell = row[0], row[1], row[2], row[3], row[4]

            if categorie:
                last_categorie = categorie
            else:
                categorie = last_categorie

            if not titre.strip():
                continue

            rows.append({
                "label":     label,
                "folder":    folder,
                "categorie": categorie,
                "titre":     titre.strip(),
                "date":      date,
                "doc":       doc_cell,
                "pdf":       pdf_cell,
            })

    return rows


def build_revolus_table(rows: list[dict]) -> str:
    """Tableau de tous les accords révolus."""
    if not rows:
        return "_Aucun accord révolu référencé._"

    lines = [
        "| Type d'accord | Catégorie | Titre | Date | Document | PDF |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        doc = _prefix_link(r["doc"], r["folder"])
        pdf = _prefix_link(r["pdf"], r["folder"])
        lines.append(
            f"| {r['label']} | {r['categorie']} | {r['titre']} | {r['date']}"
            f" | {doc} | {pdf} |"
        )
    return "\n".join(lines)


def update_index_md():
    """Met à jour docs/index.md avec les tableaux combinés."""
    if not os.path.exists(INDEX_PATH):
        print(f"[ERREUR] index.md introuvable : {INDEX_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(INDEX_PATH, encoding="utf-8") as f:
        current = f.read()

    if SECTION_MARKER in current:
        current = current[: current.index(SECTION_MARKER)]
        print("  → Section précédente supprimée, régénération…")

    print("  → Construction du tableau combiné…")
    try:
        import tiktoken  # noqa: F401
        print("  → Comptage de tokens via tiktoken (cl100k_base)")
    except ImportError:
        print("  → tiktoken non installé — approximation len(texte)//4 utilisée")
        print("     Pour un comptage précis : pip install tiktoken")

    rows, totals, counts = collect_data()
    summary = build_summary_table(totals, counts)
    detail  = build_detail_table(rows)

    revolus_rows  = collect_revolus_data()
    revolus_table = build_revolus_table(revolus_rows)

    section = (
        "### Détail de tous les accords\n\n"
        + detail
        + "\n\n### Récapitulatif par type d'accord\n\n"
        + summary
        + "\n"
    )
    revolus_section = revolus_table + "\n"

    new_content = current + SECTION_MARKER + section + REVOLUS_MARKER + revolus_section

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(
        f"  ✓ index.md mis à jour — {len(rows)} accords actifs, "
        f"{len(revolus_rows)} accords révolus, "
        f"total {totals['**Total**']:,} tokens.".replace(",", "\u202f")
    )


# ===========================================================================
# Section 2 — Régénération de la nav: dans mkdocs.yml
# ===========================================================================

def yaml_quote(s: str) -> str:
    """Entoure la valeur de guillemets doubles si nécessaire pour YAML."""
    if any(c in _YAML_SPECIAL for c in s):
        return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
    return s


def extract_md_link(cell: str) -> str | None:
    """Extrait la cible d'un lien markdown pointant vers un .md, ou None."""
    m = re.search(r'\[.*?\]\(([^)]+\.md)\)', cell)
    return m.group(1) if m else None


def build_section_nav(folder: str, section_label: str) -> list[str]:
    """Génère les lignes YAML pour une section de la nav."""
    sommaire_path = os.path.join(DOCS_DIR, folder, "SOMMAIRE.md")
    if not os.path.exists(sommaire_path):
        print(f"  [WARN] SOMMAIRE.md introuvable : {sommaire_path}")
        return []

    with open(sommaire_path, encoding="utf-8") as f:
        content = f.read()

    all_rows = parse_table_rows(content)
    if len(all_rows) < 2:
        return []

    categories: dict[str, list[tuple[str, str]]] = {}
    cat_order: list[str] = []
    last_cat = ""

    for row in all_rows[1:]:
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

    lines: list[str] = []
    lines.append(f"  - {yaml_quote(section_label)}:")
    lines.append(f"      - Sommaire: {folder}/SOMMAIRE.md")

    for cat in cat_order:
        lines.append(f"      - {yaml_quote(cat)}:")
        for titre, path in categories[cat]:
            lines.append(f"          - {yaml_quote(titre)}: {path}")

    return lines


def build_nav() -> str:
    """Construit la section nav: complète."""
    lines = ["nav:", "  - Accueil: index.md"]

    for folder, label in SECTIONS:
        lines.append("")
        lines.extend(build_section_nav(folder, label))

    return "\n".join(lines) + "\n"


def update_mkdocs_nav():
    """Régénère la section nav: dans mkdocs.yml."""
    with open(MKDOCS_PATH, encoding="utf-8") as f:
        original = f.read()

    nav_match = re.search(r'^nav:.*', original, flags=re.MULTILINE | re.DOTALL)
    before = original[: nav_match.start()] if nav_match else original.rstrip() + "\n\n"

    new_content = before + build_nav()

    with open(MKDOCS_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    nav_entries = sum(1 for l in new_content.splitlines() if l.strip().startswith("- ") and ".md" in l)
    print(f"  ✓ mkdocs.yml mis à jour ({nav_entries} entrées dans nav:)")


# ===========================================================================
# Point d'entrée
# ===========================================================================

def main():
    print("=== Mise à jour de docs/index.md ===")
    update_index_md()

    print()
    print("=== Mise à jour de mkdocs.yml (nav:) ===")
    update_mkdocs_nav()


if __name__ == "__main__":
    main()
