---
source_type: raw_ssb_document
topic: oslo-rent
title: Rental market survey - annual overview
statistics_name: Rental market survey
source_url: https://www.ssb.no/en/priser-og-prisindekser/statistikker/lmu/aar
retrieval_date: 2026-04-29
source_updated_date: 2020-12-18
language: en
license: CC BY 4.0
---

# Rental market survey - annual overview

This curated source is based on Statistics Norway's yearly rental market survey overview page.

It complements the first Oslo and Baerum seed source by adding:

- a more compact annual overview structure
- selected tables listed together in one place
- clearer definitions for predicted monthly rents
- more direct context for later use of table `09897`

## What this annual page adds

The page brings together the main yearly outputs from the rental market survey and points to the main StatBank tables:

- `09895`: average monthly rents and annual rents per square metre by price zone and number of rooms
- `09897`: predicted monthly rents by price zone, number of rooms, and utility floor space
- `06230`: rents by period of tenancy
- `09896`: landlords in the main cities, by type of landlord

That makes it a useful bridge page between raw explanation and structured query work.

## Key figures shown on the page

The annual page shows selected 2020 figures for two-room dwellings:

- The whole country: `9,320` NOK average monthly rent and `2,350` NOK annual rent per square metre
- Oslo and Baerum municipality: `12,080` NOK average monthly rent and `3,180` NOK annual rent per square metre
- Bergen municipality: `9,150` NOK average monthly rent and `2,390` NOK annual rent per square metre
- Trondheim municipality: `9,560` NOK average monthly rent and `2,520` NOK annual rent per square metre
- Stavanger municipality: `8,740` NOK average monthly rent and `1,980` NOK annual rent per square metre

These values are from the same rental statistics family as table `09895`.

## Definitions

The page defines rents as the actual rent of the rental object. Monthly rents are selected.

It also says that no adjustments are made for rents that include electricity and or heating, except for predicted monthly rents in table `09897`, where the markup for electricity and or heating is excluded.

Number of rooms means bedrooms and living rooms, excluding kitchens, bathrooms, and storage rooms. Rooms beyond eight are omitted.

The page also defines predicted monthly rents as rents estimated by a regression model using observed dwelling characteristics.

## Why table 09897 matters

The annual page explicitly points to table `09897` as a more detailed output.

That table is useful because it breaks the rental market into smaller price zones, including Oslo-specific grouped areas such as:

- Oslo - Sentrum, Frogner, Ullern and St. Hanshaugen
- Oslo - Grunerlokka, Gamle Oslo, Sagene, Nordre Aker and Vestre Aker
- Oslo - Ostensjo, Nordstrand and Bjerke
- Oslo - Sondre Nordstrand, Grorud, Stovner and Alna

These are not official administrative bydeler as a statistical publication standard. They are SSB price zones used inside the rent model output.

## Comparability warnings

The annual page says the rental market survey is a price level survey and is not conducted for price development.

Average rent levels from different years are not directly comparable because each year uses a unique sample that can differ on variables that matter for rent levels.

The same page also notes that from 2012 detailed predicted monthly rents are estimated by hedonic techniques.

## Production and sampling notes

The page says the population is all rental units inhabited by private tenants in Norway.

Rents are mainly collected by web questionnaires directly with households. Electronic register data from municipalities and student organisations are also collected.

The gross sample in the cited production section is about `35,286` persons or addresses, including an overrepresentation of the largest municipalities. The net sample is about `9,727`.

The page also states that detailed predicted monthly rents for different geographical areas and size groups are estimated using a regression model.

## Recommended use in this project

This file is suitable for:

- retrieval questions about what the rental market survey is
- grounding questions about predicted monthly rents
- explaining why `09897` uses price zones instead of bydeler
- future wiki pages about rent methodology, comparability, and Oslo price-zone logic

## Source note

Source page:

- https://www.ssb.no/en/priser-og-prisindekser/statistikker/lmu/aar
