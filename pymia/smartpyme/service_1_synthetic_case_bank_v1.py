from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "SERVICE_1_SYNTHETIC_CASE_BANK_V1"
SERVICE_NAME = "SERVICE_1"

STATUS_REGRESSION_READY = "REGRESSION_READY"
STATUS_FIXTURE_MISSING = "FIXTURE_MISSING"
STATUS_INCOMPLETE_SPEC = "INCOMPLETE_SPEC"

CASE_KIND_CANONICAL_CLI = "CANONICAL_CLI"
CASE_KIND_TOOL_PROBE = "TOOL_PROBE"

REQUIRED_COVERAGE = (
    "precio_margen_basico",
    "caja_diaria_triage",
    "gastos_triage",
    "proveedores_precio_variacion_triage",
)


@dataclass(frozen=True)
class Service1SyntheticCaseSpecV1:
    case_id: str
    title: str
    kind: str
    input_xlsx_path: str
    tool_requests_path: str | None
    expected_artifacts: tuple[str, ...]
    covered_tool_refs: tuple[str, ...]
    expected_delivery_status: str
    expected_human_review_status: str
    runtime_authorized: bool
    autonomous_use_authorized: bool
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["expected_artifacts"] = list(self.expected_artifacts)
        data["covered_tool_refs"] = list(self.covered_tool_refs)
        data["notes"] = list(self.notes)
        return data


@dataclass(frozen=True)
class Service1SyntheticCaseBankValidationV1:
    schema_version: str
    service_name: str
    status: str
    base_dir: str
    total_cases: int
    ready_case_ids: tuple[str, ...]
    blocked_case_ids: tuple[str, ...]
    missing_coverage: tuple[str, ...]
    case_results: tuple[dict[str, Any], ...]
    runtime_authorized: bool
    autonomous_use_authorized: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["ready_case_ids"] = list(self.ready_case_ids)
        data["blocked_case_ids"] = list(self.blocked_case_ids)
        data["missing_coverage"] = list(self.missing_coverage)
        data["case_results"] = list(self.case_results)
        return data


def service_1_synthetic_case_bank_v1() -> tuple[Service1SyntheticCaseSpecV1, ...]:
    return (
        Service1SyntheticCaseSpecV1(
            case_id="S1_SYNTH_001_CAFETERIA_CASH_MARGIN",
            title="Cafeteria cash and margin canonical CLI regression",
            kind=CASE_KIND_CANONICAL_CLI,
            input_xlsx_path="SERVICE_1_SYNTHETIC_CASE_001_CAFETERIA_CASH_MARGIN.xlsx",
            tool_requests_path="SERVICE_1_SYNTHETIC_CASE_001_OUTPUT/tool_requests.json",
            expected_artifacts=(
                "operator_packet.json",
                "pipeline_result.json",
                "post_tool_owner_delivery_summary.md",
                "human_review_gate.json",
                "final_qa_delivery_gate.json",
                "manifest.json",
            ),
            covered_tool_refs=("precio_margen_basico", "caja_diaria_triage"),
            expected_delivery_status="READY_FOR_HUMAN_REVIEW",
            expected_human_review_status="PENDING_HUMAN_REVIEW",
            runtime_authorized=False,
            autonomous_use_authorized=False,
            notes=("Canonical regression case; regression-only, without commercial claim.",),
        ),
        Service1SyntheticCaseSpecV1(
            case_id="S1_SYNTH_002_GASTOS_TRIAGE_PROBE",
            title="Gastos triage tool-probe regression",
            kind=CASE_KIND_TOOL_PROBE,
            input_xlsx_path="cafeteria_abc.xlsx",
            tool_requests_path="SERVICE_1_GASTOS_TRIAGE_RUN_OUTPUT/tool_requests_gastos_triage.json",
            expected_artifacts=(
                "SERVICE_1_GASTOS_TRIAGE_RUN_OUTPUT/gastos_triage_result.json",
                "SERVICE_1_GASTOS_TRIAGE_RUN_OUTPUT/mapping_decision.json",
                "SERVICE_1_GASTOS_TRIAGE_RUN_OUTPUT/workbook_structure.json",
            ),
            covered_tool_refs=("gastos_triage",),
            expected_delivery_status="TOOL_PROBE_RECORDED",
            expected_human_review_status="HUMAN_REVIEW_REQUIRED",
            runtime_authorized=False,
            autonomous_use_authorized=False,
            notes=("Probe case documents regression evidence only; no fiscal classification claim.",),
        ),
        Service1SyntheticCaseSpecV1(
            case_id="S1_SYNTH_003_PROVEEDORES_PRECIO_VARIACION_PROBE",
            title="Proveedores price variation tool-probe regression",
            kind=CASE_KIND_TOOL_PROBE,
            input_xlsx_path="cafeteria_abc.xlsx",
            tool_requests_path=None,
            expected_artifacts=(
                "SERVICE_1_PROVEEDORES_PRECIO_VARIACION_RUN_OUTPUT/proveedores_precio_variacion_result.json",
                "SERVICE_1_PROVEEDORES_PRECIO_VARIACION_RUN_OUTPUT/mapping_decision.json",
                "SERVICE_1_PROVEEDORES_PRECIO_VARIACION_RUN_OUTPUT/workbook_structure.json",
            ),
            covered_tool_refs=("proveedores_precio_variacion_triage",),
            expected_delivery_status="TOOL_PROBE_RECORDED",
            expected_human_review_status="HUMAN_REVIEW_REQUIRED",
            runtime_authorized=False,
            autonomous_use_authorized=False,
            notes=("Probe case documents supplier price variation regression only.",),
        ),
        Service1SyntheticCaseSpecV1(
            case_id="S1_SYNTH_004_CAJA_DIARIA_POR_FECHA_PROBE",
            title="Caja diaria por fecha tool-probe regression",
            kind=CASE_KIND_TOOL_PROBE,
            input_xlsx_path="cafeteria_abc.xlsx",
            tool_requests_path=None,
            expected_artifacts=(
                "SERVICE_1_CAJA_DIARIA_POR_FECHA_RUN_OUTPUT/caja_por_fecha_result.json",
                "SERVICE_1_CAJA_DIARIA_POR_FECHA_RUN_OUTPUT/mapping_decision.json",
                "SERVICE_1_CAJA_DIARIA_POR_FECHA_RUN_OUTPUT/SERVICE_1_CAJA_DIARIA_POR_FECHA_CLOSEOUT.md",
            ),
            covered_tool_refs=("caja_diaria_triage",),
            expected_delivery_status="TOOL_PROBE_RECORDED",
            expected_human_review_status="HUMAN_REVIEW_REQUIRED",
            runtime_authorized=False,
            autonomous_use_authorized=False,
            notes=("Probe case records daily cash regression by date without bank reconciliation claim.",),
        ),
    )


