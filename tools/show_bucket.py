# tools/show_bucket.py
"""
Show all questions in a bucket, with gold verses rendered in Arabic.

Optionally write to a file for offline review.

Usage:
    python tools\\show_bucket.py roman_urdu --with-verses --limit 100
    python tools\\show_bucket.py roman_urdu --with-verses --out review.txt
    python tools\\show_bucket.py semantic_ar --with-verses --limit 10 --offset 10
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(r"D:\quran-retrieval-benchmark")
EVAL_FILE = ROOT / "data" / "ahmad_eval_v1.json"

RETRIEVER_ROOT = Path(r"D:\Ahmad-AI\ahmad_v2")
SIMPLE = RETRIEVER_ROOT / "data" / "quran_simple_clean.json"


def load_simple():
    if not SIMPLE.exists():
        return {}
    return {r["reference"]: r["text"] for r in json.loads(
        SIMPLE.read_text(encoding="utf-8"))}


def render(args, data, simple):
    """Return the full text of the review output as a string."""
    subset = [q for q in data if q["bucket"] == args.bucket]
    total = len(subset)
    if args.offset:
        subset = subset[args.offset:]
    if args.limit:
        subset = subset[:args.limit]

    lines = []
    lines.append(f"Bucket: {args.bucket}")
    lines.append(f"Showing {len(subset)} of {total} "
                 f"(offset={args.offset}, limit={args.limit})")
    lines.append("=" * 78)
    lines.append("")

    for i, q in enumerate(subset, 1):
        idx = args.offset + i
        lines.append(f"[{idx}/{total}] {q['qid']}")
        lines.append(f"  query : {q['query']}")
        lines.append(f"  lang  : {q['lang']}")
        lines.append(f"  notes : {q.get('notes', '')}")
        refs = q["expected_verses"]
        if not refs:
            lines.append(f"  refs  : (none — unanswerable)")
        else:
            lines.append(f"  refs  ({len(refs)}):")
            for ref in refs:
                lines.append(f"    - {ref}")
                if args.with_verses:
                    ar = simple.get(ref, "<not found>")
                    lines.append(f"        {ar[:200]}")
        lines.append(f"  VERDICT: ____________________")
        lines.append("")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bucket")
    ap.add_argument("--with-verses", action="store_true",
                    help="show Arabic text of each gold verse")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--out", type=str, default=None,
                    help="write output to this file (default: stdout)")
    args = ap.parse_args()

    data = json.loads(EVAL_FILE.read_text(encoding="utf-8"))
    simple = load_simple()

    text = render(args, data, simple)

    if args.out:
        out_path = Path(args.out)
        out_path.write_text(text, encoding="utf-8")
        print(f"Wrote {out_path} ({len(text)} chars)")
    else:
        print(text)


if __name__ == "__main__":
    main()