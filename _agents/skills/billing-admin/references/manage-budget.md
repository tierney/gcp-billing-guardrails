# Managing the Budget

## View Current Budget
```bash
source .env
./gcloud-agent.sh billing budgets list --billing-account=$ACCOUNT_ID
```
Note the budget ID (the UUID in the `name` field, e.g. `0b917b2f-910d-47d5-...`).

## Update Budget Amount
Use this to raise the cap after the kill switch has tripped, to prevent a re-link loop:
```bash
./gcloud-agent.sh billing budgets update [BUDGET_ID] \
  --billing-account=$ACCOUNT_ID \
  --budget-amount=[NEW_AMOUNT].00
```

## Delete and Recreate Budget
If the budget needs to be fully reset:
```bash
./gcloud-agent.sh billing budgets delete [BUDGET_ID] --billing-account=$ACCOUNT_ID
./setup.sh  # Re-run setup to recreate the budget
```
