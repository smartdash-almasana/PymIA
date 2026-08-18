"""F13 wiring from governed F12/F9 execution evidence into result memory.

The wiring derives only structural persistence metadata: observed period and
owner-evidence references. It does not recalculate analytical results.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping

from pymia.smartpyme.service_1_analysis_result_projection_v1 import Service1AnalysisResultProjectionV1
from pymia.smartpyme.service_1_computability_v1 import Service1GovernedAnalysisInputV1
from pymia.smartpyme.service_1_result_memory_v1 import (
    Service1ResultMemoryErrorV1,
    Service1ResultMemoryPeriodV1,
    Service1ResultMemoryRecordV1,
    build_service_1_result_memory_record_v1,
)
from pymia.smartpyme.service_1_tenant_identity_contract_v1 import Service1TenantIdentityContractV1


def _blocked(code: str, detail: str) -> Service1ResultMemoryErrorV1:
    return Service1ResultMemoryErrorV1(code, detail)


def _p6_decisions(semantic_run: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    reentry = semantic_run.get("reentry_packet")
    if not isinstance(reentry, Mapping):
        return []
    return [item for item in (reentry.get("p6_decisions") or []) if isinstance(item, Mapping)]


def _parse_observed_date(value: object) -> date | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, (int, float)):
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    for pattern in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, pattern).date()
        except ValueError:
            continue
    return None


def _normalized_column_key(table: Mapping[str, Any], column_ref: str) -> str | None:
    headers = list(table.get("headers") or [])
    normalized = list(table.get("normalized_headers") or [])
    if len(headers) == len(normalized):
        for header, normalized_header in zip(headers, normalized):
            if str(header or "").strip() == column_ref:
                return str(normalized_header or "").strip() or None
    rows = [row for row in (table.get("rows") or []) if isinstance(row, Mapping)]
    if rows and column_ref in rows[0]:
        return column_ref
    return None


def derive_service_1_result_memory_period_v1(
    *,
    governed_analysis_input: Service1GovernedAnalysisInputV1,
    result_projection: Service1AnalysisResultProjectionV1,
    semantic_run: Mapping[str, Any],
    ingestion_output: Mapping[str, Any],
) -> Service1ResultMemoryPeriodV1:
    """Derive one observed period from an owner-confirmed operation_date column."""
    source_sheets = set(result_projection.result_set.source_sheet_refs)
    candidates: list[Mapping[str, Any]] = []
    for decision in _p6_decisions(semantic_run):
        if str(decision.get("status") or "") != "APPROVED":
            continue
        if str(decision.get("approved_role") or "") != "operation_date":
            continue
        sheet = str(decision.get("sheet_ref") or "").strip()
        if sheet in source_sheets:
            candidates.append(decision)
    identities = {
        (str(item.get("sheet_ref") or "").strip(), str(item.get("column_ref") or "").strip())
        for item in candidates
    }
    identities.discard(("", ""))
    if len(identities) != 1:
        reason = "missing" if not identities else "ambiguous"
        raise _blocked(
            "RESULT_MEMORY_PERIOD_EVIDENCE_REQUIRED",
            f"owner-confirmed operation_date evidence is {reason} for longitudinal persistence",
        )
    sheet_ref, column_ref = next(iter(identities))
    tables = [
        table
        for table in (ingestion_output.get("normalized_tables") or [])
        if isinstance(table, Mapping) and str(table.get("sheet_name") or "").strip() == sheet_ref
    ]
    if len(tables) != 1:
        raise _blocked("RESULT_MEMORY_PERIOD_EVIDENCE_REQUIRED", "period source sheet is unavailable or ambiguous")
    table = tables[0]
    normalized_key = _normalized_column_key(table, column_ref)
    if not normalized_key:
        raise _blocked("RESULT_MEMORY_PERIOD_EVIDENCE_REQUIRED", "period source column is unavailable")
    observed: list[date] = []
    for row in (table.get("rows") or []):
        if not isinstance(row, Mapping):
            continue
        parsed = _parse_observed_date(row.get(normalized_key))
        if parsed is None:
            raise _blocked(
                "RESULT_MEMORY_PERIOD_EVIDENCE_INVALID",
                f"period source contains a non-date value: {sheet_ref}.{column_ref}",
            )
        observed.append(parsed)
    if not observed:
        raise _blocked("RESULT_MEMORY_PERIOD_EVIDENCE_REQUIRED", "period source has no observed rows")
    start = min(observed).isoformat()
    end = max(observed).isoformat()
    source_ref = f"{sheet_ref}.{column_ref}"
    return Service1ResultMemoryPeriodV1(
        period_ref=f"{start}/{end}",
        start_date=start,
        end_date=end,
        basis_ref=f"OBSERVED_OPERATION_DATE_RANGE:{source_ref}",
        source_refs=(source_ref,),
    )


def derive_service_1_owner_evidence_refs_v1(
    *,
    governed_analysis_input: Service1GovernedAnalysisInputV1,
    semantic_run: Mapping[str, Any],
) -> tuple[str, ...]:
    decisions = _p6_decisions(semantic_run)
    refs: list[str] = []
    for role, source_ref in governed_analysis_input.source_bindings.items():
        source_text = str(source_ref or "").strip()
        if not source_text:
            raise _blocked(
                "RESULT_MEMORY_OWNER_EVIDENCE_REQUIRED",
                f"source binding is missing for role {role}",
            )
        matching: list[Mapping[str, Any]] = []
        if "." in source_text:
            sheet_ref, column_ref = source_text.split(".", 1)
            matching = [
                decision
                for decision in decisions
                if str(decision.get("status") or "") == "APPROVED"
                and str(decision.get("approved_role") or "") == role
                and str(decision.get("sheet_ref") or "").strip() == sheet_ref.strip()
                and str(decision.get("column_ref") or "").strip() == column_ref.strip()
            ]
        else:
            matching = [
                decision
                for decision in decisions
                if str(decision.get("status") or "") == "APPROVED"
                and str(decision.get("approved_role") or "") == role
                and str(decision.get("column_ref") or "").strip() == source_text
            ]
        question_refs = [
            str(item.get("owner_confirmation_question_ref") or item.get("question_ref") or "").strip()
            for item in matching
        ]
        question_refs = [ref for ref in question_refs if ref]
        if not question_refs:
            raise _blocked(
                "RESULT_MEMORY_OWNER_EVIDENCE_REQUIRED",
                f"owner evidence is missing for {role}:{source_ref}",
            )
        for ref in question_refs:
            if ref not in refs:
                refs.append(ref)
    for relationship_ref, binding in governed_analysis_input.relationship_bindings.items():
        if not isinstance(binding, Mapping) or binding.get("confirmed_by_owner") is not True:
            raise _blocked(
                "RESULT_MEMORY_OWNER_EVIDENCE_REQUIRED",
                f"relationship lacks owner confirmation: {relationship_ref}",
            )
        ref = str(
            binding.get("question_ref")
            or binding.get("owner_confirmation_question_ref")
            or binding.get("confirmation_event_ref")
            or ""
        ).strip()
        if not ref:
            raise _blocked(
                "RESULT_MEMORY_OWNER_EVIDENCE_REQUIRED",
                f"relationship owner evidence ref is missing: {relationship_ref}",
            )
        if ref not in refs:
            refs.append(ref)
    if not refs:
        raise _blocked("RESULT_MEMORY_OWNER_EVIDENCE_REQUIRED", "owner evidence refs are required")
    return tuple(refs)


def build_service_1_result_memory_from_execution_v1(
    *,
    identity_contract: Service1TenantIdentityContractV1,
    governed_analysis_input: Service1GovernedAnalysisInputV1,
    result_projection: Service1AnalysisResultProjectionV1,
    semantic_run: Mapping[str, Any],
    ingestion_output: Mapping[str, Any],
    executed_at: str | None = None,
) -> Service1ResultMemoryRecordV1:
    if not isinstance(semantic_run, Mapping) or semantic_run.get("status") != "CONFIRMED_BINDINGS":
        raise _blocked("RESULT_MEMORY_OWNER_EVIDENCE_REQUIRED", "confirmed semantic bindings are required")
    period = derive_service_1_result_memory_period_v1(
        governed_analysis_input=governed_analysis_input,
        result_projection=result_projection,
        semantic_run=semantic_run,
        ingestion_output=ingestion_output,
    )
    owner_refs = derive_service_1_owner_evidence_refs_v1(
        governed_analysis_input=governed_analysis_input,
        semantic_run=semantic_run,
    )
    return build_service_1_result_memory_record_v1(
        identity_contract=identity_contract,
        governed_analysis_input=governed_analysis_input,
        result_projection=result_projection,
        period=period,
        owner_evidence_refs=owner_refs,
        executed_at=executed_at,
    )


__all__ = [
    "derive_service_1_result_memory_period_v1",
    "derive_service_1_owner_evidence_refs_v1",
    "build_service_1_result_memory_from_execution_v1",
]
