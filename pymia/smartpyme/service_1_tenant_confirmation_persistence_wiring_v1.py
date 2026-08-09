"""Pure wiring boundary from owner confirmation to tenant semantic persistence.

This module intentionally knows nothing about Supabase, HTTP, JWT, sessions, or
filesystem layout. Infrastructure is injected through a minimal persistence port.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from pymia.smartpyme.service_1_owner_confirmation_event_v1 import (
    Service1OwnerConfirmationEventV1,
)
from pymia.smartpyme.service_1_tenant_identity_contract_v1 import (
    Service1TenantIdentityContractV1,
    service_1_tenant_identity_contract_from_mapping_v1,
)
from pymia.smartpyme.service_1_tenant_semantic_contract_v1 import (
    Service1TenantSemanticContractErrorV1,
    Service1TenantSemanticContractV1,
    build_service_1_tenant_semantic_contract_v1,
)

STATUS_PERSISTED = "TENANT_CONFIRMATION_PERSISTED"


@dataclass(frozen=True)
class Service1TenantConfirmationPersistenceResultV1:
    status: str
    tenant_id: str
    cliente_id: str | None
    case_id: str
    confirmation_event_ref: str
    contract_id: str
    persisted: bool
    contract: Service1TenantSemanticContractV1


PersistencePortV1 = Callable[
    [Service1OwnerConfirmationEventV1, Service1TenantSemanticContractV1],
    object,
]


def _identity(
    value: Service1TenantIdentityContractV1 | Mapping[str, object],
) -> Service1TenantIdentityContractV1:
    if isinstance(value, Service1TenantIdentityContractV1):
        return value
    if isinstance(value, Mapping):
        return service_1_tenant_identity_contract_from_mapping_v1(value)
    raise Service1TenantSemanticContractErrorV1(
        "BLOCKED_INVALID_TENANT_IDENTITY",
        "tenant identity contract is required",
    )


def _event(
    value: Service1OwnerConfirmationEventV1 | Mapping[str, object],
) -> Service1OwnerConfirmationEventV1:
    if isinstance(value, Service1OwnerConfirmationEventV1):
        return value
    if not isinstance(value, Mapping):
        raise Service1TenantSemanticContractErrorV1(
            "BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT",
            "canonical owner confirmation event is required",
        )
    try:
        return Service1OwnerConfirmationEventV1(
            case_id=str(value.get("case_id") or "").strip(),
            file_ref=str(value.get("file_ref")).strip() if value.get("file_ref") is not None else None,
            region_ref=str(value.get("region_ref")).strip() if value.get("region_ref") is not None else None,
            sheet_ref=str(value.get("sheet_ref") or "").strip(),
            column_ref=str(value.get("column_ref") or "").strip(),
            question_ref=str(value.get("question_ref") or "").strip(),
            proposed_role=str(value.get("proposed_role")).strip() if value.get("proposed_role") else None,
            proposed_variable=str(value.get("proposed_variable")).strip() if value.get("proposed_variable") else None,
            owner_answer=str(value.get("owner_answer") or "").strip(),
            confirmed_role=str(value.get("confirmed_role")).strip() if value.get("confirmed_role") else None,
            corrected_meaning=str(value.get("corrected_meaning")).strip() if value.get("corrected_meaning") else None,
            confirmation_scope=str(value.get("confirmation_scope") or "").strip(),
            confirmed_by_owner=value.get("confirmed_by_owner") is True,
            timestamp=str(value.get("timestamp") or "").strip(),
            provenance=dict(value.get("provenance") or {}),
            schema_version=str(value.get("schema_version") or ""),
        )
    except (TypeError, ValueError) as exc:
        raise Service1TenantSemanticContractErrorV1(
            "BLOCKED_INVALID_OWNER_CONFIRMATION_EVENT",
            "canonical owner confirmation event is invalid",
        ) from exc


def persist_service_1_owner_confirmation_v1(
    *,
    identity_contract: Service1TenantIdentityContractV1 | Mapping[str, object],
    owner_confirmation_event: Service1OwnerConfirmationEventV1 | Mapping[str, object],
    source_column_name: str,
    normalized_column_ref: str,
    persist_contract: PersistencePortV1,
    inferred_data_type: str | None = None,
    neighboring_column_refs: tuple[str, ...] = (),
    vertical_ref: str | None = None,
) -> Service1TenantConfirmationPersistenceResultV1:
    """Build canonical semantic persistence and fail closed on infrastructure errors.

    The identity contract is the authority for tenant/client/owner/source identity.
    The owner-confirmation event remains the evidence authority. Infrastructure
    receives both canonical artifacts and must confirm durable persistence.
    """

    identity = _identity(identity_contract)
    event = _event(owner_confirmation_event)

    if event.case_id != identity.case_id:
        raise Service1TenantSemanticContractErrorV1(
            "BLOCKED_EVENT_CONTEXT_MISMATCH",
            "owner confirmation case does not match tenant identity contract",
        )
    if event.file_ref != identity.workbook_ref:
        raise Service1TenantSemanticContractErrorV1(
            "BLOCKED_EVENT_CONTEXT_MISMATCH",
            "owner confirmation workbook does not match tenant identity contract",
        )

    contract = build_service_1_tenant_semantic_contract_v1(
        tenant_id=identity.tenant_id,
        cliente_id=identity.cliente_id,
        owner_actor_id=identity.owner_actor_id,
        owner_actor_role=identity.owner_actor_role,
        source_system_ref=identity.source_system_ref,
        source_context_ref=identity.source_context_ref,
        workbook_ref=identity.workbook_ref,
        expected_case_id=identity.case_id,
        expected_sheet_ref=event.sheet_ref,
        expected_question_ref=event.question_ref,
        source_column_name=source_column_name,
        normalized_column_ref=normalized_column_ref,
        owner_confirmation_event=event,
        inferred_data_type=inferred_data_type,
        neighboring_column_refs=neighboring_column_refs,
        vertical_ref=vertical_ref,
    )

    try:
        persistence_result = persist_contract(event, contract)
    except Exception as exc:  # infrastructure failure must never become success
        raise Service1TenantSemanticContractErrorV1(
            "BLOCKED_PERSISTENCE_FAILURE",
            "tenant semantic persistence failed",
        ) from exc

    if persistence_result is None or persistence_result is False:
        raise Service1TenantSemanticContractErrorV1(
            "BLOCKED_PERSISTENCE_FAILURE",
            "tenant semantic persistence did not confirm durable write",
        )

    return Service1TenantConfirmationPersistenceResultV1(
        status=STATUS_PERSISTED,
        tenant_id=identity.tenant_id,
        cliente_id=identity.cliente_id,
        case_id=identity.case_id,
        confirmation_event_ref=contract.confirmation_event_ref,
        contract_id=contract.contract_id,
        persisted=True,
        contract=contract,
    )


__all__ = [
    "STATUS_PERSISTED",
    "PersistencePortV1",
    "Service1TenantConfirmationPersistenceResultV1",
    "persist_service_1_owner_confirmation_v1",
]
