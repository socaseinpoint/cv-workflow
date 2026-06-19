# cv-workflow — architecture

A system that builds a resume as the **intersection of truth about you and what the market wants** —
with traceability and no fabrication. Rendering is a separate engine
([cv-generator](https://github.com/socaseinpoint/ats-cv-generator)).

## Big picture

```
┌─ CORE (about you) ─────┐
│  general anchors,      │
│  markdown, no numbers  ├──► MASTER ──► @JOB-TITLE ──► @COMPANY ──► CV (pdf)
├─ SPEC (about market) ──┤    cv.json     narrow         JD          (cv-generator)
│  what a CV should be   │      ▲
│  @master/@title/@comp  │      │
├─ EVIDENCE BANK ────────┘──────┘  (secondary, grows per application, provenance)
│
└─ GAP = spec − core → what to learn / build (career roadmap)
```

## Three layers (keep separate)

| Layer | About | Properties | Where |
|---|---|---|---|
| **CORE** (facts) | **you** — what you actually did | stable, general, append-only, no numbers | `data/facts.md` (yours, not in git) |
| **SPEC** | the **market** — what a resume should be now | moves with the market, not you; parameterized by target level | `data/spec/` (from research tool) |
| **EVIDENCE BANK** | confirmed specifics (numbers/details) + provenance | secondary, grows per application, reused | `data/evidence/` |

**Core ≠ Spec.** Core doesn't know about the market (truth is stable). Spec doesn't know about you
(it moves with the market). Analogy: core = ingredients, spec = recipe, master = the dish.

## Principle #1 — keep core general ON PURPOSE

Specifics in the core become fabrication hooks: people latch onto them and start inventing → overclaim.
"Built a RAG pipeline" — yes. "RAG precision@5 = 87%" — NOT in the core.
Numbers/details are derived later, by questions, per vacancy — only if you can back them (→ evidence bank).

## Targeting — specificity spectrum

One entity (`cv.json`), progressively narrowed:

```
MASTER (no target) → JOB-TITLE (areas) → COMPANY (specific JD)
```

- **Master** is assembled with NO vacancy, driven by `spec@master` (general market bar).
- **Job-title** (fullstack / frontend / …) — analyze what's in demand for that title now, written from
  your skills. `spec@title`.
- **Company** — a specific JD that leans toward one particular skill. `spec@company`.
- Job-title and company are similar: both narrow the spec; company just leans toward a special skill on top.

Spec is parameterized by target level: `@master → @title → @company`. This is "spec in general + per area".

## Flow

```
1. CORE     collect general anchors (about you)                  → data/facts.md
2. SPEC     research: what a resume should be (@master/@title)   → data/spec/
3. MASTER   core × spec@master → general cv.json (no vacancy)
4. TAILOR   master × spec@title/@company + JD → cv.json per target
5. RENDER   cv.json → CV.pdf                                     (cv-generator)
6. LOOP     apply → track callback-rate → tune spec/emphasis
```

## Collector

- Runs **gap-driven, from the vacancy, gradually**. No upfront sweep.
- Logic: what the spec/JD needs − what's already in the bank = gap → a targeted question to you →
  you answer truthfully → into the bank (with provenance).
- The bank is secondary: it grows slowly across applications and is reused so you aren't re-asked.

## GAP — a by-product

`spec − core = the gap`. Read two ways:
- **for the CV** — what to surface from what you already have;
- **for growth** — what's missing → what to learn/build (a career roadmap).

## Spec form — hybrid (prose + machine rules)

Each spec level is a PAIR of files in `data/spec/`:
- `<level>.md` — prose, the 6-part skeleton (Message / Required sections / Keyword mirror /
  Priority signals / Anti-patterns / What I am not), human-readable with rationale.
- `<level>.rules.yaml` — extracted machine-checkable layer, two tiers:
  - `hard_gates` — binary pass/fail, BLOCK render (max_pages, single_column, required_sections,
    banned_phrases, contact_in_body, no_fact_outside_core).
  - `soft_rubric` — weighted 0-100 score, advisory (bullets_have_metrics, xyz_formula,
    jd_keyword_coverage, seniority_verbs_frontloaded).

The check step (arc 03) consumes `rules.yaml`; the generator and the human read both.

## Updater

Spec is versioned (`data/spec/CHANGELOG.md`, `version:` in each rules.yaml).
Update flow: re-run the research tool (lore) → diff vs current spec → human approves → bump version.
Callback-rate is a COARSE trigger ("time to revisit"), NOT an automatic rule-tuner (low application
volume → no statistical significance). The apply→callback→tune funnel lives in the merge-loop stage.

## Boundaries (anti-drift)

- One core, one spec (parameterized); the render is disposable.
- No fact in the CV that isn't in the core (a number lives in the bank with provenance).
- Don't bend the core to the market; the spec doesn't depend on your experience; never hand-edit the PDF.
- Personal data (`data/`) is NOT in git.
