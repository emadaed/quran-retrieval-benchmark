# tools/fix_roman_urdu_batch1.py
"""
Session 7a review — roman_urdu bucket.

Changes:
  ae_roman_urdu_027 : keep 3:133, 7:43; drop 2:82, 3:185, 7:42
  ae_roman_urdu_028 : keep 2:24, 3:131, 4:14; drop 2:39, 3:116
  ae_roman_urdu_035 : DELETE (query "ilm aur amal" but gold verses
                      only address "amal", no ilm)

All other questions in this bucket reviewed and confirmed correct.

Idempotent. Backup before write.
"""
import json
import shutil
import sys
from pathlib import Path

EVAL_FILE = Path(r"D:\quran-retrieval-benchmark\data\ahmad_eval_v1.json")
BACKUP = EVAL_FILE.with_suffix(".json.ru_batch_bak")

KEEP_REFS = {
    "ae_roman_urdu_027": {"3:133", "7:43"},
    "ae_roman_urdu_028": {"2:24", "3:131", "4:14"},
}
DELETE_QIDS = {"ae_roman_urdu_035"}


def main() -> int:
    apply = "--apply" in sys.argv
    data = json.loads(EVAL_FILE.read_text(encoding="utf-8"))
    before = len(data)
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

    to_delete = [q["qid"] for q in data if q["qid"] in DELETE_QIDS]
    data = [q for q in data if q["qid"] not in DELETE_QIDS]
    for qid in to_delete:
        changes.append(f"deleted {qid}")

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