import unittest
from pathlib import Path

from research_integrity import run_integrity_audit


class ResearchIntegrityTests(unittest.TestCase):
    def test_audit_exposes_known_blockers_and_verified_controls(self):
        audit = run_integrity_audit(Path("." )).set_index("check_id")
        self.assertEqual(audit.loc["DATA-001", "status"], "PASS")
        self.assertEqual(audit.loc["DATA-002", "status"], "PASS")
        self.assertEqual(audit.loc["DATA-003", "status"], "PASS")
        self.assertEqual(audit.loc["DATA-004", "status"], "PASS")
        self.assertEqual(audit.loc["TIME-001", "status"], "PASS")
        self.assertEqual(audit.loc["TIME-002", "status"], "PASS")
        self.assertEqual(audit.loc["LEAK-001", "status"], "PASS")
        self.assertEqual(audit.loc["LEAK-002", "status"], "PASS")
        self.assertEqual(audit.loc["COST-002", "status"], "PASS")

    def test_every_check_has_evidence_and_requirement(self):
        audit = run_integrity_audit(Path("."))
        self.assertTrue(audit["check_id"].is_unique)
        self.assertFalse(audit[["evidence", "requirement"]].isna().any().any())
        self.assertTrue(audit["status"].isin({"PASS", "FAIL"}).all())


if __name__ == "__main__":
    unittest.main()
