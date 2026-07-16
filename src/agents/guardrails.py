# guardrails.py
# input validation and a call budget - so a bad document or an
# unexpectedly large category list doesn't just run wild. imported into
# graph.py, not meant to run standalone as the main thing, but has a quick
# test at the bottom.

MAX_DOCUMENT_CHARS = 50_000  # roughly 15-20 dense pages - past this, needs real pagination, not supported yet
MIN_DOCUMENT_CHARS = 50  # basically empty, nothing worth analyzing

MAX_CATEGORIES = 15  # a reasonable planner shouldn't need more than this per document
# each category costs roughly: 1 retriever call + 1 reviewer call + maybe 1
# calculator call + maybe 1 classifier call. 15 categories * ~4 calls is
# already 60 real api calls for one document - that's the ceiling worth
# protecting against, not the current 8-category planner which is nowhere
# close to it


class DocumentValidationError(Exception):
    pass


class CallBudgetError(Exception):
    pass


def validate_document(text):
    if not text or len(text.strip()) < MIN_DOCUMENT_CHARS:
        raise DocumentValidationError("Document is empty or too short to analyze meaningfully.")

    if len(text) > MAX_DOCUMENT_CHARS:
        raise DocumentValidationError(
            f"Document is {len(text)} characters, over the {MAX_DOCUMENT_CHARS} limit. "
            "Longer documents need chunked/paginated analysis - not supported yet."
        )


def check_call_budget(categories):
    if len(categories) > MAX_CATEGORIES:
        raise CallBudgetError(
            f"Planner produced {len(categories)} categories, over the {MAX_CATEGORIES} limit. "
            "Refusing to run - this would mean too many real API calls for one document."
        )


if __name__ == "__main__":
    # quick manual checks - both should raise, proving the guardrails actually work
    try:
        validate_document("")
    except DocumentValidationError as e:
        print(f"empty doc correctly rejected: {e}")

    try:
        validate_document("x" * 60_000)
    except DocumentValidationError as e:
        print(f"oversized doc correctly rejected: {e}")

    try:
        check_call_budget([f"category {i}" for i in range(20)])
    except CallBudgetError as e:
        print(f"too many categories correctly rejected: {e}")

    # and a normal case that should NOT raise
    validate_document("A real lease document with enough content to actually analyze." * 5)
    check_call_budget(["category 1", "category 2"])
    print("normal-sized inputs correctly passed through")
