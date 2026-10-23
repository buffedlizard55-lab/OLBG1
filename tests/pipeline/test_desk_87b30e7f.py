import unittest

from scripts.s87b30e7f_validate import validate_desk


class TestDesk87b30e7f(unittest.TestCase):
    def test_desk_invariants_and_html_provenance(self) -> None:
        errors = validate_desk()
        self.assertEqual(errors, [], f"Session 87b30e7f validation failed: {errors}")


if __name__ == "__main__":
    unittest.main()
