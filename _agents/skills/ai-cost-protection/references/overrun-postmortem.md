# Overrun Post-Mortem: GCP Billing Propagation Delay

## What Happened

On **April 19, 2026**, a Veo 2.0 video generation pipeline incurred **$180
in charges** despite a $20 Budget Alert and an automated Kill Switch being
active. Support Case **#70390779** was filed.

## Root Cause

GCP's billing reporting pipeline has an inherent **4–12 hour propagation delay**.
The sequence of events was:

```
T+0:00   Pipeline starts. VeoCallGuard NOT yet deployed.
T+0:05   ~85 Veo video generations triggered in rapid succession.
T+0:10   API calls complete. $180 in usage committed on Google's servers.
T+4:00   GCP billing engine processes usage and emits Pub/Sub alert.
T+4:00   Kill Switch Cloud Function fires and disables billing.
T+4:00   $180 already irreversibly charged. Alert fires too late.
```

## Why the Kill Switch Didn't Prevent It

The Kill Switch worked **exactly as designed**. The problem is architectural:

1. The Kill Switch is **reactive** — it responds to GCP alerts.
2. GCP alerts are **delayed** — they reflect usage from hours ago.
3. Modern AI APIs are **fast** — they can burn through a $20 budget in seconds.

## Resolution

- Google Cloud Support issued a **partial billing credit** after the
  automated guardrails were demonstrated (Case #70390779).
- `VeoCallGuard` was implemented as a **proactive, in-process hard cap**
  to prevent any future overrun, regardless of billing lag.

## Prevention Checklist

- [ ] `VeoCallGuard` is instantiated before any Veo/Gemini API call loop
- [ ] `max_calls` is set to a conservative value (≤ 10 for testing)
- [ ] `max_cost_usd` is explicitly calculated from session budget
- [ ] GCP API Quota cap is set: `Vertex AI → Quotas → Generate Video → Requests/day`
- [ ] GCP Budget Alert is set at 50%, 90%, and 100% thresholds
- [ ] Kill Switch Cloud Function is deployed and tested
- [ ] `guard.summary()` is logged in every session HALT event
