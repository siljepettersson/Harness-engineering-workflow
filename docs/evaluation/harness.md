# Evaluation Harness

The harness defines what good means.

Quality dimensions:

- retrieval quality
- structured query correctness
- routing correctness
- grounding quality
- regression safety
- fallback behavior

The first harness should be lightweight and file-based.

Use stable eval cases so changes to chunking, embedding, routing, prompts, or providers can be compared against the same cases.
