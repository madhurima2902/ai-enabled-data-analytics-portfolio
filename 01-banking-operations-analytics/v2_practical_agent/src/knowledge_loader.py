import re
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = PROJECT_DIR / "knowledge"


def load_knowledge_files() -> list[dict[str, str]]:
    """Load approved markdown knowledge files."""

    documents: list[dict[str, str]] = []

    for file_path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        documents.append(
            {
                "source": file_path.name,
                "content": file_path.read_text(encoding="utf-8"),
            }
        )

    return documents


def split_into_sections(document: dict[str, str]) -> list[dict[str, str]]:
    """Split a markdown document at level-two headings.

    Each chunk keeps its source and section title so retrieval results are
    explainable in the interview demo.
    """

    text = document["content"].strip()
    sections = re.split(r"\n(?=##\s+)", text)
    chunks: list[dict[str, str]] = []

    for index, section in enumerate(sections, start=1):
        cleaned = section.strip()
        if not cleaned:
            continue

        first_line = cleaned.splitlines()[0].strip()
        section_title = re.sub(r"^#+\s*", "", first_line)

        chunks.append(
            {
                "source": document["source"],
                "section": section_title or f"section-{index}",
                "content": cleaned,
            }
        )

    return chunks


def load_all_chunks() -> list[dict[str, str]]:
    chunks: list[dict[str, str]] = []
    for document in load_knowledge_files():
        chunks.extend(split_into_sections(document))
    return chunks


if __name__ == "__main__":
    documents = load_knowledge_files()
    chunks = load_all_chunks()

    print(f"Loaded {len(documents)} knowledge files")
    print(f"Created {len(chunks)} chunks")

    for chunk in chunks:
        print(f"{chunk['source']} -> {chunk['section']}")
