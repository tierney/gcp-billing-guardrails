#!/usr/bin/env bash
# scripts/pre-commit.sh — GCP Billing Guardrails pre-commit hook
# Install with: make hooks

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PYTEST_CMD="$REPO_ROOT/venv/bin/python -m pytest"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  🧪  Running test suite before commit...     ║"
echo "╚══════════════════════════════════════════════╝"

set +e
$PYTEST_CMD "$REPO_ROOT/tests/" -v --tb=short 2>&1
PYTEST_EXIT=$?
set -e

if [ $PYTEST_EXIT -eq 0 ]; then
  echo ""; echo "✅  All tests passed. Proceeding with commit."; echo ""
  exit 0
fi

echo ""; echo "❌  Tests FAILED (exit code: $PYTEST_EXIT)"

if [ "${ALLOW_BROKEN_TESTS:-0}" = "1" ]; then
  COMMIT_MSG_FILE="$REPO_ROOT/.git/COMMIT_EDITMSG"
  if [ -f "$COMMIT_MSG_FILE" ]; then
    echo "[⚠️ BROKEN TESTS] $(cat $COMMIT_MSG_FILE)" > "$COMMIT_MSG_FILE"
    echo "⚠️  Committing with [⚠️ BROKEN TESTS] prefix. Fix before merging!"; echo ""
    exit 0
  fi
fi

echo "🛑  Commit BLOCKED. Fix tests or set ALLOW_BROKEN_TESTS=1 to force."; echo ""
exit 1
