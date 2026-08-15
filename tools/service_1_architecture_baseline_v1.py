from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

VERDICT_PASS = "PASS_ARCHITECTURE_BASELINE_V1"
VERDICT_BLOCK = "BLOCK_ARCHITECTURE_BASELINE_V1"

BEHAVIOR_TESTS = (
    "tests/smartpyme/test_service_1_owner_confirmation_event_v1.py",
    "tests/smartpyme/test_service_1_p6_approval_decision_v1.py",
    "tests/smartpyme/test_service_1_computability_v1.py",
    "tests/smartpyme/test_service_1_requirement_match_v1.py",
    "tests/smartpyme/test_service_1_generic_capability_kernel_v1.py",
    "tests/smartpyme/test_service_1_canonical_ingestion_output_to_semantic_bridge_v1.py",
    "tests/smartpyme/test_service_1_product_pipeline_v1.py",
    "tests/smartpyme/test_service_1_canonical_ingestion_to_region_evidence_adapter_v1.py",
    "tests/smartpyme/test_service_1_pyme_011_productive_root_v1.py",
    "tests/smartpyme/test_service_1_ren_001_productive_root_v1.py",
)

TEMPORARY_ADAPTER = "service_1_canonical_ingestion_to_region_evidence_adapter_v1"
ROOT_MODULE = "service_1_product_pipeline_v1"


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_registry(root: Path) -> dict:
    return json.loads((root / "docs" / "service_1_module_disposition.v1.json").read_text(encoding="utf-8"))


def _productive_importers(registry: dict, module_name: str) -> list[str]:
    return sorted(
        item["module"]
        for item in registry["modules"]
        if item.get("disposition") == "PRODUCTIVE"
        and module_name in tuple(item.get("imports_service_1") or ())
    )


