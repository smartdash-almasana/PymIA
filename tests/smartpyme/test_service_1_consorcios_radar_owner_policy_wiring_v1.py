from pymia.smartpyme.service_1_consorcios_collection_aging_v1 import (
    evaluate_collection_aging_from_normalized_tables_v1,
)
from pymia.smartpyme.service_1_consorcios_radar_owner_policy_wiring_v1 import (
    build_consorcios_radar_owner_menu_v1,
    evaluate_consorcios_radar_observation_with_owner_policy_v1,
    persist_consorcios_radar_owner_policy_v1,
)
from pymia.smartpyme.service_1_consorcios_radar_plug_v1 import (
    OBS_DEBT_EQUIVALENT_PERIODS,
    project_collection_aging_to_radar_v1,
)
from pymia.smartpyme.service_1_radar_observation_policy_v1 import COMM_ALERT
from pymia.smartpyme.service_1_radar_observable_v1 import OP_GTE
from pymia.smartpyme.service_1_tenant_identity_contract_v1 import (
    build_service_1_tenant_identity_contract_v1,
)


class _MemoryPolicyStore:
    def __init__(self) -> None:
        self.rows = {}

    def save_policy(self, policy):
        key = (policy.tenant_id, policy.policy_ref)
        existing = self.rows.get(key)
        if existing is not None and existing.to_dict() != policy.to_dict():
            raise ValueError("conflicting replay")
        self.rows[key] = policy
        return True

    def list_policies(self, *, tenant_id: str, enabled_only: bool = False):
        values = [
            policy
            for (tenant, _), policy in self.rows.items()
            if tenant == tenant_id and (not enabled_only or policy.enabled)
        ]
        return tuple(sorted(values, key=lambda item: item.policy_ref))


def _identity(tenant_id: str = "tenant-consorcio-1"):
    return build_service_1_tenant_identity_contract_v1(
        tenant_id=tenant_id,
        case_id="case-consorcio-2026-08",
        cliente_id="cliente-consorcio",
        owner_actor_id="owner-user-1",
        owner_actor_role="OWNER",
        source_system_ref="assisted-web",
        source_context_ref="consorcios-radar-policy",
        workbook_ref="workbook-consorcio-2026-08",
    )


def test_owner_menu_exposes_neutral_consorcios_catalog() -> None:
    menu = build_consorcios_radar_owner_menu_v1(identity_contract=_identity())
    refs = {item["observable_ref"] for item in menu["observables"]}
    assert OBS_DEBT_EQUIVALENT_PERIODS in refs
    assert menu["tenant_id"] == "tenant-consorcio-1"
    assert menu["owner_authority"]["confirmation_required"] is True
    for item in menu["observables"]:
        assert "severity" not in item
        assert "risk" not in item
        assert "communication_level" not in item


def test_owner_confirmed_policy_persists_and_drives_real_observation_event() -> None:
    identity = _identity()
    store = _MemoryPolicyStore()
    policy = persist_consorcios_radar_owner_policy_v1(
        identity_contract=identity,
        owner_request={
            "policy_ref": "debt-two-periods-alert",
            "observable_ref": OBS_DEBT_EQUIVALENT_PERIODS,
            "enabled": True,
            "operator": OP_GTE,
            "comparison_value": "2",
            "communication_level": COMM_ALERT,
            "confirmed_by_owner": True,
        },
        policy_store=store,
    )
    assert policy.tenant_id == identity.tenant_id
    assert store.list_policies(tenant_id=identity.tenant_id, enabled_only=True) == (policy,)

    result = evaluate_collection_aging_from_normalized_tables_v1(
        normalized_tables=[
            {
                "sheet_name": "Expensas",
                "rows": [
                    {
                        "unidad_funcional": "UF-12",
                        "saldo_anterior": 250,
                        "expensa_mes": 100,
                    }
                ],
            }
        ]
    )
    observation = project_collection_aging_to_radar_v1(
        computation_result=result
    )[0]
    events = evaluate_consorcios_radar_observation_with_owner_policy_v1(
        identity_contract=identity,
        observation=observation,
        policy_store=store,
    )
    assert len(events) == 1
    assert events[0].tenant_id == identity.tenant_id
    assert events[0].communication_level == COMM_ALERT
    assert events[0].comparison_value == "2"
    assert events[0].observed_value == "2.5"


def test_missing_owner_confirmation_fails_closed() -> None:
    store = _MemoryPolicyStore()
    try:
        persist_consorcios_radar_owner_policy_v1(
            identity_contract=_identity(),
            owner_request={
                "policy_ref": "not-confirmed",
                "observable_ref": OBS_DEBT_EQUIVALENT_PERIODS,
                "enabled": True,
                "operator": OP_GTE,
                "comparison_value": "2",
                "communication_level": COMM_ALERT,
                "confirmed_by_owner": False,
            },
            policy_store=store,
        )
    except ValueError as exc:
        assert "confirmation" in str(exc).lower()
    else:
        raise AssertionError("unconfirmed owner policy must fail closed")


def test_other_tenant_policy_is_not_loaded_for_owner() -> None:
    owner_a = _identity("tenant-a")
    owner_b = _identity("tenant-b")
    store = _MemoryPolicyStore()
    persist_consorcios_radar_owner_policy_v1(
        identity_contract=owner_a,
        owner_request={
            "policy_ref": "tenant-a-only",
            "observable_ref": OBS_DEBT_EQUIVALENT_PERIODS,
            "enabled": True,
            "operator": OP_GTE,
            "comparison_value": "1",
            "communication_level": COMM_ALERT,
            "confirmed_by_owner": True,
        },
        policy_store=store,
    )
    result = evaluate_collection_aging_from_normalized_tables_v1(
        normalized_tables=[
            {
                "sheet_name": "Expensas",
                "rows": [
                    {
                        "unidad_funcional": "UF-1",
                        "saldo_anterior": 200,
                        "expensa_mes": 100,
                    }
                ],
            }
        ]
    )
    observation = project_collection_aging_to_radar_v1(computation_result=result)[0]
    assert evaluate_consorcios_radar_observation_with_owner_policy_v1(
        identity_contract=owner_b,
        observation=observation,
        policy_store=store,
    ) == ()
