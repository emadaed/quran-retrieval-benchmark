# tools/add_label.py
"""
Add a hand-labeled question to the benchmark's eval file.

Usage:
    python tools\\add_label.py <bucket> "<query>" <ref1> <ref2> ...
    python tools\\add_label.py unanswerable_ar "<query>"

Examples:
    python tools\\add_label.py lexical_ar "الاستغفار" 3:135 71:10 110:3
    python tools\\add_label.py roman_urdu "namaz kaise padhe" 2:45 20:14
    python tools\\add_label.py unanswerable_ar "ما حكم شراء العملات الرقمية؟"

Guarantees:
    - Validates every ref exists in the canonical Quran DB.
    - Refuses if the computed qid already exists (no collisions).
    - Refuses if the same (bucket, query) already exists (dedup).
    - Assigns qid from max(existing NNN in bucket) + 1, not from count.

Writes to: data/ahmad_eval_v1.json (this repo).
Reads (read-only): canonical_quran.db from the retriever repo.
"""
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(r"D:\quran-retrieval-benchmark")
EVAL_FILE = ROOT / "data" / "ahmad_eval_v1.json"

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

# Legacy qid prefixes -> bucket (for max-number computation).
LEGACY_PREFIX = {
    "ae_en": "cross_lingual_en",
    "ae_sem_wahi": "semantic_ar",
    "ae_multi_hop_ar": "multi_hop_ar",
}
QID_RE = re.compile(r"^ae_(.+)_(\d{3,})$")


def qid_bucket(qid: str):
    for prefix in sorted(LEGACY_PREFIX, key=len, reverse=True):
        if qid.startswith(prefix + "_"):
            return LEGACY_PREFIX[prefix]
    m = QID_RE.match(qid)
    return m.group(1) if m else None


def qid_number(qid: str):
    m = re.search(r"_(\d{3,})$", qid)
    return int(m.group(1)) if m else 0


def max_number_for_bucket(data, bucket):
    """Highest NNN currently used for this bucket, across all qid styles."""
    m = 0
    for q in data:
        if qid_bucket(q["qid"]) == bucket:
            m = max(m, qid_number(q["qid"]))
    return m


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

    # Dedup check
    for q in data:
        if q["bucket"] == bucket and q["query"] == query:
            print(f'SKIP: "{query}" already exists as {q["qid"]}')
            sys.exit(0)

    # Compute next qid from max existing number in this bucket
    max_n = max_number_for_bucket(data, bucket)
    next_n = max_n + 1
    qid = f"ae_{bucket}_{next_n:03d}"

    # Collision guard (belt-and-braces; should never trigger after the fix)
    existing_qids = {q["qid"] for q in data}
    guard = 0
    while qid in existing_qids:
        next_n += 1
        qid = f"ae_{bucket}_{next_n:03d}"
        guard += 1
        if guard > 10000:
            print(f"ERROR: could not find free qid in bucket {bucket}")
            sys.exit(1)

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