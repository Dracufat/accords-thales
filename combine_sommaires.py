#!/usr/bin/env python3
"""
combine_sommaires.py
--------------------
Combine tous les SOMMAIRE.md en un tableau global ajouté à docs/index.md.

Colonnes ajoutées :
  - Première colonne : Type d'accord (périmètre)
  - Dernière colonne  : Tokens (nombre de tokens du fichier .md)

Usage :
    python combine_sommaires.py

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

DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
INDEX_PATH = os.path.join(DOCS_DIR, "index.md")

# Ordre d'affichage et labels
SOURCES = [
    ("accords-groupe",            "Accord Groupe"),
    ("las-fr",                    "LAS France"),
    ("las-rungis-toulouse",       "LAS Rungis - Toulouse"),
    ("accords-interprofessionnels", "Accord Interprofessionnel"),
]

# Marqueur pour identifier la section générée (permet la mise à jour idempotente)
SECTION_MARKER = "\n\n---\n\n## Sommaire global\n\n"


# ---------------------------------------------------------------------------
# Comptage de tokens
# ---------------------------------------------------------------------------

def count_tokens(text: str) -> int:
    """Compte les tokens avec tiktoken si disponible, sinon approximation."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except ImportError:
        # ~4 caractères par token (approximation GPT standard)
        return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# Parsing du tableau markdown
# ---------------------------------------------------------------------------

def parse_table_rows(content: str) -> list[list[str]]:
    """
    Extrait les lignes d'un tableau markdown.
    Retourne une liste de listes de cellules (sans la ligne header ni séparateur).
    La première liste retournée est l'entête.
    """
    rows = []
    for line in content.splitlines():
        line = line.strip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        # Ignorer les lignes séparatrices (---)
        if re.fullmatch(r'[\|\s\-:]+', line):
            continue
        cells = [c.strip() for c in line[1:-1].split("|")]
        rows.append(cells)
    return rows


def extract_link_target(cell: str) -> str | None:
    """Extrait la cible d'un lien markdown `[texte](cible)` ou None."""
    m = re.search(r'\[.*?\]\(([^)]+)\)', cell)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Construction du tableau combiné
# ---------------------------------------------------------------------------

def collect_data() -> tuple[list[dict], dict[str, int]]:
    """
    Parcourt tous les SOMMAIRE.md et retourne :
      - rows   : liste de dicts avec les champs de chaque ligne
      - totals : dict label → total tokens (+ clé "TOTAL" pour le grand total)
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

        data_rows = all_rows[1:]
        last_categorie = ""
        type_total = 0

        for row in data_rows:
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
                "label": label,
                "categorie": categorie,
                "titre": titre,
                "date": date,
                "doc": doc_cell,
                "pdf": pdf_cell,
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
        lines.append(
            f"| {r['label']} | {r['categorie']} | {r['titre']} | {r['date']}"
            f" | {r['doc']} | {r['pdf']} | {r['tokens_str']} |"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def main():
    if not os.path.exists(INDEX_PATH):
        print(f"[ERREUR] index.md introuvable : {INDEX_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(INDEX_PATH, encoding="utf-8") as f:
        current = f.read()

    # Suppression de la section précédemment générée (idempotent)
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
    detail = build_detail_table(rows)

    section = (
        "### Détail de tous les accords\n\n"
        + detail
        + "\n\n### Récapitulatif par type d'accord\n\n"
        + summary
        + "\n"
    )
    new_content = current + SECTION_MARKER + section

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"  ✓ index.md mis à jour — {len(rows)} accords listés, total {totals['**Total**']:,} tokens.".replace(",", "\u202f"))


if __name__ == "__main__":
    main()
