# SSB CPI Hybrid RAG Assistant

This project is a focused hybrid assistant for Norwegian public statistics, starting with the Consumer Price Index (CPI) from Statistics Norway (SSB).

The goal is not to build a generic chatbot. The goal is to build a source-grounded assistant that combines:

- structured CPI time-series data from SSB Statbank
- unstructured SSB documentation such as definitions, methodology notes, CPI/HICP explanations, and seasonal adjustment pages
- lightweight session memory for follow-up questions
- an optional source-bound LLM Wiki layer for persistent synthesis
- an evaluation harness and feedback loop for measuring retrieval, grounding, routing, and regression

The project is intentionally scoped to CPI first. A narrow, well-tested CPI assistant is more valuable than a broad statistics platform with shallow coverage.

## Core Architecture

The target system has three evidence layers:

```text
User question
    ↓
Conversation state / route decision
    ↓
Structured SSB query and/or document retrieval
    ↓
Grounded answer generation
    ↓
Evaluation harness and feedback loop
```

Example behavior:

- "How has CPI changed in Norway over the last ten years?" uses structured CPI time-series data.
- "What does CPI measure?" retrieves SSB definition and methodology documents.
- "Explain recent CPI changes and describe the measurement method" combines structured data with retrieved documentation.
- "What about Oslo?" reuses session context instead of treating the question as isolated.

## Why CPI

CPI is a strong first domain because it naturally combines statistical data and explanatory text.

It supports:

- time-series analysis
- inflation and index interpretation
- CPI vs. HICP comparison
- method and weighting changes
- seasonal adjustment explanations
- future forecasting or anomaly-detection extensions

The first version should not try to cover every SSB topic. CPI gives enough depth to demonstrate hybrid retrieval, structured data querying, source grounding, evaluation, and later controlled agentic planning.

## Current Baseline

The repository currently contains a modular RAG baseline:

- Streamlit UI in `app.py`
- assistant orchestration in `src/assistant.py`
- retrieval in `src/query.py`
- chunking and indexing in `src/chunking.py` and `src/indexing.py`
- Chroma vector store support in `src/vectorstore.py`
- local multilingual embeddings through `sentence-transformers`
- optional OpenAI-compatible or Anthropic LLM generation through `src/llm.py`
- structured response objects in `src/schemas.py`

The next implementation step is to replace placeholder data with curated SSB CPI sources and a small fixed structured CPI dataset.

## Data Plan

The intended data layout is:

```text
data/
├── raw/
│   ├── archive/
│   │   └── ssb/
│   │       └── cpi/
│   │           ├── 2026-04-23-about-cpi.html
│   │           └── 2026-04-23-monthly-cpi-api-response.json
│   └── ssb/
│       └── cpi/
│           ├── about-cpi.md
│           ├── cpi-methodology.md
│           ├── hicp.md
│           └── seasonal-adjustment.md
├── structured/
│   └── cpi/
│       ├── monthly-cpi.csv
│       ├── metadata.json
│       └── ssb-query.json
└── evals/
    └── cpi/
        ├── retrieval_cases.json
        ├── structured_cases.json
        └── grounding_cases.json
```

The first data version should be curated, not broad-scraped. A small number of high-quality SSB pages and one or two fixed Statbank tables are enough for the first milestone.

Raw SSB sources remain the source of truth. Curated Markdown under `data/raw/ssb/` is the normal retrieval and grounding layer. Original capture snapshots under `data/raw/archive/` preserve provenance and source-drift history, but they should not be indexed by default. Derived summaries, wiki pages, and generated answers must stay traceable to raw documentation or structured table output.

For Oslo-specific work, keep a separate geography schema. Use Oslo `bydel` names for general place understanding and session memory, but use exact SSB published area labels for structured statistics. Do not implicitly map one layer to the other.

## Session Memory

The first user-visible enhancement after CPI data migration should be lightweight session memory, implemented as structured conversation state.

This is not long-term personal memory. It is task context for the current session.

First-version state should focus on fields that directly support follow-up questions:

```json
{
  "current_topic": "cpi",
  "current_metric": "CPI",
  "current_region": "Norway",
  "current_time_range": "last_10_years",
  "last_route": "hybrid"
}
```

Additional fields such as `last_sources`, `last_structured_table`, and `preferred_language` can be recorded early, but they do not need to drive first-version logic.

