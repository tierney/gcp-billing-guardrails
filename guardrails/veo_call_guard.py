"""
guardrails/veo_call_guard.py
-----------------------------
Client-side hard cap on Veo (and similar) video generation API calls.

This guard fires BEFORE any API request is made, making it immune to the
4–12 hour propagation delay in GCP's billing reporting system — the root
cause of most Vertex AI cost overruns.

Usage:
    from guardrails import VeoCallGuard

    guard = VeoCallGuard(max_calls=5, max_cost_usd=10.00)

    async def generate():
        await guard.check_and_increment()   # raises if limit exceeded
        # ... make your API call here ...

Design rationale:
    GCP Budget Alerts are reactive — they notify AFTER usage is reported.
    This guard is proactive — it raises BEFORE the call goes out.
    Both layers are needed: this guard for speed, GCP alerts for backup.
"""

import asyncio
from typing import Optional


# ---------------------------------------------------------------------------
# Pricing constants (update if Google changes pricing)
# ---------------------------------------------------------------------------
# Veo 2.0 approximate pricing as of April 2026
VEO2_COST_PER_SECOND_USD = 0.35

# Veo 3.1 Lite approximate pricing as of April 2026
VEO31_LITE_COST_PER_SECOND_USD = 0.25


class VeoCallGuard:
    """Thread-safe, async-safe hard cap on AI video generation API calls.

    Raises RuntimeError *before* the API call is made if either:
    - The call count would exceed ``max_calls``, or
    - The estimated cumulative cost would exceed ``max_cost_usd``.

    This is intentionally separate from GCP Budget Alerts, which can have
    a 4–12 hour propagation delay and therefore cannot be trusted as a
    hard stop for high-velocity API usage (e.g. Veo video generation).

    Args:
        max_calls:         Maximum number of API calls allowed per session.
        max_cost_usd:      Maximum estimated spend allowed per session (USD).
        cost_per_call_usd: Estimated cost per API call. Defaults to Veo 2.0
                           pricing at 6 seconds per video (~$2.10/call).
        model_label:       Optional label for log messages (e.g. "veo-2.0").

    Example::

        guard = VeoCallGuard(max_calls=5, max_cost_usd=10.00)

        async def safe_generate(prompt):
            await guard.check_and_increment()
            return await veo_client.generate(prompt)
    """

    def __init__(
        self,
        max_calls: int = 5,
        max_cost_usd: float = 10.00,
        cost_per_call_usd: float = VEO2_COST_PER_SECOND_USD * 6,  # 6s default
        model_label: Optional[str] = None,
    ):
        self._max_calls      = max_calls
        self._max_cost_usd   = max_cost_usd
        self._cost_per_call  = cost_per_call_usd
        self._model_label    = model_label or "veo"
        self._call_count     = 0
        self._estimated_cost = 0.0
        self._lock           = asyncio.Lock()

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------

    @property
    def call_count(self) -> int:
        """Number of approved API calls so far this session."""
        return self._call_count

    @property
    def estimated_cost_usd(self) -> float:
        """Estimated cumulative spend so far this session (USD)."""
        return self._estimated_cost

    @property
    def calls_remaining(self) -> int:
        """How many more calls are allowed before the hard cap."""
        return max(0, self._max_calls - self._call_count)

    @property
    def budget_remaining_usd(self) -> float:
        """How much estimated budget remains before the cost cap."""
        return max(0.0, self._max_cost_usd - self._estimated_cost)

    # ------------------------------------------------------------------
    # Core guard method
    # ------------------------------------------------------------------

    async def check_and_increment(self) -> None:
        """Call this BEFORE every Veo API request.

        Atomically checks both limits and increments the counter if safe.

        Raises:
            RuntimeError: If the next call would exceed either the call
                          count limit or the estimated cost cap.
        """
        async with self._lock:
            projected_calls = self._call_count + 1
            projected_cost  = self._estimated_cost + self._cost_per_call

            if projected_calls > self._max_calls:
                raise RuntimeError(
                    f"🛑 [{self._model_label}] VeoCallGuard: Hard call limit reached. "
                    f"({self._call_count}/{self._max_calls} calls used, "
                    f"~${self._estimated_cost:.2f} estimated spend). "
                    f"Increase max_calls or start a new session."
                )

            if projected_cost > self._max_cost_usd:
                raise RuntimeError(
                    f"🛑 [{self._model_label}] VeoCallGuard: Estimated cost cap reached. "
                    f"(~${projected_cost:.2f} would exceed ${self._max_cost_usd:.2f} limit). "
                    f"Increase max_cost_usd or start a new session."
                )

            self._call_count     = projected_calls
            self._estimated_cost = projected_cost

            print(
                f"[VeoCallGuard:{self._model_label}] ✅ Call {self._call_count}/{self._max_calls} "
                f"approved. Est. session cost: ~${self._estimated_cost:.2f} "
                f"(${self._budget_remaining:.2f} remaining)"
            )

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    @property
    def _budget_remaining(self) -> float:
        return max(0.0, self._max_cost_usd - self._estimated_cost)

    def summary(self) -> dict:
        """Return a JSON-serialisable summary for logging and auditing."""
        return {
            "model":            self._model_label,
            "calls_used":       self._call_count,
            "calls_remaining":  self.calls_remaining,
            "estimated_cost":   round(self._estimated_cost, 2),
            "budget_remaining": round(self.budget_remaining_usd, 2),
            "max_calls":        self._max_calls,
            "max_cost_usd":     self._max_cost_usd,
        }

    def __repr__(self) -> str:
        return (
            f"VeoCallGuard(model={self._model_label!r}, "
            f"calls={self._call_count}/{self._max_calls}, "
            f"cost=${self._estimated_cost:.2f}/${self._max_cost_usd:.2f})"
        )
