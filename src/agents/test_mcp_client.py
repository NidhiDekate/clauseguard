# test_mcp_client.py
# calls the clause_search mcp tool the same way an agent eventually will -
# no langgraph involved yet, just proving the mcp server itself actually works
#
# usage: python src/agents/test_mcp_client.py

import asyncio

from fastmcp import Client
from clause_search_server import mcp


async def main():
    with open("data/sample_docs/pa_lease_sample.txt", encoding="utf-8") as f:
        doc = f.read()

    # in-process client - connects straight to the mcp object, no separate
    # server process needed for this kind of quick test
    async with Client(mcp) as client:
        result = await client.call_tool(
            "clause_search",
            {
                "document_text": doc,
                "query": "does this lease have an early termination fee?",
                "k": 2,
            },
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
