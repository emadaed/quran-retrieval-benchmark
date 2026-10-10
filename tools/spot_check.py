# tools/spot_check.py
"""
Spot-check gold verses: sample N questions, print each query and each
gold verse (Arabic + English), for human review.

Usage:
    python tools\\spot_check.py                     # 10 random, all buckets
    python tools\\spot_check.py --n 20              # 20 random
    python tools\\spot_check.py --bucket lexical_ar # all from one bucket
    python tools\\spot_check.py --seed 42           # reproducible sample

Read-only. Does not modify any file.
"""
import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(r"D:\quran-retrieval-benchmark")
EVAL_FILE = ROOT / "data" / "ahmad_eval_v1.json"

RETRIEVER_ROOT = Path(r"D:\Ahmad-AI\ahmad_v2")
DATA = RETRIEVER_ROOT / "data"
SIMPLE = DATA / "quran_simple_clean.json"


def load_simple():
    if not SIMPLE.exists():
        print(f"ERROR: {SIMPLE} not found.")
        sys.exit(1)
    return {r["reference"]: r["text"] for r in json.loads(
        SIMPLE.read_text(encoding="utf-8"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--bucket", default=None)
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()

    data = json.loads(EVAL_FILE.read_text(encoding="utf-8"))
    if args.bucket:
        data = [q for q in data if q["bucket"] == args.bucket]
        print(f"Filtered to bucket={args.bucket}: {len(data)} questions")
    if args.seed is not None:
        random.seed(args.seed)

    n = min(args.n, len(data))
    sample = random.sample(data, n)

    simple = load_simple()

    print(f"\n{'='*78}")
    print(f"SPOT CHECK — {n} questions")
    print(f"{'='*78}\n")

    for i, q in enumerate(sample, 1):
        print(f"[{i}/{n}] {q['qid']}")
        print(f"  bucket: {q['bucket']}")
        print(f"  query : {q['query']}")
        print(f"  notes : {q.get('notes','')}")
        print(f"  gold verses:")
        for ref in q["expected_verses"]:
            ar = simple.get(ref, "<not found>")
            print(f"    {ref}: {ar[:120]}")
        print()


if __name__ == "__main__":
    main()