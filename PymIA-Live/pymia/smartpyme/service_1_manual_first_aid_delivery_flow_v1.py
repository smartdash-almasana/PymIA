from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Final, Sequence, TypedDict

from pymia.smartpyme.first_aid_delivery_aggregate_v1 import (
    FirstAidDeliveryAggregateV1,
    build_first_aid_delivery_aggregate_v1,
)
from pymia.smartpyme.first_aid_tool_result_v1 import FirstAidToolResultV1
from pymia.smartpyme.first_aid_xlsx_delivery_v1 import (
    FirstAidXlsxDeliveryV1,
    build_first_aid_xlsx_delivery_v1,
)

FLOW_SCHEMA_VERSION: Final[str] = "1.0"
SERVICE_NAME: Final[str] = "SERVICE_1"


class Service1ManualFirstAidDeliveryFlowV1(TypedDict):
    schema_version: str
    service_name: str
    delivery_count: int
    aggregate_id: str
    tool_refs: list[str]
    statuses: list[str]
    deliveries: list[FirstAidXlsxDeliveryV1]
    summary_text: str
    runtime_authorized: bool
    notes: list[str]


def build_service_1_manual_first_aid_delivery_flow_v1(
    tool_results: Sequence[FirstAidToolResultV1],
    output_dir: str | Path,
) -> Service1ManualFirstAidDeliveryFlowV1:
    normalized_results = list(tool_results)
    if not normalized_results:
        raise ValueError("MANUAL_FIRST_AID_DELIVERY_FLOW requires at least one tool result.")

    for tool_result in normalized_results:
        if tool_result["runtime_authorized"]:
            raise ValueError(
                "MANUAL_FIRST_AID_DELIVERY_FLOW does not accept runtime_authorized=True."
            )

    output_path = Path(output_dir)
    if not output_path.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_path}")

    aggregate = build_first_aid_delivery_aggregate_v1(normalized_results)

    deliveries: list[FirstAidXlsxDeliveryV1] = []
    for index, tool_result in enumerate(normalized_results, start=1):
        tool_ref = str(tool_result["tool_ref"])
        delivery_path = output_path / f"first_aid_{index:03d}_{_safe_filename_token(tool_ref)}.xlsx"
        delivery = build_first_aid_xlsx_delivery_v1(
            tool_result=tool_result,
            output_path=str(delivery_path),
        )
        deliveries.append(delivery)

    summary_text = _build_summary_text(aggregate, normalized_results)
    flow_id = _build_flow_id(aggregate)

    return {
        "schema_version": FLOW_SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "delivery_count": len(normalized_results),
        "aggregate_id": aggregate["aggregate_id"],
        "tool_refs": list(aggregate["tool_refs"]),
        "statuses": list(aggregate["statuses"]),
        "deliveries": deliveries,
        "summary_text": summary_text,
        "runtime_authorized": False,
        "notes": [
            "Manual First Aid delivery flow executed.",
            f"Flow ID: {flow_id}",
            "No runtime execution occurred.",
        ],
    }


def _build_summary_text(
    aggregate: FirstAidDeliveryAggregateV1,
    tool_results: Sequence[FirstAidToolResultV1],
) -> str:
    lines: list[str] = [
        f"Resultados procesados: {aggregate['tool_count']}",
    ]

    for tool_result in tool_results:
        lines.append(
            f"- {tool_result['tool_ref']}: {tool_result['status']}"
        )

    existing_missing = [
        entry for entry in aggregate["missing_inputs"] if entry["missing_inputs"]
    ]
    if existing_missing:
        lines.append("")
        lines.append("Faltantes detectados:")
        for entry in existing_missing:
            for missing in entry["missing_inputs"]:
                lines.append(f"- {entry['tool_ref']}: {missing}")

    if aggregate["limitations"]:
        lines.append("")
        lines.append("Limitaciones principales:")
        for limitation in aggregate["limitations"]:
            lines.append(f"- {limitation}")

    lines.append("")
    lines.append("Entrega preliminar basada en datos declarados.")
    return "\n".join(lines)


def _safe_filename_token(value: str) -> str:
    safe_chars = [char if char.isalnum() or char in ("-", "_") else "_" for char in value]
    safe_value = "".join(safe_chars).strip("._")
    return safe_value or "tool"


def _build_flow_id(aggregate: FirstAidDeliveryAggregateV1) -> str:
    canonical = json.dumps(
        {"aggregate_id": aggregate["aggregate_id"]},
        ensure_ascii=False,
        sort_keys=True,
    )
    payload_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return f"manual_first_aid_delivery_flow_v1:{payload_hash}"
