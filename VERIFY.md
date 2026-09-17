# VERIFY.md -- Fresh-clone verification transcript

This file records verification of the **repair A** revision and the later documentation-only **B**.

## A -- Repair A (the tested implementation revision)

**Commit A** is the repair that:
- BE=1 establishes backup eligibility, not current sync state (1,0 eligible not currently backed up vs 1,1 currently backed up);
- attestation presence alone, without sufficient trusted metadata/evidence, does not establish hardware binding for these synthetic cases (modeled-evidence conclusion, not a universal WebAuthn rule);
- HN ledger is 5 distinct retrieved comments (patja 49629098, VCFundedGenYer 49629041, hn993302 49629573, andychiare 49629045, jimz 49629749);
- stubs cleaned; workflow fixed to `bash verify.sh`.

## Fresh-clone verification of A (unauthenticated HTTPS, no file://)

```sh
git clone https://github.com/necat101/hn-webauthn-passkey-state-boundary-lab.git
cd hn-webauthn-passkey-state-boundary-lab
git rev-parse HEAD          # -> A
python3 evaluator.py
python3 -m unittest tests/test_passkey_boundary.py -v
bash verify.sh
git rev-parse HEAD && git status && git diff --stat   # HEAD/origin/status checks
# Compare generated evidence vs HEAD (should be no diff -- results.json is gitignored)
bash verify.sh && git diff --stat  # generated-evidence diff check
```

### Actual run for this repo (filled after A is pushed; see transcript below)

```
# 2026-09-17 -- fresh clone at A (recorded after A push)
# (this section is updated to the real transcript once A is verified)
```

## B -- Documentation-only follow-up

**Commit B** records that A was fresh-clone matched and executed; B does not claim to self-verify.

B's own Actions status is inspected via approved GitHub tooling (`github__list_workflow_runs` / `github__get_workflow_run` / REST `actions/runs`).

## Workflow

`.github/workflows/verify.yml` runs `python3 evaluator.py`, `python3 -m unittest tests/test_passkey_boundary.py -v`, and `bash verify.sh` on push/PR.
