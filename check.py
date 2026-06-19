#!/usr/bin/env python3
"""check.py — enforce a spec <level>.rules.yaml against a cv.json.

Two tiers (see docs/architecture.md → Spec form):
  hard_gates  — binary pass/fail; any FAIL blocks render (non-zero exit).
  soft_rubric — weighted 0-100 advisory score.

Gates not computable from cv.json alone are reported SKIPPED (never silent).
Metric/verb heuristics adapted from the MIT-licensed sunnypatell/ats-screener
(quantified-bullet regex set, ≥40% target; action-verb-first, ≥70% target) and
canonical action-verb lists (Harvard OCS / MIT CAPD / Yale).

Usage:
    python3 check.py <cv.json> <level.rules.yaml> [--pdf out.pdf] [--facts facts.md]

Deps: pyyaml (required), pypdf (optional — only for the max_pages gate).
"""
import argparse
import json
import re
import sys
from collections import namedtuple
from pathlib import Path

import yaml

GateResult = namedtuple("GateResult", ["name", "status", "detail"])

# --- word lists (research: R2 — Harvard/MIT/Yale career centers) ------------

STRONG_VERBS = {
    # leadership / ownership
    "led", "directed", "spearheaded", "orchestrated", "oversaw", "headed",
    "managed", "supervised", "coordinated", "executed", "drove", "owned",
    # built / created
    "built", "designed", "engineered", "architected", "created", "founded",
    "launched", "established", "developed", "constructed", "programmed",
    "pioneered", "introduced", "integrated", "implemented", "shipped",
    # improved / optimized
    "improved", "increased", "optimized", "streamlined", "reduced",
    "accelerated", "boosted", "transformed", "overhauled", "doubled",
    "eliminated", "maximized", "scaled", "migrated", "automated",
    # analyzed / communication / enabled
    "analyzed", "evaluated", "diagnosed", "investigated", "quantified",
    "authored", "negotiated", "presented", "mentored", "coached", "trained",
    "facilitated", "enabled", "guided", "defined", "set", "championed",
}

SENIORITY_VERBS = {
    "architected", "owned", "led", "drove", "spearheaded", "set", "defined",
    "scaled", "founded", "mentored", "hired", "established", "championed",
    "directed", "oversaw", "headed", "drove", "orchestrated",
}

# weak openers (hard signal of duty-framing) — research R2 blocklist
WEAK_OPENERS = [
    "responsible for", "duties included", "tasked with", "in charge of",
    "worked on", "helped to", "helped with", "helped", "assisted with",
    "assisted in", "assisted", "involved in", "participated in",
]

