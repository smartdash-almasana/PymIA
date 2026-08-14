"""Supabase infrastructure adapter for Servicio 1 tenant semantic persistence.

Domain authority stays in the canonical identity, owner-confirmation and semantic
contract modules. This adapter only serializes already validated artifacts.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Mapping

from pymia.smartpyme.service_1_owner_confirmation_event_v1 import (
    Service1OwnerConfirmationEventV1,
)
from pymia.smartpyme.service_1_tenant_semantic_contract_v1 import (
    Service1TenantSemanticContractV1,
    service_1_tenant_semantic_contract_from_mapping_v1,
)

SUPABASE_URL_ENV = "PYMIA_SUPABASE_URL"
SUPABASE_SERVICE_ROLE_KEY_ENV = "PYMIA_SUPABASE_SERVICE_ROLE_KEY"
OWNER_CONFIRMATIONS_TABLE = "service1_owner_confirmations"
SEMANTIC_CONTRACTS_TABLE = "service1_tenant_semantic_contracts"


class Service1SupabasePersistenceErrorV1(RuntimeError):
    pass


@dataclass(frozen=True)
class Service1SupabaseConfigV1:
    url: str
    service_role_key: str


def load_service_1_supabase_config_v1(
    environ: Mapping[str, str] | None = None,
) -> Service1SupabaseConfigV1:
    env = os.environ if environ is None else environ
    url = str(env.get(SUPABASE_URL_ENV) or "").strip()
    key = str(env.get(SUPABASE_SERVICE_ROLE_KEY_ENV) or "").strip()
    if not url:
        raise Service1SupabasePersistenceErrorV1(
            f"missing required configuration: {SUPABASE_URL_ENV}"
        )
    if not key:
        raise Service1SupabasePersistenceErrorV1(
            f"missing required configuration: {SUPABASE_SERVICE_ROLE_KEY_ENV}"
        )
    return Service1SupabaseConfigV1(url=url, service_role_key=key)


def create_service_1_supabase_client_v1(config: Service1SupabaseConfigV1) -> Any:
    try:
        from supabase import create_client
    except ImportError as exc:
        raise Service1SupabasePersistenceErrorV1(
            "supabase package is required for the Supabase persistence adapter"
        ) from exc
    return create_client(config.url, config.service_role_key)


def _response_data(response: object) -> object:
    return getattr(response, "data", None)


def _confirmed_insert(response: object, *, expected_key: str, expected_value: str) -> bool:
    data = _response_data(response)
    if not isinstance(data, list) or len(data) != 1:
        return False
    row = data[0]
    return isinstance(row, Mapping) and str(row.get(expected_key) or "") == expected_value


def _owner_confirmation_row(
    event: Service1OwnerConfirmationEventV1,
    contract: Service1TenantSemanticContractV1,
) -> dict[str, object]:
    return {
        "confirmation_event_ref": contract.confirmation_event_ref,
        "tenant_id": contract.tenant_id,
        "cliente_id": contract.cliente_id,
        "case_id": contract.case_id,
        "owner_actor_id": contract.owner_actor_id,
        "owner_actor_role": contract.owner_actor_role,
        "source_system_ref": contract.source_system_ref,
        "source_context_ref": contract.source_context_ref,
        "workbook_ref": contract.workbook_ref,
        "sheet_ref": event.sheet_ref,
        "column_ref": event.column_ref,
        "question_ref": event.question_ref,
        "confirmation_scope": event.confirmation_scope,
        "owner_answer": event.owner_answer,
        "confirmed_role": event.confirmed_role,
        "corrected_meaning": event.corrected_meaning,
        "confirmed_at": event.timestamp,
        "event_payload": event.to_dict(),
    }


def _semantic_contract_row(contract: Service1TenantSemanticContractV1) -> dict[str, object]:
    return {
        "contract_id": contract.contract_id,
        "mapping_series_id": contract.mapping_series_id,
        "tenant_id": contract.tenant_id,
        "cliente_id": contract.cliente_id,
        "case_id": contract.case_id,
        "confirmation_event_ref": contract.confirmation_event_ref,
        "source_system_ref": contract.source_system_ref,
        "source_context_ref": contract.source_context_ref,
        "workbook_ref": contract.workbook_ref,
        "sheet_ref": contract.sheet_ref,
        "source_column_name": contract.source_column_name,
        "normalized_column_ref": contract.normalized_column_ref,
        "owner_actor_id": contract.owner_actor_id,
        "owner_actor_role": contract.owner_actor_role,
        "confirmed_at": contract.confirmed_at,
        "revision": contract.revision,
        "supersedes_contract_id": contract.supersedes_contract_id,
        "contract_payload": contract.to_dict(),
    }


class Service1SupabasePersistenceAdapterV1:
    """Append-only persistence adapter for the two canonical Servicio 1 artifacts."""

    def __init__(self, client: Any) -> None:
        self._client = client

    @classmethod
    def from_environment(
        cls,
        environ: Mapping[str, str] | None = None,
    ) -> "Service1SupabasePersistenceAdapterV1":
        config = load_service_1_supabase_config_v1(environ)
        return cls(create_service_1_supabase_client_v1(config))

    def list_owner_confirmation_memory(
        self,
        tenant_id: str,
    ) -> tuple[dict[str, object], ...]:
        tenant = str(tenant_id or "").strip()
        if not tenant:
            raise Service1SupabasePersistenceErrorV1("tenant_id is required for memory lookup")
        try:
            response = (
                self._client.table(OWNER_CONFIRMATIONS_TABLE)
                .select(
                    "confirmation_event_ref,tenant_id,sheet_ref,column_ref,"
                    "question_ref,owner_answer,confirmed_at"
                )
                .eq("tenant_id", tenant)
                .order("confirmed_at", desc=True)
                .execute()
            )
        except Exception as exc:
            raise Service1SupabasePersistenceErrorV1(
                "Supabase tenant memory lookup failed"
            ) from exc
        data = _response_data(response)
        if data is None:
            return ()
        if not isinstance(data, list):
            raise Service1SupabasePersistenceErrorV1(
                "Supabase tenant memory lookup returned invalid data"
            )
        rows: list[dict[str, object]] = []
        for raw in data:
            if not isinstance(raw, Mapping) or str(raw.get("tenant_id") or "") != tenant:
                raise Service1SupabasePersistenceErrorV1(
                    "Supabase tenant memory lookup crossed tenant boundary"
                )
            rows.append(dict(raw))
        return tuple(rows)

    def list_persisted_cases(
        self,
        tenant_id: str,
    ) -> tuple[dict[str, object], ...]:
        """Return one durable owner-evidence read-model row per case for a tenant."""
        tenant = str(tenant_id or "").strip()
        if not tenant:
            raise Service1SupabasePersistenceErrorV1("tenant_id is required for case lookup")
        try:
            response = (
                self._client.table(OWNER_CONFIRMATIONS_TABLE)
                .select(
                    "tenant_id,cliente_id,case_id,workbook_ref,source_system_ref,"
                    "source_context_ref,owner_actor_id,owner_actor_role,confirmed_at"
                )
                .eq("tenant_id", tenant)
                .order("confirmed_at", desc=True)
                .execute()
            )
        except Exception as exc:
            raise Service1SupabasePersistenceErrorV1(
                "Supabase persisted case listing failed"
            ) from exc
        data = _response_data(response)
        if data is None:
            return ()
        if not isinstance(data, list):
            raise Service1SupabasePersistenceErrorV1(
                "Supabase persisted case listing returned invalid data"
            )
        by_case: dict[str, dict[str, object]] = {}
        for raw in data:
            if not isinstance(raw, Mapping) or str(raw.get("tenant_id") or "") != tenant:
                raise Service1SupabasePersistenceErrorV1(
                    "Supabase persisted case listing crossed tenant boundary"
                )
            case_id = str(raw.get("case_id") or "").strip()
            if not case_id:
                continue
            if case_id not in by_case:
                by_case[case_id] = {
                    "case_ref": case_id,
                    "case_id": case_id,
                    "tenant_id": tenant,
                    "cliente_id": raw.get("cliente_id"),
                    "workbook_ref": str(raw.get("workbook_ref") or "").strip(),
                    "source_system_ref": str(raw.get("source_system_ref") or "").strip(),
                    "source_context_ref": str(raw.get("source_context_ref") or "").strip(),
                    "owner_actor_id": str(raw.get("owner_actor_id") or "").strip(),
                    "owner_actor_role": str(raw.get("owner_actor_role") or "").strip(),
                    "updated_at": str(raw.get("confirmed_at") or "").strip(),
                    "service_ref": "SERVICE_1",
                    "service_name": "Servicio 1 · evidencia confirmada",
                    "status": "EVIDENCIA PERSISTIDA",
                    "kind": "persisted_owner_evidence",
                }
        return tuple(by_case.values())

    def load_persisted_case(
        self,
        tenant_id: str,
        case_id: str,
    ) -> dict[str, object] | None:
        """Load durable owner evidence for one exact tenant/case identity."""
        tenant = str(tenant_id or "").strip()
        case_ref = str(case_id or "").strip()
        if not tenant or not case_ref:
            raise Service1SupabasePersistenceErrorV1(
                "tenant_id and case_id are required for case reentry"
            )
        try:
            response = (
                self._client.table(OWNER_CONFIRMATIONS_TABLE)
                .select(
                    "confirmation_event_ref,tenant_id,cliente_id,case_id,workbook_ref,"
                    "source_system_ref,source_context_ref,owner_actor_id,owner_actor_role,"
                    "sheet_ref,column_ref,question_ref,confirmation_scope,owner_answer,"
                    "confirmed_role,corrected_meaning,confirmed_at,event_payload"
                )
                .eq("tenant_id", tenant)
                .eq("case_id", case_ref)
                .order("confirmed_at", desc=False)
                .execute()
            )
        except Exception as exc:
            raise Service1SupabasePersistenceErrorV1(
                "Supabase persisted case lookup failed"
            ) from exc
        data = _response_data(response)
        if data is None or data == []:
            return None
        if not isinstance(data, list):
            raise Service1SupabasePersistenceErrorV1(
                "Supabase persisted case lookup returned invalid data"
            )
        evidence: list[dict[str, object]] = []
        first: Mapping[str, object] | None = None
        for raw in data:
            if (
                not isinstance(raw, Mapping)
                or str(raw.get("tenant_id") or "") != tenant
                or str(raw.get("case_id") or "") != case_ref
            ):
                raise Service1SupabasePersistenceErrorV1(
                    "Supabase persisted case lookup crossed tenant/case boundary"
                )
            first = first or raw
            evidence.append(dict(raw))
        assert first is not None
        return {
            "case_ref": case_ref,
            "case_id": case_ref,
            "tenant_id": tenant,
            "cliente_id": first.get("cliente_id"),
            "workbook_ref": str(first.get("workbook_ref") or "").strip(),
            "source_system_ref": str(first.get("source_system_ref") or "").strip(),
            "source_context_ref": str(first.get("source_context_ref") or "").strip(),
            "owner_actor_id": str(first.get("owner_actor_id") or "").strip(),
            "owner_actor_role": str(first.get("owner_actor_role") or "").strip(),
            "kind": "persisted_owner_evidence",
            "evidence": evidence,
        }

    def load_current_semantic_contract(
        self,
        tenant_id: str,
        source_system_ref: str,
        source_context_ref: str,
        sheet_ref: str,
        source_column_name: str,
    ) -> Service1TenantSemanticContractV1 | None:
        tenant = str(tenant_id or "").strip()
        system_ref = str(source_system_ref or "").strip()
        context_ref = str(source_context_ref or "").strip()
        sheet = str(sheet_ref or "").strip()
        column = str(source_column_name or "").strip()
        if not all((tenant, system_ref, context_ref, sheet, column)):
            raise Service1SupabasePersistenceErrorV1(
                "complete tenant semantic series identity is required"
            )
        try:
            response = (
                self._client.table(SEMANTIC_CONTRACTS_TABLE)
                .select("tenant_id,revision,contract_id,contract_payload")
                .eq("tenant_id", tenant)
                .eq("source_system_ref", system_ref)
                .eq("source_context_ref", context_ref)
                .eq("sheet_ref", sheet)
                .eq("source_column_name", column)
                .order("revision", desc=True)
                .limit(2)
                .execute()
            )
        except Exception as exc:
            raise Service1SupabasePersistenceErrorV1(
                "Supabase current semantic contract lookup failed"
            ) from exc
        data = _response_data(response)
        if data is None or data == []:
            return None
        if not isinstance(data, list):
            raise Service1SupabasePersistenceErrorV1(
                "Supabase current semantic contract lookup returned invalid data"
            )
        contracts: list[Service1TenantSemanticContractV1] = []
        for raw in data:
            if not isinstance(raw, Mapping) or str(raw.get("tenant_id") or "") != tenant:
                raise Service1SupabasePersistenceErrorV1(
                    "Supabase current semantic contract lookup crossed tenant boundary"
                )
            payload = raw.get("contract_payload")
            if not isinstance(payload, Mapping):
                raise Service1SupabasePersistenceErrorV1(
                    "Supabase current semantic contract payload is invalid"
                )
            contract = service_1_tenant_semantic_contract_from_mapping_v1(payload)
            if (
                contract.tenant_id != tenant
                or contract.source_system_ref != system_ref
                or contract.source_context_ref != context_ref
                or contract.sheet_ref != sheet
                or contract.source_column_name != column
            ):
                raise Service1SupabasePersistenceErrorV1(
                    "Supabase current semantic contract does not match requested series"
                )
            contracts.append(contract)
        highest_revision = max(contract.revision for contract in contracts)
        latest = [contract for contract in contracts if contract.revision == highest_revision]
        if len({contract.contract_id for contract in latest}) != 1:
            raise Service1SupabasePersistenceErrorV1(
                "Supabase current semantic contract revision is ambiguous"
            )
        return latest[0]

    def __call__(
        self,
        event: Service1OwnerConfirmationEventV1,
        contract: Service1TenantSemanticContractV1,
    ) -> bool:
        owner_row = _owner_confirmation_row(event, contract)
        contract_row = _semantic_contract_row(contract)
        try:
            owner_response = (
                self._client.table(OWNER_CONFIRMATIONS_TABLE)
                .upsert(
                    owner_row,
                    on_conflict="confirmation_event_ref",
                    ignore_duplicates=True,
                )
                .select("confirmation_event_ref")
                .execute()
            )
            if not _confirmed_insert(
                owner_response,
                expected_key="confirmation_event_ref",
                expected_value=contract.confirmation_event_ref,
            ):
                # An ignored duplicate may return no row. Verify canonical identity exists.
                existing_owner = (
                    self._client.table(OWNER_CONFIRMATIONS_TABLE)
                    .select("confirmation_event_ref")
                    .eq("confirmation_event_ref", contract.confirmation_event_ref)
                    .eq("tenant_id", contract.tenant_id)
                    .limit(1)
                    .execute()
                )
                if not _confirmed_insert(
                    existing_owner,
                    expected_key="confirmation_event_ref",
                    expected_value=contract.confirmation_event_ref,
                ):
                    return False

            contract_response = (
                self._client.table(SEMANTIC_CONTRACTS_TABLE)
                .upsert(
                    contract_row,
                    on_conflict="contract_id",
                    ignore_duplicates=True,
                )
                .select("contract_id")
                .execute()
            )
            if _confirmed_insert(
                contract_response,
                expected_key="contract_id",
                expected_value=contract.contract_id,
            ):
                return True

            existing_contract = (
                self._client.table(SEMANTIC_CONTRACTS_TABLE)
                .select("contract_id")
                .eq("contract_id", contract.contract_id)
                .eq("tenant_id", contract.tenant_id)
                .limit(1)
                .execute()
            )
            return _confirmed_insert(
                existing_contract,
                expected_key="contract_id",
                expected_value=contract.contract_id,
            )
        except Exception as exc:
            raise Service1SupabasePersistenceErrorV1(
                "Supabase persistence failed"
            ) from exc


__all__ = [
    "SUPABASE_URL_ENV",
    "SUPABASE_SERVICE_ROLE_KEY_ENV",
    "OWNER_CONFIRMATIONS_TABLE",
    "SEMANTIC_CONTRACTS_TABLE",
    "Service1SupabaseConfigV1",
    "Service1SupabasePersistenceErrorV1",
    "Service1SupabasePersistenceAdapterV1",
    "load_service_1_supabase_config_v1",
    "create_service_1_supabase_client_v1",
]
