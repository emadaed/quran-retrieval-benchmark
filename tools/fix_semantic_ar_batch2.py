# tools/fix_semantic_ar_batch2.py
"""
Session 7a review — semantic_ar batch 2 (questions 11-20).

Change:
  Delete ae_semantic_ar_014 (duplicate of ae_multi_hop_ar_001).

All other questions in this batch reviewed and confirmed correct.

Idempotent. Backup before write.

Usage:
    python tools\\fix_semantic_ar_batch2.py            # dry-run
    python tools\\fix_semantic_ar_batch2.py --apply
"""
import json
import shutil
import sys
from pathlib import Path

EVAL_FILE = Path(r"D:\quran-retrieval-benchmark\data\ahmad_eval_v1.json")
BACKUP = EVAL_FILE.with_suffix(".json.batch2_bak")

DELETE_QIDS = {"ae_semantic_ar_014"}


def main() -> int:
    apply = "--apply" in sys.argv
    data = json.loads(EVAL_FILE.read_text(encoding="utf-8"))
    before = len(data)

    to_delete = [q["qid"] for q in data if q["qid"] in DELETE_QIDS]
    data = [q for q in data if q["qid"] not in DELETE_QIDS]
    after = len(data)

    print(f"File: {EVAL_FILE}")
    print(f"Questions before: {before}")
    print(f"Questions after : {after}")
    print()
    print("Changes:")
    if to_delete:
        for qid in to_delete:
            print(f"  - deleted {qid}")
    else:
        print("  - no change needed (already deleted)")
    print()

    if not apply:
        print("DRY RUN — no changes written.")
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