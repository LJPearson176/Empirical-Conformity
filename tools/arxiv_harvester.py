#!/usr/bin/env python3
"""arXiv Harvester for Second-Order Cybernetics & LLM Conformity (SOC-LMC) Archive.

Queries the arXiv Atom API, extracts paper metadata, classifies conformity dimensions,
and outputs structured Markdown dossiers conforming to the SOC-LMC taxonomy.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Constants
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

CONFIG_PATH = BASE_DIR / "config" / "queries.yaml"
PAPERS_DIR = BASE_DIR / "corpus" / "papers"
CATALOG_PATH = BASE_DIR / "corpus" / "catalog.json"
BIBLIOGRAPHY_PATH = BASE_DIR / "corpus" / "bibliography.bib"

ARXIV_API_URL = "https://export.arxiv.org/api/query"
USER_AGENT = "soc-llm-conformity-harvester/0.1.0 (academic-research-archive; contact: research@example.org)"
LAST_REQUEST_TIME = 0.0
RATE_LIMIT_DELAY = 3.1  # arXiv requires >= 3.0 seconds between requests

# XML Namespaces
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def rate_limited_get(url: str) -> str:
    """Fetch URL respecting arXiv's >= 3.0s rate limiting policy."""
    global LAST_REQUEST_TIME
    elapsed = time.time() - LAST_REQUEST_TIME
    if elapsed < RATE_LIMIT_DELAY:
        sleep_duration = RATE_LIMIT_DELAY - elapsed
        time.sleep(sleep_duration)

    headers = {"User-Agent": USER_AGENT}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        content = response.read().decode("utf-8")
    LAST_REQUEST_TIME = time.time()
    return content


