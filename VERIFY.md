# VERIFY.md — Verification transcript

This file records verification of the **repair A** revision and the later documentation-only **B**.

## A — Repair A (the tested implementation revision)

**Commit A:** `f3d45bc6c09680d598c258989f41266ff953638d` — 2026-09-17

Repairs:
- `BE=1` establishes backup eligibility, not current sync state (`1,0` eligible not currently backed up vs `1,1` currently backed up); README/evaluator/fixtures/tests wording narrowed;
- attestation presence alone, without sufficient trusted metadata/evidence, does not establish hardware binding for these synthetic cases (modeled-evidence conclusion, not a universal WebAuthn rule);
- HN ledger repaired to **5 distinct retrieved comments** (patja 49629098, VCFundedGenYer 49629041, hn993302 49629573, andychiare 49629045, jimz 49629749) — no double-counting, no absence-of-evidence row;
- direct BE/BS/attestation discussion sparse on HN 49628011 (stated separately, not as a ledger row).

## Fresh-clone verification of A (unauthenticated HTTPS, no file://)

Procedure (executed from a fresh HTTPS clone, no `file://` substitute):

```sh
git clone https://github.com/necat101/hn-webauthn-passkey-state-boundary-lab.git /tmp/repairA_clone
cd /tmp/repairA_clone
git rev-parse HEAD          # -> A
python3 evaluator.py
python3 -m unittest tests/test_passkey_boundary.py -v
bash verify.sh
git rev-parse HEAD && git status && git diff --stat
bash verify.sh && git diff --stat
```

### Actual results for A (`f3d45bc6c09680d598c258989f41266ff953638d`)

```
Cloning into '/tmp/repairA_clone'...
f3d45bc6c09680d598c258989f41266ff953638d
HEAD matches origin/main: f3d45bc6c09680d598c258989f41266ff953638d
On branch main — nothing to commit, working tree clean

python3 evaluator.py
-> 10 cases - 4 single-device - 5 multi-device - 1 invalid -> results.json + RESULTS.md

python3 -m unittest tests/test_passkey_boundary.py -v
-> 13 tests OK (0.006s)
   - test_all_required_be_bs_combinations_present: ok
   - test_attestation_presence_alone_without_trusted_metadata_does_not_prove_hardware_binding: ok
   - test_be0_bs0_is_single_device: ok
   - test_be0_bs1_is_invalid: ok (BE=0 BS=1 invalid per L3 S.6.1.3)
   - test_be1_establishes_eligibility_not_current_sync_state: ok (1,0 != 1,1)
   - test_discoverable_does_not_prove_sync_state: ok
   - test_evaluator_matches_oracle: ok
   - test_lack_of_attestation_does_not_prove_synced: ok
   - test_no_overall_secure_verdict: ok
   - test_outputs_are_separate: ok (6 orthogonal outputs)
   - test_passkey_includes_device_bound: ok (device-bound passkey with BE=0 BS=0)
   - test_platform_does_not_imply_synced: ok
   - test_roaming_does_not_imply_single_device: ok

bash verify.sh
-> verify OK (evaluator + tests + RESULTS.md cat + results.json summary)
   Summary: 10 cases, 4 single, 5 multi, 1 invalid, hw_proven_any=False

HEAD/origin/status checks:
-> HEAD == origin/main == f3d45bc — match
-> git status: working tree clean before evaluator; after generation: results.json ignored (gitignored),
     RESULTS.md shows trivial trailing-newline diff (working 2255 vs committed 2254, strip-equal True).
     This is cosmetic (evaluator writes lines+"" then join+"\n" => double trailing newline vs committed single).

Generated-evidence diff check:
-> bash verify.sh && git diff --stat shows RESULTS.md 1 insertion (trailing newline) — no functional
   generation mismatch; results.json remains gitignored. Recorded honestly as observed.
```

## B — Documentation-only follow-up

**This commit (B) records that A was fresh-clone matched and executed; B does not claim to self-verify.**

A was verified at `f3d45bc` via the procedure above. B only updates this documentation.

B's own Actions status is inspected separately via approved GitHub tooling
(`actions/runs` REST + `github__get_file_contents` / workflow file check).

## Workflow

`.github/workflows/verify.yml` runs `python3 evaluator.py`, `python3 -m unittest tests/test_passkey_boundary.py -v`, and `bash verify.sh` on push/PR.
