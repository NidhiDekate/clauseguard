# chunking.py
# two ways to split a document into pieces for retrieval - fixed size (dumb,
# generic) vs clause-boundary aware (splits on the numbered sections a lease
# actually has). compare_chunking.py tests which one retrieves better.

import re


def chunk_fixed_size(text, chunk_size=500, overlap=50):
    # the generic approach - just cut the text every N characters, with a
    # little overlap so we don't slice a sentence in half at the boundary.
    # doesn't know or care that this is a legal document.
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start = end - overlap
    return [c for c in chunks if c]  # drop empty ones


def chunk_by_clause(text):
    # leases number their sections differently depending on who wrote the
    # template - some use roman numerals (I. II. III.), some use plain
    # numbers (1. 2. 3.). splitting on only one style meant this silently
    # treated an entire arabic-numbered document as a single chunk - found
    # that the hard way when every retrieval query returned the exact same
    # result on a real document. now matches either style.
    pattern = r"\n(?=(?:[IVXLCDM]+\.|[0-9]+\.)\s)"
    pieces = re.split(pattern, text)
    return [p.strip() for p in pieces if p.strip()]


if __name__ == "__main__":
    # quick manual check - run this file directly to see both strategies
    # side by side on the sample lease
    with open("data/sample_docs/pa_lease_sample.txt", encoding="utf-8") as f:
        doc = f.read()

    fixed = chunk_fixed_size(doc)
    by_clause = chunk_by_clause(doc)

    print(f"fixed-size: {len(fixed)} chunks")
    print(f"by-clause: {len(by_clause)} chunks\n")

    # more useful comparison than "first chunk" - does a real, longer clause
    # (XXXI, the maintenance one) survive intact in each strategy, or does
    # fixed-size cut it apart?
    print("--- fixed-size chunk(s) containing 'XXXI' ---")
    for c in fixed:
        if "XXXI" in c:
            print(c)
            print("---")

    print("\n--- by-clause chunk containing 'XXXI' ---")
    for c in by_clause:
        if c.startswith("XXXI.") or c.startswith("XXXI "):  # exact clause, not XXXII/XXXIII/etc which also start with "XXXI"
            print(c)
            print("---")