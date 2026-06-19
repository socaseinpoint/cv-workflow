# Decisions (append-only log)

Why it's built this way. One line per turn.

- **Three layers kept apart: core / spec / evidence bank.** Core = about you (truth, stable),
  spec = about the market (moves with the market), bank = confirmed specifics. Mixing them = drowning
  in overclaim.
- **Keep the core general on purpose.** Specifics become hooks for invention/fabrication. Numbers go
  to the evidence bank, not the core.
- **Core format — markdown.** Easy for a human to extend; the general style doesn't slide into numbers.
  Structured (yaml/json) invites "fill in the blanks" → pulls toward hooks.
- **Collector — gap-driven, from the vacancy.** Don't build the bank upfront (YAGNI). The bank is
  secondary and grows per application.
- **Evidence bank is reused.** Confirm a number once → it sits there with provenance → no re-asking.
  The exact shape of the bank is NOT locked in advance — it follows convenience in real use.
- **Primary artifact is the MASTER, with no vacancy.** Assembled from `spec@master`. A vacancy is a
  light tailoring pass on top.
- **Master = the generator's `cv.json` (option A).** Title/company are edits to that same file →
  re-render. Fewest entities, one format.
- **Spec is parameterized by target level** (`@master/@title/@company`). Title and company both narrow
  the spec.
- **GAP (spec − core) is its own output.** Not just a CV, but a "what to learn" roadmap.
- **Rendering engine is a separate repo** ([cv-generator](https://github.com/socaseinpoint/ats-cv-generator)).
  Loose dependency (documented), not a submodule at the start.
- **Method (`.arcs/`) ≠ product.** `.arcs` tracks the work; this repo is the result/system.
- **Personal data is not in git.** The system design is public; your facts are not.