def clean_text(text: Optional[str]) -> str:
    """Normalize whitespace and remove unwanted linebreaks."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def parse_arxiv_entry(entry: ET.Element) -> Dict[str, Any]:
    """Parse an individual entry element from an arXiv Atom XML feed."""
    raw_id = entry.findtext("atom:id", "", namespaces=ATOM_NS)
    # Extract clean arXiv ID (e.g. 2409.01754 or 2409.01754v4)
    arxiv_id_match = re.search(r"(\d{4}\.\d{4,5}(?:v\d+)?)", raw_id)
    arxiv_id = arxiv_id_match.group(1) if arxiv_id_match else raw_id.split("/")[-1]
    # Base ID without version
    base_id = re.sub(r"v\d+$", "", arxiv_id)

    title = clean_text(entry.findtext("atom:title", "", namespaces=ATOM_NS))
    summary = clean_text(entry.findtext("atom:summary", "", namespaces=ATOM_NS))
    published = entry.findtext("atom:published", "", namespaces=ATOM_NS)
    year = int(published[:4]) if published and len(published) >= 4 else 2024

    authors = []
    for author_elem in entry.findall("atom:author", namespaces=ATOM_NS):
        name = clean_text(author_elem.findtext("atom:name", "", namespaces=ATOM_NS))
        if name:
            authors.append(name)

    categories = []
    for cat_elem in entry.findall("atom:category", namespaces=ATOM_NS):
        term = cat_elem.attrib.get("term")
        if term:
            categories.append(term)

    # DOI if present
    doi = entry.findtext("arxiv:doi", "", namespaces=ATOM_NS)
    if not doi:
        doi_elem = entry.find("atom:link[@title='doi']", namespaces=ATOM_NS)
        if doi_elem is not None:
            doi = doi_elem.attrib.get("href", "")

    # Primary category
    primary_cat_elem = entry.find("arxiv:primary_category", namespaces=ATOM_NS)
    primary_category = primary_cat_elem.attrib.get("term", "") if primary_cat_elem is not None else (categories[0] if categories else "cs.CL")

    # Links
    pdf_url = f"https://arxiv.org/pdf/{base_id}.pdf"
    abs_url = f"https://arxiv.org/abs/{base_id}"

    return {
        "id": base_id,
        "full_id": arxiv_id,
        "title": title,
        "summary": summary,
        "authors": authors,
        "year": year,
        "published": published,
        "primary_category": primary_category,
        "categories": categories,
        "doi": doi or f"10.48550/arXiv.{base_id}",
        "abs_url": abs_url,
        "pdf_url": pdf_url,
    }


def classify_paper(title: str, summary: str) -> Dict[str, List[str]]:
    """Heuristic classifier mapping paper text to SOC-LMC conformity levels and cybernetic concepts."""
    text = (title + " " + summary).lower()

    conformity_levels = set()
    cybernetic_concepts = set()

    # Level 1: Lexical
    if any(k in text for k in ["lexical", "vocabulary", "delv", "excess word", "token distribution", "spoken communication", "speech", "word occurrence", "words that chatgpt"]):
        conformity_levels.add("L1_lexical")
        cybernetic_concepts.add("lexical_entrenchment")

    # Level 2: Syntactic & Stylistic
    if any(k in text for k in ["stylistic", "syntactic", "writing assistance", "writing style", "complexity variance", "homogeniz", "hedging", "writing of astronomy", "academic writing"]):
        conformity_levels.add("L2_syntactic_stylistic")
        cybernetic_concepts.add("variance_reduction")

    # Level 3: Semantic & Ideational
    if any(k in text for k in ["semantic", "opinion", "belief", "consensus", "ideation", "persuasion", "view", "conceptual"]):
        conformity_levels.add("L3_semantic_ideational")
        cybernetic_concepts.add("consensus_attractor")

    # Level 4: Symbolic & Pragmatic
    if any(k in text for k in ["pragmatic", "accommodation", "interactive alignment", "prompt", "dialogue", "conversational", "turn-taking", "semiotic"]):
        conformity_levels.add("L4_symbolic_pragmatic")
        cybernetic_concepts.add("communicative_accommodation")

    # Level 5: Systemic & Second-Order Cybernetic
    if any(k in text for k in ["model collapse", "curse of recursion", "recursion", "feedback loop", "autophagous", "synthetic data", "cybernetic", "circular causality"]):
        conformity_levels.add("L5_systemic_recursive")
        cybernetic_concepts.add("circular_causality")
        cybernetic_concepts.add("structural_coupling")

    # Default fallbacks if empty
    if not conformity_levels:
        conformity_levels.add("L1_lexical")
    if not cybernetic_concepts:
        cybernetic_concepts.add("structural_coupling")

    return {
        "conformity_levels": sorted(list(conformity_levels)),
        "cybernetic_concepts": sorted(list(cybernetic_concepts)),
    }


def generate_bibtex(paper: Dict[str, Any]) -> str:
    """Generate BibTeX entry for the paper."""
    first_author_surname = "unknown"
    if paper["authors"]:
        name_parts = paper["authors"][0].split()
        first_author_surname = name_parts[-1].lower()
        first_author_surname = re.sub(r"[^a-z]", "", first_author_surname)

    cite_key = f"{first_author_surname}{paper['year']}{paper['id'].replace('.', '')}"
    authors_str = " and ".join(paper["authors"])

    bibtex = f"""@article{{{cite_key},
  title={{{{{paper['title']}}}}},
  author={{{authors_str}}},
  journal={{arXiv preprint arXiv:{paper['id']}}},
  year={{{paper['year']}}},
  eprint={{{paper['id']}}},
  archivePrefix={{arXiv}},
  primaryClass={{{paper['primary_category']}}},
  url={{{paper['abs_url']}}}
}}"""
    return bibtex


def generate_dossier_markdown(paper: Dict[str, Any], classification: Dict[str, List[str]]) -> str:
    """Generate structured markdown content with YAML frontmatter."""
    authors_yaml = "\n".join(f'  - "{a}"' for a in paper["authors"])
    cats_yaml = "\n".join(f'  - "{c}"' for c in paper["categories"])
    levels_yaml = "\n".join(f'  - "{l}"' for l in classification["conformity_levels"])
    concepts_yaml = "\n".join(f'  - "{c}"' for c in classification["cybernetic_concepts"])
    bibtex = generate_bibtex(paper)

    frontmatter = f"""---
id: "{paper['id']}"
title: "{paper['title']}"
authors:
{authors_yaml}
year: {paper['year']}
venue: "arXiv preprint ({paper['primary_category']})"
arxiv_id: "{paper['id']}"
doi: "{paper['doi']}"
url: "{paper['abs_url']}"
pdf_url: "{paper['pdf_url']}"
categories:
{cats_yaml}
conformity_levels:
{levels_yaml}
cybernetic_concepts:
{concepts_yaml}
empirical_substrate: "Scientific corpus / human interaction"
status: "ingested"
---"""

    body = f"""
# {paper['title']}

## 1. Executive Summary
{paper['summary']}

## 2. Second-Order Cybernetic Framing
This work illuminates the coupling between human communicative behaviour and world-scale language models:
- **Circular Causality**: Documents how language generated by statistical models is absorbed by human agents and reflected in observational corpora.
- **Structural Coupling & Eigenforms**: Highlights the emerging consensus boundaries and attractor dynamics where machine statistical priors condition human expressive variance.

