from __future__ import annotations

import ast
import json
from pathlib import Path

from pymia.smartpyme.microservice_dispatcher import MicroserviceExecutionResult


def _valid_result(path: Path) -> dict:
    return {
        "tenant_id": "tenant_1",
        "intake_id": "intake_1",
        "runtime_classification": "excel_diagnostic",
        "microservice_name": "excel_diagnostic_worker",
        "status": "EXECUTED",
        "output_refs": [str(path)],
        "findings_count": 2,
        "raw_result": {"ok": True, "findings": [{"code": "A"}]},
        "executed_at": "2026-05-26T00:00:00+00:00",
        "warnings": [],
    }


def test_import_smoke():
    from pymia.smartpyme.execution_result_gate import (  # noqa: F401
        ExecutionResultGateVerdict,
        validate_execution_result,
        VERDICT_PASS,
        VERDICT_BLOCKED,
        VERDICT_FAILED,
        VERDICT_UNDELIVERABLE,
    )


def test_pass_with_valid_executed_result(tmp_path):
    from pymia.smartpyme.execution_result_gate import validate_execution_result, VERDICT_PASS

    out = tmp_path / "report.md"
    out.write_text("ok", encoding="utf-8")

    verdict = validate_execution_result(_valid_result(out))
    assert verdict.verdict == VERDICT_PASS


def test_blocked_with_status_blocked(tmp_path):
    from pymia.smartpyme.execution_result_gate import validate_execution_result, VERDICT_BLOCKED

    out = tmp_path / "report.md"
    out.write_text("ok", encoding="utf-8")

    result = _valid_result(out)
    result["status"] = "BLOCKED"
    verdict = validate_execution_result(result)
    assert verdict.verdict == VERDICT_BLOCKED


def test_failed_with_status_failed(tmp_path):
    from pymia.smartpyme.execution_result_gate import validate_execution_result, VERDICT_FAILED

    out = tmp_path / "report.md"
    out.write_text("ok", encoding="utf-8")

    result = _valid_result(out)
    result["status"] = "FAILED"
    verdict = validate_execution_result(result)
    assert verdict.verdict == VERDICT_FAILED


def test_blocked_with_status_unsupported(tmp_path):
    from pymia.smartpyme.execution_result_gate import validate_execution_result, VERDICT_BLOCKED

    out = tmp_path / "report.md"
    out.write_text("ok", encoding="utf-8")

    result = _valid_result(out)
    result["status"] = "UNSUPPORTED"
    verdict = validate_execution_result(result)
    assert verdict.verdict == VERDICT_BLOCKED


def test_undeliverable_with_unknown_status(tmp_path):
    from pymia.smartpyme.execution_result_gate import validate_execution_result, VERDICT_UNDELIVERABLE

    out = tmp_path / "report.md"
    out.write_text("ok", encoding="utf-8")

    result = _valid_result(out)
    result["status"] = "WAT"
    verdict = validate_execution_result(result)
    assert verdict.verdict == VERDICT_UNDELIVERABLE


def test_undeliverable_with_empty_tenant_id(tmp_path):
    from pymia.smartpyme.execution_result_gate import validate_execution_result, VERDICT_UNDELIVERABLE

    out = tmp_path / "report.md"
    out.write_text("ok", encoding="utf-8")

    result = _valid_result(out)
    result["tenant_id"] = ""
    verdict = validate_execution_result(result)
    assert verdict.verdict == VERDICT_UNDELIVERABLE


def test_undeliverable_with_empty_intake_id(tmp_path):
    from pymia.smartpyme.execution_result_gate import validate_execution_result, VERDICT_UNDELIVERABLE

    out = tmp_path / "report.md"
    out.write_text("ok", encoding="utf-8")

    result = _valid_result(out)
    result["intake_id"] = ""
    verdict = validate_execution_result(result)
    assert verdict.verdict == VERDICT_UNDELIVERABLE