def _case_result(*, base: Path, spec: Service1SyntheticCaseSpecV1) -> dict[str, Any]:
    missing: list[str] = []
    input_path = base / spec.input_xlsx_path
    if not input_path.is_file():
        missing.append(spec.input_xlsx_path)
    if spec.tool_requests_path is not None and not (base / spec.tool_requests_path).is_file():
        missing.append(spec.tool_requests_path)
    for artifact in spec.expected_artifacts:
        if not (base / artifact).exists():
            missing.append(artifact)
    status = STATUS_REGRESSION_READY if not missing else STATUS_FIXTURE_MISSING
    if not spec.case_id or not spec.covered_tool_refs:
        status = STATUS_INCOMPLETE_SPEC
    return {
        "case_id": spec.case_id,
        "kind": spec.kind,
        "status": status,
        "missing_paths": missing,
        "covered_tool_refs": list(spec.covered_tool_refs),
        "runtime_authorized": spec.runtime_authorized,
        "autonomous_use_authorized": spec.autonomous_use_authorized,
    }


def validate_service_1_synthetic_case_bank_v1(*, base_dir: str | Path, cases: tuple[Service1SyntheticCaseSpecV1, ...] | None = None) -> Service1SyntheticCaseBankValidationV1:
    base = Path(base_dir)
    selected_cases = cases if cases is not None else service_1_synthetic_case_bank_v1()
    results = tuple(_case_result(base=base, spec=spec) for spec in selected_cases)
    ready = tuple(result["case_id"] for result in results if result["status"] == STATUS_REGRESSION_READY)
    blocked = tuple(result["case_id"] for result in results if result["status"] != STATUS_REGRESSION_READY)
    covered = {tool for spec in selected_cases for tool in spec.covered_tool_refs}
    missing_coverage = tuple(tool for tool in REQUIRED_COVERAGE if tool not in covered)
    status = STATUS_REGRESSION_READY if not blocked and not missing_coverage else STATUS_FIXTURE_MISSING
    return Service1SyntheticCaseBankValidationV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        base_dir=str(base),
        total_cases=len(selected_cases),
        ready_case_ids=ready,
        blocked_case_ids=blocked,
        missing_coverage=missing_coverage,
        case_results=results,
        runtime_authorized=False,
        autonomous_use_authorized=False,
        metadata={
            "hardening_scope": "S1_FULL_ASSISTED_V1_HARDENING",
            "does_not_reopen_full_assisted_v1_closure": True,
            "not_a_demo": True,
        },
    )


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_REGRESSION_READY",
    "STATUS_FIXTURE_MISSING",
    "STATUS_INCOMPLETE_SPEC",
    "CASE_KIND_CANONICAL_CLI",
    "CASE_KIND_TOOL_PROBE",
    "REQUIRED_COVERAGE",
    "Service1SyntheticCaseSpecV1",
    "Service1SyntheticCaseBankValidationV1",
    "service_1_synthetic_case_bank_v1",
    "validate_service_1_synthetic_case_bank_v1",
]
