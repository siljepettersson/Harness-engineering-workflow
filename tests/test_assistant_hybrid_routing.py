import unittest
from unittest.mock import patch

from src.assistant import answer_question, is_first_oslo_rent_hybrid_question
from src.schemas import AssistantResponse


class AssistantHybridRoutingTests(unittest.TestCase):
    def test_detects_first_oslo_rent_hybrid_question_shape(self) -> None:
        question = (
            "What is the average monthly rent for 2-room dwellings in Oslo and Baerum municipality, "
            "and can it be directly compared across years?"
        )

        self.assertTrue(is_first_oslo_rent_hybrid_question(question))

    def test_does_not_match_general_rent_question(self) -> None:
        question = "What is the average monthly rent for 2-room dwellings in Oslo and Baerum municipality?"

        self.assertFalse(is_first_oslo_rent_hybrid_question(question))

    def test_answer_question_routes_first_hybrid_shape_to_hybrid_path(self) -> None:
        question = (
            "What is the average monthly rent for 2-room dwellings in Oslo and Baerum municipality, "
            "and can it be directly compared across years?"
        )
        expected_response = AssistantResponse(
            question=question,
            status="answered",
            answer="Hybrid answer",
            sources=["[Structured Source] table 09895 2025 2 rooms - Oslo and Baerum municipality"],
        )

        with patch("src.assistant.answer_oslo_rent_hybrid_question", return_value=expected_response) as mocked_hybrid:
            response = answer_question(question)

        mocked_hybrid.assert_called_once()
        self.assertEqual(response, expected_response)


if __name__ == "__main__":
    unittest.main()
