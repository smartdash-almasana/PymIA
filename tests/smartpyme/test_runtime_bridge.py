from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest


def _make_readiness(
    *,
    tenant_id: str = "t1",
    intake_id: str = "i1",
    status: str = "READY_FOR_ANALYSIS",
    runtime_classification: str | None = "excel_diagnostic",
    can_execute: bool = True,
    blocking_reasons: list[str] | None = None,
    matched_evidence_ids: list[str] | None = None,
    warnings: list[str] | None = None,
    audit_notes: list[str] | None = None,
) -> dict:
    return {
        "tenant_id": tenant_id,
        "intake_id": intake_id,
        "status": status,
        "suggested_next_state": status,
        "runtime_classification": runtime_classification,
        "can_execute": can_execute,
        "blocking_reasons": blocking_reasons or [],
        "missing_request_ids": [],
        "matched_evidence_ids": matched_evidence_ids or ["ev_1"],
        "warnings": warnings or [],
        "audit_notes": audit_notes or [],
        "created_at": "2026-05-25T00:00:00+00:00",
    }


def test_import_smoke():
    from pymia.smartpyme.runtime_bridge import (  # noqa: F401
        RuntimeExecutionCandidate,
        prepare_runtime_execution,
        EXECUTION_READY_TO_EXECUTE,
        EXECUTION_BLOCKED,
        EXECUTION_UNSUPPORTED,
        MICROSERVICE_MAP,
    )


def test_ready_for_analysis_returns_ready_to_execute():
    from pymia.smartpyme.runtime_bridge import (
        prepare_runtime_execution,
        EXECUTION_READY_TO_EXECUTE,
    )

    c = prepare_runtime_execution(_make_readiness())
    assert c.status == EXECUTION_READY_TO_EXECUTE
    assert c.can_dispatch is True


def test_blocked_readiness_returns_blocked_execution():
    from pymia.smartpyme.runtime_bridge import (
        prepare_runtime_execution,
        EXECUTION_BLOCKED,
    )

    c = prepare_runtime_execution(
        _make_readiness(status="NEEDS_EVIDENCE", can_execute=False)
    )
    assert c.status == EXECUTION_BLOCKED
    assert c.can_dispatch is False


def test_unsupported_runtime_returns_unsupported_execution():
    from pymia.smartpyme.runtime_bridge import (
        prepare_runtime_execution,
        EXECUTION_UNSUPPORTED,
    )

    c = prepare_runtime_execution(
        _make_readiness(runtime_classification="unknown_runtime", can_execute=True)
    )
    assert c.status == EXECUTION_UNSUPPORTED
    assert c.can_dispatch is False


def test_microservice_name_derived_from_runtime_classification_excel():
    from pymia.smartpyme.runtime_bridge import prepare_runtime_execution

    c = prepare_runtime_execution(_make_readiness(runtime_classification="excel_diagnostic"))
    assert c.microservice_name == "excel_diagnostic_worker"


def test_microservice_name_derived_from_runtime_classification_supplier():
    from pymia.smartpyme.runtime_bridge import prepare_runtime_execution

    c = prepare_runtime_execution(
        _make_readiness(runtime_classification="supplier_duplicate_check")
    )
    assert c.microservice_name == "supplier_duplicate_check_worker"


def test_evidence_ids_propagated_from_readiness():
    from pymia.smartpyme.runtime_bridge import prepare_runtime_execution

    c = prepare_runtime_execution(_make_readiness(matched_evidence_ids=["ev_11", "ev_12"]))
    assert c.evidence_ids == ["ev_11", "ev_12"]


def test_can_dispatch_false_when_blocked():
    from pymia.smartpyme.runtime_bridge import prepare_runtime_execution

    c = prepare_runtime_execution(_make_readiness(status="BLOCKED", can_execute=False))
    assert c.can_dispatch is False


def test_accepts_dict_input():
    from pymia.smartpyme.runtime_bridge import prepare_runtime_execution

    c = prepare_runtime_execution(_make_readiness())
    assert c.tenant_id == "t1"


