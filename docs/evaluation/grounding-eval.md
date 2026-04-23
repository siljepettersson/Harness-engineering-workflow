# Grounding Evaluation

Grounding evaluation checks whether the answer is supported by evidence.

Checks:

- numeric claims come from structured data
- definitions come from SSB text
- comparison claims cite sources for both sides
- unsupported claims are flagged
- weak evidence triggers fallback

This should start with simple rules and grow toward verifier-assisted checks later.
