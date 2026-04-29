from collections.abc import Callable

from .config import AppConfig, config
from .rag_pipeline import format_retrieved_context, format_source_list
from .schemas import AssistantResponse, RetrievedContext
from .structured_query import StructuredRentResult, find_rent_row_by_area


COMPARABILITY_KEYWORDS = (
    "not directly comparable",
    "price level survey",
    "unique sample",
)
STRUCTURED_FIGURE_KEYWORDS = (
    "oslo and baerum municipality",
    "15,260",
    "4,060",
    "two rooms",
    "2-room",
    "2 rooms",
    "2025",
)


def extract_comparability_warning(retrieved_context: RetrievedContext) -> str:
    """Extract or synthesize the comparability warning from retrieved rent sources."""
    lowered_context = retrieved_context.context_block.lower()

    if "not directly comparable" in lowered_context:
        return (
            "These figures should not be treated as directly comparable across years."
        )

    if "price level survey" in lowered_context and "unique sample" in lowered_context:
        return (
            "These figures should not be treated as a direct time-series because the "
            "rental market survey is a price level survey and each year uses a unique sample."
        )

    return (
        "The retrieved rent sources do not give enough support for a stronger time-series claim, "
        "so the figures should be treated cautiously across years."
    )


def score_hybrid_support_chunk(chunk_text: str) -> int:
    """Score a retrieved chunk for the first narrow hybrid rent path."""
    lowered = chunk_text.lower()
    score = 0

    for keyword in COMPARABILITY_KEYWORDS:
        if keyword in lowered:
            score += 3

    for keyword in STRUCTURED_FIGURE_KEYWORDS:
        if keyword in lowered:
            score += 2

    return score


def trim_retrieved_context_for_hybrid_path(
    retrieved_context: RetrievedContext,
    max_chunks: int = 2,
) -> RetrievedContext:
    """Keep only the most useful retrieved chunks for the first hybrid route."""
    ranked_chunks = sorted(
        retrieved_context.retrieved_chunks,
        key=lambda doc: score_hybrid_support_chunk(doc.page_content),
        reverse=True,
    )
    selected_chunks = ranked_chunks[:max_chunks]
    selected_source_labels = format_source_list(selected_chunks)
    selected_context_block = format_retrieved_context(selected_chunks)

    retrieval_notes = [
        *retrieved_context.retrieval_notes,
        f"Trimmed hybrid support evidence to {len(selected_chunks)} chunk(s).",
    ]

    return RetrievedContext(
        question=retrieved_context.question,
        retrieved_chunks=selected_chunks,
        source_labels=selected_source_labels,
        context_block=selected_context_block,
        topic_filter_used=retrieved_context.topic_filter_used,
        retrieval_notes=retrieval_notes,
    )


def build_oslo_rent_hybrid_answer_text(
    structured_result: StructuredRentResult,
    comparability_warning: str,
) -> str:
    """Build the first narrow hybrid answer from structured and retrieved evidence."""
    return (
        f"The average monthly rent for {structured_result.number_of_rooms} dwellings in "
        f"{structured_result.area_label} is NOK {structured_result.average_monthly_rent_nok:,} "
        f"in {structured_result.year}. The average annual rent per square metre is "
        f"NOK {structured_result.average_annual_rent_per_sqm_nok:,}. "
        f"{comparability_warning}"
    )


def build_structured_source_label(structured_result: StructuredRentResult) -> str:
    """Create a readable source label for the seed structured extract."""
    return (
        f"[Structured Source] table {structured_result.source_table} "
        f"{structured_result.year} {structured_result.number_of_rooms} - {structured_result.area_label}"
    )


def answer_oslo_rent_hybrid_question(
    question: str,
    area_label: str = "Oslo and Baerum municipality",
    app_config: AppConfig = config,
    retriever: Callable[[str, str | None, AppConfig], RetrievedContext] | None = None,
) -> AssistantResponse:
    """Answer the first narrow hybrid Oslo-rent question with structured and raw evidence."""
    if retriever is None:
        from .assistant import retrieve_context

        retriever = retrieve_context

    try:
        structured_result = find_rent_row_by_area(area_label)
    except LookupError as exc:
        return AssistantResponse(
            question=question,
            status="configuration_error",
            answer="The requested area is not available in the current structured rent sample.",
            sources=[],
            error=str(exc),
        )

    try:
        retrieved_context = retriever(
            question,
            topic_filter="oslo-rent",
            app_config=app_config,
        )
    except Exception as exc:
        return AssistantResponse(
            question=question,
            status="runtime_error",
            answer="The structured rent value was found, but the supporting raw-source retrieval failed.",
            sources=[build_structured_source_label(structured_result)],
            error=str(exc),
        )

    if not retrieved_context.retrieved_chunks:
        return AssistantResponse(
            question=question,
            status="no_results",
            answer="The structured rent value was found, but no supporting raw-source context was retrieved.",
            sources=[build_structured_source_label(structured_result)],
            retrieved_context=retrieved_context,
        )

    retrieved_context = trim_retrieved_context_for_hybrid_path(retrieved_context)
    warning = extract_comparability_warning(retrieved_context)
    answer_text = build_oslo_rent_hybrid_answer_text(structured_result, warning)
    sources = [build_structured_source_label(structured_result), *retrieved_context.source_labels]

    return AssistantResponse(
        question=question,
        status="answered",
        answer=answer_text,
        sources=sources,
        retrieved_context=retrieved_context,
    )
