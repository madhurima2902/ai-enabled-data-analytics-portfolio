from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
KNOWLEDGE_DIR = PROJECT_DIR / "knowledge"

def load_knowledge_files():
    documents = []

    for file_path in KNOWLEDGE_DIR.glob("*.md"):
        text = file_path.read_text(encoding="utf-8")
        documents.append(
            {
            "source":file_path.name,
            "content": text
            }
        )

    return documents


def split_into_sections(document):
    text = document["content"]
    # Implement section splitting logic here
    sections = text.split("\n## ")

    chunks = []
    for section in sections:
        if section.strip():
            chunks.append (
                {
                    "source": document["source"],
                    "content": section.strip()
                }
            )

    return chunks


if __name__ == "__main__":
    documents = load_knowledge_files()
    print(f"Loaded {len(documents)} knowledge files:")

    chunks = []

    for document in documents:
        document_chunks = split_into_sections(document)
        chunks.extend(document_chunks)
    print(f"Split into {len(chunks)} chunks")

    for chunk in chunks:
        print(
            chunk["source"],
            "->",
            chunk["content"][:80]

            )
    