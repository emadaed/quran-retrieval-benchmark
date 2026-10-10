# Quran Retrieval Benchmark

A public benchmark for verse-level Quranic retrieval.

**Status:** Ahmad-Eval v1 — 68 hand-labeled questions. Phase A (250–300
questions, tafsir-grounded) in progress.

---

## Why this exists

No clean public benchmark for verse-level Quranic retrieval exists. During
the initial audit (see `docs/REJECTED_SOURCES.md`), every candidate dataset
turned out to be the wrong shape — instruction-tuning corpora, extractive
QA on passages, or gated and undocumented. Ahmad-Eval had to be built by hand.

This repository is that benchmark, cleaned up and prepared for public use.

---

## What's in this repository
data/
ahmad_eval_v1.json the 68-question benchmark (v1)
phase_a_drafts.json working file for the Phase A expansion

tools/
label_helper.py search and inspect candidate verses
add_label.py validate and append a labeled question

docs/
SCHEMA.md JSON schema for a question
PROVENANCE.md per-question origin
REJECTED_SOURCES.md audit of datasets we rejected and why
HANDOFF.md brief for the Phase A labeling assistant

LICENSES/
tanzil.md license notes for Tanzil-derived data
wahi.md license notes for wahi-derived questions

text

**Not in this repository:** the canonical Quran database
(`canonical_quran.db`) and the English Tanzil translation
(`en.yusufali.txt`). Both are used by the labeling tools but are kept
out of this repo for size and licensing reasons. See `docs/SCHEMA.md`
for setup instructions.

---

## Benchmarks

Per-bucket baselines are published with each version. For Ahmad-Eval v1,
the best-known baselines (weighted RRF + BGE-reranker-v2-m3) are:

| bucket | n | R@5 |
|---|---|---|
| cross_lingual_en | 20 | 21.2% |
| lexical_ar | 15 | 20.8% |
| multi_hop_ar | 2 | 22.2% |
| semantic_ar | 4 | 6.2% |
| roman_urdu | 20 | 1.1% |
| unanswerable_ar | 7 | n/a |

These numbers are illustrative. They will change; the dataset is the
stable artifact.

---

## Question taxonomy

Six buckets, each testing a different failure mode:

- **lexical_ar** — keyword query in Arabic. Tests root/surface matching.
- **semantic_ar** — thematic query in Arabic. Tests paraphrase matching.
- **multi_hop_ar** — two concepts combined. Tests multi-constraint retrieval.
- **cross_lingual_en** — English query, Arabic gold. Tests cross-lingual.
- **roman_urdu** — Roman-Urdu query, Arabic gold. Low-resource transliteration.
- **unanswerable_ar** — the Quran does not answer. Adversarial by design.

See `docs/SCHEMA.md` for exact bucket definitions and the JSON schema.

---

## How to use

Ahmad-Eval v1 is a JSON file:

```python
import json
questions = json.load(open("data/ahmad_eval_v1.json"))
for q in questions:
    print(q["qid"], q["query"], q["expected_verses"])
Each entry has expected_verses — a list of surah:ayah references. The
benchmark scores retrieval by whether a gold verse appears in the top-k
of the retrieval system's output.