# AGENTS.md

## Project Mission

Build a source-grounded SSB CPI hybrid assistant.

The project starts with Norway's Consumer Price Index (CPI) from Statistics Norway (SSB), then combines structured Statbank data, raw SSB documentation, a source-bound Markdown wiki, lightweight session memory, and evaluation-driven feedback loops.

## Non-Negotiable Rules

- Raw SSB sources and structured SSB data are the source of truth.
- Wiki pages are derived synthesis and must link back to raw sources.
- Answers must be grounded in retrieved sources or structured table output.
- Weak evidence should trigger fallback, not confident unsupported answers.
- Keep the first real-data version scoped to CPI.
- Do not put retrieval, indexing, prompt construction, or provider logic directly in `app.py`.
- Do not commit real API keys, generated vector stores, caches, or generated reports unless explicitly intended.

## Repository Map

- `app.py`: Streamlit UI only.
- `src/`: application and pipeline code.
- `data/raw/ssb/`: curated source-of-truth SSB documents used for retrieval and grounding.
- `data/raw/archive/`: original source capture snapshots for provenance; do not index by default.
- `data/structured/`: fixed SSB table extracts and metadata.
- `data/evals/`: stable evaluation cases and hard cases.
- `wiki/`: source-bound derived synthesis pages.
- `artifacts/`: eval runs, interaction logs, and wiki lint reports.
- `docs/`: detailed architecture, operations, evaluation, wiki, and data docs.

## Common Commands

- Install dependencies: `uv sync`
- Run baseline pipeline: `uv run python -m src.rag_pipeline`
- Run Streamlit app: `uv run streamlit run app.py`
- Future wiki lint: `uv run python -m src.wiki_lint`

Use `uv run ...` so commands use the locked project environment.

## Task Routing

Read the relevant detail doc only when needed:

- Architecture overview: `docs/architecture/overview.md`
- Hybrid RAG design: `docs/architecture/hybrid-rag.md`
- Conversation state: `docs/architecture/conversation-state.md`
- Source-bound wiki design: `docs/architecture/source-bound-wiki.md`
- Structured query path: `docs/architecture/structured-query.md`
- Controlled agents: `docs/architecture/controlled-agents.md`
- LLM Wiki workflow: `docs/operations/llm-wiki-workflow.md`
- Wiki lint workflow: `docs/operations/wiki-lint.md`
- Evaluation harness: `docs/evaluation/harness.md`
- Wiki frontmatter schema: `docs/wiki/frontmatter-schema.md`
- Wiki page types and style: `docs/wiki/page-types.md`
- Data source policy: `docs/data/source-policy.md`
- Roadmap: `docs/ssb-cpi-hybrid-roadmap.md`

## Completion Criteria

Before finishing a change:

- Keep raw/wiki/structured/artifact boundaries clear.
- Update docs when behavior, structure, or workflow changes.
- Preserve source links when editing wiki pages.
- Run relevant checks when code changes.
- Summarize what changed and call out anything not verified.

## Skills Policy

Do not turn every document into a skill.

Use docs for detailed knowledge and rules. Create a skill only when a workflow is stable, repeated, and has clear inputs, steps, outputs, and completion criteria.

Good future skill candidates:

- ingest SSB source
- run wiki lint
- promote answer to wiki
- add hard case
- run retrieval evaluation
