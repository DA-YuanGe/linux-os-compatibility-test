#!/usr/bin/env bash

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$PROJECT_ROOT"

echo "========================================"
echo " Linux OS Compatibility Test Tool"
echo "========================================"
echo

PYTHONPATH="$PROJECT_ROOT/src" python3 src/orchestrator/runner.py

echo
echo "Test completed."
echo "Report: $PROJECT_ROOT/reports/result.json"
