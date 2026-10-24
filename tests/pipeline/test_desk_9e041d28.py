import unittest

from scripts.s9e041d28_validate import validate_desk


class TestDesk9e041d28(unittest.TestCase):
    def test_desk_invariants_and_html_provenance(self) -> None:
        errors = validate_desk()
        self.assertEqual(errors, [], f"Session 9e041d28 validation failed: {errors}")


if __name__ == "__main__":
    unittest.main()
