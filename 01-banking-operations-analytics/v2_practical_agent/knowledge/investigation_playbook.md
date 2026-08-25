# Banking Operations Investigation Playbook

## Purpose

This document contains approved investigation guidance for the Banking Operations Agent.
It helps the agent interpret evidence without inventing unsupported root causes or thresholds.

## General Investigation Rule

Start with the KPI definition and the exact reporting period. Use trusted warehouse data for the measured result. Compare with an adjacent period or relevant segment when the question asks whether performance improved, deteriorated, or appears unusual.

Do not convert an observed increase or decrease into a root-cause statement unless the evidence supports that cause.

## Transaction Failure Investigation

When transaction failure rate is being investigated:

1. Confirm the selected period and channel.
2. Retrieve failed transactions and total transactions from the trusted warehouse.
3. Calculate failure rate using the approved KPI definition.
4. If the question asks whether the result is concerning and no approved threshold is defined, compare with a prior period and describe the change rather than inventing a threshold.
5. Channel-level differences can identify where further investigation should focus, but they do not by themselves prove a technical root cause.

## Complaint Investigation

When complaint performance is being investigated:

- use complaint volume and resolution performance together;
- normalize complaint volume by transaction activity when comparing channels with different transaction volumes;
- avoid inferring employee performance from complaint KPIs alone.

## SLA Investigation

When SLA breach rate is being investigated:

- confirm the ticket period and relevant team or priority;
- compare breached tickets with total tickets;
- treat a high breach rate as an operational signal requiring investigation, not proof of a specific staffing or system issue.

## Campaign Investigation

When campaign conversion is being investigated:

- distinguish engagement from conversion;
- use campaign offers sent as the approved conversion-rate denominator;
- stronger engagement with weaker conversion should be described as a funnel issue requiring further analysis, not automatically as a product problem.

## Insufficient Evidence

If the available data shows what changed but does not support why it changed, the agent should state the observed evidence and say that the root cause is not established by the current evidence.

If an approved threshold or business rule is missing, the agent must not invent one.
