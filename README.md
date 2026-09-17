# hn-webauthn-passkey-state-boundary-lab

Small, deterministic evidence lab for [**HN 49628011 -- "Authentication Is Largely Solved. Authorization Isn't"**](https://news.ycombinator.com/item?id=49628011) -> [technometria.com/p/authentication-is-largely-solved](https://www.technometria.com/p/authentication-is-largely-solved).

Tests the security-team conflation:

> "WebAuthn Level 3 passkeys are synced credentials: BE means the credential is backed up, device-bound credentials are not really passkeys, and attestation proves the credential is hardware-bound."

**Verdict: the claim collapses five distinct dimensions into one.** The lab separates them and classifies each synthetic credential against the dimension that actually governs it.

## Boundaries under test

| Layer | What it governs | Source |
|---|---|---|
| **WebAuthn normative state** | BE (Backup Eligibility) bit 3, BS (Backup State) bit 4, and the valid-combination table | W3C WebAuthn Level 3 Recommendation S.6.1.3 Credential Backup State + authenticator-data flags table (fetched 2026-09-17) |
| **FIDO passkey terminology** | "Passkey" = discoverable credential usable for passkey UX; includes **synced (multi-device currently-backed-up)** and **device-bound (single-device, BE=0)** passkeys. | FIDO Alliance guidance (via WebAuthn L3 discoverable-credential definition + FIDO deployment terminology). **BE=1 establishes backup eligibility, not current sync state** -- see also BS. |
| **RP policy inference** | What an RP may infer or enforce after seeing BE/BS/attestation (e.g. "prompt to add second factor when BS 1->0") | WebAuthn L3 S.6.1.3 RP guidance (non-exhaustive examples, RECOMMENDED/SHOULD/MAY) |
| **Implementation/deployment behavior** | How authenticators set BE/BS, platform vs roaming transport, UX prompts, sync service health | Authenticator implementation; platform/roaming are authenticator categories, not sync proofs |
| **HN opinion** | Comments on whether auth is "solved," deployment consistency, and operational vs technological framing | HN 49628011 thread (see table below) |

Rule: **one layer's signal != another layer's conclusion.** Each of the six classifier outputs answers one layer only.

**Corrected:** BE=1 establishes backup eligibility, not current sync state (1,0 is eligible not currently backed up; 1,1 is currently backed up).

## What WebAuthn Level 3 actually says (verified 2026-09-17 via `w3.org/TR/webauthn-3`)

- **Backup Eligibility (BE), bit 3:** 1 means the public-key credential source is backup-eligible; 0 means it is not. Determined at creation; MUST NOT change after registration. **BE=1 does not by itself mean "currently backed up" / "synced" -- that requires BS=1.**
- **Backup State (BS), bit 4:** 1 means the source is *currently* backed up; 0 means it is not. May change over time; SHOULD NOT be set if backup status is uncertain. Only meaningful when BE=1.
- **Valid combinations (normative table):** `0,0` = single-device credential - `0,1` = **not allowed** - `1,0` = multi-device / backup-eligible, not currently backed up - `1,1` = multi-device, currently backed up.
- **BE=0 BS=1 is invalid** -- "If the BE bit ... is not set, verify that the BS bit is not set" (registration + authentication ceremony steps).
- ** Discoverable credential != sync proof:** "discoverable" (formerly resident key) governs whether the credential can be enumerated without a prior `allowCredentials` list; BE/BS govern backup. One does not imply the other.
- **Attestation is optional** (`attestation: none/direct/indirect/enterprise`); it can inform RP policy but **attestation presence alone, without sufficient trusted metadata/evidence, does not establish hardware binding for these synthetic cases** (modeled-evidence conclusion, not a universal WebAuthn rule).

## FIDO passkey terminology (as reflected in L3 + FIDO usage)

- A **passkey** is a discoverable credential presented with passkey UX. Both **synced passkeys (multi-device currently-backed-up, BE=1 BS=1)** and **device-bound passkeys** (BE=0, discoverable, e.g. platform single-device or roaming single-device with resident key) are passkeys.
- "Device-bound credentials are not really passkeys" is false under FIDO terminology.
- FIDO deployment notes distinguish **synced vs device-bound** passkeys by BE/BS backup behavior, not by discoverability alone. **BE=1 alone is backup-eligible; "synced" in this lab means currently backed up (BE=1 BS=1).**
- Device-bound credentials (BE=0 BS=0, single-device) can still be passkeys when discoverable.

## RP policy inference is separate from normative signal

- RP examples in S.6.1.3 are explicitly **non-exhaustive + RECOMMENDED/SHOULD/MAY**: e.g. "When BE=0 ... SHOULD ensure additional authenticators," "When BS 0->1 MAY prompt to remove password," "When BS 1->0 SHOULD guide user to add factor." These are *policy choices*, not protocol guarantees.
- Attestation may inform policy (e.g. enterprise `attestation: direct` flows) but for these synthetic records, **attestation presence alone, without sufficient trusted metadata/evidence, does not establish hardware binding** (modeled-evidence conclusion). This is not a claim that attestation can never prove hardware properties in richer evidentiary contexts.

## Implementation / deployment behavior

- **Platform authenticator** does not automatically mean backup-eligible or currently backed-up -- a platform authenticator can create BE=0 single-device credentials (including device-bound passkeys).
- **Roaming authenticator** does not automatically mean single-device -- a roaming authenticator can be backup-eligible (BE=1) in some deployments.
- Whether a credential "is really backed up" vs merely "backup-eligible" is the BE vs BS distinction (`1,0` eligible not currently backed up vs `1,1` currently backed up), plus sync-service state -- not discoverability or transport.

## HN 49628011 audit (comments actually retrieved -- via `hn.algolia.com/api/v1/items/49628011`)

Quoted text is abbreviated; IDs and authors are exact -- re-fetch `https://hacker-news.firebaseio.com/v0/item/<id>.json` or the Algolia mirror to verify.

### HN claims checked

| # | Proposition seen on thread | Source (ID - author) | Assessment |
|---|---|---|---|
| 1 | The article's claim that **authentication is "largely solved"** (by passkeys/FIDO-style tech) is overstated; presents as self-promotion / book ad. | **patja - 49629098** -- verbatim: "I find it jarring to hear that authentication is "largely solved" by passkeys and FIDO, technology that a very very small minority of applications support" (+ notes article is "an advertisement for his book") | **HN opinion reacting to article claim.** Consistent with deployment reality (low adoption breadth) but is an *opinion about operational maturity*, not a normative WebAuthn/FIDO statement. Lab separates it as **HN opinion**, not evidence about BE/BS semantics. |
| 2 | **Operationally, nothing is solved** -- logins have fragmented into SMS 2FA, passwords, passkeys (often "implemented in the wrong way"), app-based MFA, magic links, email codes; passkey UX is called "terrible." | **VCFundedGenYer - 49629041** (top-level) -- "Every website/app/platform handles logins differently... Some are still doing SMS 2FA... some implemented passkeys in the wrong way..." | **Deployment/UX observation.** True as a description of current ecosystem fragmentation and inconsistent deployment (lab maps this to **implementation/deployment behavior**, not to WebAuthn correctness). Does not describe BE/BS semantics. |
| 3 | Even where **passkeys exist, browsers and sites use them inconsistently** -- "so many prompts before you're actually logged in with one" and "The name is also unclear"; GitHub + 1Password TOTP setup is inconsistent and error-prone. | **hn993302 - 49629573** (reply to 49629041) -- "I like passkeys, but somewhere between websites and browsers, even those aren't used in a consistent way. And idk why there are so many prompts... The name is also unclear... [1Password/GitHub anecdote]" | **Implementation/deployment behavior + UX.** Documents inconsistent deployment and confusing passkey/TOTP UX, consistent with the "solved technology != solved operations" distinction in the article's authorization thesis. Not a claim about BE/BS; does not support "BE means backed up." |
| 4 | **Authorization is the primary question; authentication is merely ancillary to it.** | **andychiare - 49629045** (top-level) -- "Authorization has always been the primary question; authentication is simply an ancillary question to help answer it." | **Conceptual framing that matches the article's thesis.** Classified as **HN opinion / conceptual claim**. The lab's contribution is to keep the authn mechanism (BE/BS, passkey type, attestation) separate from the "who may do what" (authorization) question, which is exactly the article's point. |
| 5 | **Sony went backwards on passkey compatibility** when merging separate OIDC setups -- WebKit/1Password detection that worked on PSN broke after the merge; shipping a visibly broken passkey integration is "pretty wild." | **jimz - 49629749** (reply within 49629041 subthread) -- verbatim core: "how Sony went backwards with passkey compatibility on their apps... tried to have a single OIDC setup instead of multiple... current webkit implementations to detect passkeys in say your 1password when it was working like a charm for years on PSN" | **Deployment/integration behavior.** Demonstrates that passkey adoption is fragile to integration changes (OIDC consolidation, WebKit detection) -- consistent with VCFundedGenYer's "passkeys implemented in the wrong way" observation. Not a normative WebAuthn claim. |

> Direct BE/BS, sync-state, or attestation-hardware semantics are sparse on this HN item -- none of the retrieved comments on 49628011 make the "BE means backed up / only synced are passkeys / attestation proves hardware-bound" conflation directly; the lab tests it because the audit task requires it, using normative specs as ground truth, not invented HN passkey quotes.

## Lab design

Pure **Python stdlib + shell**, no WebAuthn ceremonies, no authenticators, no biometrics, no network, no external packages. Every credential is a synthetic JSON record; the evaluator maps each record to **six orthogonal outputs**, never to an overall "secure passkey" verdict.

### Fixtures (`fixtures/cases.json`)

Ten synthetic records -- each carries the facts the evaluator must interpret:

| ID | BE | BS | Discoverable | Attestation | Authenticator | Point |
|---|---|---|---|---|---|---|
| `single-device-platform-no-attest` | 0 | 0 | no | none | platform | Single-device baseline |
| `multidevice-not-backed-up` | 1 | 0 | yes | none | platform | Backup-eligible, not currently backed up (BE=1 does not mean synced) |
| `multidevice-backed-up` | 1 | 1 | yes | none | platform | Currently backed up (BE=1 BS=1) |
| `invalid-be0-bs1` | 0 | 1 | yes | none | roaming | **Invalid** combination ( SHALL be rejected) |
| `device-bound-passkey-attested` | 0 | 0 | **yes** | packed (self) | -- | Device-bound **passkey** (FIDO still calls this a passkey) |
| `synced-passkey-with-attestation` | 1 | 1 | yes | packed (x5c) | -- | Currently backed up passkey with attestation (attestation alone without trusted metadata does not establish hardware binding) |
| `roaming-multidevice-not-backed` | 1 | 0 | yes | none | **roaming** | Roaming BE=1 BS=0 -- backup-eligible, not currently backed up |
| `platform-single-device-discoverable` | 0 | 0 | yes | none | **platform** | Platform BE=0 BS=0 -- platform does not imply backup-eligible |
| `single-device-no-attest-lack-does-not-prove-synced` | 0 | 0 | no | none | roaming | Lack of attestation != proof of currently backed up |
| `synced-no-attest-discoverable` | 1 | 1 | yes | none | platform | Currently backed up; state comes from BS=1 when BE=1, not attestation |

### Evaluator (`evaluator.py`)

`python3 evaluator.py` reads `fixtures/cases.json`, applies the normative BE/BS table, and emits **six independent outputs** per case:

```
credential_scope        single-device | multi-device | invalid
backup_eligible         BE==1 (not "synced"; currently_backed_up is separate)
currently_backed_up     BS==1 and BE==1 (only meaningful when BE==1)
discoverable            input boolean, not derived from BE/BS
attestation_present     format != "none"
hardware_binding_proven False for all synthetic records (attestation presence alone,
                        without sufficient trusted metadata/evidence, does not
                        establish hardware binding for these cases)
```

Also emits `valid_combination` and per-output reasons. Exit 0; writes `results.json` + `RESULTS.md`. **BE=1 establishes backup eligibility, not current sync state** (1,0 vs 1,1 must differ).

### Tests (`tests/test_passkey_boundary.py`)

Independent oracle -- re-derives expected values from raw record fields without calling `evaluator.classify`. Catches:

- treating `BE=1` as "currently backed up / synced" (misses the `1,0` case)
- treating `BE=0 BS=1` as valid
- deriving sync state from `discoverable`
- deriving sync/eligibility state from `platform` / `roaming`
- excluding device-bound discoverable credentials from "passkey"
- treating attestation presence alone (without sufficient trusted metadata/evidence) as proof of hardware binding
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
- FIDO Alliance passkey terminology (via WebAuthn discoverable-credential definition + FIDO deployment usage: passkey includes synced and device-bound variants; BE=1 is backup eligibility, 1,0 vs 1,1 is eligibility vs currently backed up)

## Result snapshot (actual)

Classifier output (evaluator `results.json` / `RESULTS.md`):

```
10 cases - 4 single-device - 5 multi-device - 1 invalid (BE=0 BS=1)
  hardware_binding_proven: 0 for all (modeled-evidence conclusion for these synthetic cases)
```

Unit-test result (independent oracle, not fixture count):

```
14 tests OK -- python3 -m unittest tests/test_passkey_boundary.py -v
```

Key conclusions (corrected):

```
BE/BS: 0,0 single-device - 0,1 invalid - 1,0 backup-eligible not currently backed up - 1,1 backup-eligible and currently backed up
BE=1 establishes backup eligibility, not current sync state (must check BS=1 for currently backed up)
passkey != backup-eligible != currently backed up != device-bound != attested hardware property
Discoverable does not prove sync state; platform does not imply backup-eligible; roaming does not imply single-device
Attestation presence alone, without sufficient trusted metadata/evidence, does not establish hardware binding for these synthetic cases
FIDO "passkey" includes both backup-eligible (BE=1) and device-bound (single-device discoverable) passkeys; 1,0 vs 1,1 distinguishes eligible vs currently backed up
```

## License

MIT
