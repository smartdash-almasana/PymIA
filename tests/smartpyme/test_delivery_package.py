from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

from pymia.smartpyme.execution_result_gate import ExecutionResultGateVerdict
from pymia.smartpyme.microservice_dispatcher import MicroserviceExecutionResult


def _result_dict() -> dict:
    return {
        "tenant_id": "tenant_1",
        "intake_id": "intake_1",
        "runtime_classification": "excel_diagnostic",
        "microservice_name": "excel_diagnostic_worker",
        "status": "EXECUTED",
        "output_refs": ["C:/tmp/diagnostic_report.md"],
        "findings_count": 2,
        "raw_result": {"ok": True},
        "executed_at": "2026-05-26T00:00:00+00:00",
        "warnings": ["w-result"],
    }


def _verdict_dict(verdict: str = "PASS") -> dict:
    return {
        "verdict": verdict,
        "reasons": ["r1"],
        "warnings": ["w-verdict"],
    }


def test_import_smoke():
    from pymia.smartpyme.delivery_package import (  # noqa: F401
        DeliveryPackage,
        build_delivery_package,
        STATUS_READY_TO_DELIVER,
        STATUS_BLOCKED,
        STATUS_FAILED,
    )


def test_pass_maps_to_ready_to_deliver():
    from pymia.smartpyme.delivery_package import build_delivery_package, STATUS_READY_TO_DELIVER

    pkg = build_delivery_package(_result_dict(), _verdict_dict("PASS"))
    assert pkg.status == STATUS_READY_TO_DELIVER


def test_blocked_maps_to_blocked():
    from pymia.smartpyme.delivery_package import build_delivery_package, STATUS_BLOCKED

    pkg = build_delivery_package(_result_dict(), _verdict_dict("BLOCKED"))
    assert pkg.status == STATUS_BLOCKED


def test_failed_maps_to_failed():
    from pymia.smartpyme.delivery_package import build_delivery_package, STATUS_FAILED

    pkg = build_delivery_package(_result_dict(), _verdict_dict("FAILED"))
    assert pkg.status == STATUS_FAILED


def test_undeliverable_maps_to_failed():
    from pymia.smartpyme.delivery_package import build_delivery_package, STATUS_FAILED

    pkg = build_delivery_package(_result_dict(), _verdict_dict("UNDELIVERABLE"))
    assert pkg.status == STATUS_FAILED


def test_accepts_result_and_verdict_dataclasses():
    from pymia.smartpyme.delivery_package import build_delivery_package, STATUS_READY_TO_DELIVER

    result = MicroserviceExecutionResult(
        tenant_id="tenant_1",
        intake_id="intake_1",
        runtime_classification="excel_diagnostic",
        microservice_name="excel_diagnostic_worker",
        status="EXECUTED",
        output_refs=["C:/tmp/diagnostic_report.md"],
        findings_count=1,
        raw_result={"ok": True},
        warnings=["w-result"],
    )
    verdict = ExecutionResultGateVerdict(
        verdict="PASS",
        reasons=["ok"],
        warnings=["w-verdict"],
    )

    pkg = build_delivery_package(result, verdict)
    assert pkg.status == STATUS_READY_TO_DELIVER
    assert pkg.warnings == ["w-result", "w-verdict"]


def test_no_mutation_of_inputs():
    from pymia.smartpyme.delivery_package import build_delivery_package

    result = _result_dict()
    verdict = _verdict_dict("PASS")
    result_before = copy.deepcopy(result)
    verdict_before = copy.deepcopy(verdict)

    build_delivery_package(result, verdict)

    assert result == result_before
    assert verdict == verdict_before


@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("tenant_id", ""),
        ("intake_id", ""),
        ("runtime_classification", ""),
    ],
)
def test_invalid_required_fields_raise_value_error(field: str, bad_value):
    from pymia.smartpyme.delivery_package import build_delivery_package

    result = _result_dict()
    result[field] = bad_value
    with pytest.raises(ValueError):
        build_delivery_package(result, _verdict_dict("PASS"))


def test_invalid_output_refs_type_raises_value_error():
    from pymia.smartpyme.delivery_package import build_delivery_package

    result = _result_dict()
    result["output_refs"] = "not-a-list"
    with pytest.raises(ValueError):
        build_delivery_package(result, _verdict_dict("PASS"))


def test_missing_output_refs_raises_value_error():
    from pymia.smartpyme.delivery_package import build_delivery_package

    result = _result_dict()
    result.pop("output_refs")
    with pytest.raises(ValueError):
        build_delivery_package(result, _verdict_dict("PASS"))


def test_unknown_verdict_raises_value_error():
    from pymia.smartpyme.delivery_package import build_delivery_package

    with pytest.raises(ValueError):
        build_delivery_package(_result_dict(), _verdict_dict("MAYBE"))


def test_to_dict_serializable():
    from pymia.smartpyme.delivery_package import build_delivery_package

    payload = build_delivery_package(_result_dict(), _verdict_dict("PASS")).to_dict()
    json.dumps(payload)


def test_does_not_import_excel_or_supplier_modules_ast():
    source = Path("pymia/smartpyme/delivery_package.py").read_text(encoding="utf-8")
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
