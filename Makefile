# =============================================================================
# GCP Billing Guardrails — Makefile
# =============================================================================
PYTHON    := python3
VENV_DIR  := venv
PIP       := $(VENV_DIR)/bin/pip
PYTEST    := $(VENV_DIR)/bin/python -m pytest
TESTS_DIR := tests

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo ""
	@echo "  🛡️   GCP Billing Guardrails — Available Commands"
	@echo "  ─────────────────────────────────────────────────"
	@echo "  make install    Create venv + install dev deps"
	@echo "  make test       Run the full offline test suite"
	@echo "  make check      Lint + test (full pre-flight)"
	@echo "  make hooks      Install git pre-commit test gate"
	@echo "  make clean      Remove venv + cache"
	@echo ""

.PHONY: install
install:
	@echo "🔧  Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip -q
	$(PIP) install -r requirements-dev.txt -q
	@echo "✅  Done. Run 'make test' to verify."

.PHONY: test
test:
	@echo ""
	@echo "🧪  Running test suite..."
	@echo "───────────────────────────"
	@$(PYTEST) $(TESTS_DIR)/ -v --tb=short; \
	STATUS=$$?; \
	if [ $$STATUS -eq 0 ]; then echo ""; echo "✅  All tests passed."; \
	else echo ""; echo "❌  Tests FAILED."; fi; \
	exit $$STATUS

.PHONY: lint
lint:
	@echo "🔍  Running lint checks..."
	@$(VENV_DIR)/bin/python -m py_compile guardrails/veo_call_guard.py \
		&& echo "  ✅  guardrails/veo_call_guard.py — syntax OK"
	@$(VENV_DIR)/bin/python -m py_compile tests/test_veo_call_guard.py \
		&& echo "  ✅  tests/test_veo_call_guard.py — syntax OK"

.PHONY: check
check: lint test
	@echo ""
	@echo "🚀  Pre-flight complete."

.PHONY: hooks
hooks:
	@echo "🔗  Installing git pre-commit hook..."
	@cp scripts/pre-commit.sh .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "✅  pre-commit hook active."

.PHONY: clean
clean:
	@rm -rf $(VENV_DIR) __pycache__ guardrails/__pycache__ tests/__pycache__ .pytest_cache
	@echo "✅  Clean."
