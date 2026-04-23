# Controlled Agents

Agents should come later and should have narrow responsibilities.

Do not start with autonomous multi-tool agents.

## Query Planning Agent

The first useful agent is a query planning agent.

It should read:

- user question
- `ConversationState`
- available routes and table registry

It should output an execution plan, not the final answer.

## Answer Verification Agent

A later verifier can check:

- numbers came from structured data
- definitions came from SSB text
- CPI and HICP were not confused
- unsupported claims were not introduced
- fallback should be used

Agents should not own hidden memory.
