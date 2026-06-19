"""Tests for gap.py — spec − core gap engine (collector core)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import gap  # noqa: E402

FACTS = """# facts (stub)
## Acme · 2023
role: senior
### Proj
- did: built a RAG pipeline, designed the API
- stack: TypeScript, React, Node
"""

RULES = {"keyword_sets": {"core": ["typescript", "react", "kubernetes"],
                          "ai": ["rag", "embeddings"]}}


def test_facts_keywords_extracts_stack():
    kws = gap.facts_keywords(FACTS)
    assert "typescript" in kws
    assert "react" in kws
    assert "node" in kws


def test_spec_wanted_flattens_keyword_sets():
    wanted = gap.spec_wanted_keywords(RULES)
    assert wanted == {"typescript", "react", "kubernetes", "rag", "embeddings"}


def test_gap_finds_missing_and_covered():
    result = gap.compute_gap(FACTS, RULES)
    assert "kubernetes" in result["gap"]
    assert "embeddings" in result["gap"]
    assert "typescript" in result["covered"]
    assert "react" in result["covered"]
    assert "kubernetes" not in result["covered"]


def test_questions_cover_gap_and_metrics():
    result = gap.compute_gap(FACTS, RULES)
    qtext = " ".join(result["questions"]).lower()
    assert "kubernetes" in qtext          # gap question
    assert "metric" in qtext               # evidence-bank metric question
    assert any("rag pipeline" in q.lower() for q in result["questions"])


def test_no_gap_when_all_present():
    rules = {"keyword_sets": {"core": ["typescript", "react", "node"]}}
    result = gap.compute_gap(FACTS, rules)
    assert result["gap"] == set()
