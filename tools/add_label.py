# tools/add_label.py
"""
Add a hand-labeled question to the benchmark's eval file.

Usage:
    python add_label.py <bucket> "<query>" <ref1> <ref2> ...
    python add_label.py unanswerable_ar "<query>"

Examples:
    python add_label.py lexical_ar "الصدقة" 2:263 2:264 2:271
    python add_label.py roman_urdu "namaz kaise padhe" 2:45 20:14
    python add_label.py unanswerable_ar "ما حكم شراء العملات الرقمية؟"

Notes:
    - Writes to the BENCHMARK repo's eval file (this repo).
    - Reads the canonical Quran DB from the retriever repo (read-only).
    - Idempotent: if the same query already exists in the same bucket, skip.
    - Validates each ref exists in the canonical DB.
    - Assigns qid automatically: ae_<bucket>_<N:03d>.

Requires:
    - The retriever repo at D:\\Ahmad-AI\\ahmad_v2 (for canonical_quran.db).
    - No third-party Python packages beyond the standard library.
"""
import json
import sqlite3
import sys
from pathlib import Path

# Where THIS repo writes. Benchmark repo, target file.
ROOT = Path(r"D:\quran-retrieval-benchmark")
EVAL_FILE = ROOT / "data" / "ahmad_eval_v1.json"

# Where the Quran DB lives. Retriever repo, read-only.
RETRIEVER_ROOT = Path(r"D:\Ahmad-AI\ahmad_v2")
DB_PATH = RETRIEVER_ROOT / "data" / "canonical_quran.db"

VALID_BUCKETS = {
    "lexical_ar": "ar",
    "semantic_ar": "ar",
    "multi_hop_ar": "ar",
    "roman_urdu": "ur-roman",
    "unanswerable_ar": "ar",
    "cross_lingual_en": "en",
}


def validate_refs(refs):
    if not DB_PATH.exists():
        print(f"ERROR: canonical DB not found at {DB_PATH}")
        print("       The retriever repo must exist for ref validation.")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    bad = []
    for ref in refs:
        try:
            s, a = ref.split(":")
            s, a = int(s), int(a)
        except Exception:
            bad.append(ref)
            continue
        cur.execute("SELECT 1 FROM verses WHERE surah=? AND ayah=?", (s, a))
        if cur.fetchone() is None:
            bad.append(ref)
    conn.close()
    return bad


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    bucket = sys.argv[1]
    query = sys.argv[2].strip()
    refs = sys.argv[3:] if len(sys.argv) > 3 else []

    if bucket not in VALID_BUCKETS:
        print(f"ERROR: bucket must be one of {list(VALID_BUCKETS.keys())}")
        sys.exit(1)

    if bucket == "unanswerable_ar":
        if refs:
            print(f"ERROR: unanswerable_ar should have no refs; got {refs}")
            sys.exit(1)
        answerable = False
    else:
        if not refs:
            print("ERROR: non-unanswerable bucket needs at least one ref")
            sys.exit(1)
        answerable = True
        bad = validate_refs(refs)
        if bad:
            print(f"ERROR: refs not found in canonical DB: {bad}")
            sys.exit(1)

    if EVAL_FILE.exists():
        data = json.loads(EVAL_FILE.read_text(encoding="utf-8"))
    else:
        data = []

    for q in data:
        if q["bucket"] == bucket and q["query"] == query:
            print(f'SKIP: "{query}" already exists as {q["qid"]}')
            sys.exit(0)

    n = sum(1 for q in data if q["bucket"] == bucket)
    qid = f"ae_{bucket}_{n:03d}"

    entry = {
        "qid": qid,
        "lang": VALID_BUCKETS[bucket],
        "bucket": bucket,
        "query": query,
        "expected_verses": refs,
        "answerable": answerable,
        "source_dataset": "manual",
        "source_id": "",
        "notes": "hand-labeled",
    }

    data.append(entry)
    EVAL_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"ADDED: {qid}")
    print(f"  bucket: {bucket}")
    print(f"  query : {query}")
    print(f"  refs  : {refs}")
    print(f"  wrote : {EVAL_FILE}")


if __name__ == "__main__":
    main()