Recommended module:

```text
src/conversation_state.py
```

Responsibilities:

- define a `ConversationState` schema
- create and reset state
- update state after each turn
- resolve simple follow-up references such as `it`, `that`, `same period`, and `what about Oslo`
- serialize state for feedback logs
- apply conservative inheritance when the user's intent shifts

The state should be visible and resettable in the UI. Clear follow-ups can inherit context, but a clear shift to another topic, metric, region, or task should weaken or reset the previous state.

## Source-Bound LLM Wiki

This project can use Andrej Karpathy's [LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) as an optional synthesis layer.

The idea is to maintain a persistent Markdown wiki of summaries, concept pages, comparisons, indexes, and logs over the raw sources. For this project, the wiki should not replace RAG or raw source retrieval. It should sit between raw SSB sources and the assistant:

```text
Raw SSB sources
    ↓
Source-bound CPI wiki
    ↓
RAG over wiki pages and raw source documents
    ↓
Structured SSB table query when needed
    ↓
Grounded hybrid answer
```

Suggested first wiki layout:

```text
wiki/
├── index.md
├── log.md
├── concepts/
│   ├── cpi.md
│   ├── hicp.md
│   └── cpi-ate.md
├── methods/
│   ├── cpi-methodology.md
│   └── seasonal-adjustment.md
├── comparisons/
│   └── cpi-vs-hicp.md
└── tables/
    └── monthly-cpi.md
```

This folder structure is domain-specific, not a requirement of the LLM Wiki pattern. Karpathy's pattern is more general: keep raw sources separate from the maintained wiki, and keep a schema or convention file that tells the LLM how to maintain the wiki. In this repository, the mapping is:

```text
data/raw/archive/  original capture snapshots for provenance
data/raw/ssb/      curated source-of-truth SSB documents
data/structured/   source-of-truth SSB table extracts
wiki/              derived CPI synthesis pages
AGENTS.md          project conventions for AI assistants
docs/operations/   operational workflows such as ingest, query, promote, and lint
artifacts/         eval runs, interaction logs, and wiki lint reports
```

The initial wiki folders reflect the kinds of CPI questions this assistant should answer:

- `concepts/` for terms such as CPI, HICP, CPI-ATE, index level, and inflation rate
- `methods/` for methodology, seasonal adjustment, weighting, and measurement notes
- `comparisons/` for pages such as CPI vs HICP or CPI vs CPI-ATE
- `tables/` for Statbank table descriptions and links to structured extracts
- `analysis/` for reviewed answer pages that are worth preserving

Folders such as `entities/` or `source-notes/` can be added later, but they are not necessary for the first CPI version. `entities/` becomes useful if the project starts tracking named organizations, places, datasets, or statistical bodies. `source-notes/` becomes useful if short source-summary pages are needed. Avoid `wiki/sources/` for now because it can be confused with `data/raw/`, which is the actual source-of-truth layer.

The wiki is a derived synthesis layer, not the source of truth. Every wiki page should link back to raw SSB sources. The harness should distinguish a `wiki hit` from `raw source grounding` to avoid summary drift.

Wiki lint is the health-check pipeline for this layer. It should be layered rather than a vague LLM review: structure lint, source lint, factual lint, and behavior lint. The detailed design is in [docs/operations/wiki-lint.md](docs/operations/wiki-lint.md).

## Evaluation Harness

The project should define quality through repeatable checks, not subjective impressions.

Key quality dimensions:

- `retrieval_quality`: expected SSB source appears in top-k results
- `structured_query_correctness`: correct table, metric, region, and time range are selected
- `routing_correctness`: the question is sent to document retrieval, structured query, or hybrid mode
- `grounding_quality`: answer claims are supported by retrieved documents or table output
- `regression_safety`: changes do not silently break previous cases
- `fallback_behavior`: weak evidence triggers a safer answer instead of confident fabrication

Initial harness files can be simple:

```text
evals/
├── cpi_retrieval_cases.json
├── cpi_structured_cases.json
├── cpi_grounding_cases.json
├── hard_cases.json
└── reports/
```

Example retrieval case:

```json
{
  "id": "cpi_hicp_difference",
  "question": "What is the difference between CPI and HICP?",
  "expected_sources": ["hicp-vs-cpi.md"],
  "expected_keywords": ["harmonised", "international comparison", "coverage"]
}
```

