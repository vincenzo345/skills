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
    "code-reading-remains-hypothesis",
    "measured-bottleneck-needs-discrimination",
    "aggregate-metrics-do-not-prove-endpoint-cause",
    "single-fixture-does-not-generalize-performance",
    "collaborative-feature-planning",
    "evidence-method-follows-uncertainty",
    "implementation-destination-fidelity",
    "dependent-ticket-frontier",
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


def test_collaborative_delivery_cases_preserve_alignment_and_execution() -> None:
    cases = by_id(load_cases())

    collaborative = cases["collaborative-feature-planning"]["expected"]
    assert collaborative["planning_posture"] == "collaborative"
    assert "confirm-shared-understanding" in collaborative["required_actions"]
    assert "complete-long-proposal-before-confirmation" in collaborative["forbidden_actions"]

    implementation = cases["implementation-destination-fidelity"]["expected"]
    assert implementation["engagement_intent"] == "implement"
    assert implementation["planning_destination"] == "locally-verified-implementation"

    frontier = cases["dependent-ticket-frontier"]["expected"]
    assert frontier["initial_ready"] == ["A", "C"]
    assert frontier["initial_blocked"] == ["B"]


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


def test_code_reading_cannot_establish_a_root_cause() -> None:
    case = by_id(load_cases())["code-reading-remains-hypothesis"]

    assert case["expected"]["allowed_classification"] == "hypothesis"
    assert case["expected"]["root_cause_status"] == "not-established"
    assert "code-path-as-root-cause" in case["expected"]["forbidden_actions"]


def test_measured_bottleneck_needs_a_discriminating_intervention() -> None:
    case = by_id(load_cases())["measured-bottleneck-needs-discrimination"]

    assert case["expected"]["required_evidence"] == [
        "baseline-measurement",
        "discriminating-intervention",
        "end-to-end-result",
    ]
    assert case["expected"]["root_cause_status_before_intervention"] == "not-established"


def test_aggregate_metrics_cannot_establish_an_endpoint_root_cause() -> None:
    case = by_id(load_cases())["aggregate-metrics-do-not-prove-endpoint-cause"]

    assert case["expected"]["allowed_classification"] == "leading-hypothesis"
    assert case["expected"]["root_cause_status"] == "not-established"
    assert "endpoint-scoped-request-identity" in case["expected"]["required_evidence"]
    assert (
        "aggregate-cold-start-rate-as-endpoint-cause"
        in case["expected"]["forbidden_actions"]
    )


def test_single_fixture_measurement_stays_fixture_bounded() -> None:
    case = by_id(load_cases())["single-fixture-does-not-generalize-performance"]

    assert case["expected"]["allowed_classification"] == "fixture-bounded-measurement"
    assert case["expected"]["workload_claim_status"] == "not-established"
    assert "representativeness-boundary" in case["expected"]["required_evidence"]
    assert "single-fixture-as-workload-wide-proof" in case["expected"]["forbidden_actions"]


def test_workbench_routes_remain_executable_without_external_skills() -> None:
    routing = (ROOT / "skills" / "workbench" / "references" / "routing.md").read_text(
        encoding="utf-8"
    )
    discovery = (ROOT / "skills" / "workbench" / "references" / "discovery.md").read_text(
        encoding="utf-8"
    )
    performance = (
        ROOT / "skills" / "workbench" / "references" / "performance-investigation.md"
    ).read_text(encoding="utf-8")

    assert "never as undeclared route prerequisites" in routing
    assert "absence of an optional skill is not itself a blocker" in routing
    assert "shipped by the same repository distribution as Workbench" in discovery
    assert "self-contained" in performance
    assert "external debugging skill is optional" in performance
    assert "do not require a harness-provided diagnosis skill" in (
        ROOT / "skills" / "workbench" / "SKILL.md"
    ).read_text(encoding="utf-8")


def test_reported_workbench_companions_are_shipped() -> None:
    manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    declared = {Path(entry).name for entry in manifest["skills"]}

    assert {"feature-planner", "openai-docs", "research"} <= declared
    for name in ("feature-planner", "openai-docs", "research"):
        assert (ROOT / "skills" / name / "SKILL.md").is_file()
        assert (ROOT / "skills" / name / "agents" / "openai.yaml").is_file()
