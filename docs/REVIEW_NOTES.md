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

## What this means for tooling

The automated validator (`validate_qids.py`) checks:
- qid uniqueness
- qid format
- bucket / lang consistency
- ref format and DB existence
- answerable flag matches bucket

The automated validator **cannot** check:
- whether the verse answers the query
- whether both halves of a multi-hop query are present
- whether the root is used in the intended sense

**Only a human can check these.** Every gold verse must be read by a
human before commit. This is the Sadaqa.

---

## Amendment to Session 5 journal (later, optional)

The retriever session journal (`Ahmad-AI/journal/2026-10-10-day24.md`)
reports "no regression on Arabic buckets" and similar metrics that
assumed the gold verses were correct. At the time, they had not been
semantically verified. Session 7a's review found ~2% of gold verses
required correction. The retriever metrics from session 5 are still
valid directionally, but the exact R@5 numbers may shift slightly after
the gold is fully cleaned. Note this in the eventual retriever journal
when we re-run the eval.

---

*This file is the reference for what hand-review catches and tools
cannot. Cite it when explaining the review methodology to anyone.*