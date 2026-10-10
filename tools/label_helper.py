# tools/label_helper.py
"""
Search the Quran for candidate verses, given a keyword or root.

Usage:
    python label_helper.py search "<keyword>"     # surface + root search
    python label_helper.py show <surah>:<ayah>    # show one verse
    python label_helper.py root "<root>"          # root-only search

Search combines:
  - Surface match on the Quran Simple Clean text
  - Root match via quran_roots.json (uses camel-tools root extraction)

Data sources (all read-only, from the retriever repo):
  D:\\Ahmad-AI\\ahmad_v2\\data\\quran_simple_clean.json
  D:\\Ahmad-AI\\ahmad_v2\\data\\quran_roots.json
  D:\\Ahmad-AI\\ahmad_v2\\lib\\root_extractor.py

Requires:
  camel-tools (installed via requirements.txt in this repo).
"""
import json
import sys
from pathlib import Path

RETRIEVER_ROOT = Path(r"D:\Ahmad-AI\ahmad_v2")
DATA = RETRIEVER_ROOT / "data"
SIMPLE = DATA / "quran_simple_clean.json"
ROOTS = DATA / "quran_roots.json"

sys.path.insert(0, str(RETRIEVER_ROOT / "lib"))
from root_extractor import extract_roots  # noqa: E402


def load_corpus():
    if not SIMPLE.exists():
        print(f"ERROR: {SIMPLE} not found.")
        print("       The retriever repo must exist for the labeling tools.")
        sys.exit(1)
    if not ROOTS.exists():
        print(f"ERROR: {ROOTS} not found.")
        sys.exit(1)
    simple = json.loads(SIMPLE.read_text(encoding="utf-8"))
    roots = json.loads(ROOTS.read_text(encoding="utf-8"))
    # English translations cache (best-effort; may fail offline).
    try:
        from huggingface_hub import hf_hub_download
        p = hf_hub_download(
            "Adanmohh/wahi-quran-retrieval-pairs",
            "corpus.json",
            repo_type="dataset",
        )
        en_data = json.load(open(p, encoding="utf-8"))
        en_by_ref = {v["key"]: v.get("en", "") for v in en_data}
    except Exception:
        en_by_ref = {}
    simple_by_ref = {r["reference"]: r["text"] for r in simple}
    return simple_by_ref, roots, en_by_ref


def search_kw(kw, simple_by_ref, roots, en_by_ref, limit=30):
    hits = {}

    for ref, txt in simple_by_ref.items():
        if kw in txt:
            hits[ref] = "surface"

    try:
        q_roots = extract_roots(kw)
    except Exception:
        q_roots = []

    for ref, rdata in roots.items():
        doc_roots = set(rdata.get("roots", []))
        if q_roots and (set(q_roots) & doc_roots):
            hits.setdefault(ref, "root")

    def sort_key(ref):
        s, a = ref.split(":")
        return (int(s), int(a))

    ordered = sorted(hits.keys(), key=sort_key)[:limit]
    return (
        [(r, simple_by_ref[r], en_by_ref.get(r, ""), hits[r]) for r in ordered],
        q_roots,
    )


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]
    simple_by_ref, roots, en_by_ref = load_corpus()

    if cmd == "search":
        if len(sys.argv) < 3:
            print("usage: search <keyword>")
            return
        kw = sys.argv[2]
        hits, q_roots = search_kw(kw, simple_by_ref, roots, en_by_ref)
        print(f'Query: "{kw}"')
        print(f"Extracted roots: {q_roots}")
        print(f"Found {len(hits)} matches (surface + root):")
        print()
        for ref, ar, en, source in hits:
            print(f"  {ref}  [{source}]")
            print(f"    {ar[:100]}")
            if en:
                print(f"    EN: {en[:130]}")
            print()

    elif cmd == "show":
        if len(sys.argv) < 3:
            print("usage: show <surah>:<ayah>")
            return
        ref = sys.argv[2]
        if ref in simple_by_ref:
            print(f"  {ref}")
            print(f"  AR: {simple_by_ref[ref]}")
            print(f"  EN: {en_by_ref.get(ref, 'n/a')}")
        else:
            print(f"  not found: {ref}")

    elif cmd == "root":
        if len(sys.argv) < 3:
            print("usage: root <root>")
            return
        r = sys.argv[2]
        hits = [ref for ref, rd in roots.items()
                if r in set(rd.get("roots", []))]

        def sort_key(ref):
            s, a = ref.split(":")
            return (int(s), int(a))

        hits = sorted(hits, key=sort_key)[:30]
        print(f'Root "{r}": {len(hits)} verses (showing first 30)')
        for ref in hits:
            print(f"  {ref}  {simple_by_ref[ref][:90]}")

    else:
        print(__doc__)


if __name__ == "__main__":
    main()