---
name: devops-orchestrator
description: Manages the end-to-end setup, verification, and repair pipeline for GCP Billing Guardrails by coordinating billing-admin and qa-testing agents. Use when you need to run a full audit or end-to-end test of the kill switch.
---

# DevOps Orchestrator Skill

## Quick Reference

The Orchestrator coordinates the full guardrails pipeline. Dispatch sub-agents in order.

## Workflow (5 Phases)

1. **Context** — `source .env` to load `PROJECT_ID`, `ACCOUNT_ID`, `BUDGET_AMOUNT`.
2. **Validate Config** — Dispatch `billing-admin` to run `references/verify-setup.md`.
3. **Soft Limit QA** — Dispatch `qa-testing` to run `scripts/test-soft-limit.sh` and confirm logs show "No action taken."
4. **Hard Limit QA** — Dispatch `qa-testing` to run `scripts/test-hard-limit.sh` and confirm `billingEnabled: false`.
5. **Repair** — Dispatch `billing-admin` to run `scripts/repair-billing.sh`. Confirm `billingEnabled: true`.

Output a final verification report when all 5 phases pass.

For detailed per-phase instructions, see `references/pipeline-phases.md`.
