# Hybrid RAG

Hybrid RAG means the assistant can use both structured data and unstructured text.

Use structured SSB data for:

- numeric questions
- time-series questions
- trend summaries
- table-backed comparisons

Use document retrieval for:

- definitions
- methodology
- CPI/HICP explanations
- seasonal adjustment explanations
- source-grounded narrative context

Use both for hybrid questions, such as:

> Explain CPI changes over the last ten years and describe how the indicator is defined.

The answer should distinguish table-derived evidence from retrieved document explanations.
