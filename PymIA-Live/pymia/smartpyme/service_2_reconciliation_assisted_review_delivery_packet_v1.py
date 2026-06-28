from __future__ import annotations

from typing import Final

DeliveryPacketV1 = dict[str, object]

SERVICE_REF: Final[str] = "S2_ADMIN_OPERATIONS_V1"
PACKET_REF: Final[str] = "S2_RECONCILIATION_ASSISTED_REVIEW_DELIVERY_PACKET_V1"
SOURCE_BLOCK_REF: Final[str] = "S2_RECONCILIATION_ASSISTED_REVIEW_BLOCK_V1"
DEPRECATION_REASON: Final[str] = (
    "Merged into S2_RECONCILIATION_ASSISTED_REVIEW_BLOCK_V1 by "
    "S2_RECONCILIATION_BLOCK_PACKET_MERGE_V1."
)


def build_reconciliation_assisted_review_delivery_packet_v1(
    assisted_review_result: object,
) -> DeliveryPacketV1:
    """Compatibility shim.

    The active S2 reconciliation output contract is now the assisted review block.
    This function does not add a new processing layer; it only marks existing block
    output with legacy packet metadata for callers not yet migrated.
    """
    if not isinstance(assisted_review_result, dict):
        return _blocked_packet(assisted_review_result)

    if _is_current_assisted_review_block(assisted_review_result):
        return {
            **assisted_review_result,
            "packet": PACKET_REF,
            "source_block": SOURCE_BLOCK_REF,
            "deprecated": True,
            "deprecation_reason": DEPRECATION_REASON,
            "source_result": assisted_review_result,
        }

    return _blocked_packet(assisted_review_result)


def _is_current_assisted_review_block(value: dict[str, object]) -> bool:
    return (
        value.get("service") == SERVICE_REF
        and value.get("block") == SOURCE_BLOCK_REF
        and isinstance(value.get("status"), str)
        and value.get("requires_human_review") is True
        and isinstance(value.get("review_summary"), dict)
        and isinstance(value.get("sections"), list)
        and value.get("markdown_ready") is True
        and value.get("io_performed") is False
        and value.get("files_created") == []
        and value.get("xlsx_created") is False
        and value.get("api_used") is False
        and value.get("llm_used") is False
    )


def _blocked_packet(assisted_review_result: object) -> DeliveryPacketV1:
    return {
        "schema_version": "1.0",
        "service": SERVICE_REF,
        "packet": PACKET_REF,
        "source_block": SOURCE_BLOCK_REF,
        "status": "BLOCKED_BY_INVALID_INPUTS",
        "source_status": None,
        "requires_human_review": True,
        "deprecated": True,
        "deprecation_reason": DEPRECATION_REASON,
        "block_reason": "expected_current_assisted_review_block_v1",
        "markdown_ready": True,
        "io_performed": False,
        "files_created": [],
        "xlsx_created": False,
        "api_used": False,
        "llm_used": False,
        "source_result": assisted_review_result,
    }
