# Tanzil — license notes

The Quran text and the English translation used by this benchmark's
tooling are sourced from [Tanzil](https://tanzil.net/).

**These files are NOT redistributed with this repository.** They are
kept locally for research use and consumed by `tools/`. Users who want
to run the tooling must download the source files themselves.

---

## Quran text (Uthmani, Simple)

- **Source:** https://tanzil.net/download/
- **License:** Tanzil's Quran text is distributed under a
  "Creative Commons Attribution 3.0" license, with additional terms:
  no modification of the text, and attribution to Tanzil.
- **Full terms:** https://tanzil.net/docs/terms

The Quran text used by the labeling tools is the Tanzil Uthmani and
Simple text. It is not shipped with this repository because the
repository is a **dataset**, not a text distribution; downstream users
who want to inspect gold verses should download the text from Tanzil
directly, or use any other trusted Quran text source.

---

## English translation — Yusuf Ali

- **Source:** https://tanzil.net/download/ → English → Yusuf Ali
- **License:** Tanzil translations are distributed under
  **CC-BY-ND 3.0** (Attribution-NoDerivatives).
- **Full terms:** https://tanzil.net/docs/terms

The English translation was used during Phase 1 of the retriever
project to build an English BM25 index over the Quran. It is **not**
shipped with this repository.

**No-derivatives caveat:** the license prohibits distributing modified
versions. We do not modify it. We do not ship it. It is downloaded
locally by the user.

---

## What this means for users of this benchmark

Nothing in this repository is under Tanzil's license. The benchmark
questions and gold verse references are our own work, published under
CC-BY-4.0 (see top-level `LICENSE`).

The `expected_verses` fields reference the Quran by `surah:ayah` — this
is a factual reference, not a reproduction of the text. Anyone can
verify the references against any Quran text source.

If you need the actual Quranic text alongside the benchmark (for
example, to fine-tune a model), download it from Tanzil or from another
public-domain source and use it according to that source's terms.