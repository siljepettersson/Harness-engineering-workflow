# Oslo Geography

This project needs a clear geography policy because Oslo can appear in two different forms:

- as a municipal administrative geography
- as an SSB-published statistical area label

Those are not the same thing.

## Two layers

### 1. Oslo bydel structure

Use the 15 Oslo bydeler as the general administrative geography layer:

- Alna
- Bjerke
- Frogner
- Gamle Oslo
- Grorud
- Grunerlokka
- Nordre Aker
- Nordstrand
- Sagene
- St. Hanshaugen
- Stovner
- Sondre Nordstrand
- Ullern
- Vestre Aker
- Ostensjo

This layer is useful for:

- query understanding
- session memory and context normalization
- future wiki pages about Oslo areas

### 2. SSB published area labels

For structured statistics, use the exact area labels from the source table.

Example from the SSB Rental market survey, table `09895`:

- The whole country
- Oslo and Baerum municipality
- Akershus except Baerum municipality
- Bergen municipality
- Trondheim municipality
- Stavanger municipality

This layer is useful for:

- structured filters
- answer citations
- table-grounded comparisons

## Policy

- Do not assume that SSB rent statistics are published by bydel.
- Do not rewrite an SSB area label into one or more bydeler unless the official source itself provides that mapping.
- If a user asks for a bydel-level answer but the table is municipality-level, say that clearly.

Machine-readable schema:

- `data/structured/oslo-geography/oslo_geography.json`
