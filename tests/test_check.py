"""Tests for check.py — the spec rules.yaml enforcer."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import check  # noqa: E402


# --- fixtures ---------------------------------------------------------------

MASTER_RULES = {
    "version": 1,
    "level": "@master",
    "hard_gates": {
        "max_pages": 2,
        "single_column": True,
        "contact_in_body": True,
        "required_sections": ["contact", "experience", "skills"],
        "banned_phrases": ["responsible for", "helped to", "assisted with"],
        "no_fact_outside_core": True,
        "acronyms_spelled_once": True,
    },
    "soft_rubric": {
        "bullets_have_metrics": 3,
        "xyz_formula": 2,
        "jd_keyword_coverage": 3,
        "seniority_verbs_frontloaded": 2,
        "recent_role_signal_first": 2,
    },
}


def clean_cv():
    return {
        "name": "First Last",
        "title": "Senior Fullstack Engineer",
        "location": "Remote (UTC-3)",
        "contacts": [{"label": "you@example.com", "href": "mailto:you@example.com"}],
        "summary": "Senior engineer with 7 years building TypeScript systems.",
        "skills": [{"group": "Primary", "items": "TypeScript, React, Node, PostgreSQL"}],
        "experience": [
            {
                "role": "Senior Engineer — Acme",
                "date": "01/2023 – Present",
                "ctx": "LLM product · Remote",
                "bullets": [
                    "Architected a RAG pipeline cutting latency by 40% using caching.",
                    "Owned the backend API end-to-end serving 50k requests/day.",
                ],
            },
            {
                "role": "Engineer — Globex",
                "date": "01/2020 – 12/2022",
                "ctx": "Web app · Remote",
                "bullets": ["Built features improving conversion by 12%."],
            },
        ],
        "languages": "English (C1)",
    }


# --- hard gates -------------------------------------------------------------

def test_required_sections_pass_on_clean_cv():
    results = check.run_hard_gates(clean_cv(), MASTER_RULES["hard_gates"])
    rs = next(r for r in results if r.name == "required_sections")
    assert rs.status == "PASS", rs.detail


def test_required_sections_fail_when_skills_missing():
    cv = clean_cv()
    cv["skills"] = []
    results = check.run_hard_gates(cv, MASTER_RULES["hard_gates"])
    rs = next(r for r in results if r.name == "required_sections")
    assert rs.status == "FAIL"
    assert "skills" in rs.detail


def test_banned_phrases_fail_when_present_in_bullet():
    cv = clean_cv()
    cv["experience"][0]["bullets"].append("Responsible for the deployment process.")
    results = check.run_hard_gates(cv, MASTER_RULES["hard_gates"])
    bp = next(r for r in results if r.name == "banned_phrases")
    assert bp.status == "FAIL"
    assert "responsible for" in bp.detail.lower()


def test_banned_phrases_pass_on_clean_cv():
    results = check.run_hard_gates(clean_cv(), MASTER_RULES["hard_gates"])
    bp = next(r for r in results if r.name == "banned_phrases")
    assert bp.status == "PASS"


def test_acronyms_gate_is_skipped_not_silent():
    results = check.run_hard_gates(clean_cv(), MASTER_RULES["hard_gates"])
    ac = next(r for r in results if r.name == "acronyms_spelled_once")
    assert ac.status == "SKIPPED"


def test_no_fact_outside_core_skipped_without_facts():
    results = check.run_hard_gates(clean_cv(), MASTER_RULES["hard_gates"])
    nf = next(r for r in results if r.name == "no_fact_outside_core")
    assert nf.status == "SKIPPED"


def test_no_fact_outside_core_warns_when_company_not_in_facts():
    facts = "Acme · senior fullstack. did: built RAG."
    results = check.run_hard_gates(clean_cv(), MASTER_RULES["hard_gates"], facts_text=facts)
    nf = next(r for r in results if r.name == "no_fact_outside_core")
    # Globex is not in facts -> WARN (not a hard FAIL, provenance is advisory on stub)
    assert nf.status in ("WARN", "FAIL")
    assert "globex" in nf.detail.lower()


def test_hard_gate_overall_fails_if_any_fail():
    cv = clean_cv()
    cv["skills"] = []
    results = check.run_hard_gates(cv, MASTER_RULES["hard_gates"])
    assert check.any_blocking_failure(results) is True


def test_hard_gate_overall_passes_on_clean():
    results = check.run_hard_gates(clean_cv(), MASTER_RULES["hard_gates"])
    assert check.any_blocking_failure(results) is False


# --- soft rubric ------------------------------------------------------------

def test_metric_detection_counts_quantified_bullets():
    assert check.bullet_has_metric("Cut latency by 40% using caching.") is True
    assert check.bullet_has_metric("Served 50k requests/day.") is True
    assert check.bullet_has_metric("Worked on the backend.") is False


def test_strong_verb_first_detection():
    assert check.starts_with_strong_verb("Architected a pipeline.") is True
    assert check.starts_with_strong_verb("Responsible for the pipeline.") is False


def test_seniority_verb_detection():
    assert check.starts_with_seniority_verb("Owned the API end-to-end.") is True
    assert check.starts_with_seniority_verb("Assisted with testing.") is False


def test_soft_score_is_higher_for_impact_cv_than_duty_cv():
    impact = clean_cv()
    duty = clean_cv()
    for job in duty["experience"]:
        job["bullets"] = ["Responsible for the backend.", "Helped with the frontend."]
    s_impact = check.run_soft_rubric(impact, MASTER_RULES["soft_rubric"], keyword_sets={})
    s_duty = check.run_soft_rubric(duty, MASTER_RULES["soft_rubric"], keyword_sets={})
    assert s_impact["total"] > s_duty["total"]
    assert 0 <= s_impact["total"] <= 100


# --- rules loading / extends ------------------------------------------------

def test_load_rules_resolves_extends(tmp_path):
    (tmp_path / "master.rules.yaml").write_text(
        "version: 1\nlevel: '@master'\n"
        "hard_gates:\n  single_column: true\n  required_sections: [contact, experience, skills]\n"
        "soft_rubric:\n  bullets_have_metrics: 3\n"
    )
    (tmp_path / "fullstack-ts.rules.yaml").write_text(
        "version: 1\nlevel: '@title:fullstack-ts'\nextends: '@master'\n"
        "hard_gates: {}\n"
        "soft_rubric:\n  stack_keyword_coverage: 3\n"
        "keyword_sets:\n  core: [typescript, react]\n"
    )
    rules = check.load_rules(tmp_path / "fullstack-ts.rules.yaml")
    # inherits master hard gate
    assert rules["hard_gates"]["single_column"] is True
    assert rules["hard_gates"]["required_sections"] == ["contact", "experience", "skills"]
    # merges soft rubric from both
    assert "bullets_have_metrics" in rules["soft_rubric"]
    assert "stack_keyword_coverage" in rules["soft_rubric"]
    assert rules["keyword_sets"]["core"] == ["typescript", "react"]
