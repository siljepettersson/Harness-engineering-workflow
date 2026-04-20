# AGENTS.md — Project Guide for AI Assistants

## What is this project?

This project started as a RAG demo/MVP, but the current direction is to evolve it into a **hybrid assistant over real open data from Statistics Norway (SSB)**.

The target domain is CPI first, not all public statistics. The project should become an SSB CPI Hybrid RAG Assistant that combines:

- structured CPI time-series data from SSB Statbank
- unstructured SSB text such as definitions, methodology, CPI/HICP explanations, seasonal adjustment notes, and table-change information
- a lightweight evaluation harness
- an evaluation-driven feedback loop
- later, controlled agentic layers for query planning and answer verification

The main engineering idea is not only to produce answers. The project should show how answer-system quality is defined, measured, compared, and improved.

## Why this direction?

SSB CPI is a strong first domain because it has real open statistical data, public documentation, and a natural split between structured and unstructured evidence.

Examples:

- A question about CPI development over ten years should use structured Statbank data.
- A question about what CPI measures should use SSB definition and methodology documents.
- A question asking for both trend explanation and indicator definition should combine structured data and retrieved text.

The project should stay focused. Do not try to build a full Norway statistics platform in the first version.

## Tech Stack

| Component | Choice | Why |
|-----------|--------|-----|
| Framework | LangChain | Industry standard for RAG |
| Vector DB | ChromaDB | Simple (pip install, no server), good for demos |
| Embeddings | paraphrase-multilingual-MiniLM-L12-v2 | Runs locally, free, good Norwegian support |
| UI | Streamlit | Quick to build, clean chat interface, easy to demo |
| Structured data | SSB Statbank / curated CSV cache | Fixed CPI tables first, no broad table search in the MVP |
| LLM | OpenAI-compatible or Anthropic provider boundary | Optional for generation; retrieval-only fallback works without a key |
| Evaluation | File-based eval cases and reports | Lightweight harness before heavier platforms |
| Language | Python | Everything in Python |

**Key design decision:** No API keys required for the core pipeline (embeddings + vector store run locally). This means anyone can clone and test the retrieval without paying for anything. The LLM is the only component that may need an API key.

LLM API keys belong in a local `.env` file and must not be committed. The UI should show only LLM providers that have API keys configured, plus a retrieval-only option. Use `.env.example` as the public template.

## Project Structure

```
RAG-knowledge-assistant/
├── AGENTS.md              # This file — project context for AI assistants
├── README.md              # Project usage notes and write-up
├── pyproject.toml         # Project metadata and dependencies
├── uv.lock                # Locked dependency set for uv
├── .gitignore             # Excludes envs/ and vectorstore/
├── app.py                 # Thin Streamlit chat UI
├── data/                  # Target is SSB CPI text and structured data
├── src/
│   ├── __init__.py
│   ├── assistant.py       # UI-facing assistant orchestration boundary
│   ├── data_loader.py     # Loads markdown documents and attaches metadata
│   ├── chunking.py        # Splits documents into retrieval chunks
│   ├── embeddings.py      # Creates the embedding model
│   ├── vectorstore.py     # Chroma create/load operations
│   ├── indexing.py        # Orchestration for indexing documents into Chroma
│   ├── llm.py             # LLM provider boundary
│   ├── query.py           # Retrieval/query logic against the vector store
│   ├── schemas.py         # Structured assistant response objects
│   └── rag_pipeline.py    # Compatibility entry point that wires indexing + query
└── vectorstore/           # Generated persisted Chroma data (gitignored)
```

## Data Direction

The data target is real SSB CPI material.

Recommended future layout:

```text
data/
├── text/
│   └── cpi/
│       ├── cpi-definition.md
│       ├── about-cpi.md
│       ├── cpi-method-changes.md
│       ├── cpi-seasonal-adjustment.md
│       ├── hicp-vs-cpi.md
│       └── statbank-table-changes.md
├── structured/
│   └── cpi/
│       ├── cpi-monthly.csv
│       ├── cpi-metadata.json
│       └── ssb-query.json
└── evals/
    └── cpi/
        ├── retrieval_cases.json
        ├── expected_sources.json
        └── expected_facts.json
```

Keep the first version narrow: CPI only, curated documents, and one or two fixed structured tables.

## Build Phases

### Phase 1: Baseline RAG Pipeline ✅
- modular RAG pipeline under `src/`
- local embedding model
- persisted Chroma vector store
- retrieval-only mode
- optional LLM generation
- Streamlit UI and retrieval trace

### Phase 2: SSB CPI Data Replacement
- add curated SSB CPI text documents
- add fixed SSB CPI structured data files
- preserve current RAG module boundaries
- document source attribution and license notes

### Phase 3: Session Memory / Conversation State
- add `src/conversation_state.py`
- first make current topic, metric, region, time range, and last route work for follow-up questions
- record last sources and last structured table, but do not require them to drive first-version logic
- keep state visible and resettable in the UI
- inherit context conservatively when intent shifts clearly
- use state to support follow-up questions
- do not implement broad long-term personal memory in the first version

### Phase 4: Evaluation Harness
- add CPI retrieval eval cases
- measure source hit rate, top-k hit rate, keyword hit rate, and failed cases
- add hard cases from observed failures
- keep the harness lightweight and file-based

### Phase 5: Basic Hybrid Path
- add fixed structured query path for known CPI tables
- add simple routing between document, structured, and hybrid questions
- add hybrid answers with both table evidence and text sources

### Phase 6: Feedback Loop and Regression
- compare results across chunking, embedding, top-k, prompt, and LLM provider changes
- save baseline reports
- convert failures and user-reported bad answers into regression cases
- include conversation state before/after each turn when useful for failure analysis

