import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from .config import config
from .query import query


@dataclass(frozen=True)
class RetrievalEvalCase:
    id: str
    question: str
    topic: str | None
    expected_sources: list[str]
    expected_keywords: list[str]
    notes: str


@dataclass(frozen=True)
class RetrievalEvalCaseResult:
    id: str
    question: str
    topic: str | None
    retrieved_sources: list[str]
    expected_sources: list[str]
    expected_keywords: list[str]
    source_hit: bool
    top_1_source_hit: bool
    keyword_hit: bool
    matched_sources: list[str]
    matched_keywords: list[str]


@dataclass(frozen=True)
class RetrievalEvalSummary:
    total_cases: int
    source_hit_rate: float
    top_1_source_hit_rate: float
    keyword_hit_rate: float
    failed_case_ids: list[str]


@dataclass(frozen=True)
class RetrievalEvalDatasetRun:
    dataset_name: str
    case_path: str
    summary: RetrievalEvalSummary
    results: list[RetrievalEvalCaseResult]


def load_retrieval_cases(path: Path) -> list[RetrievalEvalCase]:
    raw_cases = json.loads(path.read_text(encoding="utf-8"))
    return [RetrievalEvalCase(**raw_case) for raw_case in raw_cases]


def extract_retrieved_source_names(retrieved_docs: list) -> list[str]:
    return [doc.metadata["filename"] for doc in retrieved_docs]


def extract_retrieved_text(retrieved_docs: list) -> str:
    return "\n".join(doc.page_content for doc in retrieved_docs).lower()


def evaluate_retrieval_case(case: RetrievalEvalCase, k: int = 4) -> RetrievalEvalCaseResult:
    retrieved_docs = query(
        case.question,
        config.paths.vectorstore_dir,
        config.retrieval.collection_name,
        config.embedding.model_name,
        embedding_device=config.embedding.device,
        normalize_embeddings=config.embedding.normalize_embeddings,
        embedding_batch_size=config.embedding.batch_size,
        max_query_length=config.retrieval.max_query_length,
        k=k,
        topic_filter=case.topic,
    )

    retrieved_sources = extract_retrieved_source_names(retrieved_docs)
    retrieved_text = extract_retrieved_text(retrieved_docs)

    matched_sources = sorted(set(retrieved_sources) & set(case.expected_sources))
    matched_keywords = [
        keyword for keyword in case.expected_keywords if keyword.lower() in retrieved_text
    ]

    top_1_source = retrieved_sources[0] if retrieved_sources else None

    return RetrievalEvalCaseResult(
        id=case.id,
        question=case.question,
        topic=case.topic,
        retrieved_sources=retrieved_sources,
        expected_sources=case.expected_sources,
        expected_keywords=case.expected_keywords,
        source_hit=bool(matched_sources),
        top_1_source_hit=top_1_source in case.expected_sources if top_1_source else False,
        keyword_hit=bool(matched_keywords),
        matched_sources=matched_sources,
        matched_keywords=matched_keywords,
    )


def summarize_results(case_results: list[RetrievalEvalCaseResult]) -> RetrievalEvalSummary:
    total_cases = len(case_results)
    source_hits = sum(result.source_hit for result in case_results)
    top_1_hits = sum(result.top_1_source_hit for result in case_results)
    keyword_hits = sum(result.keyword_hit for result in case_results)
    failed_case_ids = [
        result.id
        for result in case_results
        if not (result.source_hit and result.keyword_hit)
    ]

    return RetrievalEvalSummary(
        total_cases=total_cases,
        source_hit_rate=(source_hits / total_cases) if total_cases else 0.0,
        top_1_source_hit_rate=(top_1_hits / total_cases) if total_cases else 0.0,
        keyword_hit_rate=(keyword_hits / total_cases) if total_cases else 0.0,
        failed_case_ids=failed_case_ids,
    )


