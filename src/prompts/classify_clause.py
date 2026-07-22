
# Runs the clause classifier using the prompt in clause_classifier_v2.txt.

import json
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from groq import RateLimitError
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_groq import ChatGroq

load_dotenv()

SYSTEM_PROMPT_PATH = Path("src/prompts/system_prompts/clause_classifier_v2.txt")
FEW_SHOT_PATH = Path("src/prompts/few_shot_examples/clause_classification_examples.json")

MODEL_NAME = "openai/gpt-oss-120b"  # picked after comparing 3 models, see docs/experiments/02_model_benchmark.md


def _load_system_prompt():
    raw = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    # the prompt has a literal json example in it, which langchain tries to read
    # as a {variable} if we don't escape the braces first. cost me an hour to find.
    return raw.replace("{", "{{").replace("}", "}}")


def _load_few_shot_examples():
    return json.loads(FEW_SHOT_PATH.read_text(encoding="utf-8"))


def build_classifier_chain(model_name):
    system_prompt = _load_system_prompt()
    examples = _load_few_shot_examples()

    example_prompt = ChatPromptTemplate.from_messages([
        ("human", "Clause: {clause}"),
        ("ai", '{{"label": "{label}", "reason": "{reason}"}}'),
    ])

    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )

    final_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        few_shot_prompt,
        ("human", "Clause: {clause}"),
    ])

    # max_retries=0 because the default groq client retries rate limit errors
    # silently with a sleep - which just looks like the script froze. handling
    # it ourselves below so there's actually a message when it happens.
    model = ChatGroq(model=model_name, temperature=0, max_retries=0)
    return final_prompt | model


def classify_clause(clause_text, model_name=MODEL_NAME):
    chain = build_classifier_chain(model_name)

    try:
        response = chain.invoke({"clause": clause_text})
    except RateLimitError as e:
        if "tokens per day" in str(e) or "TPD" in str(e):
            # daily quota, not per-minute - a 20s retry won't help, groq's own
            # message says to wait 10-25+ minutes. just fail this one.
            raise ValueError(f"hit daily token limit, skipping: {e}") from e
        print("\n  [rate limited, waiting 20s before retrying this one]", end=" ", flush=True)
        time.sleep(20)
        response = chain.invoke({"clause": clause_text})  # only retrying once, not looping forever

    content = response.content.strip()

    # gpt-oss on Groq sometimes returns a <think> block before the JSON.
    # Strip it before parsing.
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"model didn't return valid json, got: {content!r}") from e


if __name__ == "__main__":
    # quick manual sanity check, run this file directly to try one clause
    test_clause = (
        "Tenant agrees to pay a $500 fine if smoking is detected, "
        "determined solely at Landlord's discretion."
    )
    print(json.dumps(classify_clause(test_clause), indent=2))
