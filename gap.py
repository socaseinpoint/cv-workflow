#!/usr/bin/env python3
"""gap.py — the collector's deterministic core: GAP = spec − core.

Reads facts.md (core: what you actually did) and a spec <level>.rules.yaml
(keyword_sets: what the market wants), and computes:

  covered   — wanted AND in facts          → surface these in the CV
  gap       — wanted but NOT in facts       → roadmap (learn/build) or "do you have it?"
  questions — targeted collector prompts: gap-keywords + per-project metric questions
              (numbers go to the evidence bank with provenance, never invented)

Gap-driven, from the spec/vacancy — NOT an upfront sweep (see docs/decisions.md).

Usage:
    python3 gap.py <facts.md> <level.rules.yaml>
"""
import argparse
import re
import sys
from pathlib import Path

import yaml

_STACK_RE = re.compile(r"(?:^|\n)\s*[-*]?\s*stack:\s*(.+)", re.IGNORECASE)
_DID_RE = re.compile(r"(?:^|\n)\s*[-*]?\s*did:\s*(.+)", re.IGNORECASE)


def facts_keywords(facts_text):
    """Tech tokens present in the core — from `stack:` lines (comma-separated)."""
    kws = set()
    for line in _STACK_RE.findall(facts_text):
        for tok in line.split(","):
            tok = tok.strip().lower()
            if tok:
                kws.add(tok)
    return kws


def spec_wanted_keywords(rules):
    """All keywords the spec wants, flattened from keyword_sets."""
    ksets = rules.get("keyword_sets") or {}
    return {t.strip().lower() for terms in ksets.values() for t in terms}


def _project_dids(facts_text):
    return [d.strip() for d in _DID_RE.findall(facts_text) if d.strip()]


def compute_gap(facts_text, rules):
    # A wanted term is "covered" if it appears anywhere in the facts (stack OR prose),
    # case-insensitive substring — more accurate for a collector than stack-only.
    text = facts_text.lower()
    wanted = spec_wanted_keywords(rules)
    covered = {kw for kw in wanted if kw in text}
    gap = wanted - covered

    questions = []
    for kw in sorted(gap):
        questions.append(
            f"Spec wants '{kw}' but it's not in your facts — do you have experience with it "
            f"to add (truthfully), or is it a learn/build gap?")
    for did in _project_dids(facts_text):
        questions.append(
            f"Can you back a metric (→ evidence bank, with provenance) for: \"{did}\"?")

    return {"covered": covered, "gap": gap, "questions": questions}


def _fmt(result):
    lines = [f"COVERED ({len(result['covered'])}): {', '.join(sorted(result['covered'])) or '—'}",
             f"GAP ({len(result['gap'])}): {', '.join(sorted(result['gap'])) or '—'}",
             "", "COLLECTOR QUESTIONS:"]
    lines += [f"  {i+1}. {q}" for i, q in enumerate(result["questions"])]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="GAP = spec − core (collector core)")
    ap.add_argument("facts")
    ap.add_argument("rules")
    args = ap.parse_args(argv)

    facts_text = Path(args.facts).read_text(encoding="utf-8")
    rules = yaml.safe_load(Path(args.rules).read_text(encoding="utf-8")) or {}
    print(_fmt(compute_gap(facts_text, rules)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