def test_accepts_dataclass_input():
    from pymia.smartpyme.readiness import AnalysisReadinessResult
    from pymia.smartpyme.runtime_bridge import prepare_runtime_execution

    r = AnalysisReadinessResult(
        tenant_id="t1",
        intake_id="i1",
        status="READY_FOR_ANALYSIS",
        suggested_next_state="READY_FOR_ANALYSIS",
        runtime_classification="excel_diagnostic",
        can_execute=True,
        matched_evidence_ids=["ev_1"],
    )
    c = prepare_runtime_execution(r)
    assert c.status == "READY_TO_EXECUTE"


def test_to_dict_json_serializable():
    from pymia.smartpyme.runtime_bridge import prepare_runtime_execution

    c = prepare_runtime_execution(_make_readiness())
    payload = c.to_dict()
    assert isinstance(payload, dict)
    json.dumps(payload)


def test_invalid_readiness_status_blocks_not_raises():
    from pymia.smartpyme.runtime_bridge import prepare_runtime_execution

    c = prepare_runtime_execution(_make_readiness(status="SOMETHING_ELSE", can_execute=True))
    assert c.status == "BLOCKED"


def test_missing_tenant_id_raises():
    from pymia.smartpyme.runtime_bridge import prepare_runtime_execution

    d = _make_readiness()
    d.pop("tenant_id")
    with pytest.raises(ValueError):
        prepare_runtime_execution(d)


def test_missing_intake_id_raises():
    from pymia.smartpyme.runtime_bridge import prepare_runtime_execution

    d = _make_readiness()
    d.pop("intake_id")
    with pytest.raises(ValueError):
        prepare_runtime_execution(d)


def test_missing_runtime_classification_blocks_ready_analysis():
    from pymia.smartpyme.runtime_bridge import (
        EXECUTION_BLOCKED,
        prepare_runtime_execution,
    )

    d = _make_readiness(runtime_classification=None)
    c = prepare_runtime_execution(d)
    assert c.status == EXECUTION_BLOCKED
    assert c.can_dispatch is False
    assert c.microservice_name == ""
    assert "Missing runtime_classification for ready analysis." in c.blocking_reasons


def test_missing_runtime_classification_allowed_when_not_ready():
    from pymia.smartpyme.runtime_bridge import (
        EXECUTION_BLOCKED,
        prepare_runtime_execution,
    )

    d = _make_readiness(
        status="NEEDS_EVIDENCE",
        can_execute=False,
        runtime_classification=None,
    )
    c = prepare_runtime_execution(d)
    assert c.status == EXECUTION_BLOCKED
    assert c.can_dispatch is False
    assert c.runtime_classification == ""


def test_inputs_not_mutated():
    from pymia.smartpyme.runtime_bridge import prepare_runtime_execution

    rr = _make_readiness()
    snapshot = json.dumps(rr, sort_keys=True)
    prepare_runtime_execution(rr)
    assert json.dumps(rr, sort_keys=True) == snapshot


def test_does_not_import_runtime_modules_ast():
    source = Path("pymia/smartpyme/runtime_bridge.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    forbidden_prefixes = (
        "pymia.smartpyme.excel_diagnostic",
        "pymia.smartpyme.classifications.supplier_duplicate_check",
        "pymia.smartpyme.supplier_duplicate_check",
    )

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith(forbidden_prefixes)
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert not module.startswith(forbidden_prefixes)


def test_does_not_import_runtime_modules_loaded_modules():
    before = set(sys.modules.keys())
    from pymia.smartpyme import runtime_bridge  # noqa: F401

    after = set(sys.modules.keys())
    newly_loaded = after - before
    assert "pymia.smartpyme.excel_diagnostic" not in newly_loaded
    assert "pymia.smartpyme.supplier_duplicate_check" not in newly_loaded
    assert "pymia.smartpyme.classifications.supplier_duplicate_check" not in newly_loaded
