import unittest
from types import SimpleNamespace

from src.config import AppConfig
from src.hybrid_answer import answer_cpi_rent_bridge_question
from src.schemas import RetrievedContext


def make_context(question: str, topic: str, filename: str, context_block: str) -> RetrievedContext:
    return RetrievedContext(
        question=question,
        retrieved_chunks=[
            SimpleNamespace(
                page_content=context_block,
                metadata={
                    "topic": topic,
                    "filename": filename,
                    "chunk_index": 0,
                },
            )
        ],
        source_labels=[f"[Source 1] {topic}/{filename}#chunk-0"],
        context_block=context_block,
        topic_filter_used=topic,
        retrieval_notes=[f"Topic filter applied: {topic}."],
    )


class BridgeAnswerTests(unittest.TestCase):
    def test_answers_first_bridge_question_with_cpi_and_rent_evidence(self) -> None:
        question = "Can the Oslo and Baerum rental market survey figure be used as Oslo CPI? Why or why not?"

        def stub_retriever(request_question: str, topic_filter: str | None, app_config: AppConfig) -> RetrievedContext:
            self.assertEqual(request_question, question)

            if topic_filter == "cpi":
                return make_context(
                    question,
                    "cpi",
                    "ssb-consumer-price-index-overview.md",
                    "The CPI describes the development in consumer prices and is published at national level only.",
                )

            if topic_filter == "oslo-rent":
                return make_context(
                    question,
                    "oslo-rent",
                    "ssb-rental-market-survey-oslo-baerum-2025.md",
                    "The rental market survey measures rent levels and the sample is also the sample of the monthly rent survey in the CPI.",
                )

            raise AssertionError(f"Unexpected topic filter: {topic_filter}")

        response = answer_cpi_rent_bridge_question(
            question,
            retriever=stub_retriever,
        )

        self.assertEqual(response.status, "answered")
        self.assertIn("should not be treated as Oslo CPI", response.answer)
        self.assertIn("national-level measure", response.answer)
        self.assertIn("monthly rent survey in the CPI", response.answer)
        self.assertEqual(len(response.sources), 2)
        self.assertIn("cpi/ssb-consumer-price-index-overview.md#chunk-0", response.sources[0])
        self.assertIn("oslo-rent/ssb-rental-market-survey-oslo-baerum-2025.md#chunk-0", response.sources[1])


if __name__ == "__main__":
    unittest.main()
