from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pandas as pd

from pymia.smartpyme.runtime_bridge import RuntimeExecutionCandidate


def _ready_candidate(runtime_classification: str = "excel_diagnostic") -> dict:
    microservice_name = (
        "excel_diagnostic_worker"
        if runtime_classification == "excel_diagnostic"
        else "supplier_duplicate_check_worker"
    )
    return {
        "tenant_id": "tenant_smoke",
        "intake_id": "intake_smoke_001",
        "runtime_classification": runtime_classification,
        "microservice_name": microservice_name,
        "evidence_ids": ["ev_1"],
        "status": "READY_TO_EXECUTE",
        "can_dispatch": True,
        "blocking_reasons": [],
        "warnings": [],
        "audit_notes": [],
        "created_at": "2026-05-25T00:00:00+00:00",
    }


def _write_excel(path: Path) -> None:
    df = pd.DataFrame(
        {
            "producto": ["A", "B", "C", "C"],
            "ventas": [100, 50, 20, 20],
            "costo": [80, None, 19, 19],
        }
    )
    df.to_excel(path, index=False)


def _write_supplier_excel(path: Path) -> None:
    df = pd.DataFrame(
        {
            "proveedor": ["Proveedor Uno", "Proveedor Uno", "Proveedor Dos", "Proveedor Tres"],
            "cuit": ["30-12345678-9", "30-12345678-9", "30-87654321-0", ""],
            "razon_social": [
                "Proveedor Uno SRL",
                "Proveedor Uno S.R.L.",
                "Proveedor Dos SA",
                "Proveedor Tres SAS",
            ],
        }
    )
    df.to_excel(path, index=False)


def test_import_smoke():
    from pymia.smartpyme.microservice_dispatcher import (  # noqa: F401
        dispatch_candidate,
        MicroserviceExecutionResult,
        EXECUTION_EXECUTED,
        EXECUTION_BLOCKED,
        EXECUTION_UNSUPPORTED,
        EXECUTION_FAILED,
    )


