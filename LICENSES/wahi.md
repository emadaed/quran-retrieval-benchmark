# wahi-quran-retrieval-pairs — license notes

Some questions in Ahmad-Eval v1 are derived from the
`Adanmohh/wahi-quran-retrieval-pairs` dataset on HuggingFace.

**These are the affected questions:** all 20 `cross_lingual_en`
questions and 2 `semantic_ar` questions (`ae_sem_wahi_000` and
`ae_sem_wahi_001`).

They are tagged in the JSON with:
"source_dataset": "wahi-quran-retrieval-pairs/benchmark"

text

---

## Source

- **Repo:** https://huggingface.co/datasets/Adanmohh/wahi-quran-retrieval-pairs
- **Sub-split used:** `benchmark.json` — 26 thematic cases
- **Provenance:** unclear. No README, no author, no methodology, no
  license file.

---

## What we did

We adapted the 22 relevant cases (20 EN + 2 AR) into our schema:

- The `query` text is taken verbatim from the wahi benchmark.
- The `expected_verses` were reviewed by the project author against the
  canonical Quran DB before inclusion.
- The `notes` field in the JSON records
  `"thematic query; any gold key counts"` for these questions.
- The `source_id` field records the original wahi case ID
  (e.g. `"patience-en"`, `"repentance-ar"`).

---

## Caveats

**Unverified provenance.** The wahi dataset has no documented source,
methodology, or license. We treat the *question prompts* as usable —
they are natural topic phrasings, not templates — but we do not vouch
for any annotation that came with them. The gold verses in this
repository were human-reviewed by us before inclusion, regardless of
what the original wahi file claimed.

**Cross-language tagging.** The original wahi benchmark includes 4
Finnish cases. We do not use them. Only the 20 English and 2 Arabic
cases were adapted.

---

## License question — read carefully

The wahi dataset has **no stated license**. This is a legal grey area.
Our position:

- The **question text** itself is short (a few words to a sentence) and
  is used as a factual prompt. We do not redistribute the wahi corpus
  as a whole.
- The **gold verse references** we publish are facts about the Quran,
  not copyrightable in any jurisdiction that treats factual references
  as such.
- We **attribute** the wahi source explicitly (this file, and the
  `source_dataset` field in the JSON).

**If the wahi uploader or any third party objects** to the inclusion of
these 22 questions, we will remove them in a future version. The
benchmark can function without them — they are a convenience, not a
structural requirement.

**Recommendation for Phase A:** hand-label new cross-lingual and
semantic questions from scratch. Do not extend wahi further. This keeps
the license footprint of the benchmark clean.

---

*When in doubt, attribute. When a source has no license, use it
sparingly, review the content, and document your use.*