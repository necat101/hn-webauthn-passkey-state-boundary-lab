# Results -- hn-webauthn-passkey-state-boundary-lab

Spec: **W3C WebAuthn Level 3** S.6.1.3 Credential Backup State + authenticator-data flags (BE bit 3, BS bit 4).
FIDO: **passkey = discoverable credential** usable for passkey UX; includes **synced** and **device-bound** variants.

**10 cases - 4 single-device - 5 multi-device - 1 invalid** (BE=0 BS=1) - hardware_binding_proven: 0 (by design)

| Case | BE | BS | Scope | backup_eligible | currently_backed_up | discoverable | attest | hw_proven | valid |
|---|---|---|---|---|---|---|---|---|---|---|
| single-device-platform-no-attest | 0 | 0 | single-device | False | False | False | False | False | True |
| multidevice-not-backed-up | 1 | 0 | multi-device | True | False | True | False | False | True |
| multidevice-backed-up | 1 | 1 | multi-device | True | True | True | False | False | True |
| invalid-be0-bs1 | 0 | 1 | invalid | False | False | True | False | False | False |
| device-bound-passkey-attested | 0 | 0 | single-device | False | False | True | True | False | True |
| synced-passkey-with-attestation | 1 | 1 | multi-device | True | True | True | True | False | True |
| roaming-multidevice-not-backed | 1 | 0 | multi-device | True | False | True | False | False | True |
| platform-single-device-discoverable | 0 | 0 | single-device | False | False | True | False | False | True |
| single-device-no-attest-lack-does-not-prove-synced | 0 | 0 | single-device | False | False | False | False | False | True |
| synced-no-attest-discoverable | 1 | 1 | multi-device | True | True | True | False | False | True |

Six outputs are kept separate -- no overall 'secure passkey' verdict is emitted.

**BE/BS normative table:** 0,0 single-device - 0,1 invalid - 1,0 multi-device not backed up - 1,1 multi-device backed up. **BE=1 establishes backup eligibility, not current sync state.**
**Discoverable** does not prove current backup state. **Platform** does not imply backup-eligible. **Roaming** does not imply single-device.
**Attestation:** presence alone, without sufficient trusted metadata/evidence, does not establish hardware binding for these synthetic cases (modeled-evidence conclusion, not a universal WebAuthn rule); lack of attestation does not prove currently backed up.