def test_dispatcher_imports_excel_diagnostic():
    source = Path("pymia/smartpyme/microservice_dispatcher.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and (node.module or "") == "pymia.smartpyme.excel_diagnostic":
            found = True
    assert found


def test_excel_synthetic_ready_candidate_executes(tmp_path):
    from pymia.smartpyme.microservice_dispatcher import dispatch_candidate, EXECUTION_EXECUTED

    excel_path = tmp_path / "ventas_costos.xlsx"
    output_dir = tmp_path / "out"
    _write_excel(excel_path)

    result = dispatch_candidate(
        _ready_candidate(),
        evidence_path=excel_path,
        output_dir=output_dir,
    )

    assert result.status == EXECUTION_EXECUTED
    assert result.findings_count > 0
    assert result.output_refs
    md_path = output_dir / "diagnostic_report.md"
    assert md_path.exists()
    assert "SmartPyme Excel Diagnostic Slice" in md_path.read_text(encoding="utf-8")


def test_findings_count_propagated(tmp_path):
    from pymia.smartpyme.microservice_dispatcher import dispatch_candidate

    excel_path = tmp_path / "ventas_costos.xlsx"
    _write_excel(excel_path)
    result = dispatch_candidate(_ready_candidate(), evidence_path=excel_path)
    assert result.findings_count == len(result.raw_result.get("findings", []))


def test_output_refs_populated_when_output_dir_provided(tmp_path):
    from pymia.smartpyme.microservice_dispatcher import dispatch_candidate

    excel_path = tmp_path / "ventas_costos.xlsx"
    output_dir = tmp_path / "out"
    _write_excel(excel_path)
    result = dispatch_candidate(_ready_candidate(), evidence_path=excel_path, output_dir=output_dir)
    assert len(result.output_refs) == 1


def test_blocked_candidate_does_not_execute(tmp_path):
    from pymia.smartpyme.microservice_dispatcher import dispatch_candidate, EXECUTION_BLOCKED

    excel_path = tmp_path / "ventas_costos.xlsx"
    _write_excel(excel_path)

    candidate = _ready_candidate()
    candidate["status"] = "BLOCKED"
    result = dispatch_candidate(candidate, evidence_path=excel_path, output_dir=tmp_path / "out")

    assert result.status == EXECUTION_BLOCKED
    assert result.output_refs == []
    assert result.findings_count == 0


def test_unsupported_runtime_returns_unsupported(tmp_path):
    from pymia.smartpyme.microservice_dispatcher import dispatch_candidate, EXECUTION_UNSUPPORTED

    excel_path = tmp_path / "ventas_costos.xlsx"
    _write_excel(excel_path)
    candidate = _ready_candidate(runtime_classification="unknown_classification")

    result = dispatch_candidate(candidate, evidence_path=excel_path)
    assert result.status == EXECUTION_UNSUPPORTED


def test_supplier_duplicate_check_ready_candidate_executes(tmp_path):
    from pymia.smartpyme.microservice_dispatcher import dispatch_candidate, EXECUTION_EXECUTED

    excel_path = tmp_path / "proveedores_duplicados.xlsx"
    output_dir = tmp_path / "out"
    _write_supplier_excel(excel_path)

    result = dispatch_candidate(
        _ready_candidate(runtime_classification="supplier_duplicate_check"),
        evidence_path=excel_path,
        output_dir=output_dir,
    )

    assert result.status == EXECUTION_EXECUTED
    assert result.runtime_classification == "supplier_duplicate_check"
    assert result.findings_count >= 1
    assert result.output_refs


def test_non_ready_status_returns_blocked(tmp_path):
    from pymia.smartpyme.microservice_dispatcher import dispatch_candidate, EXECUTION_BLOCKED

    excel_path = tmp_path / "ventas_costos.xlsx"
    _write_excel(excel_path)
    candidate = _ready_candidate()
    candidate["status"] = "NEEDS_EVIDENCE"

    result = dispatch_candidate(candidate, evidence_path=excel_path)
    assert result.status == EXECUTION_BLOCKED


def test_missing_excel_path_returns_failed(tmp_path):
    from pymia.smartpyme.microservice_dispatcher import dispatch_candidate, EXECUTION_FAILED

    result = dispatch_candidate(_ready_candidate(), evidence_path=tmp_path / "missing.xlsx")
    assert result.status == EXECUTION_FAILED


def test_corrupt_excel_returns_failed(tmp_path):
    from pymia.smartpyme.microservice_dispatcher import dispatch_candidate, EXECUTION_FAILED

    bad_path = tmp_path / "corrupt.xlsx"
    bad_path.write_text("not-an-excel", encoding="utf-8")

    result = dispatch_candidate(_ready_candidate(), evidence_path=bad_path)
    assert result.status == EXECUTION_FAILED


def test_accepts_candidate_dict_and_dataclass(tmp_path):
    from pymia.smartpyme.microservice_dispatcher import dispatch_candidate, EXECUTION_EXECUTED

    excel_path = tmp_path / "ventas_costos.xlsx"
    _write_excel(excel_path)

    dict_result = dispatch_candidate(_ready_candidate(), evidence_path=excel_path)
    assert dict_result.status == EXECUTION_EXECUTED

    dc = RuntimeExecutionCandidate(
        tenant_id="tenant_smoke",
        intake_id="intake_smoke_001",
        runtime_classification="excel_diagnostic",
        microservice_name="excel_diagnostic_worker",
        evidence_ids=["ev_1"],
        status="READY_TO_EXECUTE",
        can_dispatch=True,
    )
    dc_result = dispatch_candidate(dc, evidence_path=excel_path)
    assert dc_result.status == EXECUTION_EXECUTED


def test_to_dict_is_json_serializable(tmp_path):
    from pymia.smartpyme.microservice_dispatcher import dispatch_candidate

    excel_path = tmp_path / "ventas_costos.xlsx"
    _write_excel(excel_path)

    payload = dispatch_candidate(_ready_candidate(), evidence_path=excel_path).to_dict()
    json.dumps(payload)


def test_inputs_not_mutated(tmp_path):
    from pymia.smartpyme.microservice_dispatcher import dispatch_candidate

    excel_path = tmp_path / "ventas_costos.xlsx"
    _write_excel(excel_path)

    candidate = _ready_candidate()
    snapshot = copy.deepcopy(candidate)
    dispatch_candidate(candidate, evidence_path=excel_path)
    assert candidate == snapshot
