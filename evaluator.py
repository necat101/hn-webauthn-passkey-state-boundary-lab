#!/usr/bin/env python3
"""
Deterministic WebAuthn Level 3 BE/BS + passkey-state classifier.

Synthetic credential records only — no browser, no authenticator, no network.
Stdlib only. Separates six orthogonal outputs:

  credential_scope        single-device | multi-device | invalid
  backup_eligible         BE==1
  currently_backed_up     BS==1 (meaningful only when BE==1)
  discoverable            input discoverable boolean
  attestation_present     attestation_format != "none"
  hardware_binding_proven False for all synthetic records (attestation informs
                          RP policy but is not proof of hardware binding)

Normative grounding: W3C WebAuthn Level 3 §6.1.3 + authenticator-data flags table.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).parent
FIXTURES = ROOT / "fixtures" / "cases.json"
RESULTS_JSON = ROOT / "results.json"
RESULTS_MD = ROOT / "RESULTS.md"

# Valid BE/BS per WebAuthn L3 Table "BE and BS flag combinations":
#  0,0 -> single-device
#  0,1 -> invalid (not allowed)
#  1,0 -> multi-device, not currently backed up
#  1,1 -> multi-device, currently backed up

def classify(record: dict) -> dict:
    rid = record["id"]
    be = record.get("be")
    bs = record.get("bs")
    discoverable = bool(record.get("discoverable", False))
    att_fmt = record.get("attestation_format", "none")
    authenticator = record.get("authenticator", "platform")

    # --- normative BE/BS logic ---
    if be not in (0, 1) or bs not in (0, 1):
        credential_scope = "invalid"
        backup_eligible = False
        currently_backed_up = False
        valid_combination = False
        reason_be_bs = "BE/BS must be 0 or 1"
    elif be == 0 and bs == 0:
        credential_scope = "single-device"
        backup_eligible = False
        currently_backed_up = False
        valid_combination = True
        reason_be_bs = "BE=0 BS=0 -> single-device credential (not backup-eligible, not backed up)"
    elif be == 0 and bs == 1:
        credential_scope = "invalid"
        backup_eligible = False
        currently_backed_up = False  # BS=1 is not allowed when BE=0; report as invalid
        valid_combination = False
        reason_be_bs = "BE=0 BS=1 -> invalid combination (BS SHALL be 0 when BE=0; Table BE/BS states 'not allowed')"
    elif be == 1 and bs == 0:
        credential_scope = "multi-device"
        backup_eligible = True
        currently_backed_up = False
        valid_combination = True
        reason_be_bs = "BE=1 BS=0 -> multi-device credential, backup-eligible but not currently backed up"
    else:  # be==1 and bs==1
        credential_scope = "multi-device"
        backup_eligible = True
        currently_backed_up = True
        valid_combination = True
        reason_be_bs = "BE=1 BS=1 -> multi-device credential, backup-eligible and currently backed up"

    attestation_present = att_fmt != "none"

    # Hardware binding is NOT proven by attestation alone (nor by BE/BS).
    # Attestation can inform RP policy but is not equivalent to "definitely hardware-bound".
    # Lack of attestation also does not prove synced. So synthetic records never prove it here.
    hardware_binding_proven = False
    hardware_reason = (
        "Attestation can inform RP policy but is not equivalent to 'definitely hardware-bound'; "
        "synthetic record alone does not prove hardware binding"
        if attestation_present else
        "No attestation present; absence does not prove synced nor hardware-bound"
    )

    # Discoverable does not prove sync state — report independently
    # Platform/roaming does not automatically mean synced — report independently
    discoverable_reason = "discoverable is orthogonal to BE/BS backup state"
    authenticator_reason = (
        f"authenticator={authenticator} does not imply sync state; BE/BS is authoritative"
    )

    return {
        "case_id": rid,
        "credential_scope": credential_scope,
        "backup_eligible": backup_eligible,
        "currently_backed_up": currently_backed_up,
        "discoverable": discoverable,
        "attestation_present": attestation_present,
        "hardware_binding_proven": hardware_binding_proven,
        "valid_combination": valid_combination,
        "be": be,
        "bs": bs,
        "attestation_format": att_fmt,
        "authenticator": authenticator,
        "reasons": {
            "be_bs": reason_be_bs,
            "discoverable": discoverable_reason,
            "authenticator": authenticator_reason,
            "hardware_binding": hardware_reason,
        },
    }

def main():
    cases = json.loads(FIXTURES.read_text())
    results = [classify(c) for c in cases]
    invalid_count = sum(1 for r in results if not r["valid_combination"])
    single = sum(1 for r in results if r["credential_scope"] == "single-device")
    multi = sum(1 for r in results if r["credential_scope"] == "multi-device")

    out = {
        "spec": "W3C WebAuthn Level 3 Recommendation (w3.org/TR/webauthn-3, §6.1.3 + authenticator-data flags)",
        "fido_terminology": "FIDO Alliance: 'passkey' includes both synced (multi-device) and device-bound (single-device) passkeys; discoverable credential is a necessary but not sufficient property",
        "be_bs_table": "0,0=single-device | 0,1=invalid | 1,0=multi-device not backed up | 1,1=multi-device backed up",
        "total": len(results),
        "single_device": single,
        "multi_device": multi,
        "invalid_combinations": invalid_count,
        "hardware_binding_proven_any": any(r["hardware_binding_proven"] for r in results),
        "results": results,
    }
    RESULTS_JSON.write_text(json.dumps(out, indent=2) + "\n")

    lines = []
    lines.append("# Results — hn-webauthn-passkey-state-boundary-lab")
    lines.append("")
    lines.append("Spec: **W3C WebAuthn Level 3** §6.1.3 Credential Backup State + authenticator-data flags (BE bit 3, BS bit 4).")
    lines.append("FIDO: **passkey = discoverable credential** usable for passkey UX; includes **synced** and **device-bound** variants.")
    lines.append("")
    lines.append(f"**{len(results)} cases · {single} single-device · {multi} multi-device · {invalid_count} invalid** (BE=0 BS=1) · hardware_binding_proven: 0 (by design)")
    lines.append("")
    lines.append("| Case | BE | BS | Scope | backup_eligible | currently_backed_up | discoverable | attest | hw_proven | valid |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in results:
        lines.append(f"| {r['case_id']} | {r['be']} | {r['bs']} | {r['credential_scope']} | {r['backup_eligible']} | {r['currently_backed_up']} | {r['discoverable']} | {r['attestation_present']} | {r['hardware_binding_proven']} | {r['valid_combination']} |")
    lines.append("")
    lines.append("Six outputs are kept separate — no overall 'secure passkey' verdict is emitted.")
    lines.append("")
    lines.append("**BE/BS normative table:** 0,0 single-device · 0,1 invalid · 1,0 multi-device not backed up · 1,1 multi-device backed up.")
    lines.append("**Discoverable** does not prove sync state. **Platform** does not imply synced. **Roaming** does not imply single-device.")
    lines.append("**Attestation** informs RP policy but is not proof of hardware binding; lack of attestation does not prove synced.")
    lines.append("")
    RESULTS_MD.write_text("\n".join(lines) + "\n")
    print(f"{len(results)} cases · {single} single-device · {multi} multi-device · {invalid_count} invalid -> results.json + RESULTS.md")

if __name__ == "__main__":
    main()
