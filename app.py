import streamlit as st

from src.assistant import answer_question
from src.config import AppConfig, LLMConfig, get_available_llm_choices
from src.schemas import AssistantResponse


TOPIC_OPTIONS = {
    "All topics": None,
    "Oslo rent": "oslo-rent",
    "CPI": "cpi",
}

HYBRID_EXAMPLE_QUESTION = (
    "What is the average monthly rent for 2-room dwellings in Oslo and Baerum municipality, "
    "and can it be directly compared across years?"
)
BRIDGE_EXAMPLE_QUESTION = (
    "Can the Oslo and Baerum rental market survey figure be used as Oslo CPI? Why or why not?"
)

STATUS_LABELS = {
    "answered": "Answered",
    "retrieval_only": "Retrieval only",
    "no_results": "No results",
    "configuration_error": "Configuration error",
    "runtime_error": "Runtime error",
}


def prettify_source_label(source: str) -> str:
    if source.startswith("[Structured Source]"):
        return source

    if source.startswith("[Source ") and "] " in source:
        _, raw_label = source.split("] ", 1)
    else:
        raw_label = source

    document_path = raw_label.split("#", 1)[0]
    filename = document_path.split("/")[-1]
    title = filename.removesuffix(".md").replace("-", " ").strip()

    if title:
        return f"Raw source: {title.title()}"

    return source


def render_sources(sources: list[str]) -> None:
    if not sources:
        st.caption("No sources.")
        return

    seen: set[str] = set()
    for source in sources:
        pretty_source = prettify_source_label(source)
        if pretty_source in seen:
            continue
        seen.add(pretty_source)
        st.markdown(f"- {pretty_source}")


def render_trace(response: AssistantResponse) -> None:
    retrieved_context = response.retrieved_context

    if response.model_name:
        st.text(f"Model: {response.model_name}")

    st.text(f"Status: {STATUS_LABELS.get(response.status, response.status)}")

    if response.error:
        st.text(f"Error: {response.error}")

    if not retrieved_context:
        return

    topic_filter = retrieved_context.topic_filter_used or "None"
    st.text(f"Topic filter: {topic_filter}")

    for note in retrieved_context.retrieval_notes:
        st.text(note)

    if retrieved_context.context_block:
        st.text_area(
            "Retrieved context",
            retrieved_context.context_block,
            height=320,
            disabled=True,
        )


def render_prompt(prompt: str | None) -> None:
    if not prompt:
        st.caption("Prompt not used for this route.")
        return

    st.text_area("Prompt", prompt, height=320, disabled=True)


def render_response(response: AssistantResponse) -> None:
    status_label = STATUS_LABELS.get(response.status, response.status)

    if response.status == "answered":
        st.success(status_label)
    elif response.status == "retrieval_only":
        st.info(status_label)
    elif response.status == "no_results":
        st.warning(status_label)
    elif response.status == "configuration_error":
        st.error(status_label)
    else:
        st.error(status_label)

    st.markdown(response.answer)

    with st.expander("Sources", expanded=bool(response.sources)):
        render_sources(response.sources)

    with st.expander("Retrieval trace"):
        render_trace(response)

    with st.expander("Prompt"):
        render_prompt(response.prompt)


def main() -> None:
    st.set_page_config(page_title="SSB Hybrid Rent and CPI Assistant", page_icon=":material/search:")
    st.title("SSB Hybrid Rent and CPI Assistant")
    st.caption(
        "Current end-to-end paths: Oslo rent hybrid answer over table 09895, and a CPI-rent bridge explanation grounded in both domains."
    )

    with st.sidebar:
        selected_topic_label = st.selectbox("Topic", list(TOPIC_OPTIONS.keys()))
        selected_topic = TOPIC_OPTIONS[selected_topic_label]
        st.caption("Try these end-to-end questions")
        st.code(HYBRID_EXAMPLE_QUESTION, language="text")
        st.code(BRIDGE_EXAMPLE_QUESTION, language="text")
        llm_choices = get_available_llm_choices()
        llm_choice_labels = ["Retrieval only"] + [choice.label for choice in llm_choices]
        selected_llm_label = st.selectbox("LLM provider", llm_choice_labels)
        selected_llm_config = None

        if selected_llm_label != "Retrieval only":
            selected_llm_config = next(
                choice.config for choice in llm_choices if choice.label == selected_llm_label
            )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and "response" in message:
                render_response(message["response"])
            else:
                st.markdown(message["content"])

    question = st.chat_input("Ask about SSB rent or CPI data and documentation")
    if not question:
        return

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching SSB knowledge base..."):
            app_config = AppConfig(
                llm=selected_llm_config
                if selected_llm_config
                else LLMConfig(
                    provider="openai_compatible",
                    model_name="your-llm-model",
                    base_url="",
                    api_key="",
                )
            )
            response = answer_question(
                question,
                topic_filter=selected_topic,
                app_config=app_config,
            )
        render_response(response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response.answer,
            "response": response,
        }
    )


if __name__ == "__main__":
    main()
