# Schema — Ahmad-Eval question format

Every question in the benchmark is a single JSON object in an array. The
array lives in `data/ahmad_eval_v1.json` (and future versions).

---

## Full example

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
Fields
qid (string, required, unique)
Unique identifier for the question. Format:

ae_<bucket>_<NNN> for hand-labeled questions (NNN is zero-padded).

ae_<bucket>_wahi_<NNN> for questions from the wahi dataset.

Examples: ae_lexical_ar_020, ae_en_000, ae_roman_urdu_035,
ae_sem_wahi_001, ae_unanswerable_ar_004.

Never reuse a qid. If a question is removed, its qid is retired.

lang (string, required)
The language of the query (not the gold verses, which are always Arabic).

value	meaning
ar	Modern Standard Arabic
en	English
ur-roman	Romanized Urdu (Latin script)
bucket (string, required)
The evaluation category. Exactly one of:

bucket	language	tests
lexical_ar	ar	root/surface keyword matching
semantic_ar	ar	paraphrase / thematic matching
multi_hop_ar	ar	multiple constraints combined
cross_lingual_en	en	cross-lingual retrieval
roman_urdu	ur-roman	low-resource transliteration
unanswerable_ar	ar	correct refusal
query (string, required)
The question text, in the stated lang. No trailing punctuation needed.
Length varies: 1–3 words for lexical_ar, full sentences for cross_lingual_en.

expected_verses (array of strings, required)
Gold-standard verse references, format "<surah>:<ayah>". At least one
entry, except for unanswerable_ar where the array is empty.

Surah and ayah are 1-indexed integers.

All references must exist in the canonical Quran (6236 verses).

"Any gold counts" — a retrieval is scored as correct if any verse in
this list appears in the top-k of the system's output.

answerable (boolean, required)
true for all buckets except unanswerable_ar. false for every
unanswerable_ar question.

source_dataset (string, required)
Where the question came from:

"manual" — hand-labeled from scratch.

"wahi-quran-retrieval-pairs/benchmark" — adapted from the wahi dataset.

(future) other dataset IDs, following the <org>/<dataset>/<split> form.

source_id (string, required)
The original ID within source_dataset, or "" for manual questions.

notes (string, required)
Free-form notes. Use this to document:

Adversarial properties of the question.

Why specific verses were or were not included.

Any ambiguity in the query.

The labeling decision if the question was borderline.

Short is fine. "hand-labeled" is a valid note. Empty string is not
recommended — every question deserves at least a one-line note.

Bucket definitions — in detail
lexical_ar
Query is a short Arabic keyword (noun, verb, or a two-word phrase). Gold
verses share a surface or root form with the query. This is the easiest
bucket for a root-based retriever — if a system fails here, it fails
basic morphology.

Example: "الصدقة" → verses that mention صدقة or share the root صدق.

semantic_ar
Query is a thematic Arabic phrase. Gold verses may share no words with
the query. This tests paraphrase matching and topic understanding.

Example: "الشدة والفرج" ("hardship and relief") → 94:5, 94:6
("with hardship comes ease") — related by meaning, not by word.

multi_hop_ar
Query combines two concepts. Gold verses must satisfy both. Tests
whether retrieval can handle compound queries.

Example: "الصبر والصلاة" ("patience and prayer") → 2:45, 2:153
(both verses mention both concepts).

cross_lingual_en
Query is English, gold verses are Arabic. Tests translation robustness.
The system must bridge the language gap before retrieval.

Example: "the prohibition of usury and interest" → 2:275, 2:276,
2:278, 3:130.

roman_urdu
Query is Romanized Urdu in Latin script, gold verses are Arabic. Same
cross-lingual challenge as above, but the source language is low-resource
and no clean transliteration standard exists.

Example: "namaz kaise padhe" → verses about صلاة (prayer).

unanswerable_ar
Query is Arabic, but the Quran does not answer it. Two subtypes:

Type (a) — obviously off-topic. Example: "من فاز بكأس العالم 1998؟"
("who won the 1998 World Cup?"). No retrieval should be possible.

Type (b) — topic appears, ruling doesn't. Example:
"كم عدد ركعات صلاة الوتر؟" ("how many rak'ahs in witr prayer?").
The word الوتر appears in 89:3, but the ruling is not in the
Quran. This is adversarial: a naive system will retrieve 89:3 and
answer incorrectly.

For type (b), a system should retrieve nothing, or retrieve candidates
and then refuse to answer because the verifier cannot confirm.

Versioning
Files in data/ follow ahmad_eval_v<major>.<minor>.json once we reach
v2. For now, ahmad_eval_v1.json is the only file.

When the schema changes in a breaking way, bump the major version and
document the migration in this file.

Validating a question
Every question should pass these checks:

qid is unique within the file.

lang is one of ar, en, ur-roman.

bucket is one of the six above.

answerable is false iff bucket == "unanswerable_ar".

Every entry in expected_verses exists in the canonical Quran.

If source_dataset == "manual", source_id is "".

The add_label.py tool enforces (1), (5), and (6) automatically.
Checks (2), (3), (4) are enforced by convention.

What makes a good question
Single-intent. One clear topic. Not "what does the Quran say about
charity and fasting and pilgrimage."

Grounded. Gold verses were verified by a human against the actual
Quranic text, not guessed.

Adversarial when useful. If a keyword has multiple meanings (e.g.
عمل = deeds / work), include it in the unanswerable bucket as a
false-positive trap, not in lexical_ar as a "gotcha."

Not duplicated. If a near-identical question exists, delete the new
one or move it to a different bucket with a different angle.

This schema is the contract between the dataset and any retrieval
system that uses it. Do not break it casually.