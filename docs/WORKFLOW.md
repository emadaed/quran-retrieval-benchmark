# Workflow — How Gemini hands work to the human

**Audience:** a fresh Gemini session working on Phase A of the
Quran Retrieval Benchmark.

**Prerequisite:** you have already read `HANDOFF.md` and `SCHEMA.md`.
This document does not repeat them. It tells you **how to deliver work
to the human**, not what work to do.

**Core principle:** the human runs every command. You do not run Python.
You do not touch the repo. You draft content and commands; the human
executes and reports back.

---

## 1. Environment facts you must know

The tools live in this repo at:
tools\label_helper.py
tools\add_label.py

text

**The human always runs commands from the benchmark repo root, with the
benchmark venv activated.**

Activation (Windows PowerShell):
cd D:\quran-retrieval-benchmark
..venv\Scripts\Activate.ps1

text

After activation, the shell prompt changes to show `(.venv)`. Every
command block you give the human must include the `cd` and the activate
line at the top, so the human never runs against the wrong Python.

**Verify activation** (if in doubt):
python -c "import sys; print(sys.prefix)"

text
Should print a path containing `quran-retrieval-benchmark\.venv`.

---

## 2. How to hand the human a NEW FILE

Every time you want the human to create or edit a file, use this exact
template:
NEW FILE
========
Path: D:\quran-retrieval-benchmark<relative path>

Open with:
notepad D:\quran-retrieval-benchmark<relative path>

Paste the content below into Notepad. Save as UTF-8. Close.

--- BEGIN FILE CONTENT ---
<full content here — no truncation, no "...", no placeholders,
no "and so on", no comments outside the actual file>
--- END FILE CONTENT ---

text

**Three hard rules:**

