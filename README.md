# Ahmad-Eval v1

**A 232-question hand-reviewed benchmark for verse-level Quranic retrieval.**

[![License: CC-BY-4.0](https://img.shields.io/badge/License-CC--BY--4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97_Dataset-ahmad1979%2Fahmad-eval--v1-yellow)](https://huggingface.co/datasets/ahmad1979/ahmad-eval-v1)
[![Questions](https://img.shields.io/badge/Questions-232-blue)]()
[![Buckets](https://img.shields.io/badge/Buckets-6-blue)]()

---

## What this is

Ahmad-Eval v1 is a **232-question evaluation benchmark** for retrieval and abstention systems built on the Quran. It is not a fiqh dataset, and it is not a fatwa service. It is a measurement instrument.

Queries are in Modern Standard Arabic, English, and Romanized Urdu. Gold verse references are always to the Arabic Quran (6,236 verses, Uthmani script), and every gold verse set was human-reviewed before inclusion.

The benchmark is published on Hugging Face with the reference pipeline's measured results — including the parts where it fails. Anyone using this benchmark as a baseline sees both the benchmark and the honest record of what a reference system did on it.

**Hugging Face:** [ahmad1979/ahmad-eval-v1](https://huggingface.co/datasets/ahmad1979/ahmad-eval-v1)

---

## Status

**Ahmad-Eval v1 — published.** 232 questions across six buckets. CC-BY-4.0. Live on Hugging Face.

**Phase A expansion** (target: 250–300 questions with tafsir-grounded items) is future work, not in progress. The current published state is complete and self-contained.

---

## Why this exists

No clean public benchmark for verse-level Quranic retrieval existed when this project began. During the initial audit (see [`docs/REJECTED_SOURCES.md`](docs/REJECTED_SOURCES.md)), every candidate dataset turned out to be the wrong shape — instruction-tuning corpora, extractive QA on passages rather than passage retrieval, thematic benchmarks without verse-level gold, or gated and undocumented repositories. Six sources were audited; four were rejected.

Ahmad-Eval was built by hand. Every question, every gold verse reference, verified against the canonical Quranic text.

---

## Composition

**Total: 232 questions.**

By bucket:

| Bucket | n | Language | What it tests |
|---|---|---|---|
| `lexical_ar` | 66 | `ar` | Root or surface keyword matching |
| `cross_lingual_en` | 46 | `en` | Cross-lingual retrieval from English to Arabic |
| `roman_urdu` | 45 | `ur-roman` | Low-resource transliteration retrieval |
| `semantic_ar` | 45 | `ar` | Paraphrase and thematic matching |
| `unanswerable_ar` | 22 | `ar` | Correct abstention (out-of-corpus questions) |
| `multi_hop_ar` | 8 | `ar` | Compound queries combining two concepts |

By source:

| `source_dataset` | n | Provenance |
|---|---|---|
| `manual` | 174 | Hand-labeled in this project, Sessions 6–7 |
| `synthetic_gemini_v2` | 36 | Contributed by an external model, hand-reviewed, frozen before evaluation (Session 7k) |
| `wahi-quran-retrieval-pairs/benchmark` | 22 | Adapted from the wahi dataset (unverified provenance; see `LICENSES/wahi.md`) |

The **36 `synthetic_gemini_v2` questions** are the "fresh" evaluation set — they were not present when the reference pipeline's retrieval stack was tuned. The 174 `manual` questions are the "calibration" set.

---

## What's in this repository
data/
ahmad_eval_v1.json the 232-question benchmark (v1)

tools/
add_label.py validate and append a labeled question
label_helper.py search and inspect candidate verses
validate_qids.py structural validator (uniqueness, format)
show_bucket.py browse a bucket for review
spot_check.py sample questions for spot-review
repair_duplicate_qids.py one-time qid repair script (Session 7a)
fix_*.py one-time review-repair scripts (Sessions 7a–7c)
import_batch.py batch-import draft questions

docs/
SCHEMA.md JSON schema, bucket definitions
PROVENANCE.md per-question origin
REJECTED_SOURCES.md audit of six candidate datasets, four rejections
REVIEW_NOTES.md patterns discovered during the gold-verse review
WORKFLOW.md labeling assistant protocol
HANDOFF.md brief for the labeling assistant

LICENSES/
tanzil.md Tanzil license notes
wahi.md wahi license notes

requirements.txt tooling dependencies (camel-tools, huggingface-hub)
LICENSE CC-BY-4.0 for our contributions


**Not in this repository:** the canonical Quran database (`canonical_quran.db`) and the English Tanzil translation (`en.yusufali.txt`). Both are used by the labeling tools but are kept out of this repo for size and licensing reasons. See `docs/SCHEMA.md` for setup instructions.

---

## Question taxonomy

Six buckets, each testing a distinct failure mode:

- **`lexical_ar`** — short Arabic keyword query (e.g., `الصدقة`). Tests root or surface-form matching. Gold verses contain the query's root.
- **`semantic_ar`** — thematic Arabic query (e.g., `الشدة والفرج`). Tests paraphrase matching. Gold verses may share no words with the query.
- **`multi_hop_ar`** — two concepts combined (e.g., `الصبر والصلاة`). Tests multi-constraint retrieval. Gold verses satisfy both concepts.
- **`cross_lingual_en`** — English query, Arabic gold (e.g., `the prohibition of usury and interest`). Tests cross-lingual retrieval.
- **`roman_urdu`** — Roman-Urdu query, Arabic gold (e.g., `namaz kaise padhe`). Tests low-resource transliteration.
- **`unanswerable_ar`** — the Quran does not address the question. Two subtypes: (a) fully off-topic, (b) topic appears but the ruling does not. Adversarial by design.

See [`docs/SCHEMA.md`](docs/SCHEMA.md) for exact bucket definitions, the JSON schema, and validation rules.

---

### How to use

Ahmad-Eval v1 is a JSON file:

```python
import json
questions = json.load(open("data/ahmad_eval_v1.json"))
for q in questions:
    print(q["qid"], q["query"], q["expected_verses"])

Each entry is an object with these fields:

Field	Type	Description
qid	string	Unique question identifier
lang	string	ar, en, or ur-roman
bucket	string	One of the six bucket names
query	string	Question text in the stated language
expected_verses	array	Gold verse refs in S:A format; empty for unanswerable_ar
answerable	bool	false iff bucket == "unanswerable_ar"
source_dataset	string	Provenance identifier
source_id	string	Original ID within source, "" for manual
notes	string	Labeling notes and adversarial properties
```

###Scoring
The benchmark scores retrieval by whether a gold verse appears in the top-k of the retrieval system's output. **Two metrics matter, and they measure different things:**

R@5 — per-gold-verse recall. If a question has 4 gold verses and 1 appears in the top 5, that question contributes 25% to R@5.

hit@5 — per-question hit. If any gold verse appears in the top 5, the question scores 100%.

Report both. **R@5 alone understates retrieval quality because the gold sets are narrow** (see Limitation 1 below). hit@5 is closer to what a user experiences.

###Splits
**test split** — all 232 questions. There is no train split. Training on this data contaminates every future evaluation on this benchmark.

**calibration (196 questions):** filter source_dataset == "manual" OR source_dataset == "wahi-quran-retrieval-pairs/benchmark". This is the set the reference pipeline was tuned against.

**fresh (36 questions):** filter source_dataset == "synthetic_gemini_v2". This is the held-out set for generalization testing.

##Reference pipeline results
The reference pipeline (retrieval + verifier + two-layer scope-routing gate) was run end-to-end on this benchmark in Sessions 7h–7k. The full analysis — including the failure-mode decomposition and the pre-registered pass-rule verdict — is in pipeline_results.md on Hugging Face.

###Short version:

**196 calibration questions (n=180 answerable):**

Outcome	Count
Verified (gold citation confirmed)	32
Abstained (gate fired)	33
Wrong (cited off-gold verse)	115
**16/16 out-of-scope questions correctly abstained; 0 false answers.**

**36 fresh questions (n=30 answerable):**

Outcome	Count
Verified	3
Abstained	17
Wrong	10

**4/6 out-of-scope correctly abstained; 2 false answers.**

The fresh-set numbers are the publishable result. They fail the pre-registered thresholds the reference pipeline committed to before running: out-of-scope false-answer rate at 2/6 exceeded the ≤ 1/6 threshold, and the 95% Wilson lower bound on the verified rate at 3/30 was 3.5%, well below the ≥ 10% threshold.

The dominant failure is that the reference pipeline's scope-routing gate over-fires on the fresh set's prose-like phrasing — 17 of 30 answerable fresh questions were gated out before reaching the retriever. This is a configuration failure in the gate's classification prompt, not a structural limit of the architecture. The retrieval, verifier, and gate all work; the prompt that drives the gate's classifier was tuned against the calibration set's phrasing and does not generalize.

###Known limitations
The dataset card on Hugging Face documents four limitations. Summarized here:

**The gold sets are narrow.**  expected_verses is *a* set of valid verses, not the set. A retrieval system returning a valid verse not in expected_verses scores as "wrong" by strict R@5, even though the verse is a valid answer. A hand review of 15 sampled failures found 13 of 15 (87%) returned at least one clearly-or-plausibly relevant verse. Report hit@5 and R@5 together.

**unanswerable_ar is out-of-corpus, not unanswerable-in-principle.** The 22 questions include type (a) questions the Quran does not address at all and type (b) questions whose topic appears in the Quran but whose ruling comes from hadith or fiqh. Type (b) is not unanswerable in Islamic scholarship — it is out-of-corpus for a Quran-only system. A system that answers type (b) from a broader corpus is correct in principle.

**The query phrasing distribution is not uniform.**  The 174 manual + 22 wahi calibration questions include a large proportion of single-word Arabic lexical queries. The 36 synthetic_gemini_v2 fresh questions are proportionally more full-sentence prose questions across all three languages. A system tuned on the calibration set will not necessarily generalize to the fresh set. If your system was developed with the calibration set visible, evaluate it on the fresh set.

**Cross-lingual translations are not perfect.** The cross_lingual_en and roman_urdu questions depend on machine translation or transliteration mappings. Some translations are non-literal (e.g., "backbiting" in the Yusuf Ali English corpus is rendered "behind their backs" in Surah 49), and a system that relies on literal translation for cross-lingual retrieval will fail on such cases.

Full details: Hugging Face dataset card.( https://huggingface.co/datasets/ahmad1979/ahmad-eval-v1 )
Intended and out-of-scope uses
Intended:

Evaluating retrieval systems built on the Quran. R@5, R@10, MRR, hit@k.

Evaluating abstention behavior on out-of-corpus questions.

Evaluating cross-lingual retrieval from English and Roman-Urdu to Arabic verses.

Reproducing the reference pipeline's evaluation using the artifacts in pipeline_results.md.

###Out of scope:

**Answering religious questions authoritatively.**  This is a benchmark, not a fatwa service. The gold verses are retrieval targets, not rulings.

**Training a model on this data.**  The 232 questions are evaluation data. Training on them contaminates every future evaluation on this benchmark.

**Publishing a "system accuracy" number without the abstention split and the failure-mode analysis.**  A verified rate without the abstention rate is not informative.

###Licensing and provenance
The Quranic text (canonical_quran.db in the reference pipeline) is public domain.

The English translation is Yusuf Ali, public domain.

The 174 manual questions were hand-labeled in this project, Sessions 6–7. Every gold verse was reviewed against the canonical text.

The 22 wahi-quran-retrieval-pairs/benchmark questions are adapted from the wahi dataset. Provenance is unverified — see LICENSES/wahi.md. The gold verses were human-reviewed by us.

The 36 synthetic_gemini_v2 questions were contributed by an external model and hand-reviewed before being frozen in the benchmark. They are not produced by the reference pipeline's authors; they were reviewed for correctness against the Uthmani text.

The dataset is released under CC-BY-4.0. See LICENSE

###Citation
If you use Ahmad-Eval v1 in published work, cite it as:

Ahmad-Eval v1: A 232-question retrieval and QA benchmark for the Quran.
Project: Ahmad-AI. Sessions 6–7, 2026.
Repository: https://github.com/emadaed/quran-retrieval-benchmark
Dataset: https://huggingface.co/datasets/ahmad1979/ahmad-eval-v1

###See also
Hugging Face dataset: ahmad1979/ahmad-eval-v1

pipeline_results.md — full reference pipeline evaluation, failure-mode analysis, confidence intervals, pre-registered pass-rule verdict

Engineering log series — the seven-chapter narrative of how this benchmark and the reference pipeline were built:

### 📘 Engineering Logs & Architecture Deep-Dives
* 📗 **[Engineering Log 01: Guardrails & Hallucination Prevention](https://emadaed.github.io/digisuite/engineering-log.html)**  
  *Building a deterministic safety layer around an LLM agent with live SQL tool-calling and strict citation verification.*
* 📙 **[Engineering Log 02: Multilingual Semantic Search & Shamela Integration](https://emadaed.github.io/digisuite/engineering-log-2.html)**  
  *Scaling Ahmad-AI to 113,842 indexed Islamic records using two-stage retrieval (`MiniLM-L12` + `GATE-Reranker-V1`).*
* 📖 **[Engineering Log 05: Building a Quran Retrieval Benchmark From Scratch](https://emadaed.github.io/digisuite/engineering-log-5.html)**  
  *68 hand-labeled questions, three rejected datasets, and the counter-intuitive finding that translating the corpus beats translating the query for cross-lingual retrieval.*
* 🧪 **[Engineering Log 06: Scaling Ahmad-Eval to 196 Hand-Reviewed Questions](https://emadaed.github.io/digisuite/engineering-log-6.html)**  
  *Growing the benchmark 3x, hand-verifying every gold verse against the Quranic text, fixing a qid collision bug, and re-evaluating the retriever on the cleaned gold.*
* 🔍 **[Engineering Log 07: The Reranker Was Hurting, and the Metric Was Wrong](https://emadaed.github.io/digisuite/engineering-log-7.html)**  
  *A corpus-wide indexing bug found by a diagnostic built for another purpose, a 12-point reranker regression hidden behind an auto-selector, and a 40-minute failure read showing the 19% metric was measuring gold-set specificity, not retriever quality.*
* 🚪 **[Engineering Log 08: The LLM Selector Failed; the Gate Ships](https://emadaed.github.io/digisuite/engineering-log-8.html)**  
  *Four local models tested as Quranic abstainers. Zero correct abstentions across 24 draws. A two-layer scope-routing gate replaced the failed hypothesis and shipped at the pre-registered threshold: 8/10 out-of-scope catches, 0/4 answerable false positives.*
* 📕 **[Engineering Log 09: The Pipeline Does Not Generalize — and That's the Finding](https://emadaed.github.io/digisuite/engineering-log-9.html)**  
  *196 calibration questions pass. 36 fresh questions fail the pre-registered thresholds on both conditions. The 232-question benchmark is published on Hugging Face with both the passing and the failing numbers, and the four-tier promise from Chapter 03 is checked against what was actually built.*  

###A note on what this benchmark is for
This benchmark exists because no clean public verse-level Quranic retrieval benchmark existed when the project began. It is published to be useful to the next person who tries to build a Quranic retrieval system.

It is published with the reference pipeline's measured results, including the parts where the pipeline fails.

###A benchmark that only documents the wins is a marketing artifact, not a benchmark.

