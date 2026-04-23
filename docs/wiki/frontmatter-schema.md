# Wiki Frontmatter Schema

Recommended wiki page frontmatter:

```yaml
---
source_type: wiki
topic: cpi
doc_type: concept
source_links:
  - data/raw/ssb/cpi/about-cpi.md
archive_links:
  - data/raw/archive/ssb/cpi/2026-04-23-about-cpi.html
tags:
  - cpi
last_updated: 2026-04-23
---
```

Required fields for first lint version:

- `source_type`
- `topic`
- `doc_type`
- `source_links`
- `last_updated`

`source_type` should be `wiki` for derived pages.

`archive_links` is optional. Use it when a curated source has an original capture snapshot.
