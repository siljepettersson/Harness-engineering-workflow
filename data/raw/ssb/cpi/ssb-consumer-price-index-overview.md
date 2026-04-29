---
source_type: raw_ssb_document
topic: cpi
title: Consumer price index - overview
statistics_name: Consumer price index
source_url: https://www.ssb.no/en/priser-og-prisindekser/konsumpriser/statistikk/konsumprisindeksen
retrieval_date: 2026-04-29
source_updated_date: 2026-04-10
language: en
geographic_coverage: National level only
license: CC BY 4.0
---

# Consumer price index - overview

This curated source is based on Statistics Norway's official Consumer price index page.

It is the first CPI-side raw source for the project and is meant to connect the Oslo-rent path to the broader CPI domain without immediately expanding into full CPI coverage.

## What the CPI measures

Statistics Norway says the CPI describes the development in consumer prices for goods and services purchased by private households in Norway.

The page also says the CPI is a common measure of inflation.

This is a different role from the rental market survey. The rental survey measures rent levels in segments of the rental market, while the CPI measures price development across household consumption.

## Scope and geographic level

The CPI page says the regional level is `National level only`.

That matters for the project architecture:

- CPI should not be treated as an Oslo bydel statistic
- CPI should not be treated as an Oslo-specific rent statistic
- Oslo-rent sources and CPI sources need to stay conceptually connected, but not collapsed into one another

## HICP relationship

The page says Statistics Norway reports the Harmonized Index of Consumer Prices (HICP) for Norway to Eurostat every month.

It also says the traditional CPI is the foundation of the HICP.

This gives the project a later path for CPI vs. HICP explanation questions, but it is separate from the current Oslo-rent milestone.

## Data sources and production notes

According to the CPI page, expenditure shares are based on National Accounts data, while prices are collected each month from a representative sample of retail and service outlets.

The page also says the CPI and HICP are based on several sources, including:

- electronic questionnaires
- electronic data from firms and dwellings
- turnover information from Statistics Norway's Business Register
- commodity trade statistics
- budget shares from the household budget survey

This is useful for later grounded explanations of how CPI differs from a single-source price statistic.

## Why this matters for the rent-to-CPI bridge

The CPI page establishes what CPI is and what level it is published at.

The rental market survey pages establish how rent survey data is used within Statistics Norway, including in the CPI.

Together, those sources support a careful bridge explanation:

- CPI is the broader inflation indicator
- rental statistics are a separate rent-level source
- rent survey data can feed CPI-related work without being the same thing as CPI itself

## Suggested use in this project

This file is suitable for:

- questions such as "What does CPI measure?"
- questions such as "Is CPI published for Oslo or only at national level?"
- bridge questions such as "How is the rental market survey related to CPI?"
- future comparison questions involving CPI and HICP

## Source note

Source page:

- https://www.ssb.no/en/priser-og-prisindekser/konsumpriser/statistikk/konsumprisindeksen
