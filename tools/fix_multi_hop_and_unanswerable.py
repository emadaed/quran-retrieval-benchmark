# tools/fix_multi_hop_and_unanswerable.py
"""
One-time fix script for Session 7a review.

Changes:
  1. ae_multi_hop_ar_000:
       keep refs 2:45, 2:153
       remove refs 2:155, 2:156, 2:157
  2. ae_multi_hop_ar_001:
       no change (keep all 4)
  3. Delete question ae_unanswerable_ar_011 (crypto duplicate of _000)
  4. ae_unanswerable_ar_014 (online shopping):
       no change (keep)

Writes a backup before any modification.
Idempotent: re-running after the fix reports "no change needed".

Usage:
    python tools\\fix_multi_hop_and_unanswerable.py --dry-run   (default)
    python tools\\fix_multi_hop_and_unanswerable.py --apply
"""
import json
import shutil
import sys
from pathlib import Path

EVAL_FILE = Path(r"D:\quran-retrieval-benchmark\data\ahmad_eval_v1.json")
BACKUP = EVAL_FILE.with_suffix(".json.pre_fix_bak")

MULTI_HOP_000_KEEP = {"2:45", "2:153"}
DELETE_QIDS = {"ae_unanswerable_ar_011"}


def main() -> int:
    apply = "--apply" in sys.argv

    data = json.loads(EVAL_FILE.read_text(encoding="utf-8"))
    changes = []

    # --- fix ae_multi_hop_ar_000 ---
    for q in data:
        if q["qid"] == "ae_multi_hop_ar_000":
            old = list(q["expected_verses"])
            new = [r for r in old if r in MULTI_HOP_000_KEEP]
            if old != new:
                removed = [r for r in old if r not in new]
                changes.append(
                    f"ae_multi_hop_ar_000: remove {removed}, keep {new}"
                )
                q["expected_verses"] = new
            else:
                changes.append("ae_multi_hop_ar_000: no change needed")
            break

    # --- delete ae_unanswerable_ar_011 ---
    before = len(data)
    data = [q for q in data if q["qid"] not in DELETE_QIDS]
    removed_count = before - len(data)
    if removed_count:
        changes.append(
            f"deleted {removed_count} question(s): {sorted(DELETE_QIDS)}"
        )
    else:
        changes.append("no questions needed deletion")

    # --- report ---
    print(f"File: {EVAL_FILE}")
    print(f"Questions before: {before}")
    print(f"Questions after : {len(data)}")
    print()
    print("Changes:")
    for c in changes:
        print(f"  - {c}")
    print()

    if not apply:
        print("DRY RUN — no changes written.")
        print("Run with --apply to write.")
        return 0

    shutil.copy2(EVAL_FILE, BACKUP)
    print(f"Backup written: {BACKUP}")

    EVAL_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"Wrote {EVAL_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())