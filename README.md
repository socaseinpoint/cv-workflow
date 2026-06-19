# cv-workflow

A workflow for building resumes as the **intersection of truth about you and what the market wants** —
with traceability and no fabrication. PDF rendering is a separate engine:
[cv-generator](https://github.com/socaseinpoint/ats-cv-generator).

```
┌─ CORE (about you) ─────┐
│  general anchors, md   ├──► MASTER ──► @JOB-TITLE ──► @COMPANY ──► CV (pdf)
├─ SPEC (about market) ──┤    cv.json     narrow         JD          (cv-generator)
│  what a CV should be   │      ▲
├─ EVIDENCE BANK ────────┘──────┘  (secondary, grows per application, provenance)
│
└─ GAP = spec − core → what to learn / build (career roadmap)
```

## Idea

- **Core (facts)** — about *you*: what you actually did. General, stable, no numbers, append-only.
  Kept deliberately general so specifics can't become fabrication hooks.
- **Spec** — about the *market*: what a resume should be right now. Parameterized by target level
  (`@master` → `@job-title` → `@company`). Moves with the market, not with you.
- **Master** — `cv.json` assembled from `core × spec@master`, with **no** vacancy. Tailoring to a
  title/company is just edits to that same file → re-render.
- **Evidence bank** — confirmed specifics (numbers/details) + provenance. Secondary; grows per
  application and is reused so you don't answer the same question twice.
- **Gap** — `spec − core` reveals not only what to surface on the CV, but what to learn/build next.

Full design: [`docs/architecture.md`](docs/architecture.md). Decision log:
[`docs/decisions.md`](docs/decisions.md).

## Layout

```
docs/         architecture + decision log
templates/    layer scaffolds (facts.template.md, spec.skeleton.md, master.md)
data/         YOUR content (facts, spec, evidence, rendered cv.json) — git-ignored
```

## Status

Design captured. Rendering engine shipped (`cv-generator`). Spec content is pending a research tool;
the core (your real facts) is filled later. Until then, this repo holds the architecture and templates.

## Relation to cv-generator

Loose dependency (not a submodule). `cv-workflow` produces a `cv.json`; `cv-generator` renders it to PDF.
