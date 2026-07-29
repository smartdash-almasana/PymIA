from __future__ import annotations

import inspect
from pathlib import Path

from pymia.smartpyme.service_1_reconciliation_request_gate_v1 import (
    BANK_RECONCILIATION,
    MERCADO_PAGO_BANK_RECONCILIATION,
    STATUS_BLOCKED,
    STATUS_MISSING_REQUIRED_FIELD,
    STATUS_MISSING_REQUIRED_SOURCE,
    STATUS_NEEDS_OWNER_CONFIRMATION,
    STATUS_READY,
    build_service_1_reconciliation_request_gate_v1,
)


def _governance(columns: tuple[str, ...]) -> dict[str, object]:
    return {
        "p5_status": "CONFIRMED",
        "p6_decisions": [
            {
                "column_ref": column,
                "status": "APPROVED",
                "approved_role": f"role:{column}",
            }
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


def _bank_packet() -> dict[str, object]:
    columns = ("mov_id", "fecha_banco", "monto", "ref", "detalle")
    return {
        "source_kind": "bank",
        "source_ref": "BANCO",
        "rows": [
            {
                "mov_id": "B-1",
                "fecha_banco": "2026-07-01",
                "monto": 1000.0,
                "ref": "R-1",
                "detalle": "Transferencia",
            }
        ],
        "field_bindings": {
            "id": "mov_id",
            "fecha": "fecha_banco",
            "importe": "monto",
            "referencia": "ref",
            "descripcion": "detalle",
        },
        "governance": _governance(columns),
    }


def _internal_packet() -> dict[str, object]:
    columns = ("cobro_id", "fecha_cobro", "importe_cobrado", "referencia")
    return {
        "source_kind": "internal",
        "source_ref": "COBROS",
        "rows": [
            {
                "cobro_id": "C-1",
                "fecha_cobro": "2026-07-01",
                "importe_cobrado": 1000.0,
                "referencia": "R-1",
            }
        ],
        "field_bindings": {
            "id": "cobro_id",
            "fecha": "fecha_cobro",
            "importe": "importe_cobrado",
            "referencia": "referencia",
        },
        "governance": _governance(columns),
    }


def _mp_packet() -> dict[str, object]:
    columns = (
        "op_id",
        "fecha",
        "bruto",
        "comision_mp",
        "retencion_mp",
        "neto",
        "lote",
        "referencia_mp",
    )
    return {
        "source_kind": "mercado_pago",
        "source_ref": "MERCADO_PAGO",
        "rows": [
            {
                "op_id": "MP-1",
                "fecha": "2026-07-01",
                "bruto": 1000.0,
                "comision_mp": 50.0,
                "retencion_mp": 20.0,
                "neto": 930.0,
                "lote": "L-1",
                "referencia_mp": "MPREF-1",
            }
        ],
        "field_bindings": {
            "operacion_mp_id": "op_id",
            "fecha_operacion": "fecha",
            "importe_bruto": "bruto",
            "comision": "comision_mp",
            "retencion": "retencion_mp",
            "importe_neto": "neto",
            "lote_id": "lote",
            "referencia": "referencia_mp",
        },
        "governance": _governance(columns),
    }


def _mp_bank_packet() -> dict[str, object]:
    columns = ("mov_id", "fecha", "importe", "lote", "referencia")
    return {
        "source_kind": "bank",
        "source_ref": "BANCO",
        "rows": [
            {
                "mov_id": "B-1",
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


def _build(
    source_packets: list[dict[str, object]],
    *,
    reconciliation_type: str = BANK_RECONCILIATION,
    **flags: bool,
) -> dict[str, object]:
    return build_service_1_reconciliation_request_gate_v1(
        case_id="CASE-001",
        owner_requested=True,
        reconciliation_type=reconciliation_type,
        source_packets=source_packets,
        **flags,
    )


def test_bank_request_prepares_governed_candidate_without_execution() -> None:
    result = _build([_bank_packet(), _internal_packet()])

    assert result["status"] == STATUS_READY
    candidate = result["reconciliation_candidate"]
    assert isinstance(candidate, dict)
    assert candidate["bank_movements"] == [
        {
            "id": "B-1",
            "fecha": "2026-07-01",
            "importe": 1000.0,
            "referencia": "R-1",
            "descripcion": "Transferencia",
        }
    ]
    assert candidate["internal_movements"] == [
        {
            "id": "C-1",
            "fecha": "2026-07-01",
            "importe": 1000.0,
            "referencia": "R-1",
        }
    ]
    assert candidate["runtime_authorized"] is False
    assert result["runtime_authorized"] is False
    assert result["tool_execution_authorized"] is False
    assert result["product_ready"] is False
    assert result["delivery_authorized"] is False
    assert result["diagnosis_generated"] is False


def test_mercado_pago_request_preserves_net_settlement_fields() -> None:
    result = _build(
        [_mp_packet(), _mp_bank_packet()],
        reconciliation_type=MERCADO_PAGO_BANK_RECONCILIATION,
    )

    assert result["status"] == STATUS_READY
    candidate = result["reconciliation_candidate"]
    assert isinstance(candidate, dict)
    assert candidate["mercado_pago_operations"] == [
        {
            "operacion_mp_id": "MP-1",
            "fecha_operacion": "2026-07-01",
            "importe_bruto": 1000.0,
            "comision": 50.0,
            "retencion": 20.0,
            "importe_neto": 930.0,
            "lote_id": "L-1",
            "referencia": "MPREF-1",
        }
    ]
    assert candidate["bank_movements"][0]["importe"] == 930.0


def test_missing_required_source_fails_closed() -> None:
    result = _build([_bank_packet()])

    assert result["status"] == STATUS_MISSING_REQUIRED_SOURCE
    assert result["missing_sources"] == ["internal"]
    assert result["reconciliation_candidate"] is None


def test_missing_required_field_binding_is_reported() -> None:
    internal = _internal_packet()
    bindings = dict(internal["field_bindings"])
    del bindings["referencia"]
    internal["field_bindings"] = bindings

    result = _build([_bank_packet(), internal])

    assert result["status"] == STATUS_MISSING_REQUIRED_FIELD
    assert result["source_kind"] == "internal"
    assert result["missing_fields"] == ["referencia"]


def test_p5_or_p6_uncertainty_requires_owner_confirmation() -> None:
    bank = _bank_packet()
    governance = dict(bank["governance"])
    governance["p5_status"] = "NEEDS_OWNER_CONFIRMATION"
    bank["governance"] = governance

    p5_result = _build([bank, _internal_packet()])
    assert p5_result["status"] == STATUS_NEEDS_OWNER_CONFIRMATION
    assert p5_result["reason"] == "P5_NEEDS_OWNER_CONFIRMATION"

    bank = _bank_packet()
    governance = dict(bank["governance"])
    decisions = list(governance["p6_decisions"])
    decisions[0] = {**decisions[0], "status": "AMBIGUOUS"}
    governance["p6_decisions"] = decisions
    bank["governance"] = governance

    p6_result = _build([bank, _internal_packet()])
    assert p6_result["status"] == STATUS_NEEDS_OWNER_CONFIRMATION
    assert p6_result["reason"] == "P6_OWNER_CONFIRMATION_REQUIRED"


def test_p7_or_p8_not_ready_blocks_candidate() -> None:
    bank = _bank_packet()
    governance = dict(bank["governance"])
    governance["p7_status"] = "NEEDS_EVIDENCE"
    bank["governance"] = governance

    p7_result = _build([bank, _internal_packet()])
    assert p7_result["status"] == STATUS_BLOCKED
    assert p7_result["reason"] == "bank:P7_REQUIREMENT_MATCH_REQUIRED"

    bank = _bank_packet()
    governance = dict(bank["governance"])
    governance["p8_status"] = "NEEDS_EVIDENCE"
    bank["governance"] = governance

    p8_result = _build([bank, _internal_packet()])
    assert p8_result["status"] == STATUS_BLOCKED
    assert p8_result["reason"] == "bank:P8_COMPUTABILITY_REQUIRED"


def test_bound_columns_must_be_p6_approved() -> None:
    bank = _bank_packet()
    governance = dict(bank["governance"])
    governance["p6_decisions"] = [
        item
        for item in governance["p6_decisions"]
        if item["column_ref"] != "ref"
    ]
    bank["governance"] = governance

    result = _build([bank, _internal_packet()])

    assert result["status"] == STATUS_BLOCKED
    assert result["reason"] == "bank:BOUND_COLUMNS_NOT_P6_APPROVED:ref"


def test_owner_request_and_safety_flags_are_mandatory() -> None:
    no_request = build_service_1_reconciliation_request_gate_v1(
        case_id="CASE-001",
        owner_requested=False,
        reconciliation_type=BANK_RECONCILIATION,
        source_packets=[_bank_packet(), _internal_packet()],
    )
    assert no_request["status"] == STATUS_BLOCKED
    assert no_request["reason"] == "EXPLICIT_OWNER_REQUEST_REQUIRED"

    flagged = _build(
        [_bank_packet(), _internal_packet()],
        runtime_authorized=True,
    )
    assert flagged["status"] == STATUS_BLOCKED
    assert flagged["reason"] == "REQUEST_SAFETY_FLAGS_FORBIDDEN"


def test_gate_does_not_read_files_call_matcher_or_modify_product_root() -> None:
    import pymia.smartpyme.service_1_reconciliation_request_gate_v1 as module
    import pymia.smartpyme.service_1_product_pipeline_v1 as product_root

    source = inspect.getsource(module)
    product_source = inspect.getsource(product_root)

    assert "openpyxl" not in source
    assert "load_workbook" not in source
    assert "build_reconciliation_match_candidates_v1" not in source
    assert "build_mercado_pago_bank_reconciliation_v1" not in source
    assert "service_2_" not in source
    assert "open(" not in source
    assert ".save(" not in source
    assert "service_1_reconciliation_request_gate_v1" not in product_source
    assert Path(module.__file__).name == "service_1_reconciliation_request_gate_v1.py"
