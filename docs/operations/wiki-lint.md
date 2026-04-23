# Wiki Lint

Wiki lint is the health-check pipeline for the source-bound CPI wiki.

It protects the derived wiki layer from becoming a collection of plausible but ungrounded summaries. The raw SSB documents and structured Statbank extracts remain the source of truth. Wiki pages are useful because they organize and synthesize those sources, but they must stay structured, linked, traceable, and consistent.

## What Lint Is Not

Wiki lint is not only Markdown formatting.

Wiki lint is also not just asking an LLM to read the whole wiki and give general comments. That is too vague to be useful as an engineering process.

Wiki lint should produce repeatable findings with:

- issue type
- severity
- affected page
- evidence or reason
- suggested action

## Lint Layers

The lint process should be layered.

```text
structure lint
    ↓
source lint
    ↓
factual lint
    ↓
behavior lint
```

Each layer checks a different risk.

## 1. Structure Lint

Structure lint checks whether wiki pages are healthy Markdown knowledge objects before judging whether their content is true.

This should be deterministic in the first version.

Checks:

- page has frontmatter
- page has one H1 title
- page is not empty
- page has `source_type`
- page has `topic`
- page has `doc_type`
- page has `source_links`
- page has `last_updated`
- page has a summary section
- page has related pages or wikilinks when relevant
- page is listed in `wiki/index.md`
- page has at least one inbound or outbound link, except `index.md` and `log.md`
- comparison pages link back to relevant concept pages
- `wiki/index.md` exists
- `wiki/log.md` exists
- wikilinks are not broken

Example issue types:

- `missing_frontmatter`
- `missing_h1`
- `empty_page`
- `missing_summary`
- `missing_index_entry`
- `orphan_page`
- `broken_wikilink`
- `invalid_doc_type`
- `missing_related_page`

## 2. Source Lint

Source lint checks whether wiki claims can be traced back to raw SSB sources or structured table output.

This matters because the wiki is a derived synthesis layer, not the source of truth.

Checks:

- `source_links` exists and is non-empty
- `source_links` point to curated files under `data/raw/ssb/` when referencing documentation
- `archive_links` point to original snapshots under `data/raw/archive/` when snapshots exist
- structured-data claims point to `data/structured/` or table metadata
- source paths exist
- definition pages cite raw SSB source documents
- comparison pages cite raw sources for each compared concept
- numeric claims cite structured data or raw table metadata
- wiki-to-wiki links do not replace raw source links

Example issue types:

- `missing_source_link`
- `broken_source_link`
- `wiki_only_grounding`
- `ungrounded_definition`
- `ungrounded_comparison`
- `ungrounded_numeric_claim`
- `missing_structured_data_reference`

## 3. Factual Lint

Factual lint checks whether wiki content is internally consistent and not stale.

This layer can be LLM-assisted after deterministic lint is stable. It should operate on small related page groups rather than the whole wiki at once.

Example page groups:

```text
wiki/concepts/cpi.md
wiki/concepts/hicp.md
wiki/comparisons/cpi-vs-hicp.md
wiki/methods/cpi-methodology.md
```

Checks:

- pages do not contradict each other
- newer raw sources do not supersede old claims
- time scope is clear when a claim is period-specific
- CPI, HICP, and CPI-ATE are not confused
- scope, coverage, and international comparability are described consistently
- important concepts mentioned repeatedly have their own pages
- pages include missing cross-references where useful

Example issue types:

- `stale_claim`
- `cross_page_contradiction`
- `metric_confusion`
- `time_scope_conflict`
- `missing_concept_page`
- `missing_cross_reference`
- `unsupported_claim`

## 4. Behavior Lint

Behavior lint connects wiki health to assistant behavior.

It checks whether the assistant can use the wiki safely in a full retrieval or hybrid-answer path. This overlaps with the evaluation harness, but the focus is still wiki-related risk.

Checks:

