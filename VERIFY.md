# VERIFY.md — Fresh-clone verification transcript

This file records verification of **C** (the execution target) and **D** (this documentation-only record).

## C — Execution target (the tested implementation revision)

**Commit C:** `22c9ec422b8995bb43c404ed84c97c11e6cc7a6d` — 2026-09-17

Repairs (substantive WebAuthn classifications unchanged):
- byte-stable generated evidence: `evaluator.py` trailing-newline now matches committed `RESULTS.md` (no tracked diff on rerun — `git diff --exit-code` 0, `git status --porcelain` empty);
- `BE=1` establishes backup eligibility, not current sync state (`1,0` eligible not currently backed up vs `1,1` currently backed up);
- attestation presence alone, without sufficient trusted metadata/evidence, does not establish hardware binding for these synthetic cases (modeled-evidence conclusion);
- HN ledger 5 distinct retrieved comments (patja 49629098 — authn "largely solved" overstated/book ad; VCFundedGenYer 49629041 — operationally nothing is solved/fragmented/UX terrible; hn993302 49629573 — passkeys inconsistently used, name unclear, 1Password anecdote; andychiare 49629045 — authorization is the primary question; jimz 49629749 — Sony OIDC/WebKit/1Password regression).

## Fresh-clone verification of C (unauthenticated HTTPS, no file://)

```sh
git clone https://github.com/necat101/hn-webauthn-passkey-state-boundary-lab.git /tmp/c_clone
cd /tmp/c_clone
git rev-parse HEAD          # -> 22c9ec422b8995bb43c404ed84c97c11e6cc7a6d
python3 evaluator.py
python3 -m unittest tests/test_passkey_boundary.py -v
bash verify.sh
git diff --exit-code        # over every tracked generated result
git status --porcelain
git rev-parse HEAD && git rev-parse origin/main   # HEAD/origin checks
```

### Actual results for C (`22c9ec422b8995bb43c404ed84c97c11e6cc7a6d`)

```
Cloning into '/tmp/c_clone'...
22c9ec422b8995bb43c404ed84c97c11e6cc7a6d
HEAD matches origin/main: 22c9ec422b8995bb43c404ed84c97c11e6cc7a6d
git status --porcelain: (empty before generation)

python3 evaluator.py
-> 10 cases - 4 single-device - 5 multi-device - 1 invalid -> results.json + RESULTS.md

python3 -m unittest tests/test_passkey_boundary.py -v
-> 13 tests OK
   including be1_establishes_eligibility_not_current_sync_state (1,0 != 1,1)
   and attestation_presence_alone_without_trusted_metadata_does_not_prove_hardware_binding

bash verify.sh
-> verify OK (evaluator + tests + RESULTS.md + results.json summary hw_proven_any=False)

git diff --exit-code: 0 (no tracked diff — byte-stable)
git status --porcelain: (empty — clean working tree)
HEAD == origin/main == 22c9ec422b8995bb43c404ed84c97c11e6cc7a6d
```

The core BE/BS conclusion (0,0 single-device | 0,1 invalid | 1,0 eligible not currently backed up | 1,1 currently backed up; device-bound passkeys can still be passkeys) was verified unchanged across the chain; only wording narrowed and trailing-newline stabilized.

## D — This commit (documentation-only)

**C was fresh-clone matched and executed; D records that verification and does not verify itself.**

D does not change `evaluator.py`, `fixtures/cases.json`, `tests/test_passkey_boundary.py`, or `RESULTS.md`.
D only updates `VERIFY.md` to replace the stale `8b4d9ecc` (and earlier `f3d45bc`) record with the actual C execution above.

## Workflow

`.github/workflows/verify.yml` runs `python3 evaluator.py`, `python3 -m unittest tests/test_passkey_boundary.py -v`, and `bash verify.sh`.

D's workflow status is inspected via approved GitHub tooling and reported separately (see email / grading reply).
