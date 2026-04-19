---
name: qa-testing
description: Tests the GCP billing kill switch by publishing Pub/Sub messages and reading Cloud Function logs. Use when you need to verify soft limits are correctly ignored and hard limits trigger a billing disconnection.
---

# QA Tester Skill

## Quick Reference

Always `source .env` first to populate `$PROJECT_ID`, `$ACCOUNT_ID`, `$BUDGET_AMOUNT`.

## Decision Tree

- **Test soft limits (50%, 90%)?** → Run `scripts/test-soft-limit.sh` — no billing impact.
- **Test hard limit (100%+)?** → Run `scripts/test-hard-limit.sh` — **billing will be disabled**, notify billing-admin to repair afterward.
- **Check function ran correctly?** → `./gcloud-agent.sh functions logs read stop-billing-fn --region=us-central1 --limit=10`
- **Confirm billing is disconnected?** → `./gcloud-agent.sh billing projects describe $PROJECT_ID`
- **What do the log messages mean?** → See `references/expected-log-output.md`

## Safety Rules
- Always notify the `billing-admin` agent or the user after running a hard limit test so the project can be repaired.
- Never run the hard limit test against a production project without explicit approval.
