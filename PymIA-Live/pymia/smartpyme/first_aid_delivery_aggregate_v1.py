from __future__ import annotations

import hashlib
import json
from typing import Final, Sequence, TypedDict

from pymia.smartpyme.first_aid_tool_result_v1 import FirstAidToolResultV1

AGGREGATE_SCHEMA_VERSION: Final[str] = "1.0"
SERVICE_NAME: Final[str] = "SERVICE_1"


class FirstAidDeliveryAggregateResultV1(TypedDict):
    tool_ref: str
    status: str
    owner_summary: str
    inputs_used: dict[str, object]
    computed_results: dict[str, object]
    missing_inputs: list[str]


class FirstAidDeliveryAggregateMissingInputsV1(TypedDict):
    tool_ref: str
    missing_inputs: list[str]


class FirstAidDeliveryAggregateV1(TypedDict):
    aggregate_id: str
    schema_version: str
    service_name: str
    tool_count: int
    tool_refs: list[str]
    statuses: list[str]
    results: list[FirstAidDeliveryAggregateResultV1]
    missing_inputs: list[FirstAidDeliveryAggregateMissingInputsV1]
    limitations: list[str]
    forbidden_claims: list[str]
    technical_notes: list[str]
    runtime_authorized: bool
    notes: list[str]


def build_first_aid_delivery_aggregate_v1(
    tool_results: Sequence[FirstAidToolResultV1],
) -> FirstAidDeliveryAggregateV1:
    normalized_tool_results = list(tool_results)
    if not normalized_tool_results:
        raise ValueError("FIRST_AID_DELIVERY_AGGREGATE_V1 requires at least one tool result.")

    for tool_result in normalized_tool_results:
        if tool_result["runtime_authorized"]:
            raise ValueError(
                "FIRST_AID_DELIVERY_AGGREGATE_V1 does not accept runtime_authorized=True."
            )

    tool_refs = [str(tool_result["tool_ref"]) for tool_result in normalized_tool_results]
    statuses = [str(tool_result["status"]) for tool_result in normalized_tool_results]
    results = [_build_result_entry(tool_result) for tool_result in normalized_tool_results]
    missing_inputs = [
        {
            "tool_ref": str(tool_result["tool_ref"]),
            "missing_inputs": list(tool_result["missing_inputs"]),
        }
        for tool_result in normalized_tool_results
    ]

    aggregate: FirstAidDeliveryAggregateV1 = {
        "aggregate_id": _build_aggregate_id(normalized_tool_results),
        "schema_version": AGGREGATE_SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "tool_count": len(normalized_tool_results),
        "tool_refs": tool_refs,
        "statuses": statuses,
        "results": results,
        "missing_inputs": missing_inputs,
        "limitations": _collect_unique_entries(
            [tool_result["limitations"] for tool_result in normalized_tool_results]
        ),
        "forbidden_claims": _collect_unique_entries(
            [tool_result["forbidden_claims"] for tool_result in normalized_tool_results]
        ),
        "technical_notes": _collect_unique_entries(
            [tool_result["technical_notes"] for tool_result in normalized_tool_results]
        ),
        "runtime_authorized": False,
        "notes": [
            "Aggregate built from FirstAidToolResultV1 payloads only.",
            "No tool execution, XLSX generation, or runtime authorization occurred.",
        ],
    }
    return aggregate


def _build_result_entry(tool_result: FirstAidToolResultV1) -> FirstAidDeliveryAggregateResultV1:
    return {
        "tool_ref": str(tool_result["tool_ref"]),
        "status": str(tool_result["status"]),
        "owner_summary": str(tool_result["owner_summary"]),
        "inputs_used": dict(tool_result["inputs_used"]),
        "computed_results": dict(tool_result["computed_results"]),
        "missing_inputs": list(tool_result["missing_inputs"]),
    }


def _collect_unique_entries(entry_groups: Sequence[list[str]]) -> list[str]:
    collected: list[str] = []
    for entry_group in entry_groups:
        for entry in entry_group:
            if entry not in collected:
                collected.append(entry)
    return collected


def _build_aggregate_id(tool_results: Sequence[FirstAidToolResultV1]) -> str:
    canonical_payload = json.dumps(
        [
            {
                "tool_ref": tool_result["tool_ref"],
                "status": tool_result["status"],
                "owner_summary": tool_result["owner_summary"],
                "inputs_used": tool_result["inputs_used"],
                "computed_results": tool_result["computed_results"],
                "missing_inputs": tool_result["missing_inputs"],
                "limitations": tool_result["limitations"],
                "forbidden_claims": tool_result["forbidden_claims"],
                "technical_notes": tool_result["technical_notes"],
            }
            for tool_result in tool_results
        ],
        ensure_ascii=False,
        sort_keys=True,
    )
    payload_hash = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()[:16]
    return f"first_aid_delivery_aggregate_v1:{payload_hash}"
