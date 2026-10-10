# tools/validate_qids.py
"""
Read-only validator for the benchmark eval file.

Checks:
  - qid uniqueness
  - qid format is one of the accepted conventions
  - qid prefix matches the bucket field (loosely)
  - lang matches the bucket
  - bucket is one of the six allowed values
  - answerable == (bucket != 'unanswerable_ar')
  - expected_verses: non-empty for answerable, empty for unanswerable
  - ref format (surah:ayah, integers, in-range surah)

Accepted qid formats:
  ae_<bucket>_<NNN>          e.g. ae_lexical_ar_060, ae_roman_urdu_040
  ae_<bucket-with-underscores>_<NNN>
                             e.g. ae_cross_lingual_en_020, ae_multi_hop_ar_000
  ae_en_<NNN>                legacy for cross_lingual_en
  ae_sem_wahi_<NNN>          legacy for semantic_ar (from wahi)

Usage:
    python tools/validate_qids.py
Exit code 0 = all checks pass.
Exit code 1 = at least one problem found.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

EVAL_FILE = Path(r"D:\quran-retrieval-benchmark\data\ahmad_eval_v1.json")

ALLOWED_BUCKETS = {
    "lexical_ar", "semantic_ar", "multi_hop_ar",
    "roman_urdu", "unanswerable_ar", "cross_lingual_en",
}
BUCKET_LANG = {
    "lexical_ar": "ar",
    "semantic_ar": "ar",
    "multi_hop_ar": "ar",
    "roman_urdu": "ur-roman",
    "unanswerable_ar": "ar",
    "cross_lingual_en": "en",
}

# Legacy qid prefixes mapped to the bucket they belong to.
LEGACY_PREFIX = {
    "ae_en": "cross_lingual_en",
    "ae_sem_wahi": "semantic_ar",
    "ae_multi_hop_ar": "multi_hop_ar",
}

QID_RE = re.compile(r"^ae_(.+)_(\d{3,})$")


def qid_bucket(qid: str):
    """Extract the bucket implied by a qid, or None if unparseable."""
    # Legacy prefixes first (longest match wins).
    for prefix in sorted(LEGACY_PREFIX, key=len, reverse=True):
        if qid.startswith(prefix + "_"):
            return LEGACY_PREFIX[prefix]
    # ae_<bucket>_<NNN>
    match = QID_RE.match(qid)
    if not match:
        return None
    return match.group(1)


def main() -> int:
    if not EVAL_FILE.exists():
        print(f"FATAL: {EVAL_FILE} not found.")
        return 1

    data = json.loads(EVAL_FILE.read_text(encoding="utf-8"))
    problems = []

    qid_counts = Counter(q["qid"] for q in data)
    dupes = [(k, v) for k, v in qid_counts.items() if v > 1]
    if dupes:
        problems.append(f"{len(dupes)} duplicate qids:")
        for k, v in sorted(dupes):
            problems.append(f"    {k}  x{v}")

    for i, q in enumerate(data):
        qid = q.get("qid", "<missing>")
        b = q.get("bucket")

        qb = qid_bucket(qid)
        if qb is None:
            problems.append(f"[{i}] {qid}: unparseable qid")
        elif qb != b:
            problems.append(
                f"[{i}] {qid}: qid implies bucket {qb!r}, "
                f"but bucket field is {b!r}"
            )

        if b not in ALLOWED_BUCKETS:
            problems.append(f"[{i}] {qid}: unknown bucket {b!r}")

        expected_lang = BUCKET_LANG.get(b)
        if q.get("lang") != expected_lang:
            problems.append(
                f"[{i}] {qid}: lang {q.get('lang')!r} "
                f"!= expected {expected_lang!r} for bucket {b!r}"
            )

        exp = q.get("answerable")
        if b == "unanswerable_ar":
            if exp is not False:
                problems.append(f"[{i}] {qid}: unanswerable must have answerable=false")
        else:
            if exp is not True:
                problems.append(f"[{i}] {qid}: answerable must be true")

        refs = q.get("expected_verses", [])
        if b == "unanswerable_ar":
            if refs:
                problems.append(f"[{i}] {qid}: unanswerable has refs: {refs}")
        else:
            if not refs:
                problems.append(f"[{i}] {qid}: answerable but no refs")

        for ref in refs:
            if ":" not in ref:
                problems.append(f"[{i}] {qid}: bad ref format {ref!r}")
                continue
            s, a = ref.split(":", 1)
            if not (s.isdigit() and a.isdigit()):
                problems.append(f"[{i}] {qid}: non-integer ref {ref!r}")
                continue
            if not (1 <= int(s) <= 114):
                problems.append(f"[{i}] {qid}: surah out of range in {ref!r}")

    print(f"File: {EVAL_FILE}")
    print(f"Total questions: {len(data)}")
    print(f"Unique qids: {len(qid_counts)}")
    print(f"By bucket: {dict(Counter(q['bucket'] for q in data))}")
    print(f"By lang  : {dict(Counter(q['lang'] for q in data))}")
    print()
    if not problems:
        print("VALIDATION OK")
        return 0

    print(f"PROBLEMS FOUND: {len(problems)}")
    for p in problems[:60]:
        print(p)
    if len(problems) > 60:
        print(f"  ... and {len(problems) - 60} more")
    return 1


if __name__ == "__main__":
    sys.exit(main())