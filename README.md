# hn-webauthn-passkey-state-boundary-lab

Small, deterministic evidence lab for HN 49628011 -- Authentication Is Largely Solved. Authorization Isnt (https://news.ycombinator.com/item?id=49628011) -> technometria.com/p/authentication-is-largely-solved

Tests the security-team conflation: "WebAuthn Level 3 passkeys are synced credentials: BE means the credential is backed up, device-bound credentials are not really passkeys, and attestation proves the credential is hardware-bound."

Verdict: the claim collapses five distinct dimensions into one. See local README for full audit.

## Quick start

```
git clone https://github.com/necat101/hn-webauthn-passkey-state-boundary-lab.git
cd hn-webauthn-passkey-state-boundary-lab
python3 evaluator.py
python3 -m unittest tests/test_passkey_boundary.py -v
./verify.sh
```

Local README is 14KB with full HN claims-checked table (6 rows), normative BE/BS table, FIDO terminology, and sources. Pushing full content in next commit.
