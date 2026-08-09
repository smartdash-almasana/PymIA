"""Tenant identity and durable-confirmation wiring for Servicio 1 assisted web.

Keeps the assisted web coordinator decoupled from tenant identity/semantic
contract implementations while preserving their canonical authority.
"""
from __future__ import annotations

from typing import Any, Callable, Mapping

from pymia.smartpyme.service_1_tenant_confirmation_persistence_wiring_v1 import (
    persist_service_1_owner_confirmation_v1,
)
from pymia.smartpyme.service_1_tenant_identity_contract_v1 import (
    build_service_1_tenant_identity_contract_v1,
)
from pymia.smartpyme.service_1_tenant_semantic_contract_v1 import (
    Service1TenantSemanticContractErrorV1,
)


class Service1AssistedWebTenantPersistenceErrorV1(ValueError):
    pass


def build_service_1_assisted_web_tenant_identity_v1(
    *,
    tenant_id: str,
    cliente_id: str | None,
    case_id: str,
    owner_actor_id: str,
    owner_actor_role: str,
    source_system_ref: str,
    source_context_ref: str,
    workbook_ref: str,
) -> object:
    try:
        return build_service_1_tenant_identity_contract_v1(
            tenant_id=tenant_id,
            cliente_id=cliente_id,
            case_id=case_id,
            owner_actor_id=owner_actor_id,
            owner_actor_role=owner_actor_role,
            source_system_ref=source_system_ref,
            source_context_ref=source_context_ref,
            workbook_ref=workbook_ref,
        )
    except ValueError as exc:
        raise Service1AssistedWebTenantPersistenceErrorV1(
            "invalid assisted-web tenant identity"
        ) from exc


def persist_service_1_assisted_web_owner_events_v1(
    *,
    identity_contract: object,
    semantic_run: Mapping[str, object] | None,
    ingestion_output: Mapping[str, object] | None,
    persist_contract: Callable[[Any, Any], object],
) -> int:
    semantic = semantic_run if isinstance(semantic_run, Mapping) else {}
    events = [
        item
        for item in (semantic.get("owner_confirmation_events") or [])
        if isinstance(item, Mapping)
    ]
    if not events:
        return 0

    ingestion = ingestion_output if isinstance(ingestion_output, Mapping) else {}
    column_refs = ingestion.get("column_refs")
    refs = [item for item in (column_refs or []) if isinstance(item, Mapping)]

    persisted = 0
    for event in events:
        sheet_ref = str(event.get("sheet_ref") or "").strip()
        column_ref = str(event.get("column_ref") or "").strip()
        matching_ref = next(
            (
                ref
                for ref in refs
                if str(ref.get("sheet_name") or "").strip() == sheet_ref
                and str(ref.get("column_name") or "").strip() == column_ref
            ),
            None,
        )
        if matching_ref is None:
            raise Service1AssistedWebTenantPersistenceErrorV1(
                "owner confirmation column is missing from canonical ingestion refs"
            )
        source_column_name = str(matching_ref.get("column_name") or "").strip()
        normalized_column_ref = str(
            matching_ref.get("normalized_column_name")
            or matching_ref.get("normalized_column_ref")
            or ""
        ).strip()
        if not source_column_name or not normalized_column_ref:
            raise Service1AssistedWebTenantPersistenceErrorV1(
                "canonical source/normalized column identity is incomplete"
            )
        try:
            persist_service_1_owner_confirmation_v1(
                identity_contract=identity_contract,
                owner_confirmation_event=event,
                source_column_name=source_column_name,
                normalized_column_ref=normalized_column_ref,
                persist_contract=persist_contract,
            )
        except Service1TenantSemanticContractErrorV1 as exc:
            raise Service1AssistedWebTenantPersistenceErrorV1(
                "assisted-web tenant persistence failed"
            ) from exc
        persisted += 1
    return persisted


__all__ = [
    "Service1AssistedWebTenantPersistenceErrorV1",
    "build_service_1_assisted_web_tenant_identity_v1",
    "persist_service_1_assisted_web_owner_events_v1",
]
