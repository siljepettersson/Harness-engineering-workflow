import unittest
from types import SimpleNamespace

from src.config import AppConfig
from src.hybrid_answer import (
    answer_oslo_rent_hybrid_question,
    build_oslo_rent_hybrid_answer_text,
    extract_comparability_warning,
)
from src.schemas import RetrievedContext
from src.structured_query import find_rent_row_by_area


def make_retrieved_context(context_block: str) -> RetrievedContext:
    return RetrievedContext(
        question="dummy",
        retrieved_chunks=[
            SimpleNamespace(
                page_content=context_block,
                metadata={
                    "topic": "oslo-rent",
                    "filename": "example.md",
                    "chunk_index": 0,
                },
            )
        ],
        source_labels=["[Source 1] oslo-rent/example.md#chunk-0"],
        context_block=context_block,
        topic_filter_used="oslo-rent",
        retrieval_notes=["Retrieved 1 chunk(s)."],
    )


class HybridAnswerTests(unittest.TestCase):
    def test_extracts_direct_comparability_warning(self) -> None:
        retrieved_context = make_retrieved_context(
            "Average rent levels from different years are not directly comparable."
        )

        warning = extract_comparability_warning(retrieved_context)

        self.assertIn("not be treated as directly comparable", warning)

    def test_builds_answer_text_from_structured_and_raw_evidence(self) -> None:
        structured_result = find_rent_row_by_area("Oslo and Baerum municipality")

        answer_text = build_oslo_rent_hybrid_answer_text(
            structured_result,
            "These figures should not be treated as directly comparable across years.",
        )

        self.assertIn("Oslo and Baerum municipality", answer_text)
        self.assertIn("NOK 15,260", answer_text)
        self.assertIn("NOK 4,060", answer_text)
        self.assertIn("not be treated as directly comparable across years", answer_text)

    def test_answers_first_hybrid_question_with_structured_and_retrieved_sources(self) -> None:
        def stub_retriever(question: str, topic_filter: str | None, app_config: AppConfig) -> RetrievedContext:
            self.assertEqual(topic_filter, "oslo-rent")
            self.assertIn("directly compared across years", question)
            return make_retrieved_context(
                "The survey is a price level survey and figures are not directly comparable across years."
            )

        response = answer_oslo_rent_hybrid_question(
            "What is the average monthly rent for 2-room dwellings in Oslo and Baerum municipality, and can it be directly compared across years?",
            retriever=stub_retriever,
        )

        self.assertEqual(response.status, "answered")
        self.assertIn("NOK 15,260", response.answer)
        self.assertIn("not be treated as directly comparable across years", response.answer)
        self.assertGreaterEqual(len(response.sources), 2)
        self.assertTrue(response.sources[0].startswith("[Structured Source] table 09895"))


if __name__ == "__main__":
    unittest.main()
