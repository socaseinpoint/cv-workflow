# collector — gap-driven core builder

Builds the CORE (`data/facts.md`) gradually, driven by the GAP between spec and what you've
already recorded. NOT an upfront interview (see docs/decisions.md).

## Engine: `gap.py` (deterministic)

```
python3 gap.py data/facts.md data/spec/<level>.rules.yaml
```
Computes `GAP = spec − core`:
- **covered** — spec keywords found in your facts → surface in the CV.
- **gap** — spec keywords absent → roadmap (learn/build) or "do you have it but didn't record it?"
- **questions** — targeted prompts: one per gap keyword + one per project ("can you back a metric?").

GAP is read two ways (parent goal): **for the CV** (what to surface) and **for growth** (what to learn).

## Procedure (interactive — needs you)

1. Run `gap.py` against the target spec level.
2. For each gap keyword: answer truthfully — have it (→ append to `facts.md`, general, no numbers)
   or don't (→ it's a growth item, leave it out of the CV).
3. For each project metric question: if you can back a number, it goes to the **evidence bank**
   with provenance — never into the general core, never invented.
4. Re-run `gap.py`; repeat from the vacancy, gradually. The bank is reused so you aren't re-asked.

## Status
Engine built + tested (on stub facts). The interactive collection of REAL facts is deferred —
it needs you to answer about your actual experience (parent goal defers personal data on purpose).
The evidence-bank file shape is intentionally not locked; it follows convenience in real use.
