# generator — facts × spec → master.cv.json

The merge step: intersect CORE (truth about you) with SPEC (what the market wants) into the
generator's `cv.json`. Every line rests on a fact; the spec decides what to surface and how.

## What is code vs judgment

- **Deterministic harness (code):** load `data/facts.md` + `data/spec/<level>.md` +
  `<level>.rules.yaml` (+ JD for `@company`), validate the produced `cv.json` against the
  cv-generator schema, then run `check.py`. Render is a separate engine.
- **The merge itself (LLM judgment):** choosing which facts to surface and phrasing them is not
  mechanical — it is an LLM task driven by the spec. There is no honest "pure code" for it.

## Procedure (per level)

1. **Sections** — emit exactly the spec's `Required sections`, in order.
2. **Pull from facts only** — every bullet traces to `facts.md`. No fact in the CV that isn't in
   the core (`no_fact_outside_core`). A number must come from the evidence bank with provenance —
   never invented.
3. **Phrase per `Priority signals`** — action-verb first, keyword early, XYZ shape
   (accomplished X measured by Y by doing Z); front-load seniority/ownership verbs.
4. **Mirror `Keyword mirror`** — reflect the spec's keywords ONLY where they exist in your facts.
   For `@company`, lean toward the JD's vocabulary.
5. **Avoid `Anti-patterns`** — no filler stems, no multi-column, no name-drops, no unbacked numbers.
6. **Gate** — run `check.py <cv.json> <level>.rules.yaml --facts facts.md [--pdf out.pdf]`.
   `hard_gates` must PASS (else fix); `soft_rubric` is an advisory 0-100 score to iterate on.

## Targeting

```
core × spec@master            → data/master.cv.json        (no vacancy)
master.cv.json × spec@title    → data/targets/<title>.cv.json
<title>.cv.json × JD (@company)→ data/targets/<company>.cv.json
<target>.cv.json → CV.pdf      (cv-generator/render.py)
```

## Status

The stub (`data/master.cv.json`) was assembled by hand (LLM playing the generator) from the stub
`facts.md` × `spec@master`, to exercise the full pipeline: it passes all hard gates, scores
85/100 soft, renders to a valid 1-page PDF. The real run needs real facts (collector, arc 01).
