"""
Independent oracle: re-derives expected BE/BS classification from raw
credential facts (be/bs/discoverable/attestation/authenticator) without
calling evaluator.classify. Catches the conflations the audit targets.
"""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).parent.parent
FIXTURES = ROOT / "fixtures" / "cases.json"
sys.path.insert(0, str(ROOT))
import evaluator as ev


def oracle(record: dict) -> dict:
    be = record.get("be")
    bs = record.get("bs")
    disc = bool(record.get("discoverable", False))
    att_fmt = record.get("attestation_format", "none")
    if be == 0 and bs == 0:
        scope, be_elig, backed, valid = "single-device", False, False, True
    elif be == 0 and bs == 1:
        scope, be_elig, backed, valid = "invalid", False, False, False
    elif be == 1 and bs == 0:
        scope, be_elig, backed, valid = "multi-device", True, False, True
    elif be == 1 and bs == 1:
        scope, be_elig, backed, valid = "multi-device", True, True, True
    else:
        scope, be_elig, backed, valid = "invalid", False, False, False
    return {
        "credential_scope": scope,
        "backup_eligible": be_elig,
        "currently_backed_up": backed,
        "discoverable": disc,
        "attestation_present": att_fmt != "none",
        "hardware_binding_proven": False,
        "valid_combination": valid,
    }


class TestBackupStateBoundary(unittest.TestCase):
    def test_all_required_be_bs_combinations_present(self):
        cases = json.loads(FIXTURES.read_text())
        combos = {(c["be"], c["bs"]) for c in cases}
        for need in [(0, 0), (0, 1), (1, 0), (1, 1)]:
            self.assertIn(need, combos, f"Missing required BE/BS combo {need}")

    def test_evaluator_matches_oracle(self):
        cases = json.loads(FIXTURES.read_text())
        for c in cases:
            exp = oracle(c)
            got = ev.classify(c)
            with self.subTest(case=c["id"]):
                self.assertEqual(got["credential_scope"], exp["credential_scope"])
                self.assertEqual(got["backup_eligible"], exp["backup_eligible"])
                self.assertEqual(got["currently_backed_up"], exp["currently_backed_up"])
                self.assertEqual(got["discoverable"], exp["discoverable"])
                self.assertEqual(got["attestation_present"], exp["attestation_present"])
                self.assertEqual(got["hardware_binding_proven"], exp["hardware_binding_proven"])
                self.assertEqual(got["valid_combination"], exp["valid_combination"])

    def test_be0_bs1_is_invalid(self):
        """BE=0 BS=1 must be invalid — BS SHALL be 0 when BE=0 (WebAuthn L3 §6.1.3 Table)."""
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "invalid-be0-bs1")
        self.assertFalse(ev.classify(c)["valid_combination"])
        self.assertEqual(ev.classify(c)["credential_scope"], "invalid")

    def test_be1_bs0_is_backup_eligible_not_backed_up(self):
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "multidevice-not-backed-up")
        r = ev.classify(c)
        self.assertTrue(r["backup_eligible"])
        self.assertFalse(r["currently_backed_up"])
        self.assertEqual(r["credential_scope"], "multi-device")
        self.assertTrue(r["valid_combination"])

    def test_be1_bs1_is_backed_up(self):
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "multidevice-backed-up")
        r = ev.classify(c)
        self.assertTrue(r["backup_eligible"])
        self.assertTrue(r["currently_backed_up"])

    def test_be0_bs0_is_single_device(self):
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "single-device-platform-no-attest")
        r = ev.classify(c)
        self.assertEqual(r["credential_scope"], "single-device")
        self.assertFalse(r["backup_eligible"])
        self.assertFalse(r["currently_backed_up"])

    def test_discoverable_does_not_prove_sync_state(self):
        """Discoverable (passkey UX) does not itself prove BE/BS sync state."""
        cases = json.loads(FIXTURES.read_text())
        # There exists a discoverable single-device (device-bound passkey) and a discoverable multi-device
        disc_single = [c for c in cases if c.get("discoverable") and c.get("be") == 0 and c.get("bs") == 0]
        disc_multi = [c for c in cases if c.get("discoverable") and c.get("be") == 1]
        self.assertTrue(disc_single, "Need a discoverable single-device fixture")
        self.assertTrue(disc_multi, "Need a discoverable multi-device fixture")
        for c in disc_single:
            r = ev.classify(c)
            self.assertEqual(r["discoverable"], True)
            self.assertEqual(r["credential_scope"], "single-device")
        for c in disc_multi:
            r = ev.classify(c)
            self.assertEqual(r["discoverable"], True)
            self.assertEqual(r["credential_scope"], "multi-device")

    def test_platform_does_not_imply_synced(self):
        """Platform authenticator does not automatically mean BE=1/BS=1."""
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "platform-single-device-discoverable")
        r = ev.classify(c)
        self.assertEqual(r["authenticator"], "platform")
        self.assertEqual(r["credential_scope"], "single-device")
        self.assertFalse(r["backup_eligible"])

    def test_roaming_does_not_imply_single_device(self):
        """Roaming authenticator does not automatically mean BE=0; a roaming multi-device exists."""
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "roaming-multidevice-not-backed")
        r = ev.classify(c)
        self.assertEqual(r["authenticator"], "roaming")
        self.assertEqual(r["credential_scope"], "multi-device")
        self.assertTrue(r["backup_eligible"])

    def test_passkey_includes_device_bound(self):
        """FIDO 'passkey' includes device-bound (discoverable single-device) passkeys."""
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "device-bound-passkey-attested")
        r = ev.classify(c)
        self.assertTrue(r["discoverable"])
        self.assertEqual(r["credential_scope"], "single-device")
        # FIDO would still call this a passkey — lab shows the term is broader than 'synced'

    def test_attestation_does_not_prove_hardware_bound(self):
        """Attestation can inform RP policy but is not proof of hardware binding."""
        cases = json.loads(FIXTURES.read_text())
        attested = [c for c in cases if c.get("attestation_format") not in ("none", None)]
        self.assertTrue(attested, "Need at least one attested fixture")
        for c in attested:
            r = ev.classify(c)
            self.assertTrue(r["attestation_present"])
            self.assertFalse(r["hardware_binding_proven"],
                f"{c['id']}: attestation must not be treated as hardware-binding proof")

    def test_lack_of_attestation_does_not_prove_synced(self):
        """Lack of attestation does not by itself prove a credential is synced."""
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "single-device-no-attest-lack-does-not-prove-synced")
        r = ev.classify(c)
        self.assertFalse(r["attestation_present"])
        self.assertEqual(r["credential_scope"], "single-device")
        self.assertFalse(r["backup_eligible"])
        self.assertFalse(r["hardware_binding_proven"])

    def test_no_overall_secure_verdict(self):
        """Evaluator must not emit an overall 'secure passkey' verdict."""
        cases = json.loads(FIXTURES.read_text())
        for c in cases:
            r = ev.classify(c)
            self.assertNotIn("secure_passkey", r)
            self.assertNotIn("compliant_authenticator", r)
            self.assertNotIn("overall_secure", r)

    def test_outputs_are_separate(self):
        """The six required outputs exist as independent keys."""
        c = json.loads(FIXTURES.read_text())[0]
        r = ev.classify(c)
        for k in ["credential_scope", "backup_eligible", "currently_backed_up",
                   "discoverable", "attestation_present", "hardware_binding_proven"]:
            self.assertIn(k, r, f"Missing required output: {k}")


if __name__ == "__main__":
    unittest.main()
