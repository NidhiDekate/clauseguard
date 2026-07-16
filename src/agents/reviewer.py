# reviewer.py
# checks whether what the retriever found actually addresses the concern
# category it was supposed to, or whether it's just the closest available
# match despite not really being relevant. this is the piece that catches
# exactly the "right of entry -> document title" kind of failure we kept
# running into.
#
# usage: python src/agents/reviewer.py

import json
import re

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

load_dotenv()

MODEL_NAME = "openai/gpt-oss-120b"

RELEVANCE_PROMPT = """You check whether a retrieved clause actually addresses a specific concern category, or whether it's just the closest available match despite not really being relevant.

Concern category: {category}
Retrieved clause: {clause}

Does this clause genuinely address the concern category? Return ONLY valid JSON:
{{"relevant": true or false, "reason": "one sentence explanation"}}

Be strict - a clause that only loosely touches the topic, or is clearly about something else, should be marked false."""


def check_relevance(category, clause_text):
    prompt = ChatPromptTemplate.from_messages([("human", RELEVANCE_PROMPT)])
    model = ChatGroq(model=MODEL_NAME, temperature=0)
    chain = prompt | model

    response = chain.invoke({"category": category, "clause": clause_text})
    content = re.sub(r"<think>.*?</think>", "", response.content.strip(), flags=re.DOTALL).strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"relevance check didn't return valid json, got: {content!r}") from e


if __name__ == "__main__":
    # test against the exact real failure we just saw - "right of entry"
    # matched to the document's title/preamble, obviously not relevant
    category = "landlord right of entry and notice period"
    clause = (
        'SAMPLE RENTAL AGREEMENT (Basic/Beginning)\n'
        'THIS AGREEMENT made this 15th Day of June, 2012, by and between ABC Properties, '
        'herein called "Landlord," and Silvia Mando, herein called "Tenant."'
    )

    result = check_relevance(category, clause)
    print(f"category: {category}")
    print(f"clause: {clause[:80]}...")
    print(f"result: {result}")

    print()

    # and a real, actually-relevant one as a sanity check the reviewer
    # doesn't just reject everything
    category2 = "security deposit terms"
    clause2 = (
        "SECURITY DEPOSIT: Tenants hereby agree to pay a security deposit of $685 "
        "to be refunded upon vacating, returning the keys to the Landlord."
    )
    result2 = check_relevance(category2, clause2)
    print(f"category: {category2}")
    print(f"clause: {clause2[:80]}...")
    print(f"result: {result2}")
