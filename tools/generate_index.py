#!/usr/bin/env python3
"""Index and Catalog Generator for SOC-LMC Archive.

Scans all paper dossiers in corpus/papers/, extracts metadata, and regenerates:
1. corpus/catalog.json (Machine-readable metadata repository)
2. corpus/bibliography.bib (Consolidated BibTeX database)
3. corpus/INDEX.md (Categorized master index tables)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

PAPERS_DIR = BASE_DIR / "corpus" / "papers"
CATALOG_PATH = BASE_DIR / "corpus" / "catalog.json"
BIB_PATH = BASE_DIR / "corpus" / "bibliography.bib"
INDEX_PATH = BASE_DIR / "corpus" / "INDEX.md"


def parse_frontmatter_fallback(text: str) -> Dict[str, Any]:
    """Simple regex parser for YAML frontmatter when PyYAML is not installed."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not match:
        return {}
    fm_raw = match.group(1)
    data: Dict[str, Any] = {}

    current_list_key = None
    for line in fm_raw.splitlines():
        line_str = line.strip()
        if not line_str or line_str.startswith("#"):
            continue

        list_match = re.match(r"^-\s*[\"']?(.*?)[\"']?$", line_str)
        if list_match and current_list_key:
            data[current_list_key].append(list_match.group(1).strip())
            continue

        key_val = re.match(r"^([a-zA-Z0-9_]+):\s*(.*)$", line_str)
        if key_val:
            k = key_val.group(1)
            v = key_val.group(2).strip()
            if not v:
                data[k] = []
                current_list_key = k
            elif v.startswith("[") and v.endswith("]"):
                items = [re.sub(r"[\"']", "", item.strip()) for item in v[1:-1].split(",") if item.strip()]
                data[k] = items
                current_list_key = None
            else:
                cleaned_v = re.sub(r"^[\"']|[\"']$", "", v)
                if cleaned_v.isdigit():
                    data[k] = int(cleaned_v)
                else:
                    data[k] = cleaned_v
                current_list_key = None

    return data


def parse_dossier(file_path: Path) -> Optional[Dict[str, Any]]:
    """Parse frontmatter and extracted bibtex from a markdown dossier."""
    text = file_path.read_text(encoding="utf-8")
    frontmatter = None
    if HAS_YAML:
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
        if match:
            try:
                frontmatter = yaml.safe_load(match.group(1))
            except Exception:
                frontmatter = None

    if not frontmatter:
        frontmatter = parse_frontmatter_fallback(text)

    if not frontmatter or "id" not in frontmatter:
        return None

    # Extract bibtex code block if present
    bib_match = re.search(r"```bibtex\s*\n(.*?)\n```", text, re.DOTALL)
    bibtex = bib_match.group(1).strip() if bib_match else ""

    record = dict(frontmatter)
    record["file_rel_path"] = str(file_path.relative_to(BASE_DIR))
    record["bibtex"] = bibtex
    return record


