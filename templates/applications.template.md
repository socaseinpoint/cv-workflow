# applications — the loop / funnel (template)

> Lives at `data/applications.md` (gitignored). Track each application to compute callback-rate,
> which is a COARSE trigger to revisit the spec (see docs/architecture.md → Updater).
> Not a per-rule auto-tuner — volume is too low for statistical significance.

| date | company | role | cv_version | spec_level | channel | status | callback |
|------|---------|------|-----------|-----------|---------|--------|----------|
| 2026-06-19 | Example Co | Senior Fullstack | master v1 | @company | linkedin | applied | — |

Statuses: applied · screen · interview · offer · rejected · ghosted.
callback = y/n (any human response beyond an auto-ack).

## Loop

```
generate (facts×spec) → check (gates) → render → APPLY → log here →
periodically: callback-rate per spec_version → if low across enough apps → trigger research-refresh
(re-run the research tool → diff spec → human approve → bump version).
```
