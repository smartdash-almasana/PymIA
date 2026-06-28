from __future__ import annotations

import inspect

from pymia.smartpyme import service_2_reconciliation_assisted_review_delivery_packet_v1 as module
from pymia.smartpyme.service_2_reconciliation_assisted_review_block_v1 import (
    build_reconciliation_assisted_review_block_v1,
)
from pymia.smartpyme.service_2_reconciliation_assisted_review_delivery_packet_v1 import (
    build_reconciliation_assisted_review_delivery_packet_v1,
)


def _ready_review_result() -> dict[str, object]:
    return build_reconciliation_assisted_review_block_v1(
        [{"id": "b1", "fecha": "2026-06-01", "importe": 1000}],
        [{"id": "i1", "fecha": "2026-06-01", "importe": 1000}],
    )


def test_builds_logical_packet_from_assisted_review_result() -> None:
    review = _ready_review_result()
    packet = build_reconciliation_assisted_review_delivery_packet_v1(review)

    assert packet["schema_version"] == "1.0"
    assert packet["service"] == "S2_ADMIN_OPERATIONS_V1"
    assert packet["packet"] == "S2_RECONCILIATION_ASSISTED_REVIEW_DELIVERY_PACKET_V1"
    assert packet["source_block"] == "S2_RECONCILIATION_ASSISTED_REVIEW_BLOCK_V1"
    assert packet["source_result"] is review


def test_ready_review_maps_to_ready_for_operator_review() -> None:
    packet = build_reconciliation_assisted_review_delivery_packet_v1(_ready_review_result())

    assert packet["status"] == "READY_FOR_OPERATOR_REVIEW"
    assert packet["source_status"] == "READY_FOR_ASSISTED_REVIEW"
    assert packet["counts"]["matches_exactos"] == 1


def test_partial_review_maps_to_partial_packet_ready() -> None:
    review = build_reconciliation_assisted_review_block_v1(
        [{"id": "b1", "fecha": "2026-06-03", "importe": 1000}],
        [{"id": "i1", "fecha": "2026-06-01", "importe": 1000}],
    )
    packet = build_reconciliation_assisted_review_delivery_packet_v1(review)

    assert packet["status"] == "PARTIAL_PACKET_READY"
    assert packet["counts"]["matches_probables"] == 1
    assert packet["counts"]["diferencias_fecha"] == 1


def test_no_candidates_status_is_preserved() -> None:
    review = build_reconciliation_assisted_review_block_v1(
        [{"id": "b1", "fecha": "2026-06-01", "importe": 1000}],
        [],
    )
    packet = build_reconciliation_assisted_review_delivery_packet_v1(review)

    assert packet["status"] == "NO_REVIEWABLE_CANDIDATES"
    assert packet["counts"]["banco_sin_imputar"] == 1


def test_missing_evidence_status_is_preserved() -> None:
    review = build_reconciliation_assisted_review_block_v1(
        [{"id": "b1", "fecha": "", "importe": 1000}],
        [],
    )
    packet = build_reconciliation_assisted_review_delivery_packet_v1(review)

    assert packet["status"] == "NEEDS_MORE_EVIDENCE"
    assert packet["counts"]["faltantes_evidencia"] == 1


def test_invalid_assisted_review_result_blocks() -> None:
    packet = build_reconciliation_assisted_review_delivery_packet_v1(None)

    assert packet["status"] == "BLOCKED_BY_INVALID_INPUTS"
    assert packet["block_reason"] == "assisted_review_result_must_be_a_dict"
    assert packet["requires_human_review"] is True


def test_invalid_review_shape_blocks_with_validation_errors() -> None:
    packet = build_reconciliation_assisted_review_delivery_packet_v1(
        {
            "service": "S2_ADMIN_OPERATIONS_V1",
            "block": "WRONG_BLOCK",
            "status": "READY_FOR_ASSISTED_REVIEW",
            "requires_human_review": False,
            "review_summary": {},
        }
    )

    assert packet["status"] == "BLOCKED_BY_INVALID_INPUTS"
    assert packet["block_reason"] == "invalid_assisted_review_result"
    assert {error["field"] for error in packet["validation_errors"]} == {
        "block",
        "requires_human_review",
    }


