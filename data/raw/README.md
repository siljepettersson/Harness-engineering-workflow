# Raw Sources

This directory contains immutable source material.

For this project, raw sources have two levels:

- `ssb/`: curated SSB documents converted or saved as Markdown for retrieval and source grounding
- `archive/`: original capture snapshots, such as downloaded HTML, PDFs, API JSON responses, or CSV exports

Curated files under `ssb/` are the normal source of truth for definitions, methodology, table explanations, and other official context. Archive files preserve provenance and make it possible to audit what was captured before cleaning or conversion.

Rules:

- Do not edit raw source content to make it fit an answer.
- Preserve source URL, retrieval date, and license notes in frontmatter when available.
- Link curated Markdown files to archive snapshots when a snapshot exists.
- Derived wiki pages must link back to these files.
- RAG answers should be traceable to raw sources or structured table output.
- Exclude `data/raw/archive/` from default RAG indexing unless a workflow explicitly opts in.
