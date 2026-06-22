from __future__ import annotations

from typing import Final, Literal, TypedDict

FirstAidToolResultStatus = Literal[
    "OK",
    "MISSING_INPUTS",
    "BLOCKED",
    "INVALID_INPUT",
    "NOT_APPLICABLE",
]

FIRST_AID_TOOL_RESULT_ALLOWED_STATUSES: Final[tuple[FirstAidToolResultStatus, ...]] = (
    "OK",
    "MISSING_INPUTS",
    "BLOCKED",
    "INVALID_INPUT",
    "NOT_APPLICABLE",
)

FIRST_AID_TOOL_RESULT_DEFAULT_FORBIDDEN_CLAIMS: Final[tuple[str, ...]] = (
    "No es un diagnostico integral de la empresa.",
    "No confirma rentabilidad real.",
    "No confirma saldo bancario real.",
    "No confirma stock fisico real.",
    "No confirma conciliacion cerrada.",
    "No confirma archivo normalizado.",
)

SCHEMA_VERSION: Final[str] = "1.0"
SERVICE_NAME: Final[str] = "SERVICE_1"


class FirstAidToolResultV1(TypedDict):
    tool_ref: str
    schema_version: Literal["1.0"]
    service_name: Literal["SERVICE_1"]
    status: FirstAidToolResultStatus
    inputs_used: dict[str, object]
    computed_results: dict[str, object]
    missing_inputs: list[str]
    limitations: list[str]
    forbidden_claims: list[str]
    owner_summary: str
    technical_notes: list[str]
    runtime_authorized: bool


def build_first_aid_tool_result_v1(
    *,
    tool_ref: str,
    status: FirstAidToolResultStatus,
    inputs_used: dict[str, object] | None = None,
    computed_results: dict[str, object] | None = None,
    missing_inputs: list[str] | None = None,
    limitations: list[str] | None = None,
    forbidden_claims: list[str] | None = None,
    owner_summary: str,
    technical_notes: list[str] | None = None,
) -> FirstAidToolResultV1:
    normalized_inputs = dict(inputs_used or {})
    normalized_results = dict(computed_results or {})
    normalized_missing_inputs = list(missing_inputs or [])
    normalized_limitations = list(limitations or [])
    normalized_forbidden_claims = _merge_forbidden_claims(forbidden_claims)
    normalized_technical_notes = list(technical_notes or [])

    _validate_status(status)
    _validate_invariants(
        status=status,
        computed_results=normalized_results,
        missing_inputs=normalized_missing_inputs,
    )

    return {
        "tool_ref": tool_ref,
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "status": status,
        "inputs_used": normalized_inputs,
        "computed_results": normalized_results,
        "missing_inputs": normalized_missing_inputs,
        "limitations": normalized_limitations,
        "forbidden_claims": normalized_forbidden_claims,
        "owner_summary": owner_summary,
        "technical_notes": normalized_technical_notes,
        "runtime_authorized": False,
    }


def build_missing_inputs_tool_result_v1(
    *,
    tool_ref: str,
    missing_inputs: list[str],
    owner_summary: str,
    inputs_used: dict[str, object] | None = None,
    limitations: list[str] | None = None,
    technical_notes: list[str] | None = None,
    forbidden_claims: list[str] | None = None,
) -> FirstAidToolResultV1:
    return build_first_aid_tool_result_v1(
        tool_ref=tool_ref,
        status="MISSING_INPUTS",
        inputs_used=inputs_used,
        computed_results={},
        missing_inputs=missing_inputs,
        limitations=limitations,
        forbidden_claims=forbidden_claims,
        owner_summary=owner_summary,
        technical_notes=technical_notes,
    )


def _validate_status(status: FirstAidToolResultStatus) -> None:
    if status not in FIRST_AID_TOOL_RESULT_ALLOWED_STATUSES:
        raise ValueError(f"Unsupported FirstAidToolResultV1 status: {status}")


def _validate_invariants(
    *,
    status: FirstAidToolResultStatus,
    computed_results: dict[str, object],
    missing_inputs: list[str],
) -> None:
    if status == "OK" and missing_inputs:
        raise ValueError("FirstAidToolResultV1 status OK cannot include missing_inputs.")

    if status == "OK" and not computed_results:
        raise ValueError("FirstAidToolResultV1 status OK requires computed_results.")

    if status == "MISSING_INPUTS" and not missing_inputs:
        raise ValueError("FirstAidToolResultV1 status MISSING_INPUTS requires missing_inputs.")


def _merge_forbidden_claims(forbidden_claims: list[str] | None) -> list[str]:
    merged: list[str] = list(FIRST_AID_TOOL_RESULT_DEFAULT_FORBIDDEN_CLAIMS)
    for claim in list(forbidden_claims or []):
        if claim not in merged:
            merged.append(claim)
    return merged