def test_packet_is_markdown_ready_but_performs_no_delivery_side_effects() -> None:
    packet = build_reconciliation_assisted_review_delivery_packet_v1(_ready_review_result())

    assert packet["markdown_ready"] is True
    assert packet["io_performed"] is False
    assert packet["files_created"] == []
    assert packet["xlsx_created"] is False
    assert packet["api_used"] is False
    assert packet["llm_used"] is False


def test_packet_has_operator_owner_and_accountant_audiences() -> None:
    packet = build_reconciliation_assisted_review_delivery_packet_v1(_ready_review_result())

    assert packet["audience"] == {
        "operator": True,
        "owner": True,
        "accountant": True,
    }
    assert "Paquete lógico" in packet["operator_brief"]
    assert "responsable o contador" in packet["owner_summary"]
    assert "revisión contable asistida" in packet["accountant_summary"]


def test_sections_include_core_review_sections() -> None:
    packet = build_reconciliation_assisted_review_delivery_packet_v1(_ready_review_result())
    section_ids = [section["id"] for section in packet["sections"]]

    assert section_ids == [
        "executive_summary",
        "exact_matches",
        "probable_matches",
        "bank_pending",
        "internal_pending",
        "amount_differences",
        "date_differences",
        "missing_evidence",
        "next_steps",
        "caveats",
    ]
    assert all(section["markdown_ready"] is True for section in packet["sections"])


def test_next_steps_and_caveats_are_carried_forward() -> None:
    review = _ready_review_result()
    packet = build_reconciliation_assisted_review_delivery_packet_v1(review)

    assert packet["next_steps"] == review["next_steps"]
    caveats_blob = " ".join(str(item) for item in packet["caveats"]).lower()
    assert "no es conciliación definitiva" in caveats_blob
    assert "requiere revisión humana" in caveats_blob


def test_forbidden_claims_are_carried_and_not_used_as_positive_output() -> None:
    packet = build_reconciliation_assisted_review_delivery_packet_v1(_ready_review_result())
    forbidden_blob = " ".join(str(item) for item in packet["forbidden_claims"]).lower()
    positive_blob = " ".join(
        [
            str(packet["status"]),
            str(packet["operator_brief"]),
            str(packet["owner_summary"]),
            str(packet["accountant_summary"]),
        ]
    ).lower()

    assert "banco conciliado" in forbidden_blob
    assert "conciliación cerrada" in forbidden_blob
    assert "saldo real confirmado" in forbidden_blob
    assert "banco conciliado" not in positive_blob
    assert "conciliación cerrada" not in positive_blob
    assert "saldo real confirmado" not in positive_blob


def test_requires_human_review_is_always_true() -> None:
    ready_packet = build_reconciliation_assisted_review_delivery_packet_v1(_ready_review_result())
    blocked_packet = build_reconciliation_assisted_review_delivery_packet_v1(None)

    assert ready_packet["requires_human_review"] is True
    assert blocked_packet["requires_human_review"] is True


def test_output_is_deterministic() -> None:
    review = build_reconciliation_assisted_review_block_v1(
        [
            {"id": "b1", "fecha": "2026-06-01", "importe": 1000},
            {"id": "b2", "fecha": "2026-06-03", "importe": 2000},
        ],
        [
            {"id": "i1", "fecha": "2026-06-01", "importe": 1000},
            {"id": "i2", "fecha": "2026-06-01", "importe": 2000},
        ],
    )

    assert build_reconciliation_assisted_review_delivery_packet_v1(review) == build_reconciliation_assisted_review_delivery_packet_v1(review)


def test_module_does_not_touch_or_import_service_1() -> None:
    source = inspect.getsource(module)

    assert "service_1" not in source.lower()


def test_module_has_no_file_delivery_dependencies() -> None:
    source = inspect.getsource(module).lower()

    forbidden_tokens = ["pathlib", "pandas", "openpyxl", "shutil"]
    assert all(token not in source for token in forbidden_tokens)


def test_no_forbidden_statuses_are_used() -> None:
    source = inspect.getsource(module)

    assert "CONCILIATED" not in source
    assert "CERTIFIED" not in source
    assert "AUDITED" not in source
    assert "TAX_READY" not in source
    assert "ACCOUNTING_CLOSED" not in source
    assert "FISCAL_CLOSED" not in source
