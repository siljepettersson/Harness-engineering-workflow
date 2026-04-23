# Raw Archive

This directory stores original capture snapshots for provenance.

Examples:

- downloaded HTML from an SSB page
- original PDF files
- raw Statbank API JSON responses
- raw CSV or XML exports
- screenshots or other capture artifacts when useful for auditability

The archive is not the default retrieval corpus. It exists so the project can later prove what source material was captured, when it was captured, and which curated Markdown or structured extract was derived from it.

Rules:

- Keep archived files close to the original captured form.
- Use date-prefixed filenames when practical, such as `2026-04-23-about-cpi.html`.
- Do not edit archive files to improve readability.
- Link curated files back to archived snapshots when a snapshot exists.
- Exclude archive files from default RAG indexing unless a workflow explicitly opts in.
