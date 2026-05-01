# Evaluation Runs

Saved harness outputs and regression reports.

Each run should record:

- timestamp
- code/config snapshot
- dataset version
- metrics
- failed cases

The retrieval runner writes:

- timestamped JSON reports, one file per run
- `retrieval-eval-latest.json` as a stable pointer to the most recent combined run