- wiki pages are retrieved for synthesis questions
- raw sources are retrieved for grounding questions
- answers distinguish wiki synthesis from raw evidence
- numeric answers come from structured data
- definition answers come from SSB text
- CPI and HICP are not mixed up
- weak evidence triggers fallback instead of confident unsupported answers

Example high-risk questions:

- What is CPI?
- What is HICP?
- What is CPI-ATE?
- What is the difference between CPI and HICP?
- Why is CPI seasonally adjusted?
- How has CPI changed over the last ten years?

Example issue types:

- `wiki_retrieval_miss`
- `raw_grounding_miss`
- `wrong_route`
- `weak_grounding`
- `needs_fallback`
- `unsupported_answer_claim`
- `structured_data_missing`

## First Implementation

The first version should be deterministic.

It should not call an LLM.

Minimum checks:

- frontmatter exists
- H1 title exists
- required metadata exists
- `source_links` exists
- source paths exist
- `wiki/index.md` exists
- `wiki/log.md` exists
- pages are listed in `wiki/index.md`
- no empty pages
- no broken wikilinks

Suggested command:

```bash
uv run python -m src.wiki_lint
```

## Later LLM-Assisted Lint

After deterministic lint works, add LLM-assisted semantic checks.

The LLM should receive:

- a small group of related wiki pages
- their linked raw source excerpts
- the allowed issue taxonomy
- a required JSON output schema

The LLM should not output only free-form advice.

## Issue Taxonomy

Use stable issue types so lint results can be counted, filtered, and promoted into regression cases.

Initial taxonomy:

```text
missing_frontmatter
missing_h1
empty_page
missing_summary
missing_index_entry
orphan_page
broken_wikilink
invalid_doc_type
missing_related_page
missing_source_link
broken_source_link
wiki_only_grounding
ungrounded_definition
ungrounded_comparison
ungrounded_numeric_claim
missing_structured_data_reference
stale_claim
cross_page_contradiction
metric_confusion
time_scope_conflict
missing_concept_page
missing_cross_reference
unsupported_claim
wiki_retrieval_miss
raw_grounding_miss
wrong_route
weak_grounding
needs_fallback
unsupported_answer_claim
structured_data_missing
```

Severity levels:

```text
error
warning
info
```

## Report Format

Detailed reports should be machine-readable and stored under:

```text
artifacts/wiki_lint/
```

Example:

```json
{
  "timestamp": "2026-04-23T12:00:00Z",
  "mode": "deterministic",
  "pages_checked": 12,
  "errors": 2,
  "warnings": 5,
  "issues": [
    {
      "severity": "error",
      "issue_type": "missing_source_link",
      "page": "wiki/comparisons/cpi-vs-hicp.md",
      "message": "Comparison page has no raw SSB source links.",
      "suggested_action": "Add source_links to raw CPI and HICP source pages."
    }
  ]
}
```

`wiki/log.md` should record only a human-readable summary and link to the detailed artifact.

Example:

```markdown
## [2026-04-23] lint
- Mode: deterministic
- Pages checked: 12
- Errors: 2
- Warnings: 5
- Report: artifacts/wiki_lint/2026-04-23T120000.json
```

## Feedback Loop

High-severity lint issues should not disappear after they are fixed.

Important lint failures can become:

- hard cases
- regression checks
- retrieval eval cases
- grounding eval cases
- structured query eval cases

This connects wiki maintenance to the broader harness and feedback-loop strategy.

```text
lint finding
    ↓
fix wiki or source metadata
    ↓
add hard case when useful
    ↓
rerun regression
```

## Position In The Roadmap

Wiki lint should come immediately after the source-bound CPI wiki layer.

Recommended sequence:

```text
1. CPI data migration
2. session memory
3. source-bound CPI wiki
4. deterministic wiki lint
5. retrieval harness
6. structured query path
7. hybrid answer
8. semantic lint and feedback loop
9. controlled query planning agent
```
