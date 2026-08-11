from types import SimpleNamespace

import pytest

from pymia.smartpyme.service_1_radar_observable_v1 import OP_GT, RadarObservableV1
from pymia.smartpyme.service_1_radar_observation_policy_v1 import (
    COMM_ALERT,
    RadarObservationPolicyV1,
)
from pymia.smartpyme.service_1_radar_supabase_persistence_v1 import (
    RADAR_POLICIES_TABLE,
    Service1RadarSupabasePersistenceAdapterV1,
)
from pymia.smartpyme.service_1_supabase_persistence_v1 import (
    Service1SupabasePersistenceErrorV1,
)


class FakeTable:
    def __init__(self, rows):
        self.rows = rows
        self.filters = []
        self.pending_upsert = None
        self.ignore_duplicates = False

    def select(self, *_args):
        return self

    def eq(self, field, value):
        self.filters.append((field, value))
        return self

    def order(self, *_args, **_kwargs):
        return self

    def limit(self, *_args):
        return self

    def upsert(self, row, *, on_conflict, ignore_duplicates):
        assert on_conflict == "tenant_id,policy_ref"
        self.pending_upsert = dict(row)
        self.ignore_duplicates = ignore_duplicates
        return self

    def execute(self):
        if self.pending_upsert is not None:
            row = self.pending_upsert
            existing = next(
                (
                    r
                    for r in self.rows
                    if r["policy_ref"] == row["policy_ref"]
                    and r["tenant_id"] == row["tenant_id"]
                ),
                None,
            )
            if existing is None:
                self.rows.append(row)
                return SimpleNamespace(data=[row])
            if self.ignore_duplicates:
                return SimpleNamespace(data=[])
        result = list(self.rows)
        for field, value in self.filters:
            result = [r for r in result if r.get(field) == value]
        return SimpleNamespace(data=result)


class FakeClient:
    def __init__(self):
        self.rows = []
        self.last_table = None

    def table(self, name):
        assert name == RADAR_POLICIES_TABLE
        self.last_table = FakeTable(self.rows)
        return self.last_table


def policy(*, tenant="tenant-a", ref="p1", enabled=True, value="90"):
    return RadarObservationPolicyV1(
        tenant_id=tenant,
        policy_ref=ref,
        observable_ref="consorcios.collection_rate_pct",
        enabled=enabled,
        operator=OP_GT,
        comparison_value=value,
        communication_level=COMM_ALERT,
        confirmed_by_owner=True,
    )


def test_save_and_load_policy_round_trip():
    client = FakeClient()
    store = Service1RadarSupabasePersistenceAdapterV1(client)
    original = policy()
    assert store.save_policy(original) is True
    loaded = store.load_policy(tenant_id="tenant-a", policy_ref="p1")
    assert loaded == original


def test_idempotent_replay_same_policy_is_accepted():
    client = FakeClient()
    store = Service1RadarSupabasePersistenceAdapterV1(client)
    original = policy()
    assert store.save_policy(original) is True
    assert store.save_policy(original) is True
    assert len(client.rows) == 1


def test_same_policy_ref_with_different_payload_fails_closed():
    client = FakeClient()
    store = Service1RadarSupabasePersistenceAdapterV1(client)
    assert store.save_policy(policy(value="90")) is True
    with pytest.raises(Service1SupabasePersistenceErrorV1, match="different payload"):
        store.save_policy(policy(value="80"))


def test_list_is_tenant_scoped_and_enabled_filter_is_preserved():
    client = FakeClient()
    store = Service1RadarSupabasePersistenceAdapterV1(client)
    assert store.save_policy(policy(ref="a1", enabled=True))
    assert store.save_policy(policy(ref="a2", enabled=False))
    assert store.save_policy(policy(tenant="tenant-b", ref="b1", enabled=True))

    all_a = store.list_policies(tenant_id="tenant-a")
    assert {p.policy_ref for p in all_a} == {"a1", "a2"}

    enabled_a = store.list_policies(tenant_id="tenant-a", enabled_only=True)
    assert [p.policy_ref for p in enabled_a] == ["a1"]


def test_cross_tenant_row_in_response_fails_closed():
    client = FakeClient()
    store = Service1RadarSupabasePersistenceAdapterV1(client)
    p = policy(tenant="tenant-b", ref="b1")
    client.rows.append({
        "policy_ref": p.policy_ref,
        "tenant_id": "tenant-a",
        "enabled": True,
        "policy_payload": p.to_dict(),
    })
    with pytest.raises(Service1SupabasePersistenceErrorV1, match="identity mismatch"):
        store.list_policies(tenant_id="tenant-a")


def test_policy_contract_itself_requires_owner_confirmation():
    with pytest.raises(ValueError, match="confirmed_by_owner"):
        RadarObservationPolicyV1(
            tenant_id="tenant-a",
            policy_ref="p1",
            observable_ref="consorcios.collection_rate_pct",
            enabled=True,
            operator=OP_GT,
            comparison_value="90",
            communication_level=COMM_ALERT,
            confirmed_by_owner=False,
        )


def test_db_payload_with_non_boolean_enabled_fails_closed():
    client = FakeClient()
    store = Service1RadarSupabasePersistenceAdapterV1(client)
    p = policy()
    payload = p.to_dict()
    payload["enabled"] = "yes"
    client.rows.append({
        "policy_ref": p.policy_ref,
        "tenant_id": p.tenant_id,
        "enabled": True,
        "policy_payload": payload,
    })

    with pytest.raises(Service1SupabasePersistenceErrorV1, match="enabled must be boolean"):
        store.load_policy(tenant_id=p.tenant_id, policy_ref=p.policy_ref)


def test_db_payload_with_non_boolean_owner_confirmation_fails_closed():
    client = FakeClient()
    store = Service1RadarSupabasePersistenceAdapterV1(client)
    p = policy()
    payload = p.to_dict()
    payload["confirmed_by_owner"] = "true"
    client.rows.append({
        "policy_ref": p.policy_ref,
        "tenant_id": p.tenant_id,
        "enabled": True,
        "policy_payload": payload,
    })

    with pytest.raises(Service1SupabasePersistenceErrorV1, match="must be owner-confirmed"):
        store.load_policy(tenant_id=p.tenant_id, policy_ref=p.policy_ref)


def test_same_policy_ref_is_allowed_for_different_tenants():
    client = FakeClient()
    store = Service1RadarSupabasePersistenceAdapterV1(client)

    assert store.save_policy(policy(tenant="tenant-a", ref="shared-ref")) is True
    assert store.save_policy(policy(tenant="tenant-b", ref="shared-ref")) is True
    assert len(client.rows) == 2
