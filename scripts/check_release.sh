#!/usr/bin/env bash
set -euo pipefail

echo "=== Python compilation ==="
python3 -m compileall app benchmarks

echo
echo "=== Frontend checks ==="
./scripts/check_frontend.sh

echo
echo "=== Test suite ==="
python3 -m pytest -q

echo
echo "=== Diff hygiene ==="
git diff --check

echo
echo "=== Benchmark guards / dry runs ==="

python3 -m benchmarks.run_phase4 \
    analysis \
    --model gemini-3.5-flash-lite \
    --label lite \
    --dry-run

python3 -m benchmarks.run_phase4 \
    achievement \
    --model gemini-3.1-flash-lite \
    --label lite \
    --dry-run

python3 -m benchmarks.run_phase4 \
    recruiter \
    --model gemini-3.5-flash-lite \
    --label lite \
    --dry-run

python3 -m benchmarks.run_phase4 \
    interview \
    --model gemini-3.5-flash-lite \
    --label lite \
    --dry-run

echo
echo "=== Release gate passed ==="
echo "No live Gemini or grounded-search request was made."
