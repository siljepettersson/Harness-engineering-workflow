from .config import AppConfig, config
from .llm import LLMConfigurationError, generate_answer
from .query import query
from .rag_pipeline import build_prompt, format_retrieved_context, format_source_list
from .schemas import AssistantResponse, RetrievedContext


ALL_TOPIC_FILTER_VALUES = {"", "all", "all topics", "alle temaer"}


def normalize_topic_filter(topic_filter: str | None) -> str | None:
    """Normalize UI topic filter values before low-level retrieval."""
    if topic_filter is None:
        return None

    cleaned_filter = topic_filter.strip()
    if cleaned_filter.lower() in ALL_TOPIC_FILTER_VALUES:
        return None

    return cleaned_filter


def retrieve_context(
    question: str,
    topic_filter: str | None = None,
    app_config: AppConfig = config,
) -> RetrievedContext:
    """Retrieve context and return a structured retrieval result."""
    normalized_topic_filter = normalize_topic_filter(topic_filter)
    retrieved_chunks = query(
        question,
        app_config.paths.vectorstore_dir,
        app_config.retrieval.collection_name,
        app_config.embedding.model_name,
        embedding_device=app_config.embedding.device,
        normalize_embeddings=app_config.embedding.normalize_embeddings,
        embedding_batch_size=app_config.embedding.batch_size,
        max_query_length=app_config.retrieval.max_query_length,
        k=app_config.retrieval.top_k,
        topic_filter=normalized_topic_filter,
    )
    source_labels = format_source_list(retrieved_chunks)
    context_block = format_retrieved_context(retrieved_chunks)
    retrieval_notes = [
        f"Retrieved {len(retrieved_chunks)} chunk(s).",
        (
            f"Topic filter applied: {normalized_topic_filter}."
            if normalized_topic_filter
            else "No topic filter applied."
        ),
    ]

    return RetrievedContext(
        question=question,
        retrieved_chunks=retrieved_chunks,
        source_labels=source_labels,
        context_block=context_block,
        topic_filter_used=normalized_topic_filter,
        retrieval_notes=retrieval_notes,
    )


def build_retrieval_only_answer() -> str:
    """Build a fallback answer when retrieval works but no LLM is configured."""
    return (
        "LLM generation is not configured yet, so this is a retrieval-only result.\n\n"
        "Relevant sources were found and the retrieved context is available in the trace."
    )


def answer_question(
    question: str,
    topic_filter: str | None = None,
    app_config: AppConfig = config,
) -> AssistantResponse:
    """Retrieve evidence, build a prompt, and generate an assistant response."""
    try:
        retrieved_context = retrieve_context(
            question,
            topic_filter=topic_filter,
            app_config=app_config,
        )
    except FileNotFoundError as exc:
        return AssistantResponse(
            question=question,
            status="configuration_error",
            answer="The vector store is not ready. Build the index before asking questions.",
            sources=[],
            error=str(exc),
        )
    except ValueError as exc:
        return AssistantResponse(
            question=question,
            status="configuration_error",
            answer="The question or retrieval settings are invalid.",
            sources=[],
            error=str(exc),
        )
    except Exception as exc:
        return AssistantResponse(
            question=question,
            status="runtime_error",
            answer="Retrieval failed before an answer could be generated.",
            sources=[],
            error=str(exc),
        )

    if not retrieved_context.retrieved_chunks:
        return AssistantResponse(
            question=question,
            status="no_results",
            answer="No relevant context was found for this question.",
            sources=[],
            retrieved_context=retrieved_context,
        )

    prompt = build_prompt(question, retrieved_context.context_block)

    try:
        llm_result = generate_answer(prompt, app_config.llm)
    except LLMConfigurationError as exc:
        return AssistantResponse(
            question=question,
            status="retrieval_only",
            answer=build_retrieval_only_answer(),
            sources=retrieved_context.source_labels,
            retrieved_context=retrieved_context,
            prompt=prompt,
            model_name=app_config.llm.model_name,
            error=str(exc),
        )
    except Exception as exc:
        return AssistantResponse(
            question=question,
            status="runtime_error",
            answer="The LLM call failed after retrieval completed.",
            sources=retrieved_context.source_labels,
            retrieved_context=retrieved_context,
            prompt=prompt,
            model_name=app_config.llm.model_name,
            error=str(exc),
        )

    return AssistantResponse(
        question=question,
        status="answered",
        answer=llm_result.answer,
        sources=retrieved_context.source_labels,
        retrieved_context=retrieved_context,
        prompt=prompt,
        model_name=llm_result.model_name,
    )
