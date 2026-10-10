# s04j_label_helper.py
"""
Ahmad-Eval hand-label helper (v2).

Usage:
    python s04j_label_helper.py search "<keyword>"     # surface + root search
    python s04j_label_helper.py show <surah>:<ayah>     # show one verse
    python s04j_label_helper.py root "<root>"           # root-only search

Search combines:
  - Surface match on Simple Clean text
  - Root match via quran_roots.json

Output: prints candidate verses with reference + Arabic + English.
"""
import json
import sys
from pathlib import Path

ROOT = Path(r'D:\Ahmad-AI\ahmad_v2')
DATA = ROOT / 'data'
SIMPLE = DATA / 'quran_simple_clean.json'
ROOTS = DATA / 'quran_roots.json'

sys.path.insert(0, str(ROOT / 'lib'))
from root_extractor import extract_roots  # noqa: E402


def load_corpus():
    simple = json.loads(SIMPLE.read_text(encoding='utf-8'))
    roots = json.loads(ROOTS.read_text(encoding='utf-8'))
    # English translations cache
    try:
        from huggingface_hub import hf_hub_download
        p = hf_hub_download('Adanmohh/wahi-quran-retrieval-pairs',
                            'corpus.json', repo_type='dataset')
        en_data = json.load(open(p, encoding='utf-8'))
        en_by_ref = {v['key']: v.get('en', '') for v in en_data}
    except Exception:
        en_by_ref = {}
    simple_by_ref = {r['reference']: r['text'] for r in simple}
    return simple_by_ref, roots, en_by_ref


def search_kw(kw, simple_by_ref, roots, en_by_ref, limit=30):
    """Surface + root search."""
    hits = {}  # ref -> source

    # Surface match
    for ref, txt in simple_by_ref.items():
        if kw in txt:
            hits[ref] = 'surface'

    # Root match
    try:
        q_roots = extract_roots(kw)
    except Exception as e:
        q_roots = []
    for ref, rdata in roots.items():
        doc_roots = set(rdata.get('roots', []))
        if q_roots and (set(q_roots) & doc_roots):
            hits.setdefault(ref, 'root')

    # Sort by surah:ayah
    def sort_key(ref):
        s, a = ref.split(':')
        return (int(s), int(a))

    ordered = sorted(hits.keys(), key=sort_key)[:limit]
    return [(r, simple_by_ref[r], en_by_ref.get(r, ''), hits[r])
            for r in ordered], q_roots


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]
    simple_by_ref, roots, en_by_ref = load_corpus()

    if cmd == 'search':
        if len(sys.argv) < 3:
            print('usage: search <keyword>')
            return
        kw = sys.argv[2]
        hits, q_roots = search_kw(kw, simple_by_ref, roots, en_by_ref)
        print(f'Query: "{kw}"')
        print(f'Extracted roots: {q_roots}')
        print(f'Found {len(hits)} matches (surface + root):')
        print()
        for ref, ar, en, source in hits:
            print(f'  {ref}  [{source}]')
            print(f'    {ar[:100]}')
            if en:
                print(f'    EN: {en[:130]}')
            print()

    elif cmd == 'show':
        ref = sys.argv[2]
        if ref in simple_by_ref:
            print(f'  {ref}')
            print(f'  AR: {simple_by_ref[ref]}')
            print(f'  EN: {en_by_ref.get(ref, "n/a")}')
        else:
            print(f'  not found: {ref}')

    elif cmd == 'root':
        r = sys.argv[2]
        hits = [ref for ref, rd in roots.items()
                if r in set(rd.get('roots', []))]
        def sort_key(ref):
            s, a = ref.split(':')
            return (int(s), int(a))
        hits = sorted(hits, key=sort_key)[:30]
        print(f'Root "{r}": {len(hits)} verses (showing first 30)')
        for ref in hits:
            print(f'  {ref}  {simple_by_ref[ref][:90]}')

    else:
        print(__doc__)


if __name__ == '__main__':
    main()