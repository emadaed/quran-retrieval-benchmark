# Provenance

Every question in Ahmad-Eval v1 has a documented origin. This file
records the source for each bucket and any relevant caveats.

---

## Summary

| source | count | buckets affected |
|---|---|---|
| Manual hand-labeling | 46 | lexical_ar (15), semantic_ar (2), multi_hop_ar (2), roman_urdu (20), unanswerable_ar (7) |
| `wahi-quran-retrieval-pairs/benchmark` | 22 | cross_lingual_en (20), semantic_ar (2) |
| **Total** | **68** | |

---

## Manual hand-labeling — 46 questions

Labeled by the project author during Day 22 of the Ahmad-AI project
(2026-10-03). Each question was researched and each gold verse was
individually inspected against the canonical Quran DB before inclusion.

**Buckets:** lexical_ar, semantic_ar (partial), multi_hop_ar, roman_urdu,
unanswerable_ar.

**Provenance tag in JSON:** `"source_dataset": "manual"`,
`"source_id": ""`.

**Labeling workflow:**

1. Draft the query.
2. Run `tools/label_helper.py search "<keyword>"` to find candidates.
3. Human review — is the candidate a genuine topical match?
4. Run `tools/label_helper.py show <ref>` to confirm.
5. `tools/add_label.py add <bucket> "<query>" <ref1> ... <refN>`.

**Average time per question:** 5–10 minutes.

---

## `wahi-quran-retrieval-pairs/benchmark` — 22 questions

Source: `Adanmohh/wahi-quran-retrieval-pairs` on HuggingFace.

**Sub-source:** `benchmark.json` split — 26 thematic cases (20 EN, 4 FI,
2 AR).

**Buckets:** all 20 `cross_lingual_en` questions, and 2 `semantic_ar`
questions (the two Arabic-language cases from that split).

**Provenance tag in JSON:** `"source_dataset": "wahi-quran-retrieval-pairs/benchmark"`,
`"source_id": "<original id>"` (e.g. `"patience-en"`, `"repentance-ar"`).

**Caveats:**

- **Provenance is unverified.** The wahi upload has no README, no
  methodology, and no authors listed. We tagged these questions with
  `source_verification: unverified` in the original audit. Treat the
  question prompts as usable; treat the gold verses as we would any
  hand-labeled set — reliable once a human confirmed them, but the
  *original* wahi annotations themselves are not independently
  attested.
- **Audit findings from Day 22:**
  - 0 duplicate query texts in the 26-case benchmark.
  - Healthy gold verse overlap (`2:155` referenced 5× across cases —
    expected, it is the central verse on patience).
  - 17/20 EN queries are natural topic phrasings ("how to be patient",
    "the story of Mary"), not templated.

**Recommendation for Phase A:** do not extend wahi further. For new
cross_lingual_en questions, hand-label them.

---

## Not included but considered

The following sources were audited and rejected (see
`REJECTED_SOURCES.md` for full details):

- `Ereeeeef3/Qu-QA-v3`
- `Emaratilicious/quranqa-parquet`
- `Salama1429/tarteel-ai-QuranQA`
- `Kandil7/Athar-Datasets`

None of these contributed questions to v1.

---

## Reproducing a question's origin

Given a `qid`, its origin is fully determined by the JSON fields:

```python
import json
q = next(x for x in json.load(open("data/ahmad_eval_v1.json"))
         if x["qid"] == "ae_en_004")
print(q["source_dataset"])  # -> "wahi-quran-retrieval-pairs/benchmark"
print(q["source_id"])       # -> "maryam-en"
print(q["notes"])           # -> "thematic query; any gold key counts"
For source_dataset == "manual", no further trace is possible — the
question was drafted and labeled in the same session and is not
recoverable to a pre-existing document.

Every question in this benchmark was human-reviewed before inclusion.
The provenance of each is a matter of record, not reconstruction.