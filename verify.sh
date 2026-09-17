#!/usr/bin/env bash
set -euo pipefail
echo "=== hn-webauthn-passkey-state-boundary-lab verify ==="
python3 -m py_compile evaluator.py
python3 evaluator.py
python3 -m unittest tests/test_passkey_boundary.py -v
echo "--- RESULTS.md ---"
cat RESULTS.md
echo "--- results.json summary ---"
python3 -c "import json; d=json.load(open('results.json')); print(f\"{d['total']} cases, {d['single_device']} single, {d['multi_device']} multi, {d['invalid_combinations']} invalid, hw_proven_any={d['hardware_binding_proven_any']}\")"
echo "verify OK"
