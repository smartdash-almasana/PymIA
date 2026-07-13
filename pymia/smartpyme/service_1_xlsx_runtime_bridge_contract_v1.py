from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, TypedDict

from pymia.smartpyme.service_1_xlsx_structure_v1 import read_service_1_xlsx_structure_v1
from pymia.smartpyme.service_1_xlsx_to_normalized_table_v1 import read_xlsx_to_normalized_table_v1

_READY = "XLSX_RUNTIME_BRIDGE_CONTRACT_READY"
_BLOCKED_MISSING_CASE_REF = "BLOCKED_MISSING_CASE_REF"
_BLOCKED_MISSING_OPERATOR_REF = "BLOCKED_MISSING_OPERATOR_REF"
_BLOCKED_XLSX_NORMALIZATION = "BLOCKED_XLSX_NORMALIZATION"
_BLOCKED_XLSX_STRUCTURE = "BLOCKED_XLSX_STRUCTURE"

BridgeContractStatusV1 = Literal[
    _READY,
    _BLOCKED_MISSING_CASE_REF,
    _BLOCKED_MISSING_OPERATOR_REF,
    _BLOCKED_XLSX_NORMALIZATION,
    _BLOCKED_XLSX_STRUCTURE,
]


class Service1XlsxRuntimeBridgePacketV1(TypedDict):
    packet_kind: Literal["SERVICE_1_XLSX_RUNTIME_BRIDGE_PACKET"]
    status: Literal[_READY]
    ready: Literal[True]
    case_ref: str
    operator_ref: str
    controlled_operational_case_ref: str
    source_path: str
    source_path_basename: str
    sheet_name: str | None
    normalized_headers: list[str]
    row_count: int
    column_count: int
    structure: dict[str, Any]
    warnings: list[str]
    blocking_errors: list[str]
    operator_review_required: Literal[True]
    controlled_xlsx_read_done: Literal[True]
    delivery_done: Literal[False]
    publish_done: Literal[False]
    notification_done: Literal[False]
    service_2_opened: Literal[False]
    phase_j_opened: Literal[False]
    saas_api_ui_opened: Literal[False]


class Service1XlsxRuntimeBridgeContractResultV1(TypedDict):
    contract_kind: Literal["SERVICE_1_XLSX_RUNTIME_BRIDGE_CONTRACT"]
    status: BridgeContractStatusV1
    ready: bool
    bridge_packet: Service1XlsxRuntimeBridgePacketV1 | None
    blocked_reasons: list[str]
    operator_review_required: Literal[True]
    controlled_xlsx_read_done: bool
    delivery_done: Literal[False]
    publish_done: Literal[False]
    notification_done: Literal[False]
    service_2_opened: Literal[False]
    phase_j_opened: Literal[False]
    saas_api_ui_opened: Literal[False]


def build_service_1_xlsx_runtime_bridge_contract_v1(
    *,
    xlsx_path: str | Path,
    case_ref: str | None,
    operator_ref: str | None,
    controlled_operational_case_ref: str | None = None,
    sheet_name: str | None = None,
) -> Service1XlsxRuntimeBridgeContractResultV1:
    if not _has_text(case_ref):
        return _blocked(_BLOCKED_MISSING_CASE_REF, ["case_ref is required"], controlled_xlsx_read_done=False)

    if not _has_text(operator_ref):
        return _blocked(_BLOCKED_MISSING_OPERATOR_REF, ["operator_ref is required"], controlled_xlsx_read_done=False)

    normalized = read_xlsx_to_normalized_table_v1(xlsx_path, sheet_name=sheet_name)

    if normalized["status"] != "OK":
        return _blocked(
            _BLOCKED_XLSX_NORMALIZATION,
            list(normalized["blocking_errors"]),
            controlled_xlsx_read_done=True,
        )

    try:
        structure = read_service_1_xlsx_structure_v1(str(xlsx_path))
    except Exception as exc:
        return _blocked(_BLOCKED_XLSX_STRUCTURE, [str(exc)], controlled_xlsx_read_done=True)

    packet: Service1XlsxRuntimeBridgePacketV1 = {
        "packet_kind": "SERVICE_1_XLSX_RUNTIME_BRIDGE_PACKET",
        "status": _READY,
        "ready": True,
        "case_ref": case_ref.strip(),
        "operator_ref": operator_ref.strip(),
        "controlled_operational_case_ref": (
            controlled_operational_case_ref.strip()
            if _has_text(controlled_operational_case_ref)
            else case_ref.strip()
        ),
        "source_path": str(Path(xlsx_path)),
        "source_path_basename": Path(xlsx_path).name,
        "sheet_name": normalized["sheet_name"],
        "normalized_headers": list(normalized["normalized_headers"]),
        "row_count": int(normalized["row_count"]),
        "column_count": int(normalized["column_count"]),
        "structure": dict(structure),
        "warnings": list(normalized["warnings"]) + list(structure.get("warnings", [])),
        "blocking_errors": [],
        "operator_review_required": True,
        "controlled_xlsx_read_done": True,
        **_closed_flags(),
    }

    return {
        "contract_kind": "SERVICE_1_XLSX_RUNTIME_BRIDGE_CONTRACT",
        "status": _READY,
        "ready": True,
        "bridge_packet": packet,
        "blocked_reasons": [],
        "operator_review_required": True,
        "controlled_xlsx_read_done": True,
        **_closed_flags(),
    }


def _blocked(
    status: BridgeContractStatusV1,
    reasons: list[str],
    *,
    controlled_xlsx_read_done: bool,
) -> Service1XlsxRuntimeBridgeContractResultV1:
    return {
        "contract_kind": "SERVICE_1_XLSX_RUNTIME_BRIDGE_CONTRACT",
        "status": status,
        "ready": False,
        "bridge_packet": None,
        "blocked_reasons": list(dict.fromkeys(reasons)),
        "operator_review_required": True,
        "controlled_xlsx_read_done": controlled_xlsx_read_done,
        **_closed_flags(),
    }


def _closed_flags() -> dict[str, Literal[False]]:
    return {
        "delivery_done": False,
        "publish_done": False,
        "notification_done": False,
        "service_2_opened": False,
        "phase_j_opened": False,
        "saas_api_ui_opened": False,
    }


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


__all__ = [
    "build_service_1_xlsx_runtime_bridge_contract_v1",
    "BridgeContractStatusV1",
    "Service1XlsxRuntimeBridgeContractResultV1",
    "Service1XlsxRuntimeBridgePacketV1",
]
