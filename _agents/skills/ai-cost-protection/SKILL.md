---
name: ai-cost-protection
description: >
  Protects against runaway AI API costs (Vertex AI, Veo, Gemini) by enforcing
  client-side hard caps BEFORE any API call is made. Use when designing,
  reviewing, or debugging any pipeline that calls expensive generative AI APIs.
  Complements the GCP-level Billing Kill Switch with an in-process guardrail
  that is immune to billing propagation delays.
---

# AI Cost Protection Skill

## The Core Problem: Billing Propagation Delay

> **GCP Budget Alerts are NOT real-time.** They have a 4–12 hour lag.
>
> If a pipeline generates 10 Veo videos in 5 minutes at ~$2.10/call, the
> billing system may not fire the $20 budget alert until $180 has already
> been spent. This is a known, documented limitation — not a bug.

**The solution is two independent layers:**

| Layer | Where | Fires | Stops charges |
|---|---|---|---|
| **VeoCallGuard** (this skill) | In Python code | Before API call | Before any money is spent |
| **GCP Billing Kill Switch** | Cloud Function | After alert fires (4–12h lag) | After significant overrun |

Both are required. Neither alone is sufficient.

---

## Quick Reference

Import and use the guard from the `guardrails` package:

```python
from guardrails import VeoCallGuard

# Veo 2.0, 6s videos: ~$2.10/call. Default: 5 calls max, $10 cap.
guard = VeoCallGuard(
    max_calls=5,
    max_cost_usd=10.00,
    cost_per_call_usd=2.10,
    model_label="veo-2.0",
)

async def generate_video(prompt: str):
    await guard.check_and_increment()  # 🛡️ raises before API call if limit hit
    # ... your API call here ...
```

---

## Decision Tree

- **Starting a new AI video pipeline?**
  → Always instantiate a `VeoCallGuard` before any API call loop.
  → Set `max_calls` conservatively (5 is a good default for testing).

- **User reports unexpected cost overrun despite a budget alert?**
  → Root cause is almost always billing propagation delay.
  → Add `VeoCallGuard` to the pipeline. See `references/overrun-postmortem.md`.

- **Need to raise the limit for a production run?**
  → Increase `max_calls` and `max_cost_usd` explicitly in code with a comment.
  → Also set a GCP API Quota cap: `APIs & Services → Vertex AI → Quotas → Generate Video`.

- **Want to test that the guard works?**
  → Run `make test` — the test suite is fully offline, no API key needed.

- **Adding a new model (Imagen, Chirp, etc.)?**
  → Add its cost constant to `guardrails/veo_call_guard.py` (see `VEO2_COST_PER_SECOND_USD`).
  → Write a test case in `tests/test_veo_call_guard.py`.
  → Update `references/model-pricing.md` with the new rate.

---

## Safety Rules

1. **Never call a generative AI video or image API without a VeoCallGuard in scope.**
2. **Never set `max_calls` higher than your session budget can absorb.**
   - Default safe values: `max_calls=5`, `max_cost_usd=10.00`
   - For production: calculate explicitly from your budget, not by feel.
3. **Log `guard.summary()` in every HALT/shutdown event** so every session is auditable.
4. **Treat the guard as a hard stop, not a suggestion.** Never catch its `RuntimeError` without notifying the user.
5. **The GCP Kill Switch is your backstop, not your primary defense.** Always use both.

---

## Pricing Reference

| Model | Cost/Second | Default 6s Video Cost |
|---|---|---|
| Veo 2.0 | ~$0.35/s | ~$2.10/call |
| Veo 3.1 Lite | ~$0.25/s | ~$1.50/call |

> Pricing is approximate. Always verify at [cloud.google.com/vertex-ai/pricing](https://cloud.google.com/vertex-ai/pricing).