### Phase 7: Controlled Agentic Layer
- add query planning agent only after hybrid path and harness are stable
- pass conversation state explicitly into future agents
- do not let agents own hidden memory
- add answer verification agent later for grounding and safer fallback
- avoid autonomous multi-tool agents in the first project versions

### Architecture Rules
- `app.py` should only handle Streamlit layout, session state, user input, and display.
- Do not put vector store loading, embedding setup, prompt construction, or LLM provider details directly in `app.py`.
- Put high-level orchestration in a dedicated module such as `src/assistant.py`.
- Put structured dataclasses or response schemas in a dedicated module such as `src/schemas.py`.
- Keep low-level retrieval in `src/query.py` or a retrieval-specific module.
- Keep prompt/source formatting utilities reusable from `src/rag_pipeline.py` unless they need to be split later.
- Put LLM API handling in a dedicated module such as `src/llm.py`.

`src/assistant.py` is the public assistant service boundary for UI callers. It should expose a small stable API such as `answer_question(...)` and coordinate retrieval, prompt building, LLM generation, and response-status mapping. It exists so `app.py` can stay focused on Streamlit display logic and does not need to know Chroma, embeddings, prompt internals, or provider-specific LLM details.

Do not put low-level retrieval algorithms or provider-specific HTTP request code in `src/assistant.py`; keep those in retrieval and LLM modules.

Recommended Phase 3 flow:

```text
app.py
    -> src.assistant.answer_question(...)
        -> retrieve context
        -> build prompt
        -> generate LLM answer
        -> return structured AssistantResponse
```

The retrieval result should not be only a raw `list[Document]` or a plain string. Use a structured object that can grow over time.

Initial retrieved-context fields:
- `question`
- `retrieved_chunks`
- `source_labels`
- `context_block`
- `topic_filter_used`
- `retrieval_notes`

Initial assistant-response fields:
- `question`
- `status`
- `answer`
- `sources`
- `retrieved_context`
- `prompt`
- `model_name`
- `error`

Include response status from the first implementation so the UI can branch cleanly. Suggested statuses:
- `answered`: retrieval and LLM generation both succeeded
- `retrieval_only`: retrieval worked, but no LLM was configured, so the app shows retrieved context or a prompt-ready fallback
- `no_results`: retrieval returned no useful context
- `configuration_error`: required settings such as an LLM API key or base URL are missing or invalid
- `runtime_error`: an unexpected error happened during retrieval or generation

Response contract conventions:
- Normalize UI display values before low-level retrieval or structured querying. In the SSB CPI direction, selection should become topic, route, and table selection; do not pass UI labels directly into low-level modules.
- `RetrievedContext.source_labels` are retrieval-produced labels for retrieved chunks.
- `AssistantResponse.sources` is the final UI-facing source list for the answer. It can initially mirror `source_labels`, but later may contain only sources used in the final answer.
- `RetrievedContext.retrieved_chunks` may contain LangChain `Document` objects internally, but `app.py` should not depend on detailed `Document.metadata` structure.
- `AssistantResponse.prompt` should store the full prompt for trace/debug. The UI can hide it by default or show a preview.

Future fields can include:
- `rewritten_queries`
- `subqueries`
- `rerank_scores`
- `evidence_status`
- `retrieval_rounds`
- `confidence`

### Harness and Feedback Loop Direction

The project should explicitly define what good means and how it is measured.

Quality dimensions:

- retrieval quality
- structured query correctness
- routing correctness
- grounding quality
- regression safety
- latency
- fallback behavior

Feedback loop means:

```text
question -> system output -> harness evaluation -> failure capture -> hard case -> future regression test
```

Do not describe this as automatic learning unless online learning or automated parameter updates are implemented. The accurate description is an evaluation-driven feedback loop.

### Agent Direction

Agents should come later and should be controlled.

Agents should read the shared conversation state explicitly. Memory belongs in `src/conversation_state.py`, not inside an agent's hidden state.

Preferred first agent:

- query planning agent that turns a natural-language question into a structured execution plan

Preferred later agent:

- answer verification agent that checks numbers, definitions, source grounding, CPI/HICP confusion, and unsupported claims

Avoid heavy autonomous agents until the hybrid architecture and evaluation harness are stable.

## Development Conventions

- **Language:** Documents are in Norwegian. Code and comments in English.
- **Git workflow:** Never push to main. Always use feature branches and PRs.
- **Branch naming:** Prefer descriptive refactor/feature branches (e.g. `refactor/query-module`)
- **PR base:** Each PR builds on the previous one until merged.
- **Dependencies:** Managed with `uv`. Defined in `pyproject.toml`, locked in `uv.lock`. Run `uv sync` to install.
- **Python version:** `>=3.11` (see `pyproject.toml`)

## Running the project

```bash
# Setup (using uv for dependency management)
uv sync

# Run the modular pipeline entry point
uv run python -m src.rag_pipeline

# Run the app
uv run streamlit run app.py
```

Do not rely on plain `python3 -m src.rag_pipeline` in the VM unless dependencies have been installed into that interpreter. The working command in this repo is the `uv run ...` invocation above.

## What to keep in mind

- The target direction is an SSB CPI hybrid assistant.
- Keep the first real-data version scoped to CPI.
- Treat session memory as structured conversation state, not broad long-term memory.
- Showing measurable quality matters more than adding flashy agent behavior.
- Favor clear module boundaries over putting everything into `app.py`.
- Prefer structured return objects over loosely passing strings and raw document lists between layers.
- Treat eval cases, hard cases, and feedback logs as first-class project artifacts.
