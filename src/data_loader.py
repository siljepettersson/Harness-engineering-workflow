from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader


def load_documents(data_dir: Path) -> list:
    """Load markdown documents from a data directory and attach topic metadata."""
    loader = DirectoryLoader(
        str(data_dir),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    docs = loader.load()

    for doc in docs:
        path = Path(doc.metadata["source"])
        relative = path.relative_to(data_dir)
        doc.metadata["topic"] = relative.parts[1] if relative.parts[0] == "text" and len(relative.parts) > 1 else relative.parts[0]
        doc.metadata["filename"] = relative.name

    return docs
