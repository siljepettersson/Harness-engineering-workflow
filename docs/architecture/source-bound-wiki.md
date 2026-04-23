# Source-Bound Wiki

The wiki is a derived synthesis layer inspired by Andrej Karpathy's LLM Wiki pattern:

<https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>

It should help the assistant reuse organized knowledge instead of rebuilding the same synthesis from raw chunks on every query.

## Rule

The wiki is not the source of truth.

Every substantive wiki page must link back to raw SSB sources or structured table metadata.

## Layers

```text
data/raw/archive/  original capture snapshots for provenance
data/raw/ssb/      curated immutable source material
wiki/              source-bound synthesis pages
docs/              schema and operating rules
artifacts/         generated checks and logs
```

The harness should distinguish `wiki hit` from `raw source grounding` to avoid summary drift.

Archive snapshots are not the normal retrieval corpus. They support reproducibility, source-drift checks, and audits of how curated Markdown or structured extracts were derived.
