# Conversation State

Conversation state is lightweight session memory for the current task.

It is not long-term personal memory.

First-version fields:

```json
{
  "current_topic": "cpi",
  "current_metric": "CPI",
  "current_region": "Norway",
  "current_time_range": "last_10_years",
  "last_route": "hybrid"
}
```

Fields such as `last_sources`, `last_structured_table`, and `preferred_language` can be recorded early, but they do not need to drive first-version logic.

## Rules

- Store state explicitly, ideally in `src/conversation_state.py`.
- Keep state visible and resettable in the UI.
- Inherit context for clear follow-up questions.
- Weaken or reset state when the user clearly changes topic, metric, region, or task.
- Future agents should receive state explicitly and return proposed state updates.
