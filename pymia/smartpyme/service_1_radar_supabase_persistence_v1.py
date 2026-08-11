"""Supabase persistence adapter for owner-confirmed RADAR observation policies.

This adapter persists already validated ``RadarObservationPolicyV1`` artifacts.
It does not invent observables, thresholds, communication levels, or owner intent.
Policy identity is append-only by ``policy_ref``: the same reference may be
replayed idempotently only when its payload is identical.
"""
from __future__ import annotations

from typing import Any, Mapping

from pymia.smartpyme.service_1_radar_observation_policy_v1 import (
    RadarObservationPolicyV1,
)
from pymia.smartpyme.service_1_supabase_persistence_v1 import (
    Service1SupabasePersistenceErrorV1,
    create_service_1_supabase_client_v1,
    load_service_1_supabase_config_v1,
)

RADAR_POLICIES_TABLE = "service1_radar_observation_policies"


def _response_data(response: object) -> object:
    return getattr(response, "data", None)


def _policy_from_payload(payload: Mapping[str, object]) -> RadarObservationPolicyV1:
    enabled = payload.get("enabled")
    confirmed = payload.get("confirmed_by_owner")
    comparison_value = payload.get("comparison_value")
    if not isinstance(enabled, bool):
        raise Service1SupabasePersistenceErrorV1(
            "Supabase RADAR policy payload enabled must be boolean"
        )
    if confirmed is not True:
        raise Service1SupabasePersistenceErrorV1(
            "Supabase RADAR policy payload must be owner-confirmed"
        )
    if isinstance(comparison_value, bool):
        parsed_value: str | bool = comparison_value
    elif isinstance(comparison_value, str) and comparison_value.strip():
        parsed_value = comparison_value
    else:
        raise Service1SupabasePersistenceErrorV1(
            "Supabase RADAR policy payload comparison_value is invalid"
        )
    try:
        return RadarObservationPolicyV1(
            tenant_id=str(payload.get("tenant_id") or ""),
            policy_ref=str(payload.get("policy_ref") or ""),
            observable_ref=str(payload.get("observable_ref") or ""),
            enabled=enabled,
            operator=str(payload.get("operator") or ""),
            comparison_value=parsed_value,
            communication_level=str(payload.get("communication_level") or ""),
            confirmed_by_owner=confirmed,
        )
    except ValueError as exc:
        raise Service1SupabasePersistenceErrorV1(
            "Supabase RADAR policy payload is invalid"
        ) from exc


def _policy_row(policy: RadarObservationPolicyV1) -> dict[str, object]:
    return {
        "policy_ref": policy.policy_ref,
        "tenant_id": policy.tenant_id,
        "observable_ref": policy.observable_ref,
        "enabled": policy.enabled,
        "operator": policy.operator,
        "comparison_value": policy.comparison_value,
        "communication_level": policy.communication_level,
        "confirmed_by_owner": policy.confirmed_by_owner,
        "policy_payload": policy.to_dict(),
    }


def _extract_single_policy(
    data: object,
    *,
    tenant_id: str,
    policy_ref: str,
) -> RadarObservationPolicyV1 | None:
    if data is None or data == []:
        return None
    if not isinstance(data, list) or len(data) != 1:
        raise Service1SupabasePersistenceErrorV1(
            "Supabase RADAR policy lookup returned ambiguous or invalid data"
        )
    row = data[0]
    if not isinstance(row, Mapping):
        raise Service1SupabasePersistenceErrorV1(
            "Supabase RADAR policy lookup returned invalid row"
        )
    if str(row.get("tenant_id") or "") != tenant_id:
        raise Service1SupabasePersistenceErrorV1(
            "Supabase RADAR policy lookup crossed tenant boundary"
        )
    if str(row.get("policy_ref") or "") != policy_ref:
        raise Service1SupabasePersistenceErrorV1(
            "Supabase RADAR policy lookup returned wrong policy"
        )
    payload = row.get("policy_payload")
    if not isinstance(payload, Mapping):
        raise Service1SupabasePersistenceErrorV1(
            "Supabase RADAR policy payload is invalid"
        )
    policy = _policy_from_payload(payload)
    if policy.tenant_id != tenant_id or policy.policy_ref != policy_ref:
        raise Service1SupabasePersistenceErrorV1(
            "Supabase RADAR policy payload identity mismatch"
        )
    return policy


