---
name: gcloud-executor
description: Runs gcloud CLI commands on the user's machine to inspect and manage Google Cloud resources. Use when you need to check billing status, read Cloud Function logs, publish Pub/Sub messages, or manage GCP configurations.
---

# GCloud Executor Skill

## Quick Reference

Use the portable wrapper — it auto-discovers `gcloud` on any machine:
```bash
./gcloud-agent.sh [command]
```

Always `source .env` first to populate `$PROJECT_ID`, `$ACCOUNT_ID`, `$BUDGET_AMOUNT`.

## Decision Tree

- **Check billing is enabled?** → `./gcloud-agent.sh billing projects describe $PROJECT_ID`
- **List budgets?** → `./gcloud-agent.sh billing budgets list --billing-account=$ACCOUNT_ID`
- **Read function logs?** → `./gcloud-agent.sh functions logs read stop-billing-fn --region=us-central1 --limit=10`
- **Publish test message?** → See `references/pubsub-testing.md`
- **Re-link billing?** → See `scripts/repair-billing.sh` (requires user approval)
- **Need install help?** → See `references/installation.md`

## Safety Rules
- **Read-only commands**: run freely without asking.
- **Write commands** (re-link billing, deploy, publish): always confirm with the user first.
