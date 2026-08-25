from __future__ import annotations

import inspect
from pathlib import Path

from pymia.smartpyme.service_1_product_pipeline_v1 import (
    STATUS_BLOCKED,
    STATUS_RECONCILIATION_NEEDS_EVIDENCE,
    STATUS_RECONCILIATION_REVIEW_READY,
    run_service_1_product_pipeline_v1,
)
from pymia.smartpyme.service_1_product_execution_contracts_v1 import (
    SPECIALIZED_DOMAIN_RECONCILIATION,
    Service1ProductExecutionDependenciesV1,
    SpecializedDomainExecuteRequestV1,
)
from pymia.smartpyme.service_1_reconciliation_product_request_v1 import (
    STATUS_NEEDS_EVIDENCE,
    STATUS_NEEDS_OWNER,
    STATUS_REVIEW_READY,
    build_service_1_reconciliation_product_request_v1,
)
from pymia.smartpyme.service_1_reconciliation_request_gate_v1 import (
    BANK_RECONCILIATION,
    MERCADO_PAGO_BANK_RECONCILIATION,
)


def _governance(columns: tuple[str, ...]) -> dict[str, object]:
    return {
        "p5_status": "CONFIRMED",
        "p6_decisions": [
            {"column_ref": column, "status": "APPROVED"}
            for column in columns
        ],
        "p7_status": "REQUIREMENT_MATCHED",
        "p8_status": "COMPUTABLE",
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _bank_source() -> dict[str, object]:
    columns = ("mov_id", "fecha_banco", "monto", "referencia")
    return {
        "source_kind": "bank",
        "source_ref": "BANCO",
        "rows": [
            {
                "mov_id": "B-1",
                "fecha_banco": "2026-07-01",
                "monto": 1000.0,
                "referencia": "REF-1",
            }
        ],
        "field_bindings": {
            "id": "mov_id",
            "fecha": "fecha_banco",
            "importe": "monto",
            "referencia": "referencia",
        },
        "governance": _governance(columns),
    }


def _internal_source() -> dict[str, object]:
    columns = ("cobro_id", "fecha_cobro", "importe", "referencia")
    return {
        "source_kind": "internal",
        "source_ref": "COBROS",
        "rows": [
            {
                "cobro_id": "C-1",
                "fecha_cobro": "2026-07-01",
                "importe": 1000.0,
                "referencia": "REF-1",
            }
        ],
        "field_bindings": {
            "id": "cobro_id",
            "fecha": "fecha_cobro",
            "importe": "importe",
            "referencia": "referencia",
        },
        "governance": _governance(columns),
    }


def _mp_source() -> dict[str, object]:
    columns = (
        "op_id",
        "fecha",
        "bruto",
        "comision",
        "retencion",
        "neto",
        "lote",
        "referencia",
    )
    return {
        "source_kind": "mercado_pago",
        "source_ref": "MERCADO_PAGO",
        "rows": [
            {
                "op_id": "MP-1",
                "fecha": "2026-07-01",
                "bruto": 1000.0,
                "comision": 50.0,
                "retencion": 20.0,
                "neto": 930.0,
                "lote": "L-1",
                "referencia": "MPREF-1",
            }
        ],
        "field_bindings": {
            "operacion_mp_id": "op_id",
            "fecha_operacion": "fecha",
            "importe_bruto": "bruto",
            "comision": "comision",
            "retencion": "retencion",
            "importe_neto": "neto",
            "lote_id": "lote",
            "referencia": "referencia",
        },
        "governance": _governance(columns),
    }


def _mp_bank_source() -> dict[str, object]:
    columns = ("mov_id", "fecha", "importe", "lote", "referencia")
    return {
        "source_kind": "bank",
        "source_ref": "BANCO",
        "rows": [
            {
                "mov_id": "B-MP-1",
                "fecha": "2026-07-02",
                "importe": 930.0,
                "lote": "L-1",
                "referencia": "MPREF-1",
            }
        ],
        "field_bindings": {
            "movimiento_banco_id": "mov_id",
            "fecha": "fecha",
            "importe": "importe",
            "lote_id": "lote",
            "referencia": "referencia",
        },
        "governance": _governance(columns),
    }


def _bank_request() -> dict[str, object]:
    return {
        "case_id": "CASE-PRODUCT-BANK",
        "owner_requested": True,
        "reconciliation_type": BANK_RECONCILIATION,
        "source_packets": [_bank_source(), _internal_source()],
    }


def _mp_request() -> dict[str, object]:
    return {
        "case_id": "CASE-PRODUCT-MP",
        "owner_requested": True,
        "reconciliation_type": MERCADO_PAGO_BANK_RECONCILIATION,
        "source_packets": [_mp_source(), _mp_bank_source()],
    }


def _assert_closed(packet: dict[str, object]) -> None:
    assert packet["runtime_authorized"] is False
    assert packet["tool_execution_authorized"] is False
    assert packet["product_ready"] is False
    assert packet["delivery_authorized"] is False
    assert packet["diagnosis_generated"] is False


def _run_product_root(request: dict[str, object], tmp_path: Path) -> dict[str, object]:
    return run_service_1_product_pipeline_v1(
        SpecializedDomainExecuteRequestV1(
            subtype=SPECIALIZED_DOMAIN_RECONCILIATION,
            payload=request,
        ),
        dependencies=Service1ProductExecutionDependenciesV1(output_dir=tmp_path),
    )


def test_product_request_prepares_bank_review() -> None:
    result = build_service_1_reconciliation_product_request_v1(
        request=_bank_request()
    )

    assert result["status"] == STATUS_REVIEW_READY
    assert result["next_allowed_action"] == "human_reconciliation_review"
    review = result["assisted_review"]
    assert isinstance(review, dict)
    assert review["review_summary"]["confirmed_candidates"] == 1
    assert result["requires_human_review"] is True
    _assert_closed(result)


def test_product_request_prepares_mercado_pago_review() -> None:
    result = build_service_1_reconciliation_product_request_v1(
        request=_mp_request()
    )

    assert result["status"] == STATUS_REVIEW_READY
    review = result["assisted_review"]
    assert isinstance(review, dict)
    assert review["review_summary"]["confirmed_candidates"] == 1
    assert review["review_summary"]["calculation_inconsistencies"] == 0
    _assert_closed(result)


def test_product_request_maps_missing_source_to_evidence_request() -> None:
    request = _bank_request()
    request["source_packets"] = [_bank_source()]

    result = build_service_1_reconciliation_product_request_v1(
        request=request
    )

    assert result["status"] == STATUS_NEEDS_EVIDENCE
    assert result["next_allowed_action"] == "provide_reconciliation_evidence"
    assert result["assisted_review"] is None


def test_product_request_preserves_owner_confirmation_boundary() -> None:
    bank = _bank_source()
    governance = dict(bank["governance"])
    governance["p5_status"] = "NEEDS_OWNER_CONFIRMATION"
    bank["governance"] = governance
    request = _bank_request()
    request["source_packets"] = [bank, _internal_source()]

    result = build_service_1_reconciliation_product_request_v1(
        request=request
    )

    assert result["status"] == STATUS_NEEDS_OWNER
    assert result["next_allowed_action"] == (
        "confirm_reconciliation_source_meanings"
    )
    assert result["assisted_review"] is None


def test_product_root_accepts_bank_reconciliation_without_semantic_shortcut(
    tmp_path: Path,
) -> None:
    result = _run_product_root(_bank_request(), tmp_path)

    assert result["status"] == STATUS_RECONCILIATION_REVIEW_READY
    assert result["semantic_run"] is None
    assert result["reconciliation_review_prepared"] is True
    assert result["requires_human_review"] is True
    assert result["tools_executed"] is False
    assert result["computation_executed"] is False
    assert result["delivery_generated"] is False
    assert list(tmp_path.iterdir()) == []
    _assert_closed(result)


def test_product_root_accepts_mercado_pago_reconciliation(
    tmp_path: Path,
) -> None:
    result = _run_product_root(_mp_request(), tmp_path)

    assert result["status"] == STATUS_RECONCILIATION_REVIEW_READY
    reconciliation_run = result["reconciliation_run"]
    assert isinstance(reconciliation_run, dict)
    review = reconciliation_run["assisted_review"]
    assert review["reconciliation_type"] == (
        MERCADO_PAGO_BANK_RECONCILIATION
    )
    assert review["review_summary"]["confirmed_candidates"] == 1
    _assert_closed(result)


def test_product_root_maps_missing_source_without_running_other_paths(
    tmp_path: Path,
) -> None:
    request = _bank_request()
    request["source_packets"] = [_bank_source()]

    result = _run_product_root(request, tmp_path)

    assert result["status"] == STATUS_RECONCILIATION_NEEDS_EVIDENCE
    assert result["semantic_run"] is None
    assert result["reconciliation_review_prepared"] is False
    assert list(tmp_path.iterdir()) == []
    _assert_closed(result)


def test_product_root_specialized_command_is_exclusive(
    tmp_path: Path,
) -> None:
    result = _run_product_root(_bank_request(), tmp_path)
    assert result["status"] == STATUS_RECONCILIATION_REVIEW_READY
    assert result["semantic_run"] is None
    assert result["reconciliation_review_prepared"] is True
    assert list(tmp_path.iterdir()) == []
    _assert_closed(result)


def test_product_request_module_has_no_file_or_network_side_effects() -> None:
    import pymia.smartpyme.service_1_reconciliation_product_request_v1 as module

    source = inspect.getsource(module)

    assert "openpyxl" not in source
    assert "load_workbook" not in source
    assert "requests" not in source
    assert "open(" not in source
    assert ".save(" not in source
    assert "service_1_product_pipeline_v1" not in source
