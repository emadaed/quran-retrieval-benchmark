# s04l_add_label.py
"""
Add a hand-labeled question to Ahmad-Eval v1.

Usage:
    python s04l_add_label.py <bucket> "<query>" <ref1> <ref2> ...

Examples:
    python s04l_add_label.py lexical_ar "الصدقة" 2:263 2:264 2:271
    python s04l_add_label.py roman_urdu "namaz kaise padhe" 2:45 20:14
    python s04l_add_label.py unanswerable "ما حكم شراء العملات الرقمية؟"

Notes:
    - Idempotent: if the same query already exists in the same bucket, skip.
    - Validates each ref exists in the canonical DB.
    - Assigns qid automatically.
"""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(r'D:\Ahmad-AI\ahmad_v2')
DATA = ROOT / 'data'
EVAL_DIR = DATA / 'ahmad_eval'
EVAL_FILE = EVAL_DIR / 'ahmad_eval_v1.json'
DB_PATH = DATA / 'canonical_quran.db'

VALID_BUCKETS = {
    'lexical_ar': 'ar',
    'semantic_ar': 'ar',
    'multi_hop_ar': 'ar',
    'roman_urdu': 'ur-roman',
    'unanswerable_ar': 'ar',
    'cross_lingual_en': 'en',
}


def validate_refs(refs):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    bad = []
    for ref in refs:
        s, a = ref.split(':')
        cur.execute('SELECT 1 FROM verses WHERE surah=? AND ayah=?',
                    (int(s), int(a)))
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
        print(f'ERROR: bucket must be one of {list(VALID_BUCKETS.keys())}')
        sys.exit(1)

    # Unanswerable must have empty refs; others must have at least one
    if bucket == 'unanswerable_ar':
        if refs:
            print(f'ERROR: unanswerable bucket should have no refs; got {refs}')
            sys.exit(1)
        answerable = False
    else:
        if not refs:
            print(f'ERROR: non-unanswerable bucket needs at least one ref')
            sys.exit(1)
        answerable = True
        bad = validate_refs(refs)
        if bad:
            print(f'ERROR: refs not found in canonical DB: {bad}')
            sys.exit(1)

    # Load existing
    if EVAL_FILE.exists():
        data = json.loads(EVAL_FILE.read_text(encoding='utf-8'))
    else:
        data = []

    # Dedup check (same bucket + same query)
    for q in data:
        if q['bucket'] == bucket and q['query'] == query:
            print(f'SKIP: "{query}" already exists as {q["qid"]}')
            sys.exit(0)

    # Count existing in bucket to assign qid
    n = sum(1 for q in data if q['bucket'] == bucket)
    qid = f'ae_{bucket}_{n:03d}'

    entry = {
        'qid': qid,
        'lang': VALID_BUCKETS[bucket],
        'bucket': bucket,
        'query': query,
        'expected_verses': refs,
        'answerable': answerable,
        'source_dataset': 'manual',
        'source_id': '',
        'notes': 'hand-labeled',
    }

    data.append(entry)
    EVAL_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=1),
        encoding='utf-8',
    )
    print(f'ADDED: {qid}')
    print(f'  bucket: {bucket}')
    print(f'  query : {query}')
    print(f'  refs  : {refs}')


if __name__ == '__main__':
    main()