def structural_checks(root: Path) -> list[Check]:
    registry = _load_registry(root)
    modules = list(registry.get("modules") or [])
    productive = [item for item in modules if item.get("disposition") == "PRODUCTIVE"]
    roots = [item for item in productive if item.get("module") == registry.get("canonical_product_root")]

    deterministic_source = (root / "pymia" / "smartpyme" / "service_1_deterministic_semantic_pipeline_v1.py").read_text(encoding="utf-8")
    product_source = (root / "pymia" / "smartpyme" / "service_1_product_pipeline_v1.py").read_text(encoding="utf-8")
    gate_source = (root / "pymia" / "smartpyme" / "service_1_semantic_bridge_to_controlled_execution_gate_v1.py").read_text(encoding="utf-8")
    owner_loop_source = (root / "pymia" / "smartpyme" / "service_1_controlled_execution_candidate_to_owner_confirmation_loop_v1.py").read_text(encoding="utf-8")
    reinjection_source = (root / "pymia" / "smartpyme" / "service_1_owner_confirmation_reinjection_to_semantic_gate_v1.py").read_text(encoding="utf-8")
    owner_event_path = root / "pymia" / "smartpyme" / "service_1_owner_confirmation_event_v1.py"
    p6_path = root / "pymia" / "smartpyme" / "service_1_p6_approval_decision_v1.py"
    p7_source = (root / "pymia" / "smartpyme" / "service_1_variable_family_bindings_v1.py").read_text(encoding="utf-8")
    p8_path = root / "pymia" / "smartpyme" / "service_1_computability_v1.py"
    p8_source = p8_path.read_text(encoding="utf-8") if p8_path.exists() else ""
    canonical_bridge_source = (root / "pymia" / "smartpyme" / "service_1_canonical_ingestion_output_to_semantic_bridge_v1.py").read_text(encoding="utf-8")
    generic_engine_source = (root / "pymia" / "smartpyme" / "service_1_generic_capability_engine_v1.py").read_text(encoding="utf-8")

    legacy_computation_plan_projection_removed = (
        "def build_computation_plan(" not in deterministic_source
        and "SERVICE_1_COMPUTATION_PLAN_V1" not in deterministic_source
    )
    post_p6_rebinding = "build_service_1_semantic_evidence_binding_result_v1(" in deterministic_source
    fused_p7_p8 = "P7/P8" in deterministic_source
    gate_owns_questions = "owner_questions" in gate_source and "_owner_questions(" in gate_source
    gate_owns_family_matching = "build_service_1_variable_family_bindings_v1(" in gate_source
    capability_branch_count = product_source.count("requested_capability ==")
    temp_importers = _productive_importers(registry, TEMPORARY_ADAPTER)
    owner_event_authority = (
        owner_event_path.exists()
        and "build_service_1_owner_confirmation_event_v1(" in owner_loop_source
        and "owner_confirmation_events" in reinjection_source
    )
    p6_authority = (
        p6_path.exists()
        and "build_service_1_p6_approval_decisions_v1(" in gate_source
        and "p6_decisions" in gate_source
    )
    p7_authority = (
        "class Service1RequirementMatchV1" in p7_source
        and "class Service1GrainV1" in p7_source
        and "def build_service_1_requirement_matches_v1(" in p7_source
        and "build_service_1_requirement_matches_v1(" in gate_source
        and "project_service_1_requirement_matches_to_variable_family_bindings_v1(" in gate_source
    )
    p8_authority = (
        p8_path.exists()
        and "class Service1ComputabilityDecisionV1" in p8_source
        and "class Service1GovernedComputationInputV1" in p8_source
        and "build_service_1_computability_decision_v1(" in deterministic_source
        and "build_service_1_semantic_evidence_binding_result_v1(" not in deterministic_source
        and legacy_computation_plan_projection_removed
    )
    pre_p6_p7_removed = "build_service_1_variable_family_bindings_v1(" not in canonical_bridge_source
    semantic_binding_projection_removed = "semantic_binding_result" not in deterministic_source
    generic_execution_consumes_governed_input = (
        "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1" in generic_engine_source
        and "governed_computation_input" in generic_engine_source
        and "_execution_input_payload(" in generic_engine_source
    )
    generic_legacy_fallback_removed = (
        "legacy_computation_plan" not in generic_engine_source
        and "SERVICE_1_COMPUTATION_PLAN_V1" not in generic_engine_source
    )
    product_root_executes_p8_directly = (
        "build_computability_decision_from_confirmed_bindings_v1(" in product_source
        and "build_computation_plan(" not in product_source
        and "SERVICE_1_COMPUTATION_PLAN_V1" not in product_source
        and '"governed_computation_input"' in product_source
        and '"computability_decision"' in product_source
    )
    allowed_legacy_plan_modules = {
        "service_1_liq_002_evaluator_v1",
        "service_1_pyme_011_evaluator_v1",
    }
    legacy_plan_modules = {
        path.stem
        for path in (root / "pymia" / "smartpyme").glob("service_1_*.py")
        if "SERVICE_1_COMPUTATION_PLAN_V1" in path.read_text(encoding="utf-8")
    }
    legacy_plan_references_bounded = legacy_plan_modules <= allowed_legacy_plan_modules
    liq001_source = (root / "pymia" / "smartpyme" / "service_1_liq_001_evaluator_v1.py").read_text(encoding="utf-8")
    ren001_source = (root / "pymia" / "smartpyme" / "service_1_ren_001_evaluator_v1.py").read_text(encoding="utf-8")
    pyme013_source = (root / "pymia" / "smartpyme" / "service_1_pyme_013_composite_v1.py").read_text(encoding="utf-8") if (root / "pymia" / "smartpyme" / "service_1_pyme_013_composite_v1.py").exists() else ""
    generic_engine_module = next((item for item in productive if item.get("module") == "service_1_generic_capability_engine_v1"), None)
    generic_kernel_in_root_closure = generic_engine_module is not None and generic_engine_module.get("canonical_root_reachable") is True
    liq002_pyme011_productive = [item for item in modules if item.get("module", "").startswith("service_1_liq_002_") or item.get("module", "").startswith("service_1_pyme_011_") if item.get("disposition") == "PRODUCTIVE"]
    liq001_uses_governed_input = "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1" in liq001_source
    ren001_uses_governed_input = "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1" in ren001_source
    pyme013_uses_governed_input = "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1" in pyme013_source
    legacy_plan_not_authority = (
        liq001_uses_governed_input
        and ren001_uses_governed_input
        and (pyme013_uses_governed_input if pyme013_source else True)
        and generic_legacy_fallback_removed
        and product_root_executes_p8_directly
    )

    checks = [
        Check(
            "ONE_CANONICAL_PRODUCT_ROOT",
            registry.get("canonical_product_root") == ROOT_MODULE and len(roots) == 1,
            f"canonical_product_root={registry.get('canonical_product_root')!r}; matching_productive_roots={len(roots)}",
        ),
        Check(
            "TEMPORARY_PACKAGE1_ADAPTER_OUTSIDE_PRODUCTIVE_PATH",
            not temp_importers,
            f"productive_importers={temp_importers}",
        ),
        Check(
            "OWNER_CONFIRMATION_EVENT_AUTHORITY_PRESENT",
            owner_event_authority,
            "owner confirmation loop emits canonical events and reinjection consumes them"
            if owner_event_authority
            else "canonical owner confirmation event authority not fully wired",
        ),
        Check(
            "P6_APPROVAL_DECISION_AUTHORITY_PRESENT",
            p6_authority,
            "controlled execution compatibility gate delegates semantic approval to canonical P6 decisions"
            if p6_authority
            else "canonical P6 approval authority not fully wired",
        ),
        Check(
            "P7_REQUIREMENT_MATCH_AUTHORITY_PRESENT",
            p7_authority,
            "canonical RequirementMatch and Grain authorities are wired after P6; legacy variable-family binding is projection only"
            if p7_authority
            else "canonical P7 RequirementMatch/Grain authority not fully wired",
        ),
        Check(
            "P8_COMPUTABILITY_AUTHORITY_PRESENT",
            p8_authority,
            "canonical ComputabilityDecision and GovernedComputationInput are wired without semantic rebinding"
            if p8_authority
            else "canonical P8 computability authority not fully wired",
        ),
        Check(
            "LEGACY_COMPUTATION_PLAN_PROJECTION_REMOVED",
            legacy_computation_plan_projection_removed,
            "deterministic semantic pipeline no longer exposes ComputationPlanV1 compatibility projection"
            if legacy_computation_plan_projection_removed
            else "legacy build_computation_plan/ComputationPlanV1 projection remains in deterministic semantic pipeline",
        ),
        Check(
            "NO_P7_MATCHING_BEFORE_P6",
            pre_p6_p7_removed,
            "canonical ingestion stops at semantic candidates; P7 starts only after P6"
            if pre_p6_p7_removed
            else "canonical ingestion still performs variable-family/P7 matching before P6",
        ),
        Check(
            "GENERIC_EXECUTION_CONSUMES_GOVERNED_INPUT",
            generic_execution_consumes_governed_input,
            "generic execution consumes canonical Service1GovernedComputationInputV1"
            if generic_execution_consumes_governed_input
            else "generic execution does not consume canonical governed computation input",
        ),
        Check(
            "GENERIC_KERNEL_HAS_NO_LEGACY_PLAN_FALLBACK",
            generic_legacy_fallback_removed,
            "generic kernel has no ComputationPlanV1 fallback path"
            if generic_legacy_fallback_removed
            else "generic kernel still contains a legacy computation-plan fallback",
        ),
        Check(
            "PRODUCT_ROOT_EXECUTES_P8_DIRECTLY",
            product_root_executes_p8_directly,
            "product root builds/exports computability decision and governed input without ComputationPlanV1"
            if product_root_executes_p8_directly
            else "product root still depends on ComputationPlanV1 or does not expose direct P8 authority",
        ),
        Check(
            "LEGACY_PLAN_REFERENCES_BOUNDED_TO_PROJECTION_OR_SUPPORT",
            legacy_plan_references_bounded,
            f"legacy plan modules={sorted(legacy_plan_modules)}; allowed={sorted(allowed_legacy_plan_modules)}",
        ),
        Check(
            "NO_SEMANTIC_BINDING_COMPATIBILITY_PROJECTION",
            semantic_binding_projection_removed,
            "legacy semantic_binding_result projection removed from computation plan"
            if semantic_binding_projection_removed
            else "semantic_binding_result compatibility projection remains active",
        ),
        Check(
            "LEGACY_COMPUTATION_PLAN_NOT_EXECUTION_AUTHORITY",
            legacy_plan_not_authority,
            "all productive execution engines consume Service1GovernedComputationInputV1; legacy plan is not execution authority"
            if legacy_plan_not_authority
            else "one or more productive engines still accept legacy computation plan as execution authority",
        ),
        Check(
            "GENERIC_KERNEL_IS_IN_PRODUCTIVE_ROOT_CLOSURE",
            generic_kernel_in_root_closure,
            "generic capability engine is PRODUCTIVE with canonical_root_reachable=true"
            if generic_kernel_in_root_closure
            else "generic capability engine is not in the productive root closure",
        ),
        Check(
            "NO_PRODUCTIVE_SPECIALIZED_LIQ002_PYME011_PARALLEL_PATH",
            not liq002_pyme011_productive,
            "specialized LIQ_002/PYME_011 evaluator paths are not PRODUCTIVE; superseded by governed generic kernel"
            if not liq002_pyme011_productive
            else f"specialized LIQ_002/PYME_011 are still PRODUCTIVE: {[m['module'] for m in liq002_pyme011_productive]}",
        ),
        Check(
            "NO_SEMANTIC_REBIND_AFTER_P6",
            not post_p6_rebinding,
            "build_computation_plan re-runs semantic evidence binding" if post_p6_rebinding else "no rebinding detected",
        ),
        Check(
            "P7_P8_BOUNDARIES_NOT_FUSED",
            not fused_p7_p8,
            "deterministic semantic pipeline explicitly owns a combined P7/P8 computation plan" if fused_p7_p8 else "P7/P8 are separated",
        ),
        Check(
            "OWNER_CONFIRMATION_NOT_OWNED_BY_CONTROLLED_EXECUTION_GATE",
            not gate_owns_questions,
            "controlled execution gate constructs owner questions" if gate_owns_questions else "owner questions are outside controlled execution gate",
        ),
        Check(
            "P6_GATE_DOES_NOT_OWN_P7_FAMILY_MATCHING",
            not gate_owns_family_matching,
            "controlled execution gate builds variable-family bindings" if gate_owns_family_matching else "family matching is outside P6 gate",
        ),
        Check(
            "CAPABILITY_EXTENSION_WITHOUT_ROOT_BRANCH_PROLIFERATION",
            capability_branch_count <= 2,
            f"requested_capability-specific branches in product root={capability_branch_count}; target<=2",
        ),
    ]
    return checks


