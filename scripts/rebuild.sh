#!/usr/bin/env bash
# Rebuild the snapshot data, the consolidated dashboard, and run the release gates.
# Usage: bash scripts/rebuild.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== 1/5 re-pricing the 22 October snapshot =="
python3 scripts/v3_build.py >/dev/null

echo "== 2/5 rendering the consolidated dashboard =="
python3 scripts/final_site.py >/dev/null

echo "== 3/5 dashboard gate =="
python3 scripts/final_validate.py | tail -3

echo "== 4/5 legacy primary-data + whole-tree link gate =="
python3 scripts/validate.py | tail -3

echo "== 5/5 snapshot gate =="
python3 scripts/v3_validate.py

echo "All gates passed."
