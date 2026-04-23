# Source-Bound CPI Wiki

This directory is the derived synthesis layer inspired by Andrej Karpathy's LLM Wiki pattern:

<https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>

The wiki is not the source of truth. It is a structured Markdown layer that summarizes, links, compares, and organizes raw SSB sources.

Rules:

- Every substantive wiki page should link back to raw SSB sources.
- Wiki pages should use frontmatter.
- The harness should distinguish `wiki` hits from `raw` source grounding.
- The wiki can be edited in Obsidian later, but plain Markdown remains the canonical format.

Recommended page frontmatter:

```yaml
---
source_type: wiki
topic: cpi
doc_type: concept
source_links:
  - data/raw/ssb/cpi/about-cpi.md
tags:
  - cpi
---
```
