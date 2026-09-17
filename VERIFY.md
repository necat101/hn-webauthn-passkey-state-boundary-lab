# VERIFY.md — Fresh-clone verification transcript

This file records the procedure to verify the lab from a fresh unauthenticated HTTPS clone.

## Public clone (no file://)

```sh
# Fresh clone — HTTPS, no authentication, no local file substitution
git clone https://github.com/necat101/hn-webauthn-passkey-state-boundary-lab.git
cd hn-webauthn-passkey-state-boundary-lab

# Check tested revision
git rev-parse HEAD
# Expected: 8b4d9eccf57189a8aee3ea4bbb048aafc3d61180 (verify date 2026-09-17)

# Run evaluator and tests from the clone — no file:// substitute
python3 evaluator.py
# Expected: 10 cases · 4 single-device · 5 multi-device · 1 invalid -> results.json + RESULTS.md

python3 -m unittest tests/test_passkey_boundary.py -v
# Expected: 14 tests OK

./verify.sh
# Expected: verify OK
```

## Actual run (2026-09-17, clone at 8b4d9eccf57189a8aee3ea4bbb048aafc3d61180)

```
Cloning into 'verify_clone'...
8b4d9eccf57189a8aee3ea4bbb048aafc3d61180

10 cases · 4 single-device · 5 multi-device · 1 invalid -> results.json + RESULTS.md

Ran 14 tests in 0.008s — OK

RESULTS.md: 10 cases · 4 single-device · 5 multi-device · 1 invalid, hw_proven_any=False
```

## What is verified

- BE/BS table: 0,0 single-device | 0,1 invalid | 1,0 multi-device not backed up | 1,1 multi-device backed up
- discoverable does not prove sync state; platform != synced; roaming != single-device
- attestation informs RP policy but is not hardware-binding proof; lack of attestation != proof of synced
- FIDO "passkey" includes device-bound and synced variants
- No overall "secure passkey" verdict emitted — six orthogonal outputs only
- No browser automation, authenticators, network, or external packages used

## Workflow status

GitHub Actions workflow `.github/workflows/verify.yml` runs `evaluator.py` + `test_passkey_boundary.py` on push/PR.
