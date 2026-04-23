# Architecture Overview

This project is a source-grounded hybrid assistant for SSB CPI data.

The system combines:

- structured CPI time-series data from SSB Statbank
- raw SSB documentation
- a source-bound Markdown wiki
- RAG retrieval over raw and wiki documents
- lightweight session memory
- evaluation harnesses and feedback loops

## Source Hierarchy

```text
data/raw/archive/  original capture snapshots for provenance
data/raw/ssb/      curated source-of-truth documentation
data/structured/   source-of-truth table extracts
wiki/              derived synthesis layer
artifacts/         generated reports and logs
```

Curated SSB sources and structured table extracts are the source of truth for answers. Archive snapshots are kept for provenance, source-drift checks, and reproducibility. Wiki pages are derived synthesis and must link back to raw sources.

## Target Flow

```text
User question
    ↓
Conversation state / route decision
    ↓
Structured query and/or document retrieval
    ↓
Grounded answer generation
    ↓
Evaluation harness and feedback loop
```

The first version should remain CPI-only until data ingestion, retrieval, grounding, and evaluation are stable.
