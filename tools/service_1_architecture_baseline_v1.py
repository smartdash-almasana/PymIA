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

    computation_section = deterministic_source.split("def build_computation_plan", 1)[1] if "def build_computation_plan" in deterministic_source else ""
    post_p6_rebinding = "build_service_1_semantic_evidence_binding_result_v1(" in computation_section
    fused_p7_p8 = "P7/P8" in computation_section or "P7/P8" in deterministic_source
    gate_owns_questions = "owner_questions" in gate_source and "_owner_questions(" in gate_source
    gate_owns_family_matching = "build_service_1_variable_family_bindings_v1(" in gate_source
    capability_branch_count = product_source.count("requested_capability ==")
    temp_importers = _productive_importers(registry, TEMPORARY_ADAPTER)
    owner_event_authority = (
        owner_event_path.exists()
        and "build_service_1_owner_confirmation_event_v1(" in owner_loop_source
        and "owner_confirmation_events" in reinjection_source
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
