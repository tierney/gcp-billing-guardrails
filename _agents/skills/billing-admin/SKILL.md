---
name: billing-admin
description: Manages GCP billing configurations, verifies budgets, and re-links disabled billing accounts. Use when you need to recover a project's billing state or audit budget Pub/Sub notification rules.
---

# Billing Administrator Skill

## Quick Reference

Always `source .env` first to populate `$PROJECT_ID`, `$ACCOUNT_ID`, `$BUDGET_AMOUNT`.

## Decision Tree

- **Is billing currently enabled?** → `./gcloud-agent.sh billing projects describe $PROJECT_ID`
- **Is the budget linked to the correct Pub/Sub topic?** → See `references/verify-setup.md`
- **Re-link a disabled project?** → Run `scripts/repair-billing.sh` (requires user approval)
- **Update budget amount?** → See `references/manage-budget.md`

## Safety Rules
- Always verify billing status before and after any repair operation.
- Warn the user if re-linking while spend is still above the budget cap — it will immediately re-trigger the kill switch.
