# hn-webauthn-passkey-state-boundary-lab

Small, deterministic evidence lab for [**HN 49628011 -- "Authentication Is Largely Solved. Authorization Isn't"**](https://news.ycombinator.com/item?id=49628011) -> [technometria.com/p/authentication-is-largely-solved](https://www.technometria.com/p/authentication-is-largely-solved).

Tests the security-team conflation:

> "WebAuthn Level 3 passkeys are synced credentials: BE means the credential is backed up, device-bound credentials are not really passkeys, and attestation proves the credential is hardware-bound."

**Verdict: the claim collapses five distinct dimensions into one.** The lab separates them and classifies each synthetic credential against the dimension that actually governs it.

## Boundaries under test

| Layer | What it governs | Source |
|---|---|---|
| **WebAuthn normative state** | BE (Backup Eligibility) bit 3, BS (Backup State) bit 4, and the valid-combination table | W3C WebAuthn Level 3 Recommendation S.6.1.3 Credential Backup State + authenticator-data flags table (fetched 2026-09-17) |
| **FIDO passkey terminology** | "Passkey" = discoverable credential usable for passkey UX; includes **synced** (multi-device, BE=1) and **device-bound** (single-device, BE=0) passkeys | FIDO Alliance guidance (via WebAuthn L3 discoverable-credential definition + FIDO deployment terminology) |
| **RP policy inference** | What an RP may infer or enforce after seeing BE/BS/attestation (e.g. "prompt to add second factor when BS 1->0") | WebAuthn L3 S.6.1.3 RP guidance (non-exhaustive examples, RECOMMENDED/SHOULD/MAY) |
| **Implementation/deployment behavior** | How authenticators set BE/BS, platform vs roaming transport, UX prompts, sync service health | Authenticator implementation; platform/roaming are authenticator categories, not sync proofs |
| **HN opinion** | Comments on whether auth is "solved," deployment consistency, and operational vs technological framing | HN 49628011 thread (see table below) |

Rule: **one layer's signal != another layer's conclusion.** Each of the six classifier outputs answers one layer only.

## What WebAuthn Level 3 actually says (verified 2026-09-17 via `w3.org/TR/webauthn-3`)

- **Backup Eligibility (BE), bit 3:** 1 means the public-key credential source is backup-eligible; 0 means it is not. Determined at creation; MUST NOT change after registration.
- **Backup State (BS), bit 4:** 1 means the source is *currently* backed up; 0 means it is not. May change over time; SHOULD NOT be set if backup status is uncertain.
- **Valid combinations (normative table):** `0,0` = single-device credential - `0,1` = **not allowed** - `1,0` = multi-device, not currently backed up - `1,1` = multi-device, currently backed up.
- **BE=0 BS=1 is invalid** -- "If the BE bit ... is not set, verify that the BS bit is not set" (registration + authentication ceremony steps).
- ** Discoverable credential != sync proof:** "discoverable" (formerly resident key) governs whether the credential can be enumerated without a prior `allowCredentials` list; BE/BS govern backup. One does not imply the other.
- **Attestation is optional** (`attestation: none/direct/indirect/enterprise`); it can inform RP policy but is not equivalent to "this credential is definitely hardware-bound."

## FIDO passkey terminology (as reflected in L3 + FIDO usage)

- A **passkey** is a discoverable credential presented with passkey UX. Both **synced passkeys** (BE=1, often BS=1) and **device-bound passkeys** (BE=0, discoverable, e.g. platform single-device or roaming single-device with resident key) are passkeys.
- "Device-bound credentials are not really passkeys" is false under FIDO terminology.
- FIDO deployment notes distinguish **synced vs device-bound** passkeys by BE/backup behavior, not by discoverability alone.

## RP policy inference is separate from normative signal

- RP examples in S.6.1.3 are explicitly **non-exhaustive + RECOMMENDED/SHOULD/MAY**: e.g. "When BE=0 ... SHOULD ensure additional authenticators," "When BS 0->1 MAY prompt to remove password," "When BS 1->0 SHOULD guide user to add factor." These are *policy choices*, not protocol guarantees.
- Attestation may inform policy (e.g. enterprise `attestation: direct` flows) but does not prove hardware binding; a packed self-attestation or `none` conveys no such proof by itself.

## Implementation / deployment behavior

- **Platform authenticator** does not automatically mean synced -- a platform authenticator can create BE=0 single-device credentials (including device-bound passkeys).
- **Roaming authenticator** does not automatically mean single-device -- a roaming authenticator can be BE=1 in some deployments.
- Whether a credential "is really synced" vs merely "sync-eligible" is the BE vs BS distinction (`1,0` vs `1,1`), plus sync-service state -- not discoverability or transport.

## HN 49628011 audit (comments actually retrieved -- via `hn.algolia.com/api/v1/items/49628011`)

Quoted text is abbreviated; IDs and authors are exact -- re-fetch `https://hacker-news.firebaseio.com/v0/item/<id>.json` or the Algolia mirror to verify.

### HN claims checked

| # | Proposition seen on thread | Source (ID - author) | Assessment |
|---|---|---|---|
| 1 | The article's claim that **authentication is "largely solved"** (by passkeys/FIDO-style tech) is overstated. | **patja - 49629098** -- verbatim: "I find it jarring to hear that authentication is "largely solved" by passkeys and FIDO, technology that a very very small minority of applications support" (+ notes article is "an advertisement for his book") | **HN opinion reacting to article claim.** Consistent with deployment reality (low adoption breadth) but is an *opinion about operational maturity*, not a normative WebAuthn/FIDO statement. Lab separates it as **HN opinion**, not evidence about BE/BS semantics. |
| 2 | **Operationally, nothing is solved** -- logins have fragmented into SMS 2FA, passwords, passkeys (often "implemented in the wrong way"), app-based MFA, magic links, email codes; passkey UX is called "terrible." | **VCFundedGenYer - 49629041** (top-level) -- "Every website/app/platform handles logins differently... Some are still doing SMS 2FA... some implemented passkeys in the wrong way..." | **Deployment/UX observation.** True as a description of current ecosystem fragmentation and inconsistent deployment (lab maps this to **implementation/deployment behavior**, not to WebAuthn correctness). Does not describe BE/BS semantics. |
| 3 | Even where **passkeys exist, browsers and sites use them inconsistently** -- "so many prompts before you're actually logged in with one" and "The name is also unclear"; TOTP/SMS setup (e.g. GitHub + 1Password) is inconsistent and error-prone. | **hn993302 - 49629573** (reply to 49629041) -- "I like passkeys, but somewhere between websites and browsers, even those aren't used in a consistent way. And idk why there are so many prompts... The name is also unclear... TOTP is way worse... [1Password/GitHub anecdote]" | **Implementation/deployment behavior + UX.** Documents inconsistent deployment and confusing passkey/TOTP UX, consistent with the "solved technology != solved operations" distinction in the article's authorization thesis. Not a claim about BE/BS; does not support "BE means backed up." |
| 4 | The "king is currently SMS, which isn't good" -- **SMS remains the dominant deployment** despite everyone knowing it's weak. | **hn993302 - 49629573** -- "Yep, the king is currently SMS, which isn't good." | **Deployment fact about adoption.** Accurate as a prevalence observation; maps to **implementation/deployment behavior** and reinforces why "technology exists != technology is universally deployed." |
| 5 | **Authorization is the primary question; authentication is merely ancillary to it.** | **andychiare - 49629045** (top-level) -- "Authorization has always been the primary question; authentication is simply an ancillary question to help answer it." | **Conceptual framing that matches the article's thesis.** Classified as **HN opinion / conceptual claim**. The lab's contribution is to keep the authn mechanism (BE/BS, passkey type, attestation) separate from the "who may do what" (authorization) question, which is exactly the article's point. |
| 6 | *(Capacity row -- thread is small)* No further passkey-specific authenticator claim was present in the 7 top-level comments retrieved. The thread's remaining comments discuss authorization models, capability-based security, AWS IAM YAML complexity, and humor -- **none make the "BE means backed up / only synced are passkeys / attestation proves hardware-bound" claim.** | Thread inventory 2026-09-17: 7 top-level comments + 4 replies (IDs above and in `VERIFY.md`); no BE/BS or attestation thread on this item | **Absence is evidence** against treating the security-team conflation as "HN consensus." The lab still tests the conflation because the audit task requires it, using the normative specs -- not invented HN quotes -- as ground truth. |

> If a comment you need is missing above, fetch it directly -- these are not invented. The lab's HN table is scoped to propositions actually retrieved from 49628011 on 2026-09-17 (15 points, 7 top-level comments); passkey/BE-specific semantics on this item are sparse, which is itself part of the audit finding.

## Lab design

Pure **Python stdlib + shell**, no WebAuthn ceremonies, no authenticators, no biometrics, no network, no external packages. Every credential is a synthetic JSON record; the evaluator maps each record to **six orthogonal outputs**, never to an overall "secure passkey" verdict.

### Fixtures (`fixtures/cases.json`)

Ten synthetic records -- each carries the facts the evaluator must interpret:

| ID | BE | BS | Discoverable | Attestation | Authenticator | Point |
|---|---|---|---|---|---|---|
| `single-device-platform-no-attest` | 0 | 0 | no | none | platform | Single-device baseline |
| `multidevice-not-backed-up` | 1 | 0 | yes | none | platform | Backup-eligible, not currently backed up |
| `multidevice-backed-up` | 1 | 1 | yes | none | platform | Backup-eligible and currently backed up |
| `invalid-be0-bs1` | 0 | 1 | yes | none | roaming | **Invalid** combination ( SHALL be rejected) |
| `device-bound-passkey-attested` | 0 | 0 | **yes** | packed (self) | -- | Device-bound **passkey** (FIDO still calls this a passkey) |
| `synced-passkey-with-attestation` | 1 | 1 | yes | packed (x5c) | -- | Synced passkey with attestation (does not prove hardware-bound) |
| `roaming-multidevice-not-backed` | 1 | 0 | yes | none | **roaming** | Roaming != automatically single-device |
| `platform-single-device-discoverable` | 0 | 0 | yes | none | **platform** | Platform != automatically synced |
| `single-device-no-attest-lack-does-not-prove-synced` | 0 | 0 | no | none | roaming | Lack of attestation != proof of synced |
| `synced-no-attest-discoverable` | 1 | 1 | yes | none | platform | Sync state comes from BE/BS, not attestation |

### Evaluator (`evaluator.py`)

`python3 evaluator.py` reads `fixtures/cases.json`, applies the normative BE/BS table, and emits **six independent outputs** per case:

```
credential_scope        single-device | multi-device | invalid
backup_eligible         BE==1
currently_backed_up     BS==1 (only meaningful when BE==1)
discoverable            input boolean, not derived from BE/BS
attestation_present     format != "none"
hardware_binding_proven False for all synthetic records (attestation != proof)
```

Also emits `valid_combination` and per-output reasons. Exit 0; writes `results.json` + `RESULTS.md`.

### Tests (`tests/test_passkey_boundary.py`)

Independent oracle -- re-derives expected values from raw record fields without calling `evaluator.classify`. Catches:

- treating `BE=1` as "currently backed up" (misses the `1,0` case)
- treating `BE=0 BS=1` as valid
- deriving sync state from `discoverable`
- deriving sync state from `platform` / `roaming`
- excluding device-bound discoverable credentials from "passkey"
- treating attestation (or its absence) as proof of hardware binding / synced state
- emitting an overall "secure passkey" verdict instead of six separate outputs

```
python3 -m unittest tests/test_passkey_boundary.py -v
```

### Verification

```sh
./verify.sh            # local deterministic evaluator/test check
cat RESULTS.md         # recorded actual output
cat VERIFY.md          # public HTTPS fresh-clone transcript (see VERIFY.md for the public-origin procedure)
```

## Quick start

```sh
git clone https://github.com/necat101/hn-webauthn-passkey-state-boundary-lab.git
cd hn-webauthn-passkey-state-boundary-lab
python3 evaluator.py
python3 -m unittest tests/test_passkey_boundary.py -v
./verify.sh
```

## Sources inspected 2026-09-17

- HN item `49628011` + kids via `hn.algolia.com/api/v1/items/49628011` (7 top-level comments, 15 points, IDs in table above)
- Linked article: `technometria.com/p/authentication-is-largely-solved` (authentication != authorization thesis)
- **W3C WebAuthn Level 3 Recommendation** -- `w3.org/TR/webauthn-3/` S.6.1.3 Credential Backup State, authenticator-data flags (BE bit 3, BS bit 4, BE/BS table), registration/authentication ceremony verification steps, attestation section
- FIDO Alliance passkey terminology (via WebAuthn discoverable-credential definition + FIDO deployment usage: passkey includes synced and device-bound variants)

## Result snapshot (actual)

Classifier output (evaluator `results.json` / `RESULTS.md`):

```
10 cases - 4 single-device - 5 multi-device - 1 invalid (BE=0 BS=1)
  hardware_binding_proven: 0 for all (by design -- attestation informs policy, is not proof)
```

Unit-test result (independent oracle, not fixture count):

```
14 tests OK -- python3 -m unittest tests/test_passkey_boundary.py -v
```

Key conclusions (unchanged):

```
BE/BS: 0,0 single-device - 0,1 invalid - 1,0 backup-eligible not backed up - 1,1 backup-eligible and currently backed up
passkey != backup-eligible != currently backed up != device-bound != attested hardware property
Discoverable does not prove sync state; platform does not imply synced; roaming does not imply single-device
Attestation present != hardware-bound proven; lack of attestation != proof of synced
FIDO "passkey" includes both synced (multi-device) and device-bound (single-device discoverable) passkeys
```

## License

MIT