Useful first metrics:

- source hit rate
- top-1 and top-3 source hit
- expected keyword hit rate
- wrong-topic contamination
- failed cases

## Feedback Loop

Feedback is an engineering artifact, not only a UI reaction.

The intended loop is:

```text
question
    ↓
system output
    ↓
harness evaluation
    ↓
failure capture
    ↓
hard case added to eval set
    ↓
future regression run
```

The system should not be described as automatically learning unless online learning or automated parameter updates are implemented. The accurate description is an evaluation-driven feedback loop: retrieval failures, grounding failures, routing mistakes, and user-reported bad answers become regression and hard-case evaluation entries.

Interaction logs should eventually capture:

- original question
- resolved question
- conversation state before and after the turn
- route
- retrieved sources
- structured table used
- final answer
- model/provider
- configuration snapshot
- feedback label

## Controlled Agentic Layer

Agents should come later and should be controlled.

The first useful agent is a query planning agent. It should not answer directly. It should read the user question plus `ConversationState`, then produce an execution plan:

```json
{
  "route": "hybrid",
  "topic": "cpi",
  "metric": "CPI-ATE",
  "region": "Norway",
  "time_range": "last_10_years",
  "structured_query": {
    "table": "monthly_cpi",
    "metric": "CPI total index"
  },
  "retrieval_query": "CPI definition and measurement method"
}
```

A later answer verification agent can check whether:

- numeric claims came from structured data
- definitions came from SSB text
- CPI and HICP were not confused
- unsupported claims were not introduced
- fallback should be used

Agents should not own hidden memory. They should receive explicit state and return explicit state updates.

## Roadmap

Recommended order:

```text
1. CPI data migration
2. lightweight session memory / conversation state
3. optional source-bound CPI wiki layer
4. deterministic wiki lint
5. retrieval harness
6. fixed structured query path
7. hybrid answer with citations
8. feedback loop and regression checks
9. semantic lint and controlled query planning agent
10. answer verification agent
```

## Project Structure

Current repository:

```text
├── app.py
├── pyproject.toml
├── uv.lock
├── README.md
├── AGENTS.md
├── artifacts/
│   ├── eval_runs/
│   ├── interaction_logs/
│   └── wiki_lint/
├── data/
│   ├── raw/
│   │   ├── archive/
│   │   │   └── ssb/
│   │   │       └── cpi/
│   │   └── ssb/
│   │       └── cpi/
│   ├── structured/
│   │   └── cpi/
│   └── evals/
│       └── cpi/
├── docs/
│   ├── architecture/
│   ├── data/
│   ├── evaluation/
│   ├── operations/
│   ├── wiki/
│   └── ssb-cpi-hybrid-roadmap.md
├── src/
│   ├── assistant.py
│   ├── chunking.py
│   ├── config.py
│   ├── data_loader.py
│   ├── embeddings.py
│   ├── indexing.py
│   ├── llm.py
│   ├── query.py
│   ├── rag_pipeline.py
│   ├── schemas.py
│   └── vectorstore.py
└── wiki/
    ├── index.md
    ├── log.md
    ├── analysis/
    ├── comparisons/
    ├── concepts/
    ├── methods/
    └── tables/
```

## Running The Current Baseline

Install dependencies:

```bash
uv sync
```

Run the indexing and retrieval demo:

```bash
uv run python -m src.rag_pipeline
```

Run the Streamlit app:

```bash
uv run streamlit run app.py
```

The current app can run in retrieval-only mode without an LLM key. LLM generation requires credentials in a local `.env` file. Do not commit real API keys.

## Tech Stack

- Python 3.11+
- Streamlit
- LangChain
- ChromaDB
- `sentence-transformers`
- OpenAI-compatible or Anthropic LLM provider boundary
- `uv` for dependency management

Dependencies are defined in `pyproject.toml` and locked in `uv.lock`.

## Portfolio Positioning

The project story:

> A hybrid assistant over SSB CPI data that combines structured Statbank queries, raw-document RAG, an optional source-bound LLM Wiki layer, lightweight session memory, and an evaluation-driven feedback loop for retrieval quality, grounding quality, routing correctness, structured query correctness, and regression safety.

The important point is that this is not only an answer-generation project. It is a project about building the ability to verify and improve answer-system quality.
