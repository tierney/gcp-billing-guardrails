# GCP Billing Guardrails

An automated, serverless kill switch to immediately disable billing on your Google Cloud Project when spend exceeds a configurable hard limit — preventing surprise bills. Includes a full ADK-compatible agent skill team for autonomous setup, testing, and recovery.

## Architecture

```
Google Cloud Budget
      │  (threshold alert)
      ▼
Pub/Sub Topic (budget-alerts)
      │  (triggers)
      ▼
Cloud Function (stop-billing-fn)
      │  (if cost >= budget)
      ▼
Billing Account Unlinked → Project Capped
```

| Component | Description |
|---|---|
| **Cloud Budget** | Monitors monthly spend with 50%, 90%, and 100% threshold rules |
| **Pub/Sub Topic** | `budget-alerts` — receives alerts from the budget |
| **Cloud Function** | `stop-billing-fn` — evaluates cost vs. budget and unlinks billing if exceeded |

## Quick Start

### 1. Configure your credentials
```zsh
cp .env.example .env
# Edit .env and fill in PROJECT_ID, ACCOUNT_ID, BUDGET_AMOUNT
```

### 2. Deploy
```zsh
./setup.sh
```

### 3. Grant Permissions (Required!)
Go to **GCP Console → Billing → Account Management** and add the Compute Engine default service account (e.g. `[PROJECT_NUMBER]-compute@developer.gserviceaccount.com`) as a **Billing Account Administrator**. The function cannot disable billing without this.

---

## Manual Testing

Use the portable `gcloud-agent.sh` wrapper (auto-discovers gcloud on any machine):

### Test a Soft Limit (no billing impact)
```zsh
source .env
./gcloud-agent.sh pubsub topics publish budget-alerts \
  --message="{\"costAmount\": $(echo "$BUDGET_AMOUNT * 0.5" | bc), \"budgetAmount\": $BUDGET_AMOUNT}"
```
Expected log output: `Budget threshold not yet reached. No action taken.`

### Test the Hard Cap (billing will be disabled!)
```zsh
source .env
./gcloud-agent.sh pubsub topics publish budget-alerts \
  --message="{\"costAmount\": $(echo "$BUDGET_AMOUNT * 1.01" | bc), \"budgetAmount\": $BUDGET_AMOUNT}"
```
Expected log output: `Budget exceeded... Disabling billing...`

### Check logs
```zsh
./gcloud-agent.sh functions logs read stop-billing-fn --region=us-central1 --limit=10
```

### Recovery after a hard cap
```zsh
source .env
./gcloud-agent.sh billing projects link $PROJECT_ID --billing-account=$ACCOUNT_ID
```
> ⚠️ **Warning**: If real spend is still above the cap, the kill switch will re-trigger immediately after re-linking. Consider increasing `BUDGET_AMOUNT` first.

---

## Agent Skills

This repo ships with a full team of [Antigravity](https://antigravity.google/docs/skills)-compatible agent skills following the [Agent Skills Standard](https://agentskills.io/).

```
_agents/skills/
├── devops-orchestrator/   ← Runs the full 5-phase setup + test + repair pipeline
├── billing-admin/         ← Verifies budgets, re-links disabled projects
├── qa-testing/            ← Simulates soft/hard limits and validates logs
└── gcloud-executor/       ← Core skill for running gcloud on any machine
```

Each skill uses a **progressive disclosure** architecture:
- `SKILL.md` — lightweight trigger with decision tree (always loaded)
- `references/` — detailed docs loaded on-demand by the agent
- `scripts/` — ready-to-run bash scripts for automation

### Run the Full Agent QA Pipeline
When equipped with the `devops-orchestrator` skill, an agent will autonomously:
1. Parse `.env` to load project config
2. Validate budget → Pub/Sub → Cloud Function wiring
3. Run soft limit test (50%) and verify "No action taken"
4. Run hard limit test (101%) and verify billing disabled
5. Repair billing and confirm project is back online
6. Output a final verification report

### Run Scripts Directly
```zsh
# Verify billing is enabled
./_agents/skills/billing-admin/scripts/verify-billing.sh

# Simulate soft limit (safe, no billing impact)
./_agents/skills/qa-testing/scripts/test-soft-limit.sh

# Simulate hard limit (disables billing!)
./_agents/skills/qa-testing/scripts/test-hard-limit.sh

# Repair billing after hard limit test
./_agents/skills/billing-admin/scripts/repair-billing.sh
```

---

## Repo Structure

```
gcp-billing-guardrails/
├── index.js              ← Cloud Function source (Node.js)
├── package.json          ← @google-cloud/billing dependency
├── setup.sh              ← One-shot deploy script
├── gcloud-agent.sh       ← Portable gcloud wrapper (auto-discovers SDK)
├── .env.example          ← Configuration template
├── .gitignore            ← Excludes .env from git
└── _agents/skills/       ← Agent skill team
```
