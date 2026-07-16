# vector_store.py
# embeds chunks and stores them so we can actually query "does this lease have
# an early termination fee?" and see what comes back. builds one collection per
# chunking strategy so we can compare which one retrieves better.
#
# usage: python src/rag/vector_store.py

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from chunking import chunk_fixed_size, chunk_by_clause

# free, local, no api key - downloads once (~90mb) then runs on your machine
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def build_collection(chunks, collection_name):
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    # not persisting to disk on purpose - this is for quick experimentation,
    # rebuilding fresh each run avoids duplicate entries piling up
    return Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        collection_name=collection_name,
    )


def query_collection(vectorstore, question, k=3):
    results = vectorstore.similarity_search(question, k=k)
    return [r.page_content for r in results]


if __name__ == "__main__":
    with open("data/sample_docs/pa_lease_sample.txt", encoding="utf-8") as f:
        doc = f.read()

    fixed_chunks = chunk_fixed_size(doc)
    clause_chunks = chunk_by_clause(doc)

    print("building vector stores... (downloads the embedding model first time)")
    fixed_store = build_collection(fixed_chunks, "fixed_size")
    clause_store = build_collection(clause_chunks, "by_clause")

    # real questions someone would actually ask about this lease
    questions = [
        "does this lease have an early termination fee?",
        "what is the late fee for rent?",
        "how many guests am I allowed to have over?",
    ]

    for q in questions:
        print(f"\n{'=' * 60}")
        print(f"Q: {q}")

        print("\n--- fixed-size top result ---")
        print(query_collection(fixed_store, q, k=1)[0][:300])

        print("\n--- by-clause top result ---")
        print(query_collection(clause_store, q, k=1)[0][:300])
