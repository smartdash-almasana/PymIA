"""Servicio 1 — provider-neutral LLM semantic interpreter adapter V1.

ADR-029 / SEM-2. This module owns no provider SDK and performs no network I/O
by itself. A provider callable is injected by composition and must return a
mapping matching the closed semantic proposal contract.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
import json
import os
import re
import sys
import time
from typing import Any, Final

from pymia.smartpyme.service_1_llm_semantic_contract_v1 import (
    Service1LLMSemanticContextV1,
    Service1LLMSemanticContractErrorV1,
    Service1LLMSemanticProposalV1,
    parse_service_1_llm_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_pydantic_ai_column_semantic_provider_v1 import (
    Service1TransientProviderFailureV1,
)
from pymia.smartpyme.service_1_workbook_business_understanding_v1 import (
    STATUS_READY as BUSINESS_UNDERSTANDING_READY,
    validate_service_1_workbook_business_understanding_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_LLM_SEMANTIC_INTERPRETER_V1"
STATUS_READY: Final[str] = "LLM_SEMANTIC_PROPOSAL_READY"
STATUS_BLOCKED: Final[str] = "BLOCKED"

BLOCK_CONTEXT_INVALID: Final[str] = "BLOCK_LLM_CONTEXT_INVALID"
BLOCK_PROVIDER_MISSING: Final[str] = "BLOCK_LLM_PROVIDER_MISSING"
BLOCK_PROVIDER_FAILED: Final[str] = "BLOCK_LLM_PROVIDER_FAILED"
BLOCK_TRANSIENT_PROVIDER_FAILURE: Final[str] = "BLOCK_TRANSIENT_PROVIDER_FAILURE"
BLOCK_PROVIDER_OUTPUT_NOT_MAPPING: Final[str] = "BLOCK_LLM_PROVIDER_OUTPUT_NOT_MAPPING"
BLOCK_PROVIDER_OUTPUT_INVALID: Final[str] = "BLOCK_LLM_PROVIDER_OUTPUT_INVALID"

ProviderCallableV1 = Callable[[dict[str, Any]], Mapping[str, Any]]

_DIAGNOSTIC_TAG: Final[str] = "[SERVICE1-LLM-DIAG]"
_SEMANTIC_PROVIDER_ENV: Final[str] = "PYMIA_SEMANTIC_PROVIDER"
_SEMANTIC_MODEL_ENV: Final[str] = "PYMIA_SEMANTIC_LLM_MODEL"
_DEFAULT_MODELS: Final[dict[str, str]] = {
    "OPENCODE_ZEN": "muse-spark-1.3-contributor-free",
    "NVIDIA_NIM": "nvidia/nemotron-3-super-120b-a12b",
}


def _safe_provider_exception_message(exc: Exception) -> str:
    """Keep local diagnostics useful without retaining credentials or payloads."""
    message = str(exc or "").strip()
    message = re.sub(r"(?i)(authorization\\s*[:=]\\s*bearer\\s+)[^\\s]+", r"\\1[REDACTED]", message)
    message = re.sub(r"(?i)(\\b(?:access[_ -]?token|api[_ -]?key|token|password)\\s*[:=]\\s*)[^\\s,;]+", r"\\1[REDACTED]", message)
    return message[:500]


def _safe_runtime_provider_model() -> tuple[str, str]:
    """Return only non-secret provider selection metadata for diagnostics."""
    provider = os.getenv(_SEMANTIC_PROVIDER_ENV, "OPENCODE_ZEN").strip().upper()
    provider = provider or "OPENCODE_ZEN"
    model = os.getenv(_SEMANTIC_MODEL_ENV, "").strip()
    return provider, model or _DEFAULT_MODELS.get(provider, "<runtime-default>")


def _safe_nested_objects(exc: Exception | None) -> tuple[Any, ...]:
    if exc is None:
        return ()
    nested: list[Any] = [exc]
    for name in ("response", "raw_response", "result", "__cause__"):
        try:
            value = getattr(exc, name, None)
        except Exception:
            value = None
        if value is not None and value is not exc:
            nested.append(value)
    return tuple(nested)


def _safe_scalar(value: Any) -> str | int | float | bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value[:120]
    return None


def _safe_attr(exc: Exception | None, names: tuple[str, ...]) -> Any:
    for obj in _safe_nested_objects(exc):
        for name in names:
            try:
                value = getattr(obj, name, None)
            except Exception:
                value = None
            if value is not None:
                return value
    return None


def _safe_http_status(exc: Exception | None) -> int | None:
    value = _safe_attr(exc, ("status_code", "http_status"))
    if isinstance(value, int) and 100 <= value <= 599:
        return value
    if isinstance(value, str) and value.isdigit() and 100 <= int(value) <= 599:
        return int(value)
    return None


def _safe_pydantic_error_summary(exc: Exception | None) -> str | None:
    if exc is None:
        return None
    errors = getattr(exc, "errors", None)
    if callable(errors):
        try:
            entries = errors()
            types: list[str] = []
            locations: list[str] = []
            for entry in entries[:5]:
                if isinstance(entry, Mapping):
                    error_type = entry.get("type")
                    location = entry.get("loc")
                    if error_type is not None:
                        types.append(str(error_type)[:80])
                    if location is not None:
                        locations.append(str(location)[:120])
            return (
                f"validation_errors={len(entries)};"
                f"types={','.join(types)};locations={','.join(locations)}"
            )
        except Exception:
            return "validation_errors=unavailable"
    return None


def _emit_provider_diagnostic(
    *,
    stage: str,
    elapsed_seconds: float,
    exc: Exception | None = None,
    raw_output: Any = None,
    response_status: Any = None,
    pydantic_error_summary: str | None = None,
) -> None:
    """Emit bounded provider-boundary metadata without payloads or credentials."""
    try:
        provider, model = _safe_runtime_provider_model()
        provider_attempts = _safe_attr(exc, ("service1_provider_attempts",))
        if isinstance(provider_attempts, (list, tuple)) and provider_attempts:
            sanitized_attempts = [
                {
                    "provider": str(item.get("provider") or "")[:80],
                    "model": str(item.get("model") or "")[:160],
                    "method": str(item.get("method") or "")[:80],
                    "provider_attempt_number": item.get("provider_attempt_number"),
                    "retry_number": item.get("retry_number"),
                    "elapsed_seconds": item.get("elapsed_seconds"),
                    "global_budget_before_seconds": item.get("global_budget_before_seconds"),
                    "global_budget_after_seconds": item.get("global_budget_after_seconds"),
                    "exception_type": item.get("exception_type"),
                    "http_status": item.get("http_status"),
                    "classification": item.get("classification"),
                    "retry_decision": item.get("retry_decision"),
                    "fallback_decision": item.get("fallback_decision"),
                    "terminal_condition": item.get("terminal_condition"),
                }
                for item in provider_attempts
                if isinstance(item, Mapping)
            ]
            if sanitized_attempts:
                provider = sanitized_attempts[-1]["provider"] or provider
                model = sanitized_attempts[-1]["model"] or model
                provider_attempts = sanitized_attempts
            else:
                provider_attempts = None
        else:
            provider_attempts = None
        http_status = _safe_http_status(exc)
        finish_reason = _safe_scalar(_safe_attr(exc, ("finish_reason", "finishReason")))
        incomplete_reason = _safe_scalar(
            _safe_attr(exc, ("incomplete_reason", "incompleteReason"))
        )
        output_text = _safe_attr(exc, ("output_text", "text"))
        output_text_present = isinstance(output_text, str) and bool(output_text)
        output_text_chars = len(output_text) if isinstance(output_text, str) else 0
        if raw_output is not None and isinstance(raw_output, str):
            output_text_present = bool(raw_output)
            output_text_chars = len(raw_output)
        json_parseable: bool | None = None
        if raw_output is not None:
            json_parseable = isinstance(raw_output, Mapping)
        elif exc is not None:
            exception_name = type(exc).__name__.lower()
            if "json" in exception_name or "parse" in exception_name:
                json_parseable = False
        event = {
            "provider": provider,
            "model": model,
            "provider_attempts": provider_attempts,
            "stage": stage,
            "http_status": http_status,
            "exception_type": None if exc is None else type(exc).__name__,
            "response_status": _safe_scalar(response_status)
            if response_status is not None
            else http_status,
            "finish_reason": finish_reason,
            "incomplete_reason": incomplete_reason,
            "output_text_present": output_text_present,
            "output_text_chars": output_text_chars,
            "json_parseable": json_parseable,
            "pydantic_error_summary": pydantic_error_summary
            or _safe_pydantic_error_summary(exc),
            "elapsed_seconds": round(max(0.0, elapsed_seconds), 3),
        }
        print(
            f"{_DIAGNOSTIC_TAG} {json.dumps(event, ensure_ascii=False, separators=(',', ':'))}",
            file=sys.stderr,
            flush=True,
        )
    except Exception:
        # Diagnostics must never alter or mask the fail-closed provider path.
        return


def interpret_service_1_semantics_v1(
    *,
    context: Any,
    provider: ProviderCallableV1 | None,
) -> dict[str, Any]:
    """Run one provider-neutral semantic interpretation pass.

    The provider receives only ``context.to_provider_payload()`` and returns raw
    structured data. The adapter parses that data into the closed proposal
    contract. It never validates ontology/evidence existence; SEM-3 owns that.
    """
    if not isinstance(context, Service1LLMSemanticContextV1):
        return _blocked(BLOCK_CONTEXT_INVALID)
    if provider is None or not callable(provider):
        return _blocked(BLOCK_PROVIDER_MISSING, case_id=context.case_id)

    provider_payload = context.to_provider_payload()
    workbook_business_understanding = None
    understand_workbook = getattr(provider, "understand_workbook", None)
    provider_started_at = time.monotonic()
    failing_stage = "WORKBOOK_BUSINESS_UNDERSTANDING"
    try:
        if callable(understand_workbook):
            candidate_understanding = understand_workbook(provider_payload)
            workbook_business_understanding = validate_service_1_workbook_business_understanding_v1(
                candidate=candidate_understanding,
                workbook_semantic_context=context.workbook_semantic_context,
            )
            if workbook_business_understanding.get("status") != BUSINESS_UNDERSTANDING_READY:
                _emit_provider_diagnostic(
                    stage="WORKBOOK_BUSINESS_UNDERSTANDING",
                    elapsed_seconds=time.monotonic() - provider_started_at,
                    raw_output=candidate_understanding,
                    response_status="BUSINESS_UNDERSTANDING_INVALID",
                    pydantic_error_summary=(
                        f"contract_error={workbook_business_understanding.get('blocked_reason')}"
                    ),
                )
                return _blocked(
                    BLOCK_PROVIDER_OUTPUT_INVALID,
                    case_id=context.case_id,
                    detail={
                        "contract_error": workbook_business_understanding.get("blocked_reason"),
                        "failing_stage": "WORKBOOK_BUSINESS_UNDERSTANDING",
                    },
                )
            provider_payload = dict(provider_payload)
            provider_payload["workbook_business_understanding"] = workbook_business_understanding
        failing_stage = "PROVIDER_CALL"
        raw = provider(provider_payload)
    except Exception as exc:  # provider boundary: fail closed, do not leak internals
        _emit_provider_diagnostic(
            stage=failing_stage,
            elapsed_seconds=time.monotonic() - provider_started_at,
            exc=exc,
        )
        if isinstance(exc, Service1TransientProviderFailureV1):
            return _blocked(
                BLOCK_TRANSIENT_PROVIDER_FAILURE,
                case_id=context.case_id,
                detail={
                    "exception_type": type(exc).__name__,
                    "attempted_providers": list(exc.attempted_providers),
                },
            )
        return _blocked(
            BLOCK_PROVIDER_FAILED,
            case_id=context.case_id,
            detail=type(exc).__name__,
        )

    if not isinstance(raw, Mapping):
        _emit_provider_diagnostic(
            stage="PROVIDER_OUTPUT",
            elapsed_seconds=time.monotonic() - provider_started_at,
            raw_output=raw,
            response_status="OUTPUT_NOT_MAPPING",
        )
        return _blocked(
            BLOCK_PROVIDER_OUTPUT_NOT_MAPPING,
            case_id=context.case_id,
        )

    provider_provenance = getattr(raw, "provider_provenance", None)
    try:
        proposal = parse_service_1_llm_semantic_proposal_v1(dict(raw))
    except Service1LLMSemanticContractErrorV1 as exc:
        _emit_provider_diagnostic(
            stage="PROVIDER_OUTPUT_SCHEMA",
            elapsed_seconds=time.monotonic() - provider_started_at,
            raw_output=raw,
            response_status="SCHEMA_MISMATCH",
            pydantic_error_summary=f"contract_error={exc.code}",
        )
        return _blocked(
            BLOCK_PROVIDER_OUTPUT_INVALID,
            case_id=context.case_id,
            detail={"contract_error": exc.code, "contract_detail": exc.detail},
        )

    return _ready(
        case_id=context.case_id,
        proposal=proposal,
        workbook_business_understanding=workbook_business_understanding,
        provider_provenance=provider_provenance,
    )


def _ready(
    *,
    case_id: str,
    proposal: Service1LLMSemanticProposalV1,
    workbook_business_understanding: Mapping[str, Any] | None = None,
    provider_provenance: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "blocked_reason": None,
        "case_id": case_id,
        "proposal": proposal,
        "proposal_payload": proposal.to_dict(),
        "workbook_business_understanding": (
            None
            if workbook_business_understanding is None
            else dict(workbook_business_understanding)
        ),
        "provider_provenance": (
            None if provider_provenance is None else dict(provider_provenance)
        ),
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _blocked(reason: str, *, case_id: str | None = None, detail: Any = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "detail": detail,
        "case_id": case_id,
        "proposal": None,
        "proposal_payload": None,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


__all__ = [
    "SCHEMA_VERSION",
    "STATUS_READY",
    "STATUS_BLOCKED",
    "BLOCK_CONTEXT_INVALID",
    "BLOCK_PROVIDER_MISSING",
    "BLOCK_PROVIDER_FAILED",
    "BLOCK_TRANSIENT_PROVIDER_FAILURE",
    "BLOCK_PROVIDER_OUTPUT_NOT_MAPPING",
    "BLOCK_PROVIDER_OUTPUT_INVALID",
    "ProviderCallableV1",
    "interpret_service_1_semantics_v1",
]
