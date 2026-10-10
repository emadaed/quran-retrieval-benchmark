# Rejected Sources — Day 22 audit

During the initial bootstrapping of Ahmad-Eval v1 (Day 22 of the
Ahmad-AI project, 2026-10-03), six public datasets were evaluated as
possible sources. Five were rejected. This document records what was
found and why, so future contributors do not repeat the investigation.

**Lesson:** no clean public benchmark for verse-level Quranic retrieval
exists. Every candidate is the wrong shape. Ahmad-Eval had to be built
by hand.

---

## 1. `Ereeeeef3/Qu-QA-v3`

**Claimed:** Quran QA dataset.

**Found:** 19,210,080 examples, 16.6 GB, schema `{input, output}`.
Instruction-tuning corpus, not a retrieval benchmark. Questions are
generated prompts; "answers" are paragraphs, not verse references.

**Rejected:** wrong shape.

---

## 2. `Emaratilicious/quranqa-parquet`

**Claimed:** QuQA in Parquet form.

**Found:** Empty repository. Only `.gitattributes`.

**Rejected:** no data.

---

## 3. `Adanmohh/wahi-quran-retrieval-pairs`

**Claimed:** Verse retrieval benchmark with cross-lingual pairs.

**Found:** Usable. Files:
- `benchmark.json` — 26 thematic cases (20 EN, 4 FI, 2 AR).
- `corpus.json` — 6,236 verses with Arabic, English, Finnish, plus
  English tafsir.
- `train.jsonl` — 11,218 pairs (Arabic anchor + English passage).

**Provenance:** no README, no author, no methodology.

**Audit:**
- 0 duplicate query texts in the benchmark split.
- Healthy gold verse overlap (`2:155` referenced 5× — it is the central
  patience verse, this is expected).
- 17/20 EN queries are natural topic phrasings, not templated.

**Kept with caveat:** tagged `source_verification: unverified`. 22 of
Ahmad-Eval v1's 68 questions come from here (all 20 cross_lingual_en,
2 semantic_ar).

**For Phase A:** do not extend. Hand-label new cross-lingual questions.

---

## 4. `Salama1429/tarteel-ai-QuranQA`

**Claimed:** Quran QA benchmark, train/test splits.

**Found:** Extractive QA on passages, not passage retrieval with gold
verses. Schema `{pq_id, passage, surah, verses, question, answers}`.
- train: 710 rows → 118 unique questions
- test: 238 rows → 22 unique questions
- test_noAnswers: 274 rows

**Fatal problem:** the `test_noAnswers` split means "no answer **in the
assigned passage**," not "no answer in the Quran." Example:

> `على من تجوز الصدقة؟` ("who is eligible to receive charity?")
> appears in `test_noAnswers`, but the Quran answers it in `2:215`,
> `2:273`, `9:60`.

Same question maps to multiple passages; the union of verses for one
question can grow to hundreds. This is the wrong task entirely.

**Rejected:** wrong shape. Extractive QA ≠ verse retrieval.

---

## 5. `Kandil7/Athar-Datasets`

**Claimed:** 15.8M scholarly passages from 8,425 books, including a
`quran_tafsir.jsonl.gz` category.

**Found:** Gated repo (access requested and granted in ~1 hour). But:
`quran_tafsir.jsonl.gz` contains scholarly passages *about* the Quran
tagged as "quran_tafsir" category — **not** verse-aligned tafsir. The
passages do not map to specific verses.

**Rejected for verse-level QA.** Potentially useful for a later
hadith/fiqh retrieval component, but not for Ahmad-Eval v1.

---

## 6. Other candidates briefly checked

- `QUQA` (academic) — no accessible distribution found.
- `QurSim` — verse similarity pairs, no questions. Not QA.
- `HAQA` — hadith QA, wrong corpus.
- `IslamicFaithQA` — bilingual QA, no verse references.

None contributed to v1.

---

## Summary table

| source | shape | verdict |
|---|---|---|
| Ereeeeef3/Qu-QA-v3 | instruction-tuning | reject |
| Emaratilicious/quranqa-parquet | empty | reject |
| Adanmohh/wahi-quran-retrieval-pairs | thematic + corpus | **kept (unverified)** |
| Salama1429/tarteel-ai-QuranQA | extractive QA | reject |
| Kandil7/Athar-Datasets | scholarly passages | reject for v1 |
| QUQA / QurSim / HAQA / IslamicFaithQA | various | reject |

---

## What this means for Phase A

Do **not** attempt to bootstrap Phase A from public sources. They do not
exist in the required shape. Hand-label every question. It is slower but
it is the only path that produces gold verse references a human has
confirmed.

The tooling in `tools/` exists to make this fast. Use it.

---

*If you find a new candidate source, audit it against these criteria:
(1) does it provide verse-level gold? (2) is the split actually "no
answer in the Quran" vs "no answer in a given passage"? (3) is provenance
documented? If any answer is no, reject.*