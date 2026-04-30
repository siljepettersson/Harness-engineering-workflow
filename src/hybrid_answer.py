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
BRIDGE_CPI_KEYWORDS = (
    "national level only",
    "development in consumer prices",
    "common measure of inflation",
    "not be treated as an oslo-specific rent statistic",
)
BRIDGE_RENT_KEYWORDS = (
    "measure rent levels",
    "oslo and baerum municipality",
    "monthly rent survey in the cpi",
    "rent level survey",
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


def score_bridge_support_chunk(chunk_text: str) -> int:
    """Score a chunk for the CPI-rent bridge explanation path."""
    lowered = chunk_text.lower()
    score = 0

    for keyword in BRIDGE_CPI_KEYWORDS:
        if keyword in lowered:
            score += 3

    for keyword in BRIDGE_RENT_KEYWORDS:
        if keyword in lowered:
            score += 3

    return score


def trim_retrieved_context_for_bridge_path(
    retrieved_context: RetrievedContext,
    max_chunks: int = 2,
) -> RetrievedContext:
    """Keep only the strongest bridge-support chunks."""
    ranked_chunks = sorted(
        retrieved_context.retrieved_chunks,
        key=lambda doc: score_bridge_support_chunk(doc.page_content),
        reverse=True,
    )
    selected_chunks = ranked_chunks[:max_chunks]
    selected_source_labels = format_source_list(selected_chunks)
    selected_context_block = format_retrieved_context(selected_chunks)

    retrieval_notes = [
        *retrieved_context.retrieval_notes,
        f"Trimmed bridge support evidence to {len(selected_chunks)} chunk(s).",
    ]

    return RetrievedContext(
        question=retrieved_context.question,
        retrieved_chunks=selected_chunks,
        source_labels=selected_source_labels,
        context_block=selected_context_block,
        topic_filter_used=retrieved_context.topic_filter_used,
        retrieval_notes=retrieval_notes,
    )


def combine_retrieved_contexts(
    question: str,
    *contexts: RetrievedContext,
) -> RetrievedContext:
    """Combine multiple retrieved contexts into one trace object."""
    combined_chunks = []
    combined_notes: list[str] = []

    for context in contexts:
        combined_chunks.extend(context.retrieved_chunks)
        combined_notes.extend(context.retrieval_notes)

    source_labels = format_source_list(combined_chunks)
    context_block = format_retrieved_context(combined_chunks)

    return RetrievedContext(
        question=question,
        retrieved_chunks=combined_chunks,
        source_labels=source_labels,
        context_block=context_block,
        topic_filter_used=None,
        retrieval_notes=combined_notes,
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


def build_cpi_rent_bridge_answer_text() -> str:
    """Build the first narrow CPI-rent bridge explanation answer."""
    return (
        "No. The Oslo and Baerum rental market survey figure should not be treated as Oslo CPI. "
        "The rental market survey gives a rent-level figure for a published area label, while CPI is a "
        "national-level measure of the development in consumer prices for goods and services purchased "
        "by private households in Norway. The two are related because Statistics Norway says the rental "
        "market survey sample is also the sample of the monthly rent survey in the CPI, but that does "
        "not make the Oslo and Baerum rent figure the same thing as CPI."
    )


def answer_cpi_rent_bridge_question(
    question: str,
    app_config: AppConfig = config,
    retriever: Callable[[str, str | None, AppConfig], RetrievedContext] | None = None,
) -> AssistantResponse:
    """Answer the first narrow CPI-rent bridge explanation question."""
    if retriever is None:
        from .assistant import retrieve_context

        retriever = retrieve_context

    try:
        cpi_context = retriever(question, topic_filter="cpi", app_config=app_config)
        rent_context = retriever(question, topic_filter="oslo-rent", app_config=app_config)
    except Exception as exc:
        return AssistantResponse(
            question=question,
            status="runtime_error",
            answer="Bridge retrieval failed before a CPI-rent explanation could be built.",
            sources=[],
            error=str(exc),
        )

    if not cpi_context.retrieved_chunks or not rent_context.retrieved_chunks:
        combined = combine_retrieved_contexts(question, cpi_context, rent_context)
        return AssistantResponse(
            question=question,
            status="no_results",
            answer="The system could not retrieve enough CPI and rent evidence for this bridge explanation.",
            sources=combined.source_labels,
            retrieved_context=combined,
        )

    combined_context = combine_retrieved_contexts(question, cpi_context, rent_context)
    combined_context = trim_retrieved_context_for_bridge_path(combined_context)

    return AssistantResponse(
        question=question,
        status="answered",
        answer=build_cpi_rent_bridge_answer_text(),
        sources=combined_context.source_labels,
        retrieved_context=combined_context,
    )
