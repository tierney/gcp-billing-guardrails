"""
gcp-billing-guardrails: Client-side cost protection utilities.

Importable guardrails for use in any project that calls expensive GCP APIs.
"""
from .veo_call_guard import VeoCallGuard

__all__ = ["VeoCallGuard"]
