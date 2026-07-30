from __future__ import annotations

import inspect
from copy import deepcopy

from pymia.smartpyme.service_1_reconciliation_candidate_to_assisted_review_v1 import (
    BANK_RECONCILER_REF,
    MERCADO_PAGO_RECONCILER_REF,
    STATUS_BLOCKED,
    STATUS_READY,
    build_service_1_reconciliation_assisted_review_v1,
)
from pymia.smartpyme.service_1_reconciliation_request_gate_v1 import (
    BANK_RECONCILIATION,
    MERCADO_PAGO_BANK_RECONCILIATION,
    build_service_1_reconciliation_request_gate_v1,
)


def _governance(columns: tuple[str, ...]) -> dict[str, object]:
    return {
        "p5_status": "CONFIRMED",
        "p6_decisions": [
            {"column_ref": column, "status": "APPROVED", "approved_role": column}
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
    columns = ("mov_id", "fecha", "importe", "referencia")
    return {
        "source_kind": "bank",
        "source_ref": "BANCO",
        "rows": [
            {
                "mov_id": "B-1",
                "fecha": "2026-07-01",
                "importe": 1000.0,
                "referencia": "R-1",
            }
        ],
        "field_bindings": {
            "id": "mov_id",
            "fecha": "fecha",
            "importe": "importe",
            "referencia": "referencia",
        },
        "governance": _governance(columns),
    }


def _internal_source() -> dict[str, object]:
    columns = ("cobro_id", "fecha", "importe", "referencia")
    return {
        "source_kind": "internal",
        "source_ref": "COBROS",
        "rows": [
            {
                "cobro_id": "C-1",
                "fecha": "2026-07-01",
                "importe": 1000.0,
                "referencia": "R-1",
            }
        ],
        "field_bindings": {
            "id": "cobro_id",
            "fecha": "fecha",
            "importe": "importe",
            "referencia": "referencia",
        },
        "governance": _governance(columns),
    }


def _mp_source() -> dict[str, object]:
    columns = (
        "operacion",
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
                "operacion": "MP-1",
                "fecha": "2026-07-01",
                "bruto": 1000.0,
                "comision": 50.0,
                "retencion": 20.0,
                "neto": 930.0,
                "lote": "L-1",
                "referencia": "REF-1",
            }
        ],
        "field_bindings": {
            "operacion_mp_id": "operacion",
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
    columns = ("movimiento", "fecha", "importe", "lote", "referencia")
    return {
        "source_kind": "bank",
        "source_ref": "BANCO",
        "rows": [
            {
                "movimiento": "B-1",
                "fecha": "2026-07-01",
                "importe": 930.0,
                "lote": "L-1",
                "referencia": "REF-1",
            }
        ],
        "field_bindings": {
            "movimiento_banco_id": "movimiento",
            "fecha": "fecha",
            "importe": "importe",
            "lote_id": "lote",
            "referencia": "referencia",
        },
        "governance": _governance(columns),
    }


def _bank_gate() -> dict[str, object]:
    return build_service_1_reconciliation_request_gate_v1(
        case_id="CASE-BANK-1",
        owner_requested=True,
        reconciliation_type=BANK_RECONCILIATION,
        source_packets=[_bank_source(), _internal_source()],
    )


def _mp_gate() -> dict[str, object]:
    return build_service_1_reconciliation_request_gate_v1(
        case_id="CASE-MP-1",
        owner_requested=True,
        reconciliation_type=MERCADO_PAGO_BANK_RECONCILIATION,
        source_packets=[_mp_source(), _mp_bank_source()],
    )


def test_bank_candidate_routes_to_assisted_review() -> None:
    result = build_service_1_reconciliation_assisted_review_v1(
        gate_packet=_bank_gate()
    )

    assert result["status"] == STATUS_READY
    assert result["reconciler_ref"] == BANK_RECONCILER_REF
    assert result["source_status"] == "READY_FOR_HUMAN_REVIEW"
    assert result["review_summary"]["confirmed_candidates"] == 1
    assert result["review_summary"]["ambiguous_groups"] == 0
    assert result["requires_human_review"] is True
    assert result["next_allowed_action"] == "human_reconciliation_review"
    assert result["runtime_authorized"] is False
    assert result["delivery_authorized"] is False


def test_mercado_pago_candidate_routes_to_net_settlement_review() -> None:
    result = build_service_1_reconciliation_assisted_review_v1(
        gate_packet=_mp_gate()
    )

    assert result["status"] == STATUS_READY
    assert result["reconciler_ref"] == MERCADO_PAGO_RECONCILER_REF
    assert result["source_status"] == "READY_FOR_HUMAN_REVIEW"
    assert result["review_summary"]["confirmed_candidates"] == 1
    assert result["review_summary"]["calculation_inconsistencies"] == 0
    review = result["review_result"]
    assert review["conciliaciones"][0]["importe_neto_esperado"] == 930.0
    assert review["conciliaciones"][0]["importe_banco_total"] == 930.0


def test_gate_must_be_ready_and_keep_safety_flags_false() -> None:
    not_ready = _bank_gate()
    not_ready["status"] = "NEEDS_OWNER_CONFIRMATION"
    blocked = build_service_1_reconciliation_assisted_review_v1(
        gate_packet=not_ready
    )
    assert blocked["status"] == STATUS_BLOCKED
    assert blocked["reason"] == "GATE_NOT_READY"
    assert blocked["review_result"] is None

    flagged = _bank_gate()
    flagged["runtime_authorized"] = True
    blocked_flagged = build_service_1_reconciliation_assisted_review_v1(
        gate_packet=flagged
    )
    assert blocked_flagged["status"] == STATUS_BLOCKED
    assert blocked_flagged["reason"] == "GATE_SAFETY_FLAGS_FORBIDDEN"


def test_candidate_identity_must_match_gate_identity() -> None:
    wrong_case = deepcopy(_bank_gate())
    wrong_case["reconciliation_candidate"]["case_id"] = "OTHER"
    result = build_service_1_reconciliation_assisted_review_v1(
        gate_packet=wrong_case
    )
    assert result["status"] == STATUS_BLOCKED
    assert result["reason"] == "CANDIDATE_CASE_MISMATCH"

    wrong_type = deepcopy(_bank_gate())
    wrong_type["reconciliation_candidate"]["reconciliation_type"] = (
        MERCADO_PAGO_BANK_RECONCILIATION
    )
    result = build_service_1_reconciliation_assisted_review_v1(
        gate_packet=wrong_type
    )
    assert result["status"] == STATUS_BLOCKED
    assert result["reason"] == "CANDIDATE_TYPE_MISMATCH"


def test_candidate_schema_and_payload_are_fail_closed() -> None:
    wrong_schema = deepcopy(_bank_gate())
    wrong_schema["reconciliation_candidate"]["schema_version"] = "OTHER"
    result = build_service_1_reconciliation_assisted_review_v1(
        gate_packet=wrong_schema
    )
    assert result["status"] == STATUS_BLOCKED
    assert result["reason"] == "CANDIDATE_SCHEMA_INVALID"

    missing_rows = deepcopy(_bank_gate())
    del missing_rows["reconciliation_candidate"]["internal_movements"]
    result = build_service_1_reconciliation_assisted_review_v1(
        gate_packet=missing_rows
    )
    assert result["status"] == STATUS_BLOCKED
    assert result["reason"] == "BANK_CANDIDATE_MOVEMENTS_REQUIRED"


def test_invalid_reconciler_input_is_exposed_without_accepting_matches() -> None:
    invalid = deepcopy(_bank_gate())
    invalid["reconciliation_candidate"]["bank_movements"][0]["importe"] = "bad"
    result = build_service_1_reconciliation_assisted_review_v1(
        gate_packet=invalid
    )

    assert result["status"] == "NEEDS_MORE_EVIDENCE"
    assert result["source_status"] == "NEEDS_MORE_EVIDENCE"
    assert result["next_allowed_action"] == "request_reconciliation_evidence"
    assert result["requires_human_review"] is True


def test_options_are_forwarded_to_the_reconciler() -> None:
    gate = deepcopy(_bank_gate())
    gate["reconciliation_candidate"]["bank_movements"][0]["importe"] = 1000.5

    strict = build_service_1_reconciliation_assisted_review_v1(
        gate_packet=gate,
        options={"importe_tolerancia_absoluta": 0.01},
    )
    tolerant = build_service_1_reconciliation_assisted_review_v1(
        gate_packet=gate,
        options={"importe_tolerancia_absoluta": 1.0},
    )

    assert strict["review_summary"]["confirmed_candidates"] == 0
    assert tolerant["review_summary"]["confirmed_candidates"] == 1


def test_adapter_has_no_io_api_llm_or_product_root_wiring() -> None:
    import pymia.smartpyme.service_1_product_pipeline_v1 as product_root
    import pymia.smartpyme.service_1_reconciliation_candidate_to_assisted_review_v1 as module

    source = inspect.getsource(module)
    product_source = inspect.getsource(product_root)

    assert "openpyxl" not in source
    assert "load_workbook" not in source
    assert "open(" not in source
    assert ".save(" not in source
    assert "requests" not in source
    assert "import openai" not in source.lower()
    assert "import anthropic" not in source.lower()
    assert result_has_no_runtime_side_effects(module)
    assert "service_1_reconciliation_candidate_to_assisted_review_v1" not in product_source


def result_has_no_runtime_side_effects(module: object) -> bool:
    result = module.build_service_1_reconciliation_assisted_review_v1(
        gate_packet=_bank_gate()
    )
    return (
        result["llm_used"] is False
        and result["api_used"] is False
        and result["io_performed"] is False
        and result["files_created"] == []
    )