class Service1RadarSupabasePersistenceAdapterV1:
    """Tenant-scoped Supabase store for canonical owner-confirmed RADAR policies."""

    def __init__(self, client: Any) -> None:
        self._client = client

    @classmethod
    def from_environment(
        cls,
        environ: Mapping[str, str] | None = None,
    ) -> "Service1RadarSupabasePersistenceAdapterV1":
        config = load_service_1_supabase_config_v1(environ)
        return cls(create_service_1_supabase_client_v1(config))

    def save_policy(self, policy: RadarObservationPolicyV1) -> bool:
        if policy.confirmed_by_owner is not True:
            raise Service1SupabasePersistenceErrorV1(
                "RADAR policy must be explicitly confirmed by owner"
            )
        row = _policy_row(policy)
        try:
            response = (
                self._client.table(RADAR_POLICIES_TABLE)
                .upsert(
                    row,
                    on_conflict="tenant_id,policy_ref",
                    ignore_duplicates=True,
                )
                .select("policy_ref,tenant_id,policy_payload")
                .execute()
            )
            data = _response_data(response)
            if isinstance(data, list) and len(data) == 1:
                stored = _extract_single_policy(
                    data,
                    tenant_id=policy.tenant_id,
                    policy_ref=policy.policy_ref,
                )
                return stored is not None and stored.to_dict() == policy.to_dict()

            existing = self.load_policy(
                tenant_id=policy.tenant_id,
                policy_ref=policy.policy_ref,
            )
            if existing is None:
                return False
            if existing.to_dict() != policy.to_dict():
                raise Service1SupabasePersistenceErrorV1(
                    "RADAR policy_ref already exists with different payload"
                )
            return True
        except Service1SupabasePersistenceErrorV1:
            raise
        except Exception as exc:
            raise Service1SupabasePersistenceErrorV1(
                "Supabase RADAR policy persistence failed"
            ) from exc

    def load_policy(
        self,
        *,
        tenant_id: str,
        policy_ref: str,
    ) -> RadarObservationPolicyV1 | None:
        tenant = str(tenant_id or "").strip()
        ref = str(policy_ref or "").strip()
        if not tenant or not ref:
            raise Service1SupabasePersistenceErrorV1(
                "tenant_id and policy_ref are required for RADAR policy lookup"
            )
        try:
            response = (
                self._client.table(RADAR_POLICIES_TABLE)
                .select("policy_ref,tenant_id,policy_payload")
                .eq("tenant_id", tenant)
                .eq("policy_ref", ref)
                .limit(2)
                .execute()
            )
        except Exception as exc:
            raise Service1SupabasePersistenceErrorV1(
                "Supabase RADAR policy lookup failed"
            ) from exc
        return _extract_single_policy(
            _response_data(response), tenant_id=tenant, policy_ref=ref
        )

    def list_policies(
        self,
        *,
        tenant_id: str,
        enabled_only: bool = False,
    ) -> tuple[RadarObservationPolicyV1, ...]:
        tenant = str(tenant_id or "").strip()
        if not tenant:
            raise Service1SupabasePersistenceErrorV1(
                "tenant_id is required for RADAR policy listing"
            )
        try:
            query = (
                self._client.table(RADAR_POLICIES_TABLE)
                .select("policy_ref,tenant_id,policy_payload")
                .eq("tenant_id", tenant)
            )
            if enabled_only:
                query = query.eq("enabled", True)
            response = query.order("policy_ref").execute()
        except Exception as exc:
            raise Service1SupabasePersistenceErrorV1(
                "Supabase RADAR policy listing failed"
            ) from exc
        data = _response_data(response)
        if data is None:
            return ()
        if not isinstance(data, list):
            raise Service1SupabasePersistenceErrorV1(
                "Supabase RADAR policy listing returned invalid data"
            )
        policies: list[RadarObservationPolicyV1] = []
        seen: set[str] = set()
        for row in data:
            if not isinstance(row, Mapping):
                raise Service1SupabasePersistenceErrorV1(
                    "Supabase RADAR policy listing returned invalid row"
                )
            if str(row.get("tenant_id") or "") != tenant:
                raise Service1SupabasePersistenceErrorV1(
                    "Supabase RADAR policy listing crossed tenant boundary"
                )
            ref = str(row.get("policy_ref") or "")
            if not ref or ref in seen:
                raise Service1SupabasePersistenceErrorV1(
                    "Supabase RADAR policy listing contains ambiguous identity"
                )
            payload = row.get("policy_payload")
            if not isinstance(payload, Mapping):
                raise Service1SupabasePersistenceErrorV1(
                    "Supabase RADAR policy payload is invalid"
                )
            policy = _policy_from_payload(payload)
            if policy.tenant_id != tenant or policy.policy_ref != ref:
                raise Service1SupabasePersistenceErrorV1(
                    "Supabase RADAR policy payload identity mismatch"
                )
            if enabled_only and not policy.enabled:
                raise Service1SupabasePersistenceErrorV1(
                    "Supabase RADAR enabled-only lookup returned disabled policy"
                )
            seen.add(ref)
            policies.append(policy)
        return tuple(policies)


__all__ = [
    "RADAR_POLICIES_TABLE",
    "Service1RadarSupabasePersistenceAdapterV1",
]
