"""
tests/test_veo_call_guard.py
-----------------------------
Unit tests for guardrails.VeoCallGuard.

All tests are fully offline — no API credentials or network required.
Run with:  make test
"""

import asyncio
import json
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from guardrails import VeoCallGuard


def run(coro):
    """Run an async coroutine — compatible with Python 3.10+."""
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# Call-count limit
# ---------------------------------------------------------------------------

class TestCallCountLimit:
    def test_single_call_succeeds(self):
        g = VeoCallGuard(max_calls=3, max_cost_usd=999)
        run(g.check_and_increment())
        assert g.call_count == 1

    def test_calls_up_to_limit_all_succeed(self):
        g = VeoCallGuard(max_calls=3, max_cost_usd=999)
        for _ in range(3):
            run(g.check_and_increment())
        assert g.call_count == 3

    def test_exceeding_call_limit_raises(self):
        g = VeoCallGuard(max_calls=2, max_cost_usd=999)
        run(g.check_and_increment())
        run(g.check_and_increment())
        with pytest.raises(RuntimeError, match="Hard call limit reached"):
            run(g.check_and_increment())

    def test_counter_does_not_increment_on_rejection(self):
        g = VeoCallGuard(max_calls=1, max_cost_usd=999)
        run(g.check_and_increment())
        with pytest.raises(RuntimeError):
            run(g.check_and_increment())
        assert g.call_count == 1  # Must remain at 1, not 2

    def test_calls_remaining_tracks_correctly(self):
        g = VeoCallGuard(max_calls=5, max_cost_usd=999)
        assert g.calls_remaining == 5
        run(g.check_and_increment())
        assert g.calls_remaining == 4
        run(g.check_and_increment())
        assert g.calls_remaining == 3


# ---------------------------------------------------------------------------
# Cost limit
# ---------------------------------------------------------------------------

class TestCostLimit:
    def test_cost_guard_blocks_before_api_call(self):
        """Cost cap fires BEFORE the call, not after."""
        g = VeoCallGuard(max_calls=999, max_cost_usd=4.99, cost_per_call_usd=5.00)
        with pytest.raises(RuntimeError, match="Estimated cost cap reached"):
            run(g.check_and_increment())

    def test_cost_accumulates_correctly(self):
        g = VeoCallGuard(max_calls=10, max_cost_usd=100, cost_per_call_usd=2.10)
        for _ in range(4):
            run(g.check_and_increment())
        assert round(g.estimated_cost_usd, 2) == 8.40

    def test_cost_cap_fires_before_fifth_call(self):
        # 4 × $2.10 = $8.40 ✓  |  5 × $2.10 = $10.50 > $10.00 ✗
        g = VeoCallGuard(max_calls=10, max_cost_usd=10.00, cost_per_call_usd=2.10)
        for _ in range(4):
            run(g.check_and_increment())
        with pytest.raises(RuntimeError, match="Estimated cost cap reached"):
            run(g.check_and_increment())

    def test_budget_remaining_tracks_correctly(self):
        g = VeoCallGuard(max_calls=10, max_cost_usd=10.00, cost_per_call_usd=2.00)
        run(g.check_and_increment())
        assert g.budget_remaining_usd == pytest.approx(8.00, abs=0.01)


# ---------------------------------------------------------------------------
# Model label
# ---------------------------------------------------------------------------

class TestModelLabel:
    def test_default_label_in_error_message(self):
        g = VeoCallGuard(max_calls=0, max_cost_usd=999)
        with pytest.raises(RuntimeError, match=r"\[veo\]"):
            run(g.check_and_increment())

    def test_custom_label_in_error_message(self):
        g = VeoCallGuard(max_calls=0, max_cost_usd=999, model_label="veo-3.1-lite")
        with pytest.raises(RuntimeError, match=r"\[veo-3\.1-lite\]"):
            run(g.check_and_increment())


# ---------------------------------------------------------------------------
# Summary / reporting
# ---------------------------------------------------------------------------

class TestSummary:
    def test_initial_state(self):
        g = VeoCallGuard(max_calls=5, max_cost_usd=10.00, cost_per_call_usd=2.10)
        s = g.summary()
        assert s["calls_used"] == 0
        assert s["calls_remaining"] == 5
        assert s["estimated_cost"] == 0.0
        assert s["budget_remaining"] == 10.00
        assert s["max_calls"] == 5
        assert s["max_cost_usd"] == 10.00

    def test_summary_after_calls(self):
        g = VeoCallGuard(max_calls=5, max_cost_usd=10.00, cost_per_call_usd=2.10)
        run(g.check_and_increment())
        run(g.check_and_increment())
        s = g.summary()
        assert s["calls_used"] == 2
        assert s["calls_remaining"] == 3
        assert s["estimated_cost"] == pytest.approx(4.20, abs=0.01)
        assert s["budget_remaining"] == pytest.approx(5.80, abs=0.01)

    def test_summary_is_json_serialisable(self):
        g = VeoCallGuard(max_calls=5, max_cost_usd=10.00, cost_per_call_usd=2.10)
        run(g.check_and_increment())
        json.dumps(g.summary())  # Must not raise

    def test_repr_contains_key_info(self):
        g = VeoCallGuard(max_calls=5, max_cost_usd=10.00, cost_per_call_usd=2.10,
                         model_label="veo-2.0")
        run(g.check_and_increment())
        r = repr(g)
        assert "veo-2.0" in r
        assert "1/5" in r


# ---------------------------------------------------------------------------
# Concurrency
# ---------------------------------------------------------------------------

class TestConcurrency:
    def test_concurrent_calls_respect_limit(self):
        """Multiple coroutines racing to call check_and_increment."""
        g = VeoCallGuard(max_calls=3, max_cost_usd=999, cost_per_call_usd=0.01)
        results = {"ok": 0, "blocked": 0}

        async def attempt():
            try:
                await g.check_and_increment()
                results["ok"] += 1
            except RuntimeError:
                results["blocked"] += 1

        async def run_all():
            await asyncio.gather(*[attempt() for _ in range(8)])

        asyncio.run(run_all())

        assert results["ok"] == 3
        assert results["blocked"] == 5
        assert g.call_count == 3