def run_behavior_suite(root: Path) -> tuple[bool, str]:
    command = [sys.executable, "-m", "pytest", "-q", *BEHAVIOR_TESTS]
    completed = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
    summary = (completed.stdout + completed.stderr).strip()
    return completed.returncode == 0, summary


def build_report(root: Path, *, run_behavior: bool) -> dict:
    checks = structural_checks(root)
    behavior_passed = None
    behavior_output = "SKIPPED"
    if run_behavior:
        behavior_passed, behavior_output = run_behavior_suite(root)
    blockers = [check.check_id for check in checks if not check.passed]
    if behavior_passed is False:
        blockers.append("BEHAVIOR_BASELINE")
    verdict = VERDICT_PASS if not blockers and behavior_passed is not False else VERDICT_BLOCK
    registry = _load_registry(root)
    return {
        "schema_version": "SERVICE_1_ARCHITECTURE_BASELINE_CERTIFICATION_V1",
        "verdict": verdict,
        "behavior_suite": {
            "executed": run_behavior,
            "passed": behavior_passed,
            "tests": list(BEHAVIOR_TESTS),
            "output": behavior_output,
        },
        "structural_checks": [asdict(check) for check in checks],
        "blockers": blockers,
        "metrics": {
            "service1_modules": registry.get("total_modules"),
            "productive": registry.get("counts", {}).get("PRODUCTIVE"),
            "support_necessary": registry.get("counts", {}).get("SUPPORT_NECESSARY"),
            "canonical_product_roots": 1 if registry.get("canonical_product_root") == ROOT_MODULE else 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Servicio 1 architecture baseline certification V1")
    parser.add_argument("--report-only", action="store_true", help="Always exit 0; keep BLOCK verdict in report.")
    parser.add_argument("--skip-behavior", action="store_true", help="Run structural checks only.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    args = parser.parse_args()

    report = build_report(_repo_root(), run_behavior=not args.skip_behavior)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(report["verdict"])
        print("BEHAVIOR:", "PASS" if report["behavior_suite"]["passed"] else report["behavior_suite"]["passed"])
        for check in report["structural_checks"]:
            print(f"{'PASS' if check['passed'] else 'BLOCK'} {check['check_id']}: {check['detail']}")
        print("BLOCKERS:", ", ".join(report["blockers"]) if report["blockers"] else "NONE")

    if args.report_only:
        return 0
    return 0 if report["verdict"] == VERDICT_PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())