def test_undeliverable_with_empty_output_refs(tmp_path):
    from pymia.smartpyme.execution_result_gate import validate_execution_result, VERDICT_UNDELIVERABLE

    out = tmp_path / "report.md"
    out.write_text("ok", encoding="utf-8")

    result = _valid_result(out)
    result["output_refs"] = []
    verdict = validate_execution_result(result)
    assert verdict.verdict == VERDICT_UNDELIVERABLE


def test_undeliverable_with_missing_output_ref(tmp_path):
    from pymia.smartpyme.execution_result_gate import validate_execution_result, VERDICT_UNDELIVERABLE

    result = _valid_result(tmp_path / "missing.md")
    verdict = validate_execution_result(result)
    assert verdict.verdict == VERDICT_UNDELIVERABLE


def test_undeliverable_with_negative_findings_count(tmp_path):
    from pymia.smartpyme.execution_result_gate import validate_execution_result, VERDICT_UNDELIVERABLE

    out = tmp_path / "report.md"
    out.write_text("ok", encoding="utf-8")

    result = _valid_result(out)
    result["findings_count"] = -1
    verdict = validate_execution_result(result)
    assert verdict.verdict == VERDICT_UNDELIVERABLE


def test_undeliverable_with_empty_raw_result(tmp_path):
    from pymia.smartpyme.execution_result_gate import validate_execution_result, VERDICT_UNDELIVERABLE

    out = tmp_path / "report.md"
    out.write_text("ok", encoding="utf-8")

    result = _valid_result(out)
    result["raw_result"] = {}
    verdict = validate_execution_result(result)
    assert verdict.verdict == VERDICT_UNDELIVERABLE


def test_undeliverable_with_non_serializable_raw_result(tmp_path):
    from pymia.smartpyme.execution_result_gate import validate_execution_result, VERDICT_UNDELIVERABLE

    out = tmp_path / "report.md"
    out.write_text("ok", encoding="utf-8")

    result = _valid_result(out)
    result["raw_result"] = {"bad": {1, 2, 3}}
    verdict = validate_execution_result(result)
    assert verdict.verdict == VERDICT_UNDELIVERABLE


def test_warnings_do_not_block(tmp_path):
    from pymia.smartpyme.execution_result_gate import validate_execution_result, VERDICT_PASS

    out = tmp_path / "report.md"
    out.write_text("ok", encoding="utf-8")

    result = _valid_result(out)
    result["warnings"] = ["warn-a", "warn-b"]
    verdict = validate_execution_result(result)
    assert verdict.verdict == VERDICT_PASS
    assert verdict.warnings == ["warn-a", "warn-b"]


def test_to_dict_serializable(tmp_path):
    from pymia.smartpyme.execution_result_gate import validate_execution_result

    out = tmp_path / "report.md"
    out.write_text("ok", encoding="utf-8")

    payload = validate_execution_result(_valid_result(out)).to_dict()
    json.dumps(payload)


def test_accepts_dataclass_result(tmp_path):
    from pymia.smartpyme.execution_result_gate import validate_execution_result, VERDICT_PASS

    out = tmp_path / "report.md"
    out.write_text("ok", encoding="utf-8")

    result = MicroserviceExecutionResult(
        tenant_id="tenant_1",
        intake_id="intake_1",
        runtime_classification="excel_diagnostic",
        microservice_name="excel_diagnostic_worker",
        status="EXECUTED",
        output_refs=[str(out)],
        findings_count=1,
        raw_result={"ok": True},
    )
    verdict = validate_execution_result(result)
    assert verdict.verdict == VERDICT_PASS


def test_gate_does_not_import_excel_or_supplier_modules_ast():
    source = Path("pymia/smartpyme/execution_result_gate.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    forbidden_prefixes = (
        "pymia.smartpyme.excel_diagnostic",
        "pymia.smartpyme.supplier_duplicate_check",
        "pymia.smartpyme.classifications.supplier_duplicate_check",
    )

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith(forbidden_prefixes)
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert not module.startswith(forbidden_prefixes)
