import unittest
from types import SimpleNamespace

from src.query import rerank_retrieved_docs, score_retrieved_doc


def make_doc(filename: str, content: str) -> SimpleNamespace:
    return SimpleNamespace(
        page_content=content,
        metadata={"filename": filename},
    )


class QueryRankingTests(unittest.TestCase):
    def test_comparability_question_prefers_warning_chunk(self) -> None:
        question = "Can Oslo and Baerum rent figures be directly compared across years?"
        warning_doc = make_doc(
            "ssb-rental-market-survey-annual-overview.md",
            "The rental market survey is a price level survey. Average rent levels are not directly comparable because each year uses a unique sample.",
        )
        generic_doc = make_doc(
            "ssb-rental-market-survey-oslo-baerum-2025.md",
            "Selected figures for 2025 show 15,260 NOK average monthly rent for Oslo and Baerum municipality.",
        )

        reranked = rerank_retrieved_docs(question, [generic_doc, warning_doc])

        self.assertEqual(reranked[0].metadata["filename"], warning_doc.metadata["filename"])

    def test_price_zone_question_prefers_annual_overview(self) -> None:
        question = "Does SSB publish these rent figures by bydel or by price zone?"
        annual_overview = make_doc(
            "ssb-rental-market-survey-annual-overview.md",
            "Table 09897 uses price zones and these are not bydeler.",
        )
        oslo_seed = make_doc(
            "ssb-rental-market-survey-oslo-baerum-2025.md",
            "This page contains official figures for Oslo and Baerum municipality.",
        )

        reranked = rerank_retrieved_docs(question, [oslo_seed, annual_overview])

        self.assertEqual(reranked[0].metadata["filename"], annual_overview.metadata["filename"])

    def test_oslo_rent_value_question_prefers_2025_seed_source(self) -> None:
        question = "What is the average monthly rent for 2-room dwellings in Oslo and Baerum municipality?"
        annual_overview = make_doc(
            "ssb-rental-market-survey-annual-overview.md",
            "The annual page shows selected 2020 figures for two-room dwellings in Oslo and Baerum municipality.",
        )
        oslo_seed = make_doc(
            "ssb-rental-market-survey-oslo-baerum-2025.md",
            "Selected figures for 2025 show 15,260 NOK average monthly rent for Oslo and Baerum municipality.",
        )

        reranked = rerank_retrieved_docs(question, [annual_overview, oslo_seed])

        self.assertEqual(reranked[0].metadata["filename"], oslo_seed.metadata["filename"])

    def test_predicted_monthly_rent_question_scores_method_chunk_higher(self) -> None:
        question = "What is predicted monthly rent in the rental market survey?"
        methodology_doc = make_doc(
            "ssb-rental-market-survey-annual-overview.md",
            "Predicted monthly rents are estimated by a regression model using observed dwelling characteristics.",
        )
        generic_doc = make_doc(
            "ssb-rental-market-survey-oslo-baerum-2025.md",
            "This page contains official figures for Oslo and Baerum municipality.",
        )

        methodology_score = score_retrieved_doc(question, methodology_doc)
        generic_score = score_retrieved_doc(question, generic_doc)

        self.assertGreater(methodology_score[0], generic_score[0])


if __name__ == "__main__":
    unittest.main()
