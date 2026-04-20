# SSB CPI Hybrid Assistant Roadmap

This document captures the intended project direction: build a focused hybrid assistant over real SSB CPI data.

## Principle

Do not expand the scope too quickly. The project should first become a reliable CPI-only hybrid assistant before expanding to other SSB topics, heavier evaluation tooling, or agentic workflows.

The first version should prove four things:

- real SSB CPI text can serve as the source corpus
- fixed structured CPI data can be queried
- follow-up questions can reuse explicit conversation state
- retrieval quality can be measured with a lightweight harness
- failures can be captured and reused as future regression cases

## Phase 1: CPI Data Replacement

Use curated SSB CPI material as the source corpus.

Target text documents:

- CPI definition
- about the CPI statistics
- CPI methodology or method-change notes
- CPI seasonal adjustment explanation
- CPI vs. HICP explanation
- Statbank table-change notes relevant to CPI

Target structured data:

- one or two fixed CPI Statbank tables
- cached CSV or JSON extract
- table metadata and original SSB query definition

The goal is not broad scraping. The goal is a small, explainable, source-grounded corpus.

## Phase 2: Session Memory / Conversation State

Add lightweight session memory as the first user-visible enhancement after the CPI data migration.

This should be implemented as structured conversation state, not broad long-term memory. The state should help the assistant resolve follow-up questions such as:

- "How has it changed over the last ten years?"
- "What about Oslo?"
- "Compare it with HICP."
- "Explain that more simply."

Recommended module:

```text
src/conversation_state.py
```

First-version logic should focus on the fields that directly resolve follow-up questions:

- current topic
- current metric
- current region
- current time range
- last route

These fields should be used before the state layer expands. The following fields can be recorded early, but they do not need to drive core logic on day one:

- last sources
- last structured table
- preferred language

First responsibilities:

- define a `ConversationState` schema
- create/reset state
- update state after each turn
- resolve simple follow-up references
- serialize state for feedback logs and evaluation artifacts
- use conservative reset/inheritance rules when the user's intent clearly shifts

The state should be visible and resettable in the UI. `app.py` may store it in Streamlit session state, but the logic should live in `src/conversation_state.py`. Topic inheritance should be conservative: clear follow-ups can reuse context, but a clear shift to another topic, metric, region, or analysis task should weaken or reset the previous state.

Future agents should read this state explicitly instead of owning hidden memory.

## Phase 3: Retrieval Harness

Add a file-based retrieval harness before adding more complex system behavior.

Minimum files:

```text
evals/
├── cpi_retrieval_cases.json
└── reports/
```

Each case should include:

- question
- expected source files
- expected keywords or facts
- optional notes explaining why the case matters

Initial metrics:

- source hit rate
- top-1 source hit
- top-3 source hit
- expected keyword hit rate
- failed cases

This makes retrieval quality visible before adding more complex routing or agent behavior.

## Phase 4: Fixed Structured Query Path

Add a narrow structured-data path for known CPI questions.

The first version should not search all Statbank tables. It should use a small registry of known CPI tables and support a limited set of questions such as:

- CPI development over the last ten years
- CPI value for a selected time period
- simple trend summary

The structured path should produce evidence that can be cited by the final answer.

## Phase 5: Hybrid Answer

Add a simple route between:

- document-only questions
- structured-data questions
- hybrid questions

Hybrid answers should combine:

- numeric evidence from the structured CPI table
- explanatory evidence from retrieved SSB text

The answer should distinguish table-derived numbers from retrieved document explanations.

## Phase 6: Feedback Loop

Feedback loop means more than UI likes and dislikes.

The intended loop is:

```text
system output -> harness evaluation -> failure capture -> hard case -> future regression test
```

Useful artifacts:

```text
artifacts/
├── eval_runs/
└── interaction_logs/
```

A future interaction log entry should capture:

- question
- resolved question
- conversation state before the turn
- conversation state after the turn
- route
- retrieved sources
- structured table used
- final answer
- model/provider
- embedding model
- top-k
- user feedback label
- timestamp
- configuration snapshot

Bad answers and failed harness cases should be promoted into hard-case eval sets.

## Phase 7: Regression

Regression testing should compare changes across stable cases.

Examples:

- chunk size 300 vs. 700
- one embedding model vs. another
- top-k 4 vs. top-k 8
- retrieval-only vs. LLM-generated answer
- old prompt vs. new prompt

The goal is to show both improvement and degradation. A change can improve source hit rate while increasing contamination or latency. The harness should make that tradeoff visible.

## Phase 8: Controlled Agentic Layer

Agents should come after the hybrid path and harness are stable.

The first agentic component should be a query planning agent. It should read `ConversationState` explicitly, not own hidden memory. It should not answer directly. It should produce an execution plan:

- route: document, structured, or hybrid
- topic: CPI
- structured table target
- time range
- retrieval query
- answer requirements

The second useful agent is an answer verification agent. It should check:

- whether numeric claims came from structured data
- whether definitions came from SSB text
- whether CPI and HICP were confused
- whether unsupported claims were introduced
- whether fallback should be used

Avoid autonomous multi-tool agents until the project has a stable evaluation harness.

## Portfolio Story

The project should be presented as:

> A hybrid assistant over SSB public CPI data, combining structured Statbank time-series queries with retrieval over SSB methodology and definition documents, supported by an evaluation harness and feedback loop for retrieval quality, grounding quality, routing correctness, structured query correctness, and regression safety.

The important engineering point is that the project does not only generate answers. It builds the ability to verify, compare, and improve answer-system quality.