1. **Full path.** Not `<repo>\...`, not `./data/...`. The literal
   absolute path starting with `D:\quran-retrieval-benchmark\`.

2. **Exact `notepad` command.** The human copies the command, runs it,
   and Notepad opens the file. They then paste the content.

3. **Complete content.** No `...` abbreviations. No "rest is obvious."
   No lines omitted. If the file is long, that is fine — paste it whole.

**Bad example (do not do this):**
Create data/phase_a_drafts.json with the 20 questions we discussed.

text

**Good example:**
NEW FILE
========
Path: D:\quran-retrieval-benchmark\data\phase_a_drafts.json

Open with:
notepad D:\quran-retrieval-benchmark\data\phase_a_drafts.json

Paste the content below into Notepad. Save as UTF-8. Close.

--- BEGIN FILE CONTENT ---
[
{
"qid": "draft_lexical_ar_001",
"lang": "ar",
"bucket": "lexical_ar",
"query": "الصبر",
"expected_verses": ["2:153", "2:155", "2:177", "3:200"],
"answerable": true,
"source_dataset": "manual",
"source_id": "",
"notes": "draft — pending human verification"
},
...
]
--- END FILE CONTENT ---

text

---

## 3. How to hand the human a COMMAND

Every time you want the human to run something, use this exact template:
COMMAND
=======
Purpose: <one short line — what this is checking or producing>

cd D:\quran-retrieval-benchmark
..venv\Scripts\Activate.ps1
<the actual command, e.g. python tools\label_helper.py search "الصبر">

Expected: <one short line — what a useful result looks like>

text

**Rules:**

1. **Always include `cd` and the activate line.** Even if the previous
   command just ran, even if the human already activated. It is safer
   to be redundant than to fail silently.

2. **Use `python`, not the full venv path.** The human activates the
   venv first; `python` resolves correctly after that. Do not write
   `.\.venv\Scripts\python.exe`.

3. **Relative paths inside the command.** After `cd` to the repo root,
   use `tools\label_helper.py`, not the absolute path. Both work, but
   the relative path is cleaner and self-documenting.

4. **No invented flags.** If you are not certain a flag or subcommand
   exists, do not include it. Check Section 4 below. If it is not
   listed there, the flag does not exist.

5. **Quote strings with spaces.** `"namaz kaise padhe"`, not
   `namaz kaise padhe`.

**Bad example:**
Run the label helper on the patience keyword.

text

**Good example:**
COMMAND
=======
Purpose: find candidate verses for the keyword "الصبر" (patience)

cd D:\quran-retrieval-benchmark
..venv\Scripts\Activate.ps1
python tools\label_helper.py search "الصبر"

Expected: a list of ~30 verses tagged [surface] or [root]. Look for
verses whose Arabic actually discusses patience, not just any
verse containing the letters ص ب ر.

text

---

## 4. Full CLI reference

### 4.1 `tools\label_helper.py`

Three subcommands. No others exist.

**search**
python tools\label_helper.py search "<keyword>"

text
- Runs a surface match (keyword substring in Quran Simple Clean text)
  and a root match (camel-tools root extraction on the keyword,
  intersected with the verse's stored roots).
- Prints up to 30 candidate verses, sorted by `surah:ayah`.
- Output format per verse:
<surah>:<ayah> [surface|root]
<Arabic>
EN: <English> (may be absent if offline)

text
- Prints the extracted roots at the top so you can see how the query
was interpreted.

**show**
python tools\label_helper.py show <surah>:<ayah>

text
- Prints one verse's Arabic and English.
- Use this to double-check a candidate after `search` returned it.

**root**
python tools\label_helper.py root "<root>"

text
- Prints up to 30 verses whose stored roots include the given Arabic
  root (letters only, e.g. `صبر`).
- Use this when you want every verse of a root, regardless of whether
  the query surface matched.

### 4.2 `tools\add_label.py`

One form. Commits a verified question to the benchmark.
python tools\add_label.py <bucket> "<query>" <ref1> <ref2> ...

text

- `bucket` — one of:
  `lexical_ar`, `semantic_ar`, `multi_hop_ar`, `roman_urdu`,
  `unanswerable_ar`, `cross_lingual_en`.
- `query` — quoted, in the bucket's language. See `SCHEMA.md` for
  language rules.
- `refs` — space-separated `surah:ayah`. **Omitted entirely** for
  `unanswerable_ar`.

Behavior:
- Validates every ref exists in the canonical Quran DB.
- Refuses if a non-unanswerable bucket has no refs.
- Refuses if `unanswerable_ar` has refs.
- Deduplicates on `(bucket, query)` — safe to re-run.
- Assigns `qid` automatically: `ae_<bucket>_<N:03d>`.
- **Writes to this repo's `data\ahmad_eval_v1.json`.**
- Does **not** write to the retriever repo. Isolation is enforced.

Output on success:
ADDED: ae_<bucket>_<NNN>
bucket: <bucket>
query : <query>
refs : [...]
wrote : D:\quran-retrieval-benchmark\data\ahmad_eval_v1.json

text

Output on duplicate:
SKIP: "<query>" already exists as ae_<bucket>_<NNN>

text

Output on error: prints the reason and exits without writing.

---

## 5. The per-batch output contract

When you deliver a batch of draft questions, structure it as:
BATCH
=====
Bucket: <bucket>
Count: <N> questions
Drafted: <timestamp>

CANDIDATE JSON
==============
<full JSON array, ready to paste into data/phase_a_drafts.json>

PER-QUESTION VERIFICATION
=========================
For each candidate, provide:

QUESTION: <qid draft>
Step 1 — find candidates:
COMMAND
=======
Purpose: search for "<keyword>"
cd D:\quran-retrieval-benchmark
..venv\Scripts\Activate.ps1
python tools\label_helper.py search "<keyword>"
Expected: <what to look for>

Step 2 — inspect each proposed verse:
COMMAND
=======
Purpose: show <ref>
cd D:\quran-retrieval-benchmark
..venv\Scripts\Activate.ps1
python tools\label_helper.py show <ref>
Expected: <what to look for>

Step 3 — commit if verified:
COMMAND
=======
Purpose: add the question to the benchmark
cd D:\quran-retrieval-benchmark
..venv\Scripts\Activate.ps1
python tools\add_label.py <bucket> "<query>" <ref1> <ref2> ...
Expected: "ADDED: ae_<bucket>_<NNN>"

text

**The human runs Steps 1, 2, 3 for every question.** They may reject
your candidate verses at Step 2 if they are not genuine matches — that
is expected and correct. The human decides.

---

## 6. What you must NEVER do

1. **Never assume a command ran.** Wait for the human to paste the
   output before drafting the next step.

2. **Never write to the retriever repo.** All your file commands target
   `D:\quran-retrieval-benchmark\`. The retriever is read-only for the
   tools and completely off-limits for you.

3. **Never invent flags or subcommands.** Only the ones listed in
   Section 4 exist. If you need a capability the tools do not have, say
   so explicitly: "This would require a new tool; here is what it would
   do."

4. **Never say "and so on" in file content.** Every file is complete.
   Every JSON array is fully enumerated. If you cannot fit it in one
   response, say so and deliver it in multiple complete chunks with
   explicit boundaries.

5. **Never modify `ahmad_eval_v1.json` directly.** Only `add_label.py`
   writes to it. If you want to change an existing question, flag it
   for the human; do not produce a new version of the file.

6. **Never guess at verse references.** If you are unsure a verse
   exists or says what you think, say so and let the human check with
   `show`.

7. **Never give a command without the `cd` and the venv activate line.**
   Even if the human just ran one. Redundancy is cheaper than a silent
   failure.

---

## 7. Reporting back

After the human runs your batch, they will report:
- Which questions were verified and committed.
- Which candidate verses they rejected, and why.
- Which commands failed, and the error.

Use their report to:
- Adjust your next batch (e.g., if 40% of verses were rejected, propose
  fewer and more carefully-chosen verses per question).
- Note recurring errors so we can improve the tools.
- Never re-propose a rejected question without a specific reason.

---

## 8. Example — a complete, correct exchange

**You (Gemini) produce:**
BATCH
=====
Bucket: lexical_ar
Count: 2 questions
Drafted: 2026-10-10

CANDIDATE JSON
==============
[
{
"qid": "draft_lexical_ar_001",
"lang": "ar",
"bucket": "lexical_ar",
"query": "الصبر",
"expected_verses": ["2:153", "2:155", "2:177", "3:200"],
"answerable": true,
"source_dataset": "manual",
"source_id": "",
"notes": "draft — pending verification"
},
{
"qid": "draft_lexical_ar_002",
"lang": "ar",
"bucket": "lexical_ar",
"query": "الشكر",
"expected_verses": ["2:152", "14:7", "31:12"],
"answerable": true,
"source_dataset": "manual",
"source_id": "",
"notes": "draft — pending verification"
}
]

PER-QUESTION VERIFICATION
=========================

QUESTION: draft_lexical_ar_001 (الصبر)
Step 1 — find candidates:
COMMAND
=======
Purpose: search for "الصبر"
cd D:\quran-retrieval-benchmark
..venv\Scripts\Activate.ps1
python tools\label_helper.py search "الصبر"
Expected: ~30 verses tagged [surface] or [root]. Verify 2:153,
2:155, 2:177, 3:200 all appear.

Step 2 — inspect 2:153, 2:155, 2:177, 3:200:
COMMAND
=======
Purpose: show 2:153
cd D:\quran-retrieval-benchmark
..venv\Scripts\Activate.ps1
python tools\label_helper.py show 2:153
Expected: Arabic + English for the verse. Confirm it discusses
patience (sabr), not just contains the letters.

(repeat for 2:155, 2:177, 3:200)

Step 3 — commit if all 4 verify:
COMMAND
=======
Purpose: add the question to the benchmark
cd D:\quran-retrieval-benchmark
..venv\Scripts\Activate.ps1
python tools\add_label.py lexical_ar "الصبر" 2:153 2:155 2:177 3:200
Expected: "ADDED: ae_lexical_ar_015"

QUESTION: draft_lexical_ar_002 (الشكر)
(same structure)

text

**The human runs the commands one by one, reports which verses were
rejected, and either commits or re-drafts.**

---

*This workflow is the contract between you and the human. Read it
carefully. Following it costs you nothing; ignoring it costs the human
hours of debugging.
___________

---

## 9. Encoding and qid rules (critical — read before drafting)

### 9.1 UTF-8 encoding is mandatory

All files you hand the human contain non-ASCII text (Arabic, sometimes
Urdu). They MUST be UTF-8 encoded. If they are not, the Arabic strings
become mojibake (e.g., `الاستغفار` becomes `Ø§Ù„Ø§Ø³ØªØºÙØ§Ø±`), and
every tool downstream fails silently or writes garbage.

**Whenever you hand the human a file:**

1. In the "Open with" command, say: `Save as UTF-8` explicitly.
2. If the human reports the Arabic looks like `Ø§Ù„...`, STOP. Ask them
   to resave with UTF-8 encoding before any command is run.

**Notepad specifically:** Notepad's "Save As" dialog has an **Encoding**
dropdown in the bottom-right corner. It must say **UTF-8**. If it says
**ANSI** or **UTF-8 with BOM**, ask the human to change it. (UTF-8
without BOM is correct.)

### 9.2 Do NOT hand-assign qids

Do not put a `qid` field in your draft JSON at all. The `add_label.py`
tool assigns qids automatically when the human commits a verified
question. If you hand-assign qids you will:

- Collide with existing qids in the benchmark (e.g. `ae_lexical_ar_021`
  already exists — 24 `lexical_ar` questions are already committed).
- Bypass the tool's deduplication.
- Create duplicates when the human runs `add_label.py`.

**Your drafts should omit `qid` entirely.** The handoff example shows a
`qid` only for illustration of the final schema — a *committed* question
has a qid; a *draft* does not.

**Correct draft entry:**
```json
{
  "lang": "ar",
  "bucket": "lexical_ar",
  "query": "الاستغفار",
  "expected_verses": ["3:135", "71:10", "110:3"],
  "answerable": true,
  "source_dataset": "manual",
  "source_id": "",
  "notes": "root غ-ف-ر / seeking forgiveness"
}
Wrong draft entry (do not do this):

