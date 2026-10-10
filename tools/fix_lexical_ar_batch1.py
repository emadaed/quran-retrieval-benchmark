# tools/fix_lexical_ar_batch1.py
"""
Session 7a review — lexical_ar bucket.

Change:
  ae_lexical_ar_058 : remove 10:56 (does not contain رحمة or its root)

All other questions reviewed and confirmed correct.

Idempotent. Backup before write.
"""
import json
import shutil
import sys
from pathlib import Path

EVAL_FILE = Path(r"D:\quran-retrieval-benchmark\data\ahmad_eval_v1.json")
BACKUP = EVAL_FILE.with_suffix(".json.lex_batch_bak")

KEEP_REFS = {
    "ae_lexical_ar_058": {"7:56", "29:23", "30:46"},
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