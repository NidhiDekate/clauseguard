# vector_store_pinecone.py
# same idea as vector_store.py but using pinecone instead of chroma, so we can
# actually compare a local vector store against a hosted one - not just take
# it on faith that one is better.
#
# pinecone persists by default (unlike chroma which we rebuild fresh every
# run), so this clears the index before adding fresh chunks each time, or
# results would pile up across runs.
#
# usage: python src/rag/vector_store_pinecone.py

import os
import time

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

from chunking import chunk_fixed_size, chunk_by_clause

load_dotenv()

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384  # this specific model outputs 384-dim vectors, has to match the index

INDEX_NAME = "clauseguard-test"


def get_or_create_index():
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

    if not pc.has_index(INDEX_NAME):
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIM,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        time.sleep(5)  # give pinecone a second to finish spinning it up

    return pc.Index(INDEX_NAME)


def build_vectorstore(chunks, namespace):
    index = get_or_create_index()
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    # clear whatever's already in this namespace so old test runs don't pile up
    try:
        index.delete(delete_all=True, namespace=namespace)
        time.sleep(2)
    except Exception:
        pass  # namespace doesn't exist yet on first run, that's fine

    vectorstore = PineconeVectorStore(index=index, embedding=embeddings, namespace=namespace)
    vectorstore.add_texts(chunks)
    return vectorstore


def query_collection(vectorstore, question, k=1):
    results = vectorstore.similarity_search(question, k=k)
    return [r.page_content for r in results]


if __name__ == "__main__":
    with open("data/sample_docs/pa_lease_sample.txt", encoding="utf-8") as f:
        doc = f.read()

    fixed_chunks = chunk_fixed_size(doc)
    clause_chunks = chunk_by_clause(doc)

    print("uploading to pinecone... (this is the part that's noticeably slower than chroma - it's a network call, not local)")
    fixed_store = build_vectorstore(fixed_chunks, namespace="fixed-size")
    clause_store = build_vectorstore(clause_chunks, namespace="by-clause")

    questions = [
        "does this lease have an early termination fee?",
        "what is the late fee for rent?",
        "how many guests am I allowed to have over?",
    ]

    for q in questions:
        print(f"\n{'=' * 60}")
        print(f"Q: {q}")

        print("\n--- fixed-size top result ---")
        print(query_collection(fixed_store, q)[0][:300])

        print("\n--- by-clause top result ---")
        print(query_collection(clause_store, q)[0][:300])