def build_eval_report(
    case_results: list[RetrievalEvalCaseResult],
    summary: RetrievalEvalSummary,
    case_path: Path,
) -> dict:
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "case_file": str(case_path),
        "collection_name": config.retrieval.collection_name,
        "embedding_model": config.embedding.model_name,
        "top_k": config.retrieval.top_k,
        "summary": asdict(summary),
        "results": [asdict(result) for result in case_results],
    }


def build_combined_eval_report(dataset_runs: list[RetrievalEvalDatasetRun]) -> dict:
    total_cases = sum(run.summary.total_cases for run in dataset_runs)
    total_source_hits = sum(
        sum(result.source_hit for result in run.results)
        for run in dataset_runs
    )
    total_top_1_hits = sum(
        sum(result.top_1_source_hit for result in run.results)
        for run in dataset_runs
    )
    total_keyword_hits = sum(
        sum(result.keyword_hit for result in run.results)
        for run in dataset_runs
    )
    failed_case_ids = [
        case_id
        for run in dataset_runs
        for case_id in run.summary.failed_case_ids
    ]

    overall_summary = {
        "total_cases": total_cases,
        "source_hit_rate": (total_source_hits / total_cases) if total_cases else 0.0,
        "top_1_source_hit_rate": (total_top_1_hits / total_cases) if total_cases else 0.0,
        "keyword_hit_rate": (total_keyword_hits / total_cases) if total_cases else 0.0,
        "failed_case_ids": failed_case_ids,
    }

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "collection_name": config.retrieval.collection_name,
        "embedding_model": config.embedding.model_name,
        "top_k": config.retrieval.top_k,
        "overall_summary": overall_summary,
        "dataset_runs": [
            {
                "dataset_name": run.dataset_name,
                "case_path": run.case_path,
                "summary": asdict(run.summary),
                "results": [asdict(result) for result in run.results],
            }
            for run in dataset_runs
        ],
    }


def write_eval_report(report: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def run_retrieval_eval(case_path: Path, output_path: Path, k: int = 4) -> dict:
    cases = load_retrieval_cases(case_path)
    case_results = [evaluate_retrieval_case(case, k=k) for case in cases]
    summary = summarize_results(case_results)
    report = build_eval_report(case_results, summary, case_path)
    write_eval_report(report, output_path)
    return report


def run_named_retrieval_eval(dataset_name: str, case_path: Path, k: int = 4) -> RetrievalEvalDatasetRun:
    cases = load_retrieval_cases(case_path)
    case_results = [evaluate_retrieval_case(case, k=k) for case in cases]
    summary = summarize_results(case_results)
    return RetrievalEvalDatasetRun(
        dataset_name=dataset_name,
        case_path=str(case_path),
        summary=summary,
        results=case_results,
    )


def main() -> None:
    case_paths = {
        "oslo-rent": config.paths.project_root / "data" / "evals" / "oslo-rent" / "retrieval_cases.json",
        "cpi": config.paths.project_root / "data" / "evals" / "cpi" / "retrieval_cases.json",
    }
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = (
        config.paths.project_root
        / "artifacts"
        / "eval_runs"
    )
    output_path = output_dir / f"retrieval-eval-{timestamp}.json"
    latest_output_path = output_dir / "retrieval-eval-latest.json"

    dataset_runs = [
        run_named_retrieval_eval(dataset_name, case_path, k=config.retrieval.top_k)
        for dataset_name, case_path in case_paths.items()
    ]
    report = build_combined_eval_report(dataset_runs)
    write_eval_report(report, output_path)
    write_eval_report(report, latest_output_path)

    print(json.dumps(report["overall_summary"], indent=2))
    print("Per dataset:")
    for dataset_run in report["dataset_runs"]:
        print(
            f"- {dataset_run['dataset_name']}: "
            f"source_hit_rate={dataset_run['summary']['source_hit_rate']:.3f}, "
            f"top_1_source_hit_rate={dataset_run['summary']['top_1_source_hit_rate']:.3f}, "
            f"keyword_hit_rate={dataset_run['summary']['keyword_hit_rate']:.3f}"
        )
    print(f"Saved report to {output_path}")
    print(f"Updated latest report at {latest_output_path}")


if __name__ == "__main__":
    main()
