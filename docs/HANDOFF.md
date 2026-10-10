# Handoff Brief — Phase A Labeling

**Audience:** Working on Phase A expansion.
**Purpose:** brief you on what the benchmark is, what Phase A needs,
and how to contribute without breaking anything.

This document is self-contained. Assume no prior context.

---

## 1. What you are working on

The **Quran Retrieval Benchmark** — a public, hand-labeled dataset for
evaluating verse-level Quranic retrieval systems. Published on
HuggingFace (planned).

Current version: **Ahmad-Eval v1**, 68 questions.
Target: **Phase A**, ~260 questions.

**What "verse-level retrieval" means:** given a natural-language query,
a retrieval system must return the correct verses from the Quran as a
ranked list. The benchmark provides the query and the gold verses. The
system's job is to find them.

---

## 2. What's in this repository
data/ahmad_eval_v1.json the 68-question benchmark
tools/label_helper.py search and inspect candidate verses
tools/add_label.py validate and append a labeled question
docs/SCHEMA.md the JSON schema, bucket definitions
docs/PROVENANCE.md per-bucket origin, caveats
docs/REJECTED_SOURCES.md datasets that did NOT work, and why

text

Read `docs/SCHEMA.md` first. It is the contract.

---

## 3. What Phase A needs

**Target: 250–300 questions.** Expand from 68 to ~260.

**Distribution goal:**

| bucket | v1 | Phase A target |
|---|---|---|
| cross_lingual_en | 20 | 60 |
| lexical_ar | 15 | 60 |
| semantic_ar | 4 | 40 |
| multi_hop_ar | 2 | 30 |
| roman_urdu | 20 | 40 |
| unanswerable_ar | 7 | 30 |
| **total** | **68** | **260** |

**New category to add in Phase A:** tafsir-grounded questions.
Questions whose gold is a verse **plus** a specific tafsir passage
supporting it. This adds a second retrieval target type. Design it
separately; do not mix it into the six existing buckets.

**Time cost:** ~5–10 minutes per question for a human labeler. 200 new
questions = 20–30 hours of human work. Do NOT try to auto-generate and
skip review. The v1 quality came from hand-labeling every gold verse.

---

## 4. How you (Gemini) participate

You are a **reasoning assistant**, not an executor. You do not run
Python. You do not touch the database. Your job is to:

1. **Draft candidate questions** in the specified bucket and language.
2. **Propose gold verses** for each question.
3. **Flag uncertainty** — if you are not sure a verse is a genuine
   match, say so. The human reviewer will decide.

The human (project author) will:
1. Run `tools/label_helper.py search "<keyword>"` to verify candidates.
2. Run `tools/label_helper.py show <ref>` to inspect each verse.
3. Run `tools/add_label.py add ...` to commit verified questions.

**You do not have to be right the first time.** It is faster for the
human to reject your bad candidates than to draft from scratch. Aim for
60–80% precision; the reviewer filters.

---

## 5. The JSON schema (short version)

Full schema in `docs/SCHEMA.md`. Summary:

```json
{
  "qid": "ae_lexical_ar_020",
  "lang": "ar",
  "bucket": "lexical_ar",
  "query": "الصدقة",
  "expected_verses": ["2:263", "2:264", "2:271", "9:60", "57:18"],
  "answerable": true,
  "source_dataset": "manual",
  "source_id": "",
  "notes": "hand-labeled"
}
Fields:

qid — unique. ae_<bucket>_<NNN>.

lang — ar, en, or ur-roman.

bucket — one of the six.

query — question text.

expected_verses — list of "surah:ayah" strings. Gold.

answerable — false only for unanswerable_ar.

source_dataset — "manual" for new questions.

source_id — "" for manual.

notes — free text, always fill something.

6. Bucket definitions — what you are drafting
lexical_ar — short Arabic keyword. Gold verses share a root or a
surface form with the query. Example: "الصبر" → verses with root صبر.

semantic_ar — thematic Arabic phrase. Gold verses share no words
with the query, only meaning. Example: "الشدة والفرج" → 94:5, 94:6.

multi_hop_ar — two concepts combined. Gold verses must satisfy
both. Example: "الصبر والصلاة" → 2:45, 2:153.

cross_lingual_en — English query, Arabic gold. Example:
"the prohibition of usury and interest" → 2:275, 2:276, 2:278, 3:130.

roman_urdu — Roman-Urdu query in Latin script, Arabic gold.
Example: "namaz kaise padhe" → verses on صلاة.

unanswerable_ar — the Quran does not answer. Two subtypes:

Type (a): obviously off-topic (e.g. "who won the 1998 World Cup?").

Type (b): a word from the question appears in the Quran, but the
ruling/answer does not. Example: "how many rak'ahs in witr prayer?" —
الوتر appears in 89:3 but no ruling.

Type (b) is deliberately adversarial. Include it.

7. What NOT to do
Do not modify existing questions. If v1 has a mistake, flag it
for the human; do not fix it unilaterally.

Do not auto-generate and skip review. Every gold verse must be
human-confirmed before commit.

Do not attempt to use public datasets. See REJECTED_SOURCES.md.
They do not exist in the required shape.

Do not invent surah:ayah references. If you are unsure whether a
verse exists or says what you think, say so and let the reviewer check.

Do not put "any verse about topic X" in expected_verses. Only
specific, verified verses. 3–5 is typical for a strong question.

Do not put the same gold verse in multiple questions unless the
queries are genuinely different (e.g. one lexical, one semantic).
Duplication is allowed when it tests a different retrieval mode.

8. First task
Read this file and docs/SCHEMA.md. Then:

Produce 20 draft lexical_ar questions in a file
data/phase_a_drafts.json (create it — do not append to the real
ahmad_eval_v1.json).

For each, propose 3–5 gold verses.

Report back with:

Time spent on the batch.

Your confidence per question (high / medium / low).

Which candidates you are least sure about.

The human will run each draft through tools/label_helper.py and
tools/add_label.py to verify. That gives us a calibration point
before scaling to the remaining 180+ questions.

9. Reporting format
When you deliver a batch, structure it as:

text
BATCH: lexical_ar (1/10)
QUESTIONS DRAFTED: 20
TIME: ~X minutes
HIGH CONFIDENCE: N
MEDIUM CONFIDENCE: N
LOW CONFIDENCE: N
NOTES: <anything worth flagging>
Then the JSON array. Then a short list of "questions I want verified
most carefully" with reasons.

Keep it tight. The human's time is the bottleneck, not yours.

This brief is the contract for Phase A contributions. If something in
it is unclear, ask before proceeding.