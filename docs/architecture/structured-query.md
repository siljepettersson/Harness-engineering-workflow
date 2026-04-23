# Structured Query

The structured query path should start narrow.

First version:

- use one or two fixed CPI Statbank extracts
- store table metadata in `data/structured/cpi/`
- support known CPI time-series questions
- avoid broad automatic Statbank table discovery

The structured path should return evidence that can be cited by the final answer.

Important checks:

- selected table is correct
- selected metric is correct
- time range is correct
- region or category is correct
- answer does not invent numbers outside table output