# quantified-bullet detection — ported from ats-screener (MIT)
METRIC_PATTERNS = [
    r"\d+\s*%",
    r"[$€£]\s*[\d,]+",
    r"\d+\s*(?:x|times)\b",
    r"\d+\+?\s*(?:users?|customers?|clients?|projects?|people|engineers?|"
    r"requests?|services?|teams?|countries|markets?)",
    r"(?:top|first|#)\s*\d+",
    r"\d+\s*(?:hours?|days?|weeks?|months?|years?|ms|seconds?|minutes?)",
    r"\d{1,3}(?:,\d{3})+",
    r"\d+\s*(?:million|billion|thousand|k|m|b)\b",
    r"\bp\d{2}\b",
]
METRIC_RE = re.compile("|".join(METRIC_PATTERNS), re.IGNORECASE)
CONNECTIVE_RE = re.compile(r"\b(?:by|via|using|through|to|resulting in)\b", re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")

METRIC_TARGET = 0.40   # ats-screener: ≥40% bullets quantified
XYZ_TARGET = 0.50      # ≥50% bullets impact-shaped (engineering synthesis)


# --- text helpers -----------------------------------------------------------

def strip_tags(text):
    return TAG_RE.sub("", text or "")

def first_token(bullet):
    t = strip_tags(bullet).strip().lower()
    m = re.match(r"[a-z]+", t)
    return m.group(0) if m else ""

def bullet_has_metric(bullet):
    return bool(METRIC_RE.search(strip_tags(bullet)))

def starts_with_strong_verb(bullet):
    return first_token(bullet) in STRONG_VERBS

def starts_with_seniority_verb(bullet):
    return first_token(bullet) in SENIORITY_VERBS

def all_bullets(cv):
    out = []
    for job in cv.get("experience", []):
        out.extend(job.get("bullets", []))
    return out

def cv_text(cv):
    parts = [strip_tags(cv.get("summary", ""))]
    for s in cv.get("skills", []):
        parts.append(s.get("items", ""))
    parts.extend(strip_tags(b) for b in all_bullets(cv))
    return " ".join(parts).lower()


# --- hard gates -------------------------------------------------------------

_SECTION_KEY = {"contact": "contacts", "contacts": "contacts",
                "experience": "experience", "skills": "skills",
                "summary": "summary", "education": "education"}

def run_hard_gates(cv, hard_gates, facts_text=None, pdf_path=None):
    results = []
    for gate, value in hard_gates.items():
        if value in (None, False):
            continue  # gate not enabled

        if gate == "required_sections":
            missing = [name for name in value
                       if not cv.get(_SECTION_KEY.get(name, name))]
            results.append(GateResult(gate, "FAIL" if missing else "PASS",
                                       f"missing: {missing}" if missing else "all present"))

        elif gate == "banned_phrases":
            text = cv_text(cv)
            hits = [p for p in value if p.lower() in text]
            results.append(GateResult(gate, "FAIL" if hits else "PASS",
                                       f"found: {hits}" if hits else "none found"))

        elif gate == "single_column":
            results.append(GateResult(gate, "PASS",
                                       "structural — cv-generator template is single-column"))

        elif gate == "contact_in_body":
            ok = bool(cv.get("contacts"))
            results.append(GateResult(gate, "PASS" if ok else "FAIL",
                                       "contacts in body (schema)" if ok else "no contacts"))

        elif gate == "no_fact_outside_core":
            if not facts_text:
                results.append(GateResult(gate, "SKIPPED", "no facts.md provided"))
            else:
                ftext = facts_text.lower()
                missing = []
                for job in cv.get("experience", []):
                    role = strip_tags(job.get("role", ""))
                    company = re.split(r"[—\-·|@]", role)[-1].strip().lower()
                    if company and company not in ftext:
                        missing.append(company)
                results.append(GateResult(
                    gate, "WARN" if missing else "PASS",
                    f"companies not in facts (provenance): {missing}" if missing
                    else "all companies trace to facts"))

        elif gate == "acronyms_spelled_once":
            results.append(GateResult(gate, "SKIPPED",
                                       "advisory — general acronym detection unreliable"))

        elif gate == "max_pages":
            results.append(_max_pages_gate(value, pdf_path))

        else:
            results.append(GateResult(gate, "SKIPPED", "no checker implemented"))
    return results


def _max_pages_gate(limit, pdf_path):
    if not pdf_path:
        return GateResult("max_pages", "SKIPPED", "render-time gate — pass --pdf to enforce")
    try:
        from pypdf import PdfReader
    except ImportError:
        return GateResult("max_pages", "SKIPPED", "pypdf not installed")
    try:
        n = len(PdfReader(str(pdf_path)).pages)
    except Exception as e:  # noqa: BLE001
        return GateResult("max_pages", "SKIPPED", f"could not read pdf: {e}")
    return GateResult("max_pages", "PASS" if n <= limit else "FAIL",
                      f"{n} page(s), limit {limit}")


def any_blocking_failure(results):
    return any(r.status == "FAIL" for r in results)


# --- soft rubric ------------------------------------------------------------

def _score_metrics(cv, ctx):
    bullets = all_bullets(cv)
    if not bullets:
        return 0.0
    ratio = sum(bullet_has_metric(b) for b in bullets) / len(bullets)
    return min(1.0, ratio / METRIC_TARGET)

def _score_xyz(cv, ctx):
    bullets = all_bullets(cv)
    if not bullets:
        return 0.0
    def xyz(b):
        return (starts_with_strong_verb(b) + bullet_has_metric(b)
                + bool(CONNECTIVE_RE.search(strip_tags(b))))
    ratio = sum(xyz(b) >= 2 for b in bullets) / len(bullets)
    return min(1.0, ratio / XYZ_TARGET)

def _score_keyword_coverage(cv, ctx):
    ksets = ctx.get("keyword_sets") or {}
    terms = [t.lower() for terms in ksets.values() for t in terms]
    if not terms:
        return None  # no keyword sets -> not applicable
    text = cv_text(cv)
    hit = sum(1 for t in terms if t in text)
    return hit / len(terms)

def _score_seniority_frontloaded(cv, ctx):
    jobs = cv.get("experience", [])
    if not jobs:
        return 0.0
    hits = sum(1 for j in jobs if j.get("bullets")
               and starts_with_seniority_verb(j["bullets"][0]))
    return hits / len(jobs)

def _score_recent_first(cv, ctx):
    jobs = cv.get("experience", [])
    if not jobs or not jobs[0].get("bullets"):
        return 0.0
    b = jobs[0]["bullets"][0]
    return 1.0 if (bullet_has_metric(b) or starts_with_strong_verb(b)) else 0.0

def _score_ai_eval(cv, ctx):
    ksets = ctx.get("keyword_sets") or {}
    ai_terms = [t.lower() for t in ksets.get("ai_differentiator", [])]
    if not ai_terms:
        return None
    ai_bullets = [strip_tags(b).lower() for b in all_bullets(cv)
                  if any(t in strip_tags(b).lower() for t in ai_terms)]
    if not ai_bullets:
        return None
    signal = re.compile(r"\b(eval|evaluation|benchmark|precision|recall|latency|"
                        r"scale|throughput|p\d{2}|accuracy|%)\b", re.IGNORECASE)
    hits = sum(1 for b in ai_bullets if signal.search(b))
    return hits / len(ai_bullets)

SCORERS = {
    "bullets_have_metrics": _score_metrics,
    "xyz_formula": _score_xyz,
    "jd_keyword_coverage": _score_keyword_coverage,
    "stack_keyword_coverage": _score_keyword_coverage,
    "seniority_verbs_frontloaded": _score_seniority_frontloaded,
    "seniority_ownership_verbs": _score_seniority_frontloaded,
    "recent_role_signal_first": _score_recent_first,
    "ai_bullets_lead_with_eval_or_scale": _score_ai_eval,
}

def run_soft_rubric(cv, soft_rubric, keyword_sets=None):
    ctx = {"keyword_sets": keyword_sets or {}}
    items, num, den = {}, 0.0, 0.0
    for key, weight in soft_rubric.items():
        scorer = SCORERS.get(key)
        if scorer is None:
            items[key] = {"status": "no-scorer", "weight": weight}
            continue
        score = scorer(cv, ctx)
        if score is None:
            items[key] = {"status": "n/a", "weight": weight}
            continue
        items[key] = {"score": round(score, 3), "weight": weight}
        num += score * weight
        den += weight
    total = round(100 * num / den, 1) if den else 0.0
    return {"total": total, "items": items}


# --- rules loading (resolve extends) ----------------------------------------

def load_rules(path):
    path = Path(path)
    rules = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    parent_name = rules.get("extends")
    if parent_name:
        # convention: parent is master.rules.yaml in the same dir
        parent_path = path.parent / "master.rules.yaml"
        if parent_path.exists():
            parent = yaml.safe_load(parent_path.read_text(encoding="utf-8")) or {}
            merged_hard = {**(parent.get("hard_gates") or {}), **(rules.get("hard_gates") or {})}
            merged_soft = {**(parent.get("soft_rubric") or {}), **(rules.get("soft_rubric") or {})}
            rules["hard_gates"] = merged_hard
            rules["soft_rubric"] = merged_soft
    rules.setdefault("hard_gates", {})
    rules.setdefault("soft_rubric", {})
    rules.setdefault("keyword_sets", {})
    return rules


# --- CLI --------------------------------------------------------------------

def _fmt(results, soft):
    icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️ ", "SKIPPED": "➖"}
    lines = ["HARD GATES:"]
    for r in results:
        lines.append(f"  {icon.get(r.status, '?')} {r.name}: {r.status} — {r.detail}")
    lines.append(f"\nSOFT RUBRIC: {soft['total']}/100")
    for key, info in soft["items"].items():
        if "score" in info:
            lines.append(f"  • {key}: {info['score']} (w{info['weight']})")
        else:
            lines.append(f"  • {key}: {info['status']} (w{info['weight']})")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Enforce spec rules.yaml against a cv.json")
    ap.add_argument("cv")
    ap.add_argument("rules")
    ap.add_argument("--pdf", help="rendered PDF, to enforce max_pages")
    ap.add_argument("--facts", help="facts.md, to enforce no_fact_outside_core")
    args = ap.parse_args(argv)

    cv = json.loads(Path(args.cv).read_text(encoding="utf-8"))
    rules = load_rules(args.rules)
    facts_text = Path(args.facts).read_text(encoding="utf-8") if args.facts else None

    results = run_hard_gates(cv, rules["hard_gates"], facts_text=facts_text, pdf_path=args.pdf)
    soft = run_soft_rubric(cv, rules["soft_rubric"], keyword_sets=rules.get("keyword_sets"))

    print(_fmt(results, soft))
    if any_blocking_failure(results):
        print("\nRESULT: BLOCKED (hard gate failed)")
        return 1
    print("\nRESULT: PASS (hard gates) — soft score advisory")
    return 0


if __name__ == "__main__":
    sys.exit(main())
