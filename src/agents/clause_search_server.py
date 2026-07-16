# clause_search_server.py
# custom mcp server exposing clause_search as a tool - this is what makes
# ClauseGuard's retrieval an actual mcp tool an agent can call, instead of
# just a python function only this codebase knows about.
#
# install: pip install fastmcp --break-system-packages
# run standalone to sanity check: python src/agents/clause_search_server.py

import hashlib
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "rag"))
from retriever import build_retriever, retrieve_clauses  # noqa: E402

from fastmcp import FastMCP

mcp = FastMCP("clauseguard-retrieval")

# cache retrievers by document hash so we don't re-embed the same document
# on every single query during one document's analysis - the planner will
# likely call this several times per document (once per concern category)
_retriever_cache = {}


def _get_retriever(document_text):
    key = hashlib.sha256(document_text.encode()).hexdigest()
    if key not in _retriever_cache:
        _retriever_cache[key] = build_retriever(document_text)
    return _retriever_cache[key]


@mcp.tool
def clause_search(document_text: str, query: str, k: int = 3) -> list[str]:
    """Search a document for clauses relevant to a query. Returns up to k matching clause texts, most relevant first."""
    retriever = _get_retriever(document_text)
    return retrieve_clauses(retriever, query, k=k)


if __name__ == "__main__":
    mcp.run()
