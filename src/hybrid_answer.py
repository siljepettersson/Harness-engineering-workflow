from collections.abc import Callable

from .assistant import retrieve_context
from .config import AppConfig, config
from .schemas import AssistantResponse, RetrievedContext
from .structured_query import StructuredRentResult, find_rent_row_by_area


COMPARABILITY_KEYWORDS = (
    "not directly comparable",
    "price level survey",
    "unique sample",
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
    retriever: Callable[[str, str | None, AppConfig], RetrievedContext] = retrieve_context,
) -> AssistantResponse:
    """Answer the first narrow hybrid Oslo-rent question with structured and raw evidence."""
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
