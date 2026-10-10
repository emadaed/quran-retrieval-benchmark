# tools/fix_semantic_ar_batch3.py
"""
Session 7a review — semantic_ar batch 3 (questions 21-30).

Change:
  ae_semantic_ar_021 : remove 16:114, keep 14:7, 35:30
  (16:114 is a command to be grateful, not a description of reward.)

All other questions in this batch reviewed and confirmed correct.

Idempotent. Backup before write.
"""
import json
import shutil
import sys
from pathlib import Path

EVAL_FILE = Path(r"D:\quran-retrieval-benchmark\data\ahmad_eval_v1.json")
BACKUP = EVAL_FILE.with_suffix(".json.batch3_bak")

KEEP_REFS = {
    "ae_semantic_ar_021": {"14:7", "35:30"},
}


def main() -> int:
    apply = "--apply" in sys.argv
    data = json.loads(EVAL_FILE.read_text(encoding="utf-8"))
    changes = []

    for q in data:
        if q["qid"] in KEEP_REFS:
            old = list(q["expected_verses"])
            keep = KEEP_REFS[q["qid"]]
            new = [r for r in old if r in keep]
            if old != new:
                removed = [r for r in old if r not in new]
                changes.append(f"{q['qid']}: remove {removed}, keep {new}")
                q["expected_verses"] = new
            else:
                changes.append(f"{q['qid']}: no change needed")

    print(f"File: {EVAL_FILE}")
    print(f"Total questions: {len(data)}")
    print()
    print("Changes:")
    for c in changes:
        print(f"  - {c}")
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