def rebuild_catalog_and_index():
    """Main execution function to scan papers and regenerate catalog, bibliography, and index."""
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    paper_files = sorted(list(PAPERS_DIR.glob("*.md")))
    records = []

    for f in paper_files:
        rec = parse_dossier(f)
        if rec:
            records.append(rec)

    # Sort records by year (descending), then ID (descending)
    records.sort(key=lambda r: (r.get("year", 0), str(r.get("id", ""))), reverse=True)

    # 1. Write catalog.json
    CATALOG_PATH.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 2. Write bibliography.bib
    bibtex_entries = [r["bibtex"] for r in records if r.get("bibtex")]
    BIB_PATH.write_text("\n\n".join(bibtex_entries) + "\n", encoding="utf-8")

    # 3. Compute Statistics
    total_papers = len(records)
    level_counts = {
        "L1_lexical": 0,
        "L2_syntactic_stylistic": 0,
        "L3_semantic_ideational": 0,
        "L4_symbolic_pragmatic": 0,
        "L5_systemic_recursive": 0,
    }
    concept_counts: Dict[str, int] = {}
    years_count: Dict[int, int] = {}

    for r in records:
        for lvl in r.get("conformity_levels", []):
            if lvl in level_counts:
                level_counts[lvl] += 1
        for concept in r.get("cybernetic_concepts", []):
            concept_counts[concept] = concept_counts.get(concept, 0) + 1
        y = r.get("year", 2024)
        years_count[y] = years_count.get(y, 0) + 1

    # Format master tables
    def format_authors(authors_val) -> str:
        if isinstance(authors_val, list):
            if len(authors_val) == 1:
                return authors_val[0]
            elif len(authors_val) == 2:
                return f"{authors_val[0]} & {authors_val[1]}"
            elif len(authors_val) > 2:
                return f"{authors_val[0]} et al."
        return str(authors_val)

    def table_row(r: Dict[str, Any]) -> str:
        title = r.get("title", "Untitled")
        paper_id = r.get("id", "")
        rel_link = f"papers/{paper_id}.md"
        authors = format_authors(r.get("authors", []))
        year = r.get("year", "N/A")
        levels = ", ".join(f"`{l.split('_', 1)[0]}`" for l in r.get("conformity_levels", []))
        substrate = r.get("empirical_substrate", "N/A")
        if len(substrate) > 40:
            substrate = substrate[:37] + "..."
        url = r.get("url", f"https://arxiv.org/abs/{paper_id}")
        return f"| [{title}]({rel_link}) | {authors} | {year} | {levels} | {substrate} | [arXiv]({url}) |"

    master_rows = [table_row(r) for r in records]

    # Level-specific rows
    def level_table(lvl_key: str) -> str:
        subset = [r for r in records if lvl_key in r.get("conformity_levels", [])]
        if not subset:
            return "*No papers cataloged in this dimension yet.*"
        lines = [
            "| Title | Authors | Year | Empirical Substrate | Links |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for r in subset:
            title = r.get("title", "Untitled")
            paper_id = r.get("id", "")
            rel_link = f"papers/{paper_id}.md"
            authors = format_authors(r.get("authors", []))
            year = r.get("year", "N/A")
            substrate = r.get("empirical_substrate", "N/A")
            url = r.get("url", f"https://arxiv.org/abs/{paper_id}")
            lines.append(f"| [{title}]({rel_link}) | {authors} | {year} | {substrate} | [arXiv]({url}) |")
        return "\n".join(lines)

    index_content = f"""# Master Corpus Index: Second-Order Cybernetics & LLM Conformity

This index provides a structured, multi-dimensional catalog of empirical and theoretical literature exploring human-LLM feedback loops, linguistic and cognitive conformity, and cultural homogenization.

---

## 1. Corpus Analytics & Distribution

- **Total Archived Papers**: `{total_papers}`
- **Conformity Stratum Breakdown**:
  - `L1` **Lexical Conformity & Vocabulary Shifts**: `{level_counts['L1_lexical']}` papers
  - `L2` **Syntactic & Stylistic Conformity**: `{level_counts['L2_syntactic_stylistic']}` papers
  - `L3` **Semantic & Ideational Conformity**: `{level_counts['L3_semantic_ideational']}` papers
  - `L4` **Symbolic & Pragmatic Conformity**: `{level_counts['L4_symbolic_pragmatic']}` papers
  - `L5` **Systemic & Second-Order Reflexive Loops**: `{level_counts['L5_systemic_recursive']}` papers

---

## 2. Master Chronological Catalog

| Title | Authors | Year | Levels | Empirical Substrate | Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
{chr(10).join(master_rows)}

---

## 3. Conformity Dimension Indices

### Level 1: Lexical Conformity & Vocabulary Shifts
Empirical evidence tracking token distribution skew, excess vocabulary (*delve*, *showcase*, *pivotal*, *intricacies*), and lexical entrenchment in human speech and writing.

{level_table('L1_lexical')}

### Level 2: Syntactic & Stylistic Conformity
Research measuring the contraction in writing complexity variance, structural flattening, and loss of authorial fingerprints.

{level_table('L2_syntactic_stylistic')}

### Level 3: Semantic & Ideational Conformity
Studies documenting opinion convergence, consensus anchoring, and semantic compression around model centroids.

{level_table('L3_semantic_ideational')}

### Level 4: Symbolic & Pragmatic Conformity
Analyses of interactive alignment, communicative accommodation, and the emergence of prompt-like instrumental framing in human discourse.

{level_table('L4_symbolic_pragmatic')}

### Level 5: Systemic & Second-Order Reflexive Loops
Theoretical and empirical investigations of autophagous loops, recursive model collapse, and cybernetic eigenforms in cultural ecosystems.

{level_table('L5_systemic_recursive')}

---

## 4. Cybernetic Concepts Cross-Index

| Cybernetic Concept | Frequency | Key Theorists & Themes |
| :--- | :--- | :--- |
| `circular_causality` | {concept_counts.get('circular_causality', 0)} | Heinz von Foerster (Outputs feed back into inputs, altering the observer) |
| `structural_coupling` | {concept_counts.get('structural_coupling', 0)} | Maturana & Varela (Recurrent interaction inducing congruent plastic changes) |
| `eigenform` / `attractor` | {concept_counts.get('eigenform', 0) + concept_counts.get('consensus_attractor', 0)} | Heinz von Foerster (Stable recursive limits of cognitive/symbolic operations) |
| `model_collapse` / `autophagy` | {concept_counts.get('autophagous_loop', 0) + concept_counts.get('model_collapse', 0)} | Shumailov et al. (Information loss in recursive training distributions) |
| `communicative_accommodation` | {concept_counts.get('communicative_accommodation', 0)} | Giles / Pickering & Garrod (Dynamic alignment between conversation partners) |

---
*Generated automatically by `tools/generate_index.py`. Do not edit directly.*
"""
    INDEX_PATH.write_text(index_content.strip() + "\n", encoding="utf-8")
    print(f"[+] Successfully regenerated catalog ({CATALOG_PATH.name}) and master index ({INDEX_PATH.name}) with {total_papers} papers.")


def main():
    rebuild_catalog_and_index()


if __name__ == "__main__":
    main()
