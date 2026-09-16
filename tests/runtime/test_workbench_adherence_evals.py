"""Contract checks for evidence-derived Workbench conformance evals."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = ROOT / "tests" / "comparison" / "workbench-adherence" / "cases.json"

REQUIRED_CASES = {
    "required-method-composition",
    "repository-store-preflight",
    "orthogonal-human-decisions",
    "quantitative-claim-provenance",
    "post-start-contract-correction",
    "authorization-source-fidelity",
}


def load_cases() -> dict:
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def by_id(document: dict) -> dict[str, dict]:
    return {case["id"]: case for case in document["cases"]}


def test_adherence_eval_catalog_covers_every_incident_seam() -> None:
    document = load_cases()
    cases = by_id(document)

    assert set(cases) == REQUIRED_CASES
    assert len(cases) == len(document["cases"])
    for case in cases.values():
        expected = case["expected"]
        assert case["stimulus"].strip()
        assert case["preconditions"]
        assert expected["required_actions"]
        assert expected["forbidden_actions"]
        assert set(expected["required_actions"]).isdisjoint(expected["forbidden_actions"])
        assert expected["observable_result"].strip()
        assert case["failure_caught"].strip()


def test_required_method_case_composes_instead_of_replacing_methods() -> None:
    case = by_id(load_cases())["required-method-composition"]

    assert case["expected"]["required_methods"] == ["workbench", "diagnosing-bugs"]
    assert case["expected"]["first_consequential_action"] == "establish-measurement-loop"
    assert "code-theory-before-measurement" in case["expected"]["forbidden_actions"]


def test_repository_preflight_precedes_first_workbench_mutation() -> None:
    case = by_id(load_cases())["repository-store-preflight"]

    assert case["expected"]["state_effect"] == "no-mutation-until-repository-and-store-resolve"
    assert case["expected"]["first_consequential_action"] == "resolve-repository-and-store"


def test_human_decision_case_keeps_orthogonal_dimensions_separate() -> None:
    case = by_id(load_cases())["orthogonal-human-decisions"]

    assert case["decision_dimensions"] == ["measurement", "delivery-depth"]
    assert case["expected"]["question_count"] == 2
    assert case["expected"]["nonselection_is_decision"] is False


def test_quantitative_claim_requires_observed_or_explicitly_bounded_basis() -> None:
    case = by_id(load_cases())["quantitative-claim-provenance"]

    assert case["expected"]["required_evidence"] == [
        "measurement-command",
        "environment",
        "fixture",
        "observed-result",
    ]
    assert "unmarked-estimate-as-fact" in case["expected"]["forbidden_actions"]
    assert "unsourced-current-price" in case["expected"]["forbidden_actions"]


def test_post_start_correction_cannot_be_replaced_by_an_artifact_override() -> None:
    case = by_id(load_cases())["post-start-contract-correction"]

    assert case["expected"]["state_effect"] == "dependent-work-held-pending-supported-correction"
    assert "artifact-claims-to-supersede-routing" in case["expected"]["forbidden_actions"]


def test_authorization_preserves_exact_source_and_source_time() -> None:
    case = by_id(load_cases())["authorization-source-fidelity"]

    assert case["expected"]["required_evidence"] == [
        "exact-user-source-reference",
        "source-occurrence-time-or-unknown",
    ]
    assert "agent-operation-time-as-grant-time" in case["expected"]["forbidden_actions"]
