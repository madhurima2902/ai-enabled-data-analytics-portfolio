import re

try:
    from .knowledge_loader import load_all_chunks
except ImportError:  # Allows: python src/retriever.py
    from knowledge_loader import load_all_chunks


STOP_WORDS = {
    "what", "is", "the", "a", "an", "of", "to", "in", "for", "and",
    "how", "do", "we", "was", "were", "did", "does", "during", "selected",
}


def normalize_text(text: str) -> list[str]:
    """Simple transparent tokenizer used by the lexical demo retriever."""

    words = re.findall(r"[a-z0-9_]+", text.lower())
    return [word for word in words if word not in STOP_WORDS]


def detect_knowledge_scope(question: str) -> list[str]:
    """Narrow retrieval to the most relevant approved knowledge areas."""

    q = question.lower()

    if any(term in q for term in ["table", "column", "field", "schema", "where is", "stored"]):
        return ["data_dictionary.md"]

    if any(term in q for term in [
        "duplicate", "missing channel", "failed transaction with fee", "high-value",
        "high value", "data quality", "dq", "business rule", "handling rule",
    ]):
        return ["business_rules.md"]

    if any(term in q for term in ["why", "concerning", "investigate", "root cause", "interpret"]):
        return ["kpi_definitions.md", "business_rules.md", "investigation_playbook.md"]

    if any(term in q for term in ["what is", "definition", "define", "mean", "formula", "numerator", "denominator"]):
        return ["kpi_definitions.md"]

    return []


def score_chunk(question: str, chunk: dict[str, str]) -> int:
    """Score lexical overlap, with a small bonus for matching the section title."""

    question_words = set(normalize_text(question))
    content_words = set(normalize_text(chunk["content"]))
    title_words = set(normalize_text(chunk.get("section", "")))

    overlap = len(question_words.intersection(content_words))
    title_overlap = len(question_words.intersection(title_words))

    return overlap + (2 * title_overlap)


def retrieve_chunks(
    question: str,
    top_k: int = 3,
    scopes: list[str] | None = None,
) -> list[dict[str, object]]:
    """Return top lexical chunks with explainable source/section/score metadata."""

    allowed_scopes = scopes if scopes is not None else detect_knowledge_scope(question)
    results: list[dict[str, object]] = []

    for chunk in load_all_chunks():
        if allowed_scopes and chunk["source"] not in allowed_scopes:
            continue

        score = score_chunk(question, chunk)
        if score <= 0:
            continue

        results.append(
            {
                "source": chunk["source"],
                "section": chunk["section"],
                "content": chunk["content"],
                "score": score,
            }
        )

    results.sort(key=lambda result: int(result["score"]), reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    questions = [
        "What is Transaction Failure Rate?",
        "Where is channel_id stored?",
        "How do we handle duplicate transactions?",
    ]

    for question in questions:
        print(f"\nQUESTION: {question}")
        print("Scope:", detect_knowledge_scope(question) or "all approved knowledge")
        for result in retrieve_chunks(question):
            print(
                f"{result['source']} -> {result['section']} "
                f"| score={result['score']}"
            )
