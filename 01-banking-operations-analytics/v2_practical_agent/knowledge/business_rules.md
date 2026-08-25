# Banking Operations Business Rules

## Purpose

This document contains approved business and data-handling rules used by the Banking Operations Agent.

The agent must use these rules when interpreting operational results or explaining data-quality behavior.

If a required business rule or threshold is not defined in an approved source, the agent must not invent one.

## Approved Sources

- `docs/8_staging_layer_notes.md`
- Approved Banking Operations documentation added to this list as the knowledge base evolves

## Failed Transaction Fee Rule

### Rule

A failed transaction must not carry a charged transaction fee in the trusted reporting layer.

### Data Handling

If a raw failed transaction contains a non-zero fee, the record is captured as a data-quality exception.

The trusted staging value is corrected to a zero fee while the original raw value remains available for audit.

### Agent Behaviour

When answering KPI or operational-analysis questions, the agent should use the trusted warehouse data.

If the user asks about data-quality exceptions or why a fee was corrected, the agent may explain the failed-transaction fee rule and reference the data-quality exception information.

### Source

`docs/8_staging_layer_notes.md`

## Duplicate Transaction Rule

### Rule

Each transaction_id must uniquely identify one transaction in the trusted reporting layer.

### Data Handling

If duplicate transaction_id values are detected in the raw data, the duplicate records are captured as data-quality exceptions.

The original source records remain available in the raw layer for audit. Only one trusted row per transaction_id is retained in the cleaned staging and warehouse layers.

### Agent Behaviour

When answering KPI or operational-analysis questions, the agent should use the trusted warehouse data, where transaction_id is unique.

If the user asks about duplicate records or data-quality exceptions, the agent may explain the duplicate transaction rule and reference the data-quality exception information.

### Source

`docs/8_staging_layer_notes.md`

## Missing Channel Rule

### Rule

A missing channel_id must be treated as a data-quality exception and must not be replaced with an invented or assumed channel value.

### Data Handling

If channel_id is missing, the record is captured as a data-quality exception.

The missing value is preserved rather than imputed so that downstream processes can distinguish unknown source data from a known channel.

### Agent Behaviour

When answering KPI or operational-analysis questions, the agent should use the trusted warehouse data.

The agent must not infer or invent a channel for records where channel information is unavailable.

If the user asks about missing-channel exceptions, the agent may explain the rule and reference the data-quality exception information.

### Source

`docs/8_staging_layer_notes.md`

## High-Value Transaction Rule

### Rule

A transaction above the defined high-value threshold must be flagged for review, but it must not automatically be treated as invalid or erroneous.

### Data Handling

If a transaction amount exceeds the defined high-value threshold, the record is captured as a `HIGH_VALUE_TRANSACTION` data-quality exception.

The transaction is retained in the trusted data because a high transaction amount may represent a legitimate business event rather than a data error.

### Agent Behaviour

When answering KPI or operational-analysis questions, the agent should not exclude or alter high-value transactions only because they are unusually large.

If the user asks about high-value transactions or data-quality exceptions, the agent may explain that these records are flagged for review and should be investigated before any decision is made to exclude or correct them.

### Source

`docs/8_staging_layer_notes.md`

