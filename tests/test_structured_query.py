import unittest

from src.structured_query import (
    StructuredRentResult,
    find_rent_row_by_area,
    get_oslo_rent_09895_sample,
)


class StructuredQueryTests(unittest.TestCase):
    def test_loads_09895_seed_extract(self) -> None:
        sample = get_oslo_rent_09895_sample()

        self.assertEqual(sample["source_table"], "09895")
        self.assertEqual(sample["year"], "2025")
        self.assertEqual(sample["filters"]["number_of_rooms"], "2 rooms")
        self.assertGreaterEqual(len(sample["rows"]), 4)

    def test_returns_exact_oslo_and_baerum_row(self) -> None:
        result = find_rent_row_by_area("Oslo and Baerum municipality")

        self.assertIsInstance(result, StructuredRentResult)
        self.assertEqual(result.source_table, "09895")
        self.assertEqual(result.year, "2025")
        self.assertEqual(result.number_of_rooms, "2 rooms")
        self.assertEqual(result.area_label, "Oslo and Baerum municipality")
        self.assertEqual(result.average_monthly_rent_nok, 15260)
        self.assertEqual(result.average_annual_rent_per_sqm_nok, 4060)

    def test_raises_for_unknown_area_label(self) -> None:
        with self.assertRaises(LookupError):
            find_rent_row_by_area("Frogner")


if __name__ == "__main__":
    unittest.main()
