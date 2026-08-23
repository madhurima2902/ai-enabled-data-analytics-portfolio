import string

from knowledge_loader import load_knowledge_files, split_into_sections

def normalize_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    words = text.split()

    stop_words = {
        "what", "is", "the", "a", "an",
        "of", "to", "in", "for", "and"
    }

    return [
        word for word in words if word not in stop_words    
    ]

def detect_knowledge_scope(question):
    question = question.lower()

    if "what is" in question or "definition" in question or "mean" in question:
        return "kpi_definitions.md"

    if "table" in question or "column" in question or "field" in question or "where" in question:
        return "data_dictionary.md"

    if "rule" in question or "handle" in question or "handling" in question:
        return "business_rules.md"

    return None


def score_chunk(question, chunk_text):
    question_words = set(normalize_text(question))
    chunk_words = set(normalize_text(chunk_text))

    matching_words = question_words.intersection(chunk_words)
    return len(matching_words)

def retrieve_chunks(question,top_k = 3):
    documents = load_knowledge_files()
    scope = detect_knowledge_scope(question)
    chunks = []

    for document in documents:
        if scope and document["source"] != scope:
            continue
        document_chunks = split_into_sections(document)
        chunks.extend(document_chunks)

    results = []

    for chunk in chunks:
        score = score_chunk(question, chunk['content'])
        if score > 0:
            results.append(
                {
                    "source": chunk['source'],
                    "content": chunk['content'],
                    "score": score
                }
            )
        results.sort(
                key = lambda result: result['score'],
                reverse=True
        )
    return results[:top_k]

#if __name__ == "__main__":
    question = "What is Transaction Failure Rate?"
    words = normalize_text(question)

    print(words)

#if __name__ == "__main__":
#    question = "What is Transaction Failure Rate?"

#    chunk_text = """
#    Transaction Failure Rate measures the percentage of total
#    transactions that failed during the selected time period.
 #   """

#    score = score_chunk(question, chunk_text)

#    print(f"Score: {score}")

if __name__ == "__main__":

    questions = [
        "What is Transaction Failure Rate?",
        "Where is channel_id stored?",
        "How do we handle duplicate transactions?"
    ]

    for question in questions:
        print("\nQUESTION:", question)

        scope = detect_knowledge_scope(question)
        print("Detected scope:", scope)

        results = retrieve_chunks(question)

        for result in results:
            print(
                "Source:",
                result["source"],
                "| Score:",
                result["score"]
            )
            print("Content:", result["content"][:120])
            print("-" * 50)