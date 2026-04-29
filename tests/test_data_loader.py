import tempfile
import unittest
from pathlib import Path

from src.data_loader import load_documents, strip_markdown_frontmatter


class StripMarkdownFrontmatterTests(unittest.TestCase):
    def test_strips_yaml_frontmatter_when_present(self) -> None:
        content = (
            "---\n"
            "title: Example\n"
            "topic: oslo-rent\n"
            "---\n"
            "\n"
            "# Heading\n"
            "Body text.\n"
        )

        stripped = strip_markdown_frontmatter(content)

        self.assertEqual(stripped, "# Heading\nBody text.\n")

    def test_leaves_content_without_frontmatter_unchanged(self) -> None:
        content = "# Heading\nBody text.\n"

        self.assertEqual(strip_markdown_frontmatter(content), content)


class LoadDocumentsTests(unittest.TestCase):
    def test_load_documents_skips_readme_and_adds_stable_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            topic_dir = data_dir / "oslo-rent"
            topic_dir.mkdir(parents=True)

            (topic_dir / "README.md").write_text("# Ignore me\n", encoding="utf-8")
            (topic_dir / "sample.md").write_text(
                "---\n"
                "title: Sample\n"
                "---\n"
                "\n"
                "# Rent levels\n"
                "This is a sample raw source.\n",
                encoding="utf-8",
            )

            docs = load_documents(data_dir)

        self.assertEqual(len(docs), 1)
        doc = docs[0]
        self.assertEqual(doc.metadata["topic"], "oslo-rent")
        self.assertEqual(doc.metadata["filename"], "sample.md")
        self.assertNotIn("title: Sample", doc.page_content)
        self.assertTrue(doc.page_content.startswith("# Rent levels"))


if __name__ == "__main__":
    unittest.main()