## 3. Conformity Classification
- **Assigned Conformity Dimensions**: {", ".join(f"`{l}`" for l in classification['conformity_levels'])}
- **Cybernetic Construct**: {", ".join(f"`{c}`" for c in classification['cybernetic_concepts'])}
- **Substrate**: {paper['primary_category']} (arXiv preprint)

## 4. BibTeX Citation
```bibtex
{bibtex}
```
"""
    return frontmatter.strip() + "\n" + body.strip() + "\n"


def query_arxiv(query_str: str, max_results: int = 10, start: int = 0) -> List[Dict[str, Any]]:
    """Query the arXiv Atom API."""
    params = {
        "search_query": query_str,
        "start": start,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"
    xml_data = rate_limited_get(url)
    root = ET.fromstring(xml_data)
    papers = []
    for entry in root.findall("atom:entry", namespaces=ATOM_NS):
        paper = parse_arxiv_entry(entry)
        # Avoid empty query placeholders
        if paper["title"] and paper["id"]:
            papers.append(paper)
    return papers


def fetch_arxiv_by_id(arxiv_id: str) -> Optional[Dict[str, Any]]:
    """Fetch an exact arXiv paper by its ID."""
    clean_id = re.sub(r"^arxiv:", "", arxiv_id, flags=re.IGNORECASE).strip()
    url = f"{ARXIV_API_URL}?id_list={urllib.parse.quote(clean_id)}"
    xml_data = rate_limited_get(url)
    root = ET.fromstring(xml_data)
    entry = root.find("atom:entry", namespaces=ATOM_NS)
    if entry is None:
        return None
    paper = parse_arxiv_entry(entry)
    # Check if arXiv returned a "not found" entry
    if not paper["title"] or "Error" in paper["title"]:
        return None
    return paper


def save_paper_dossier(paper: Dict[str, Any]) -> Path:
    """Save paper to corpus/papers/{id}.md."""
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    classification = classify_paper(paper["title"], paper["summary"])
    md_content = generate_dossier_markdown(paper, classification)
    file_path = PAPERS_DIR / f"{paper['id']}.md"
    file_path.write_text(md_content, encoding="utf-8")
    return file_path


def main():
    parser = argparse.ArgumentParser(description="SOC-LMC arXiv Harvester and Research Ingestion CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: fetch
    fetch_parser = subparsers.add_parser("fetch", help="Fetch a paper by arXiv ID and create a dossier")
    fetch_parser.add_argument("--id", required=True, help="arXiv ID (e.g. 2409.01754)")
    fetch_parser.add_argument("--no-index", action="store_true", help="Do not trigger index regeneration")

    # Command: search
    search_parser = subparsers.add_parser("search", help="Search arXiv and display results")
    search_parser.add_argument("--query", required=True, help="arXiv search query")
    search_parser.add_argument("--max-results", type=int, default=5, help="Number of results (default: 5)")
    search_parser.add_argument("--ingest", action="store_true", help="Automatically create dossiers for all results")

    args = parser.parse_args()

    if args.command == "fetch":
        print(f"[*] Fetching arXiv paper ID: {args.id}...")
        paper = fetch_arxiv_by_id(args.id)
        if not paper:
            print(f"[!] Error: Paper with ID '{args.id}' not found on arXiv.", file=sys.stderr)
            sys.exit(1)
        path = save_paper_dossier(paper)
        print(f"[+] Successfully generated dossier: {path.relative_to(BASE_DIR)}")
        print(f"    Title: {paper['title']}")
        print(f"    Authors: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")

        if not args.no_index:
            try:
                import tools.generate_index as gen_idx
                gen_idx.rebuild_catalog_and_index()
                print("[+] Successfully updated corpus index and catalog.")
            except Exception as e:
                print(f"[-] Note: Could not auto-regenerate index: {e}")

    elif args.command == "search":
        print(f"[*] Querying arXiv for: '{args.query}' (max {args.max_results})...")
        papers = query_arxiv(args.query, max_results=args.max_results)
        print(f"[+] Found {len(papers)} papers:\n")
        for i, p in enumerate(papers, 1):
            print(f"{i}. [{p['id']}] {p['title']} ({p['year']})")
            print(f"   Authors: {', '.join(p['authors'][:2])}")
            print(f"   Categories: {', '.join(p['categories'][:3])}")
            print(f"   URL: {p['abs_url']}")
            if args.ingest:
                path = save_paper_dossier(p)
                print(f"   -> Ingested: {path.relative_to(BASE_DIR)}")
            print()

        if args.ingest and papers:
            try:
                import tools.generate_index as gen_idx
                gen_idx.rebuild_catalog_and_index()
                print("[+] Successfully updated corpus index and catalog.")
            except Exception as e:
                print(f"[-] Note: Could not auto-regenerate index: {e}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
