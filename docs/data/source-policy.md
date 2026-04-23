# Source Policy

Raw SSB sources and structured SSB table extracts are the source of truth.

Rules:

- Store curated raw documentation under `data/raw/ssb/`.
- Store original capture snapshots under `data/raw/archive/`.
- Store structured extracts under `data/structured/`.
- Preserve source URLs, retrieval date, and license notes when available.
- Do not edit raw source content for convenience.
- Use wiki pages for synthesis, not source replacement.
- Do not index `data/raw/archive/` by default. Archive files support provenance, source-drift checks, lint, and reproducibility.
