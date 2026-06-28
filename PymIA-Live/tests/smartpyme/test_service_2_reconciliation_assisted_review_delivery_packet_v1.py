from __future__ import annotations

import inspect

from pymia.smartpyme import service_2_reconciliation_assisted_review_delivery_packet_v1 as module
from pymia.smartpyme.service_2_reconciliation_assisted_review_block_v1 import (
    build_reconciliation_assisted_review_block_v1,
)
from pymia.smartpyme.service_2_reconciliation_assisted_review_delivery_packet_v1 import (
    build_reconciliation_assisted_review_delivery_packet_v1,
)


def test_delivery_packet_is_deprecated_compatibility_shim() -> None:
    review = build_reconciliation_assisted_review_block_v1(
        [{"id": "b1", "fecha": "2026-06-01", "importe": 1000}],
        [{"id": "i1", "fecha": "2026-06-01", "importe": 1000}],
    )

    packet = build_reconciliation_assisted_review_delivery_packet_v1(review)

    assert packet["deprecated"] is True
    assert "Merged into S2_RECONCILIATION_ASSISTED_REVIEW_BLOCK_V1" in packet["deprecation_reason"]
    assert packet["source_result"] is review
    assert packet["status"] == review["status"]
    assert packet["packet"] == "S2_RECONCILIATION_ASSISTED_REVIEW_DELIVERY_PACKET_V1"


def test_shim_does_not_add_active_processing_layer() -> None:
    review = build_reconciliation_assisted_review_block_v1(
        [{"id": "b1", "fecha": "2026-06-03", "importe": 1000}],
        [{"id": "i1", "fecha": "2026-06-01", "importe": 1000}],
    )

    packet = build_reconciliation_assisted_review_delivery_packet_v1(review)

    assert packet["review_summary"] == review["review_summary"]
    assert packet["sections"] == review["sections"]
    assert packet["next_steps"] == review["next_steps"]
    assert packet["caveats"] == review["caveats"]
    assert packet["forbidden_claims"] == review["forbidden_claims"]


def test_invalid_input_blocks_conservatively() -> None:
    packet = build_reconciliation_assisted_review_delivery_packet_v1(None)

    assert packet["status"] == "BLOCKED_BY_INVALID_INPUTS"
    assert packet["deprecated"] is True
    assert packet["requires_human_review"] is True
    assert packet["block_reason"] == "expected_current_assisted_review_block_v1"


def test_invalid_legacy_shape_blocks_conservatively() -> None:
    packet = build_reconciliation_assisted_review_delivery_packet_v1(
        {
            "service": "S2_ADMIN_OPERATIONS_V1",
            "block": "WRONG_BLOCK",
            "status": "READY_FOR_ASSISTED_REVIEW",
            "requires_human_review": True,
            "review_summary": {},
        }
    )

    assert packet["status"] == "BLOCKED_BY_INVALID_INPUTS"
    assert packet["source_result"]["block"] == "WRONG_BLOCK"


def test_shim_preserves_no_side_effect_flags() -> None:
    review = build_reconciliation_assisted_review_block_v1([], [])
    packet = build_reconciliation_assisted_review_delivery_packet_v1(review)

    assert packet["markdown_ready"] is True
    assert packet["io_performed"] is False
    assert packet["files_created"] == []
    assert packet["xlsx_created"] is False
    assert packet["api_used"] is False
    assert packet["llm_used"] is False


def test_requires_human_review_is_always_true() -> None:
    review = build_reconciliation_assisted_review_block_v1([], [])
    ready_packet = build_reconciliation_assisted_review_delivery_packet_v1(review)
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