json
{
  "qid": "ae_lexical_ar_021",   <- NEVER. add_label.py assigns this.
  ...
}
9.3 Before drafting, ask the human for the current state
The benchmark has grown. You do not know how many questions are in
each bucket today, or which queries already exist. Ask the human to
run:

text
COMMAND
=======
Purpose: report current per-bucket counts
  cd D:\quran-retrieval-benchmark
  .\.venv\Scripts\Activate.ps1
  python -c "import json; d=json.load(open('data/ahmad_eval_v1.json',encoding='utf-8')); from collections import Counter; print(Counter(q['bucket'] for q in d))"
Expected: a Counter showing how many questions exist per bucket
Use the result to:

Avoid duplicating existing queries (check the human's paste).

Know which buckets need the most new questions.

Do this at the start of every new session where you will draft
questions. State changes between sessions.

9.4 Self-check before delivering a batch
Before you hand the human any JSON file, mentally verify:

□ No qid fields in the drafts.
□ All strings are literal UTF-8 (not mojibake, not HTML entities).
□ Every expected_verses entry follows surah:ayah with integers.
□ answerable is false only for unanswerable_ar.
□ The file is complete — no ..., no "and so on".
□ Every "COMMAND" block includes cd + activate + python.
□ Every "NEW FILE" block includes the full absolute path and the
Save as UTF-8 instruction.
If any box is unchecked, fix before sending.

_______________________________
## 10. Prefer `add_label.py` commands over draft JSON files

Section 2 teaches you to hand the human a new file with the
`notepad <path>` + full content template. That still applies for
**documentation**, **READMEs**, and **any ASCII-only content**.

**But for question data containing Arabic or Urdu, do NOT hand the human
a JSON file to save in Notepad.** Here is why.

### 10.1 The encoding failure we have seen

Arabic text passed through a chat message → clipboard → Notepad can be
mangled. Real example from an earlier session:

- Intended: `"query": "الاستغفار"`
- What Notepad saved: `"query": "Ø§Ù„Ø§Ø³ØªØºÙØ§Ø±"`

That is UTF-8 bytes reinterpreted as Latin-1 (mojibake). Every command
downstream fails, the human has to debug, and the failure is silent —
the tool accepts the string, it is just wrong.

The workflow doc already tells the human to "Save as UTF-8". That is
necessary but not sufficient. Notepad's encoding dropdown does not
always win, and even if it does, a mojibake string that arrives at the
human's clipboard is already broken before Notepad sees it.

### 10.2 The rule

**For any content containing non-ASCII text (Arabic, Urdu, or any
non-Latin script), do NOT produce a file. Produce `add_label.py`
commands instead.**

The tool writes the benchmark file directly. If the Arabic arrives at
the human's clipboard mangled, the `add_label.py` command visibly fails
— the human sees garbage in the terminal — and nothing is committed.
The failure is loud instead of silent.

### 10.3 What this looks like in practice

**Wrong — do not do this:**
NEW FILE
========
Path: D:\quran-retrieval-benchmark\data\phase_a_drafts.json
...
[full JSON with Arabic queries]
...

text

**Right — do this instead:**

For each candidate question, hand the human three commands. Example for
one question:
QUESTION
========
bucket: lexical_ar
query: الاستغفار (root غ-ف-ر, "seeking forgiveness")
candidate verses: 3:135, 71:10, 110:3, 3:17
rationale: 3:135 and 71:10 explicitly link istighfar to forgiveness;
110:3 is a command to seek forgiveness; 3:17 names the
"seekers of forgiveness" among the righteous.

VERIFY — Step 1, list candidates for this query:

COMMAND
=======
Purpose: search the Quran for الاستغفار
cd D:\quran-retrieval-benchmark
..venv\Scripts\Activate.ps1
python tools\label_helper.py search "الاستغفار"

Expected: a list of verses tagged [surface] or [root]. Confirm each
of 3:135, 71:10, 110:3, 3:17 appears and is relevant.

VERIFY — Step 2, inspect each proposed verse:

COMMAND
=======
Purpose: show 3:135
cd D:\quran-retrieval-benchmark
..venv\Scripts\Activate.ps1
python tools\label_helper.py show 3:135

Expected: Arabic + English. Confirm the verse discusses seeking
forgiveness, not just contains the root.

(repeat for 71:10, 110:3, 3:17)

COMMIT — after the human verifies all verses:

COMMAND
=======
Purpose: add the question to the benchmark
cd D:\quran-retrieval-benchmark
..venv\Scripts\Activate.ps1
python tools\add_label.py lexical_ar "الاستغفار" 3:135 71:10 110:3 3:17

Expected: "ADDED: ae_lexical_ar_<NNN>"

text

The human runs the commands. If a verse is wrong, they reject it and
you re-propose. If the query string arrived mangled, the `search`
command visibly prints garbage. Either way, nothing is committed until
the human types the final `add_label.py` line.

### 10.4 When a file IS still appropriate

Section 2 remains correct for:

- Documentation (`WORKFLOW.md`, `SCHEMA.md`, `README.md`, etc.).
- ASCII-only JSON (e.g., a manifest of question IDs).
- Scripts and config.

For anything else with non-ASCII content, use `add_label.py` commands.

### 10.5 The one exception — English-only drafts

If you are drafting a batch of `cross_lingual_en` questions, the
`query` fields are English (ASCII). Those can safely go in a draft JSON
file. But even then, the `add_label.py` command path is preferred,
because it means the human never has to reconcile a draft file against
the committed file.

**Default to `add_label.py` commands. Fall back to files only for
ASCII-only content or documentation.**

### 10.6 Summary — three ways to hand the human work

| What you are delivering | How to deliver it |
|---|---|
| Documentation (ASCII) | NEW FILE template (Section 2) |
| Non-ASCII question content | `add_label.py` commands (this section) |
| English-only question content | Either; `add_label.py` preferred |

If in doubt, use `add_label.py`