# LLM Wiki Workflow

This workflow adapts Andrej Karpathy's LLM Wiki pattern to the SSB CPI assistant.

Reference:

<https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>

## Layers

```text
data/raw/archive/  original capture snapshots
data/raw/ssb/      curated source-of-truth Markdown documents
wiki/              derived source-bound synthesis layer
AGENTS.md          project schema and conventions for AI assistants
artifacts/         eval runs, interaction logs, lint reports
```

## Ingest

1. Save the original capture snapshot under `data/raw/archive/ssb/cpi/` when practical.
2. Add a curated SSB source to `data/raw/ssb/cpi/`.
3. Preserve URL, retrieval date, license metadata, and archive path.
4. Create or update relevant wiki pages.
5. Update `wiki/index.md`.
6. Append an entry to `wiki/log.md`.

## Query

1. Search wiki pages for synthesis.
2. Search raw sources for grounding.
3. Use structured CPI data for numeric or time-series questions.
4. Answer with citations to raw sources and/or structured table output.

Archive files are normally excluded from retrieval. Use them for audits, source drift checks, and reproducing how a curated source was created.

## Promote

If an answer is useful beyond the current chat, save it as a reviewed analysis page in `wiki/analysis/`.

The promoted page must link to raw sources.

## Lint

Periodically check the wiki for:

- missing source links
- orphan pages
- stale claims
- contradictions
- missing frontmatter
- concepts mentioned but not defined
