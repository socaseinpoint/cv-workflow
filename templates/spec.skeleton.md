# spec — skeleton (content filled by the research tool)

> Spec = about the MARKET, not you. What a resume should be right now. Parameterized by target level.
> This file is an empty skeleton. The real content (what's in demand) comes from the research tool.

## Target levels

```
@master   — general market bar (no title/company)
@title    — slice per job title (fullstack / frontend / …): what's in demand now
@company  — a specific JD: one special skill on top
```

Files: `data/spec/master.md`, `data/spec/<title>.md`; company tailoring happens per application.

## Spec structure (at each level)

### Message
<the core signal the resume should send at this level — TBD via research>

### Required sections
<which sections a recruiter/ATS expects + order — TBD via research>

### Keyword mirror
<keywords/skills to reflect (from yours, never invented) — TBD via research>

### Priority signals
<what's top-of-attention at this level right now — TBD via research>

### Anti-patterns
<what must NOT appear (overclaim, noise, format traps) — TBD via research + cv principles>

### What I am not
<boundaries, so nothing is over-promised — TBD>

## Machine layer (paired file: `<level>.rules.yaml`)

Each level is a PAIR: this prose (human + why) + a `<level>.rules.yaml` with the
machine-checkable gates extracted from it. See `spec.rules.skeleton.yaml`.

- **hard_gates** ← `Required sections` (+order) · `Anti-patterns` (format traps) · max pages · no-fact-outside-core
- **soft_rubric** ← `Keyword mirror` · `Priority signals` · `Message` (scored 0-100, advisory)
- **What I am not** stays prose-only (boundaries, anti-overclaim).

Why yaml here but markdown for the core: core specifics become fabrication hooks; spec
*gates* are not hooks — they are machine-checkable by nature. Different layer, different rule.

---
*Sources for content: the research tool (in progress) + prior CV principles / intent / market research.*
