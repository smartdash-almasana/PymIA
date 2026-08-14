"""Servicio 1 — provider-neutral LLM semantic interpreter adapter V1.

ADR-029 / SEM-2. This module owns no provider SDK and performs no network I/O
by itself. A provider callable is injected by composition and must return a
mapping matching the closed semantic proposal contract.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, Final

from pymia.smartpyme.service_1_llm_semantic_contract_v1 import (
    Service1LLMSemanticContextV1,
    Service1LLMSemanticContractErrorV1,
    Service1LLMSemanticProposalV1,
    parse_service_1_llm_semantic_proposal_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_LLM_SEMANTIC_INTERPRETER_V1"
STATUS_READY: Final[str] = "LLM_SEMANTIC_PROPOSAL_READY"
STATUS_BLOCKED: Final[str] = "BLOCKED"

BLOCK_CONTEXT_INVALID: Final[str] = "BLOCK_LLM_CONTEXT_INVALID"
BLOCK_PROVIDER_MISSING: Final[str] = "BLOCK_LLM_PROVIDER_MISSING"
BLOCK_PROVIDER_FAILED: Final[str] = "BLOCK_LLM_PROVIDER_FAILED"
BLOCK_PROVIDER_OUTPUT_NOT_MAPPING: Final[str] = "BLOCK_LLM_PROVIDER_OUTPUT_NOT_MAPPING"
BLOCK_PROVIDER_OUTPUT_INVALID: Final[str] = "BLOCK_LLM_PROVIDER_OUTPUT_INVALID"

ProviderCallableV1 = Callable[[dict[str, Any]], Mapping[str, Any]]


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

    try:
        raw = provider(context.to_provider_payload())
    except Exception as exc:  # provider boundary: fail closed, do not leak internals
        return _blocked(
            BLOCK_PROVIDER_FAILED,
            case_id=context.case_id,
            detail=type(exc).__name__,
        )

    if not isinstance(raw, Mapping):
        return _blocked(
            BLOCK_PROVIDER_OUTPUT_NOT_MAPPING,
            case_id=context.case_id,
        )

    try:
        proposal = parse_service_1_llm_semantic_proposal_v1(dict(raw))
    except Service1LLMSemanticContractErrorV1 as exc:
        return _blocked(
            BLOCK_PROVIDER_OUTPUT_INVALID,
            case_id=context.case_id,
            detail={"contract_error": exc.code, "contract_detail": exc.detail},
        )

    return _ready(case_id=context.case_id, proposal=proposal)


def _ready(*, case_id: str, proposal: Service1LLMSemanticProposalV1) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "blocked_reason": None,
        "case_id": case_id,
        "proposal": proposal,
        "proposal_payload": proposal.to_dict(),
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
    "BLOCK_PROVIDER_OUTPUT_NOT_MAPPING",
    "BLOCK_PROVIDER_OUTPUT_INVALID",
    "ProviderCallableV1",
    "interpret_service_1_semantics_v1",
]
