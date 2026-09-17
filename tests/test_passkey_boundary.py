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
        """BE=0 BS=1 must be invalid -- BS SHALL be 0 when BE=0 (WebAuthn L3 S.6.1.3 Table)."""
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "invalid-be0-bs1")
        self.assertFalse(ev.classify(c)["valid_combination"])
        self.assertEqual(ev.classify(c)["credential_scope"], "invalid")

    def test_be1_establishes_eligibility_not_current_sync_state(self):
        """BE=1 establishes backup eligibility, not current sync state: 1,0 != 1,1."""
        c_10 = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "multidevice-not-backed-up")
        c_11 = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "multidevice-backed-up")
        r_10 = ev.classify(c_10)
        r_11 = ev.classify(c_11)
        self.assertTrue(r_10["backup_eligible"])
        self.assertTrue(r_11["backup_eligible"])
        self.assertFalse(r_10["currently_backed_up"], "BE=1 BS=0 is not currently backed up")
        self.assertTrue(r_11["currently_backed_up"], "BE=1 BS=1 is currently backed up")
        # Must not conflate BE=1 with synced/currently backed up
        self.assertNotEqual(r_10["currently_backed_up"], r_11["currently_backed_up"])

    def test_be0_bs0_is_single_device(self):
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "single-device-platform-no-attest")
        r = ev.classify(c)
        self.assertEqual(r["credential_scope"], "single-device")
        self.assertFalse(r["backup_eligible"])
        self.assertFalse(r["currently_backed_up"])

    def test_discoverable_does_not_prove_sync_state(self):
        """Discoverable (passkey UX) does not itself prove BE/BS sync state."""
        cases = json.loads(FIXTURES.read_text())
        disc_single = [c for c in cases if c.get("discoverable") and c.get("be") == 0 and c.get("bs") == 0]
        disc_multi_eligible = [c for c in cases if c.get("discoverable") and c.get("be") == 1 and c.get("bs") == 0]
        disc_backed = [c for c in cases if c.get("discoverable") and c.get("be") == 1 and c.get("bs") == 1]
        self.assertTrue(disc_single, "Need a discoverable single-device fixture")
        self.assertTrue(disc_multi_eligible, "Need a discoverable BE=1 BS=0 fixture (eligible not backed up)")
        self.assertTrue(disc_backed, "Need a discoverable BE=1 BS=1 fixture (currently backed up)")
        for c in disc_single:
            r = ev.classify(c)
            self.assertEqual(r["discoverable"], True)
            self.assertEqual(r["credential_scope"], "single-device")
        for c in disc_multi_eligible:
            r = ev.classify(c)
            self.assertEqual(r["discoverable"], True)
            self.assertFalse(r["currently_backed_up"], "Discoverable BE=1 BS=0 is not proof of currently backed up")
        for c in disc_backed:
            r = ev.classify(c)
            self.assertEqual(r["discoverable"], True)
            self.assertTrue(r["currently_backed_up"])

    def test_platform_does_not_imply_synced(self):
        """Platform authenticator does not automatically mean backup-eligible or currently backed up."""
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "platform-single-device-discoverable")
        r = ev.classify(c)
        self.assertEqual(r["authenticator"], "platform")
        self.assertEqual(r["credential_scope"], "single-device")
        self.assertFalse(r["backup_eligible"])

    def test_roaming_does_not_imply_single_device(self):
        """Roaming authenticator does not automatically mean BE=0; a roaming backup-eligible exists."""
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "roaming-multidevice-not-backed")
        r = ev.classify(c)
        self.assertEqual(r["authenticator"], "roaming")
        self.assertEqual(r["credential_scope"], "multi-device")
        self.assertTrue(r["backup_eligible"])
        self.assertFalse(r["currently_backed_up"], "BE=1 BS=0 alone does not mean currently backed up")

    def test_passkey_includes_device_bound(self):
        """FIDO 'passkey' includes device-bound (discoverable single-device) passkeys."""
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "device-bound-passkey-attested")
        r = ev.classify(c)
        self.assertTrue(r["discoverable"])
        self.assertEqual(r["credential_scope"], "single-device")
        # FIDO would still call this a passkey -- lab shows the term is broader than backup-eligible

    def test_attestation_presence_alone_without_trusted_metadata_does_not_prove_hardware_binding(self):
        """Attestation presence alone, without sufficient trusted metadata/evidence, does not establish hardware binding for these synthetic cases."""
        cases = json.loads(FIXTURES.read_text())
        attested = [c for c in cases if c.get("attestation_format") not in ("none", None)]
        self.assertTrue(attested, "Need at least one attested fixture")
        for c in attested:
            r = ev.classify(c)
            self.assertTrue(r["attestation_present"])
            self.assertFalse(r["hardware_binding_proven"],
                f"{c['id']}: attestation presence alone, without sufficient trusted metadata/evidence, does not establish hardware binding for this synthetic case")
            self.assertIn("sufficient trusted metadata", r["reasons"]["hardware_binding"].lower())

    def test_lack_of_attestation_does_not_prove_synced(self):
        """Lack of attestation does not by itself prove a credential is currently backed up."""
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "single-device-no-attest-lack-does-not-prove-synced")
        r = ev.classify(c)
        self.assertFalse(r["attestation_present"])
        self.assertEqual(r["credential_scope"], "single-device")
        self.assertFalse(r["backup_eligible"])
        self.assertFalse(r["currently_backed_up"])
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
