from pathlib import Path
import re

from langchain_community.document_loaders import DirectoryLoader, TextLoader


FRONTMATTER_PATTERN = re.compile(r"\A---\n.*?\n---\n+", re.DOTALL)


def strip_markdown_frontmatter(content: str) -> str:
    """Remove leading YAML frontmatter from markdown content when present."""
    return FRONTMATTER_PATTERN.sub("", content, count=1)


def load_documents(data_dir: Path) -> list:
    """Load curated markdown documents and attach stable metadata."""
    loader = DirectoryLoader(
        str(data_dir),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    docs = [doc for doc in loader.load() if Path(doc.metadata["source"]).name.lower() != "readme.md"]

    for doc in docs:
        path = Path(doc.metadata["source"])
        relative = path.relative_to(data_dir)
        doc.page_content = strip_markdown_frontmatter(doc.page_content).strip()
        doc.metadata["topic"] = relative.parts[0]
        doc.metadata["filename"] = relative.name

    return docs
