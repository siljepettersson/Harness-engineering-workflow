# Structured Data

Structured data should start with fixed SSB CPI extracts.

Each extract should have:

- source table identifier
- query metadata
- retrieval date
- archive path for the original API response when available
- dimensions
- metric description
- local file path

Geographic labels should also stay source-faithful. If an SSB table is published with labels such as `Oslo and Baerum municipality`, keep that exact label in structured data instead of rewriting it into Oslo bydeler.

Avoid broad automatic table discovery in the first implementation.
