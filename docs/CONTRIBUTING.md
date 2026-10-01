# Contributing to the SOC-LMC Archive

We welcome contributions of scientific papers, empirical benchmarks, analytical tools, and theoretical essays exploring Second-Order Cybernetics and human-LLM conformity.

---

## 1. Adding a New Paper Dossier

To add a paper to `corpus/papers/`, follow these steps:

### Option A: Using the Automated arXiv Harvester
The fastest way to ingest a paper from arXiv is via our CLI tool:

```bash
# Ingest by arXiv ID (fetches metadata, classifies taxonomy, formats dossier)
python3 tools/arxiv_harvester.py fetch --id 2409.01754

# Rebuild the master index and catalog
python3 tools/generate_index.py
```

### Option B: Manual Creation
Create a new file `corpus/papers/{arxiv_id_or_slug}.md` adhering to this template:

```markdown
---
id: "2409.01754"
title: "Empirical evidence of Large Language Model's influence on human spoken communication"
authors:
  - "Jannik Brinkmann"
  - "Christian von der Weth"
  - "Mohan Kankanhalli"
year: 2024
venue: "arXiv preprint / Nature Human Behaviour"
arxiv_id: "2409.01754"
doi: "10.48550/arXiv.2409.01754"
url: "https://arxiv.org/abs/2409.01754"
categories: ["cs.CL", "cs.CY", "cs.HC"]
conformity_levels:
  - "L1_lexical"
  - "L4_symbolic_pragmatic"
cybernetic_concepts:
  - "circular_causality"
  - "structural_coupling"
  - "consensual_domain_drift"
empirical_substrate: "Spoken podcasts (737,083 hours) & controlled lab experiments (N=496)"
metrics:
  - "Excess word frequency Z-score"
  - "Synthetic-control causal inference"
  - "Vocabulary entrenchment persistence"
---

# Empirical evidence of Large Language Model's influence on human spoken communication

## 1. Executive Summary
Brief summary of the paper's core hypothesis, empirical setting, and findings.

## 2. Second-Order Cybernetic Framing
How does this study illustrate circular causality, the observer as participant, or autopoietic drift?

## 3. Empirical Methodology & Data Substrates
Details on datasets, control groups, and statistical models.

## 4. Key Findings & Quantitative Indicators
Bullet points of empirical effect sizes, significant tokens, or variance metrics.

## 5. BibTeX Citation
```bibtex
@article{brinkmann2024empirical,
  title={Empirical evidence of Large Language Model's influence on human spoken communication},
  author={Brinkmann, Jannik and others},
  journal={arXiv preprint arXiv:2409.01754},
  year={2024}
}
```
```

---

## 2. Running Automated Index Generation

Whenever paper dossiers are added or modified, run:

```bash
python3 tools/generate_index.py
```

This updates:
1. `corpus/catalog.json` (machine-readable database)
2. `corpus/INDEX.md` (categorized human-readable master index)
3. `corpus/bibliography.bib` (BibTeX repository)

---

## 3. Developing and Extending Harvester Queries

To add new query patterns, modify `config/queries.yaml`. Test query syntax with:

```bash
python3 tools/arxiv_harvester.py search --strategy lexical_conformity --max-results 5
```

Always respect arXiv's rate limit of at least 3 seconds per request.
