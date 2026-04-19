# Orchestrator Pipeline Phases — Detailed Instructions

## Phase 1: Context Gathering
Parse the `.env` file to determine the project's configuration:
```bash
source .env
echo "Project: $PROJECT_ID | Account: $ACCOUNT_ID | Budget: $BUDGET_AMOUNT"
```

## Phase 2: Configuration Validation
Dispatch `billing-admin` to run the full verification in `billing-admin/references/verify-setup.md`.
All three checks must pass before proceeding.

## Phase 3: Soft Limit QA
Dispatch `qa-testing` to run `scripts/test-soft-limit.sh`.
- Calculate 50% of `$BUDGET_AMOUNT` for the `costAmount` value.
- Parse logs and confirm the output matches the expected "No action taken" pattern in `qa-testing/references/expected-log-output.md`.

## Phase 4: Hard Limit QA
Get explicit user confirmation before proceeding — this WILL disable billing.
Dispatch `qa-testing` to run `scripts/test-hard-limit.sh`.
- Calculate 101% of `$BUDGET_AMOUNT` for the `costAmount` value.
- Wait 15 seconds, then confirm `billingEnabled: false`.

## Phase 5: Repair & Final Verification
Immediately dispatch `billing-admin` to run `scripts/repair-billing.sh`.
Confirm `billingEnabled: true` before generating the final report.

## Final Report Template
```
✅ GCP Billing Guardrails — Verification Report
================================================
Project: [PROJECT_ID]
Budget Cap: $[BUDGET_AMOUNT]
Cloud Function: stop-billing-fn [ACTIVE]
Budget: [BUDGET_DISPLAY_NAME] → budget-alerts topic ✅
Soft Limit Test (50%): PASSED — No action taken ✅
Hard Limit Test (101%): PASSED — Billing disabled ✅
Repair: PASSED — Billing re-enabled ✅
================================================
Kill switch is verified and operational.
```
