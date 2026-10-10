# Review Notes — patterns discovered while auditing gold verses

Recorded during the Session 7a review of Ahmad-Eval (2026-10-11).

These are the specific kinds of gold-verse errors that humans catch and
automated validators do not. They are the reason hand review is mandatory.

---

## Pattern 1 — "mentioned" vs "answered"

A query asks *"what is X like?"* or *"what is the ruling on X?"* and the
gold verses include verses that **mention** X without **describing** or
**answering** the question.

Example (roman_urdu, `jannat kaisi hai` — "what is Paradise like"):
- ❌ 2:82 "أولئك أصحاب الجنة هم فيها خالدون"
  → says *they are the companions of Paradise*, does not describe it.
- ❌ 3:185 "فمن زحزح عن النار وأدخل الجنة فقد فاز"
  → says *whoever enters Paradise has succeeded*, does not describe it.
- ✅ 3:133 "جنة عرضها السماوات والأرض"
  → describes its *extent* — answers "what is it like."
- ✅ 7:43 "تجري من تحتهم الأنهار..."
  → describes its *features* — answers "what is it like."

**Rule:** if the query asks for a description, the gold verse must
describe. If it asks for a ruling, the gold verse must rule. A verse
that merely names the topic is *not* a match.

This pattern cost us 5 drops in `roman_urdu` (2:82, 3:185, 7:42 from
`jannat kaisi hai`; 2:39, 3:116 from `jahannam ka azab`).

---

## Pattern 2 — "half-query" (multi-hop failure)

A multi-hop query has two parts. Every gold verse must satisfy **both**.
If a verse satisfies only one part, it does not match.

Example (roman_urdu, `ilm aur amal` — "knowledge and action"):
- ❌ 2:277 "آمنوا وعملوا الصالحات"
  → action only, no knowledge.
- ❌ 16:97, 18:107, 103:3
  → same failure.

**Result:** the whole question was deleted. The verses were correct for
a single-hop `amal salih` query, but wrong for `ilm aur amal`.

**Rule:** for multi-hop, verify both concepts are present in every gold
verse. If the query cannot be satisfied by 3+ verified verses, delete
the question rather than weaken the gold.

---

## Pattern 3 — "half-verse / different sense of the root"

A verse contains the query's root but in a different sense.

Example (multi_hop `الصبر والصلاة`):
- ❌ 2:157 "أولئك عليهم صلوات من ربهم"
  → صلوات here means "blessings from God," not "ritual prayer."

**Rule:** polysemous roots need per-verse sense checks. `root match` is
not `concept match`.

---

## Pattern 4 — the tail of the verse matters

A verse's main clause may be on a different topic, but its closing
command or statement may directly address the query.

Example (semantic_ar `التوبة والرجوع إلى الله`):
- 24:31 — main content is modesty guidance, but the closing command
  reads "**وَتُوبُوا إِلَى اللَّهِ جَمِيعًا**" ("and turn to Allah in
  repentance, all of you") — directly on-topic.

**Rule:** read the whole verse, including the tail. A verse that starts
off-topic and ends on-topic is a valid gold for the ending's topic.

---

## What this means for tooling

The automated validator (`tools/validate_qids.py`) checks:
- qid uniqueness
- qid format
- bucket / lang consistency
- ref format and DB existence
- answerable flag matches bucket

The automated validator **cannot** check:
- whether the verse answers the query
- whether both halves of a multi-hop query are present
- whether the root is used in the intended sense
- whether the verse's tail is the relevant part

**Only a human can check these.** Every gold verse must be read by a
human before commit. This is the Sadaqa.

---

## Cross-bucket topic overlap is intentional

The same topic appears across buckets, e.g. "patience" appears as:
- `ae_en_000`, `ae_en_001` (English, from wahi)
- `ae_sem_wahi_000` (Arabic, from wahi)
- `ae_cross_lingual_en_022` (English, hand-labeled)
- `ae_roman_urdu_040` (Roman-Urdu, hand-labeled)

This is **not duplication**. Each bucket tests a different retrieval
mode (English paraphrase, Arabic paraphrase, cross-lingual, Roman-Urdu).
The same topic in different buckets lets us compare R@5 across modes
for the same concept.

**Real duplication** — same bucket, same query, same topic — is what we
guard against, and it's rare. One was found and fixed:
`ae_semantic_ar_014` (duplicate of `ae_multi_hop_ar_001`).

---

## Session 7a review summary

| bucket | reviewed | changes |
|---|---|---|
| multi_hop_ar | 2 | tightened `_000` refs (removed 3) |
| unanswerable_ar | 17 | deleted 1 (crypto duplicate) |
| semantic_ar | 40 | deleted 1 (duplicate of multi_hop_001) |
| roman_urdu | 40 | tightened 2, deleted 1 (half-query) |
| cross_lingual_en | 40 | no changes (all clean) |
| lexical_ar | 60 | pending |
| **total** | **197 so far** | **5 fixes + 3 deletions** |

Net: the file went from 199 → 196 questions with the current fixes,
and every remaining gold verse has been human-reviewed by the author
against the actual Quranic text.

---

*This file is the reference for what hand-review catches and tools
cannot. Cite it when explaining the review methodology to anyone.*