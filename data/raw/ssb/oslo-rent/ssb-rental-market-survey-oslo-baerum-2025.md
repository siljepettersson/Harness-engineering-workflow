---
source_type: raw_ssb_document
topic: oslo-rent
title: Rental market survey - Oslo and Baerum seed source
statistics_name: Rental market survey
source_url: https://www.ssb.no/en/priser-og-prisindekser/boligpriser-og-boligprisindekser/statistikk/leiemarkedsundersokelsen
source_table: 09895
retrieval_date: 2026-04-29
source_updated_date: 2025-12-22
language: en
geographic_coverage: Oslo and Baerum municipality
license: CC BY 4.0
---

# Rental market survey

This curated source is based on Statistics Norway's official Rental market survey page. It is intentionally kept medium-sized: large enough for chunking, retrieval, and later wiki promotion, but still small enough to avoid unnecessary token cost.

## What the statistic measures

Statistics Norway says the purpose of the survey is to measure rent levels in Norway grouped into different segments of the rental market.

This is an Oslo-relevant source because the selected figures and the source table publish values for `Oslo and Baerum municipality`. That makes it suitable for a first real-data milestone in this project, where Oslo-specific structured statistics are needed.

## Why this source is useful

This page contains several things the assistant will need later:

- a plain-language description of what the statistic measures
- official figures for Oslo and Baerum municipality
- definitions for what rent means in this survey
- a warning that the survey is a rent level survey, not a direct time-series index
- methodology and sampling notes
- a direct link to StatBank source table `09895`

## Selected figures for 2025

The official page shows selected figures for dwellings with two rooms.

- The whole country: average monthly rent `11,790` NOK, average annual rent per square metre `3,040` NOK
- Oslo and Baerum municipality: average monthly rent `15,260` NOK, average annual rent per square metre `4,060` NOK
- Bergen municipality: average monthly rent `11,870` NOK, average annual rent per square metre `3,200` NOK
- Trondheim municipality: average monthly rent `11,850` NOK, average annual rent per square metre `3,190` NOK
- Stavanger municipality: average monthly rent `11,400` NOK, average annual rent per square metre `2,880` NOK

The same statistics page links these values to StatBank table `09895`.

## Definitions

The page defines rents as the actual rent of the rental object. Monthly rents are selected.

It also states that no adjustments are made for rents that include electricity and or heating, except for predicted monthly rents in another table.

The page defines number of rooms as bedrooms and living rooms, excluding kitchens, bathrooms, and storage rooms. Rooms beyond eight are omitted.

These definitions matter for grounding. The assistant should not turn these figures into broader claims about total housing costs or full cost-of-living pressure unless the source supports that.

## Scope and comparability limits

The survey measures rent levels. It should not be treated as a direct rent development index.

The page explains that the annual survey uses a new sample each year. Because the sample changes, average rent levels from different years are not directly comparable as a pure development series.

That means the assistant should be careful with questions such as:

- "How much is rent in Oslo and Baerum in 2025?" -> supported
- "How has rent changed over time in Oslo and Baerum?" -> answer more cautiously and mention comparability limits

## Method and sampling notes

Statistics Norway says rents are mainly collected by web questionnaires directly with households.

Because registers of rental units and tenants are incomplete, the potential population is built by linking several registers. The sample is then drawn by random selection from this population.

The page says the gross sample is about `35,000` persons or addresses, with overrepresentation of the largest municipalities. The net sample is about `10,000` responses. A new sample is selected each year without overlap with previous samples.

## Relation to CPI

The page also says the statistics are used within Statistics Norway by the National Accounts, the Consumer Price Index, and the Household Budget Survey.

It further states that the Rental Market Survey sample is also the sample of the monthly rent survey in the CPI.

That makes this source useful even inside a CPI-oriented repository: it is an Oslo-relevant statistics source that still connects back to the CPI ecosystem.

## Recommended use in this project

This file is suitable for:

- retrieval questions such as "What does the rental market survey measure?"
- definition questions such as "What counts as a room?"
- grounding questions such as "Are Oslo and Baerum figures directly comparable across years?"
- hybrid answers that combine structured values from table `09895` with explanatory text from this page

## Source note

Source page:

- https://www.ssb.no/en/priser-og-prisindekser/boligpriser-og-boligprisindekser/statistikk/leiemarkedsundersokelsen

Source table:

- https://www.ssb.no/en/statbank/table/09895
