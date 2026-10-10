# tools/repair_duplicate_qids.py
"""
One-time repair: renumber later occurrences of duplicate qids.

Rule:
  - Walk the file in order.
  - Track qids seen so far.
  - When a qid has already been seen, renumber THIS occurrence to the
    next free number in its bucket (max + 1).
  - The first occurrence of each qid is never changed.

Writes a .bak backup before touching the file.

Usage:
    python tools/repair_duplicate_qids.py            # dry-run (default)
    python tools/repair_duplicate_qids.py --apply    # write changes
"""
import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

EVAL_FILE = Path(r"D:\quran-retrieval-benchmark\data\ahmad_eval_v1.json")
BACKUP = EVAL_FILE.with_suffix(".json.bak")

QID_RE = re.compile(r"^ae_(.+)_(\d{3,})$")


def bucket_max_number(data, bucket):
    """Highest NNN currently used in ae_<bucket>_<NNN>."""
    m = 0
    for q in data:
        match = QID_RE.match(q["qid"])
        if not match:
            continue
        b, n = match.group(1), int(match.group(2))
        if b == bucket:
            m = max(m, n)
    return m


def main() -> int:
    apply = "--apply" in sys.argv

    if not EVAL_FILE.exists():
        print(f"FATAL: {EVAL_FILE} not found.")
        return 1

    data = json.loads(EVAL_FILE.read_text(encoding="utf-8"))
    original = json.loads(EVAL_FILE.read_text(encoding="utf-8"))

    # Track used qids and the max per bucket (recomputed after each renumber)
    seen = set()
    bucket_max = defaultdict(int)
    for q in data:
        match = QID_RE.match(q["qid"])
        if match:
            b, n = match.group(1), int(match.group(2))
            bucket_max[b] = max(bucket_max[b], n)

    changes = []
    for i, q in enumerate(data):
        qid = q["qid"]
        if qid not in seen:
            seen.add(qid)
            continue

        # Duplicate — renumber
        match = QID_RE.match(qid)
        if not match:
            print(f"[{i}] cannot renumber malformed qid {qid!r}; skipping")
            continue
        bucket = match.group(1)
        new_num = bucket_max[bucket] + 1
        new_qid = f"ae_{bucket}_{new_num:03d}"
        while new_qid in seen:
            new_num += 1
            new_qid = f"ae_{bucket}_{new_num:03d}"

        changes.append((i, qid, new_qid, q.get("query", "")[:40]))
        q["qid"] = new_qid
        seen.add(new_qid)
        bucket_max[bucket] = new_num

    # Report
    print(f"File: {EVAL_FILE}")
    print(f"Total questions: {len(data)}")
    print(f"Renumbered: {len(changes)}")
    print()
    for i, old, new, qtext in changes:
        print(f"  [{i:3d}] {old}  ->  {new}   ({qtext})")

    if not changes:
        print("Nothing to change.")
        return 0

    # Sanity: no duplicate qids should remain
    from collections import Counter
    c = Counter(q["qid"] for q in data)
    remaining_dupes = [(k, v) for k, v in c.items() if v > 1]
    if remaining_dupes:
        print(f"\nWARN: {len(remaining_dupes)} duplicates remain after renumber")
        for k, v in remaining_dupes:
            print(f"  {k}  x{v}")
        return 1

    if not apply:
        print("\nDRY RUN — no changes written.")
        print("Run with --apply to write.")
        return 0

    # Backup then write
    shutil.copy2(EVAL_FILE, BACKUP)
    print(f"\nBackup written: {BACKUP}")

    EVAL_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"Wrote {EVAL_FILE}")
    print(f"Questions after repair: {len(data)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())