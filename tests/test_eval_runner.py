import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src.eval_runner import (
    RetrievalEvalCase,
    RetrievalEvalDatasetRun,
    RetrievalEvalCaseResult,
    build_eval_report,
    build_combined_eval_report,
    evaluate_retrieval_case,
    load_retrieval_cases,
    run_named_retrieval_eval,
    summarize_results,
    write_eval_report,
)


class EvalRunnerTests(unittest.TestCase):
    def test_load_retrieval_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            case_path = Path(tmpdir) / "cases.json"
            case_path.write_text(
                json.dumps(
                    [
                        {
                            "id": "case_1",
                            "question": "What does CPI measure?",
                            "topic": "cpi",
                            "expected_sources": ["ssb-consumer-price-index-overview.md"],
                            "expected_keywords": ["inflation"],
                            "notes": "demo",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            cases = load_retrieval_cases(case_path)

        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0].id, "case_1")
        self.assertEqual(cases[0].topic, "cpi")

    def test_evaluate_retrieval_case_computes_hits(self) -> None:
        case = RetrievalEvalCase(
            id="case_1",
            question="What does CPI measure?",
            topic="cpi",
            expected_sources=["ssb-consumer-price-index-overview.md"],
            expected_keywords=["inflation"],
            notes="demo",
        )

        fake_docs = [
            SimpleNamespace(
                page_content="The CPI is a common measure of inflation.",
                metadata={"filename": "ssb-consumer-price-index-overview.md"},
            )
        ]

        with patch("src.eval_runner.query", return_value=fake_docs):
            result = evaluate_retrieval_case(case, k=4)

        self.assertTrue(result.source_hit)
        self.assertTrue(result.top_1_source_hit)
        self.assertTrue(result.keyword_hit)
        self.assertEqual(result.matched_sources, ["ssb-consumer-price-index-overview.md"])
        self.assertEqual(result.matched_keywords, ["inflation"])

    def test_summarize_results(self) -> None:
        case_results = [
            SimpleNamespace(id="ok_1", source_hit=True, top_1_source_hit=True, keyword_hit=True),
            SimpleNamespace(id="fail_1", source_hit=False, top_1_source_hit=False, keyword_hit=False),
        ]

        summary = summarize_results(case_results)

        self.assertEqual(summary.total_cases, 2)
        self.assertEqual(summary.source_hit_rate, 0.5)
        self.assertEqual(summary.top_1_source_hit_rate, 0.5)
        self.assertEqual(summary.keyword_hit_rate, 0.5)
        self.assertEqual(summary.failed_case_ids, ["fail_1"])

    def test_write_eval_report(self) -> None:
        report = build_eval_report(
            case_results=[],
            summary=summarize_results([]),
            case_path=Path("data/evals/oslo-rent/retrieval_cases.json"),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.json"
            write_eval_report(report, output_path)
            saved_report = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertIn("timestamp", saved_report)
        self.assertIn("summary", saved_report)
        self.assertIn("results", saved_report)

    def test_build_combined_eval_report(self) -> None:
        dataset_runs = [
            RetrievalEvalDatasetRun(
                dataset_name="oslo-rent",
                case_path="data/evals/oslo-rent/retrieval_cases.json",
                summary=summarize_results(
                    [SimpleNamespace(id="ok_1", source_hit=True, top_1_source_hit=True, keyword_hit=True)]
                ),
                results=[
                    RetrievalEvalCaseResult(
                        id="ok_1",
                        question="Q1",
                        topic="oslo-rent",
                        retrieved_sources=["a.md"],
                        expected_sources=["a.md"],
                        expected_keywords=["x"],
                        source_hit=True,
                        top_1_source_hit=True,
                        keyword_hit=True,
                        matched_sources=["a.md"],
                        matched_keywords=["x"],
                    )
                ],
            ),
            RetrievalEvalDatasetRun(
                dataset_name="cpi",
                case_path="data/evals/cpi/retrieval_cases.json",
                summary=summarize_results(
                    [SimpleNamespace(id="fail_1", source_hit=False, top_1_source_hit=False, keyword_hit=False)]
                ),
                results=[
                    RetrievalEvalCaseResult(
                        id="fail_1",
                        question="Q2",
                        topic="cpi",
                        retrieved_sources=["b.md"],
                        expected_sources=["c.md"],
                        expected_keywords=["y"],
                        source_hit=False,
                        top_1_source_hit=False,
                        keyword_hit=False,
                        matched_sources=[],
                        matched_keywords=[],
                    )
                ],
            ),
        ]

        report = build_combined_eval_report(dataset_runs)

        self.assertEqual(report["overall_summary"]["total_cases"], 2)
        self.assertEqual(report["overall_summary"]["source_hit_rate"], 0.5)
        self.assertEqual(report["overall_summary"]["top_1_source_hit_rate"], 0.5)
        self.assertEqual(report["overall_summary"]["keyword_hit_rate"], 0.5)
        self.assertEqual(report["overall_summary"]["failed_case_ids"], ["fail_1"])
        self.assertEqual(len(report["dataset_runs"]), 2)

    def test_run_named_retrieval_eval(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            case_path = Path(tmpdir) / "cases.json"
            case_path.write_text(
                json.dumps(
                    [
                        {
                            "id": "case_1",
                            "question": "What does CPI measure?",
                            "topic": "cpi",
                            "expected_sources": ["ssb-consumer-price-index-overview.md"],
                            "expected_keywords": ["inflation"],
                            "notes": "demo",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            fake_docs = [
                SimpleNamespace(
                    page_content="The CPI is a common measure of inflation.",
                    metadata={"filename": "ssb-consumer-price-index-overview.md"},
                )
            ]

            with patch("src.eval_runner.query", return_value=fake_docs):
                dataset_run = run_named_retrieval_eval("cpi", case_path, k=4)

        self.assertEqual(dataset_run.dataset_name, "cpi")
        self.assertEqual(dataset_run.summary.total_cases, 1)
        self.assertEqual(dataset_run.summary.source_hit_rate, 1.0)


if __name__ == "__main__":
    unittest.main()
