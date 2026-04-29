import json
import unittest
from pathlib import Path


class CpiEvalCasesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        cls.eval_path = repo_root / "data" / "evals" / "cpi" / "retrieval_cases.json"
        cls.cpi_raw_dir = repo_root / "data" / "raw" / "ssb" / "cpi"
        cls.oslo_rent_raw_dir = repo_root / "data" / "raw" / "ssb" / "oslo-rent"
        cls.cases = json.loads(cls.eval_path.read_text(encoding="utf-8"))

    def test_eval_case_file_contains_expected_number_of_cases(self) -> None:
        self.assertEqual(len(self.cases), 3)

    def test_each_case_has_required_fields(self) -> None:
        required_fields = {
            "id",
            "question",
            "topic",
            "expected_sources",
            "expected_keywords",
            "notes",
        }

        for case in self.cases:
            self.assertTrue(required_fields.issubset(case.keys()), case)
            self.assertTrue(case["question"].strip())
            self.assertTrue(case["expected_sources"])
            self.assertTrue(case["expected_keywords"])

    def test_case_ids_are_unique(self) -> None:
        ids = [case["id"] for case in self.cases]
        self.assertEqual(len(ids), len(set(ids)))

    def test_expected_sources_exist_in_raw_source_directories(self) -> None:
        available_sources = {
            *(path.name for path in self.cpi_raw_dir.glob("*.md")),
            *(path.name for path in self.oslo_rent_raw_dir.glob("*.md")),
        }

        for case in self.cases:
            for expected_source in case["expected_sources"]:
                self.assertIn(expected_source, available_sources)


if __name__ == "__main__":
    unittest.main()
