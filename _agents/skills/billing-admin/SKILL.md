---
name: billing-admin
description: Manages GCP billing configurations, verifies budgets, and re-links disabled billing accounts. Use when you need to recover a project's billing state or audit budget Pub/Sub rules.
---

# Billing Administrator Skill

You are responsible for managing the Google Cloud billing lifecycle and ensuring the project's financial guardrails are functioning and correctly attached.

## Core Capabilities

### 1. Verify Budget Configuration
To check if the project has the correct budget and that it is linked to the `budget-alerts` Pub/Sub topic, run:
```zsh
gcloud billing budgets list --billing-account=$ACCOUNT_ID
```
Ensure that `notificationsRule.pubsubTopic` exists and points to the correct topic.

### 2. Verify Project Billing Status
To check if the kill switch has tripped or if the project is currently active, run:
```zsh
gcloud billing projects describe $PROJECT_ID
```
If `billingEnabled` is `true`, the project is online. If `false`, the kill switch has tripped.

### 3. Repair / Re-link Billing Account
If the kill switch has tripped and the human requests the project be brought back online, you must re-link the billing account:
```zsh
gcloud billing projects link $PROJECT_ID --billing-account=$ACCOUNT_ID
```
*Warning: If the project's current spend is still above the budget hard cap, re-linking will cause a loop where it gets immediately disabled again. Advise the human to increase the budget limit before re-linking.*
