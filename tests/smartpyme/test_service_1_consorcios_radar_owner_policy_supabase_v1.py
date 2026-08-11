import os
import uuid

import pytest

from pymia.smartpyme.service_1_consorcios_collection_aging_v1 import (
    evaluate_collection_aging_from_normalized_tables_v1,
)
from pymia.smartpyme.service_1_consorcios_radar_owner_policy_wiring_v1 import (
    evaluate_consorcios_radar_observation_with_owner_policy_v1,
    persist_consorcios_radar_owner_policy_v1,
)
from pymia.smartpyme.service_1_consorcios_radar_plug_v1 import (
    OBS_DEBT_EQUIVALENT_PERIODS,
    project_collection_aging_to_radar_v1,
)
from pymia.smartpyme.service_1_radar_observation_policy_v1 import COMM_ALERT
from pymia.smartpyme.service_1_radar_observable_v1 import OP_GTE
from pymia.smartpyme.service_1_radar_supabase_persistence_v1 import (
    RADAR_POLICIES_TABLE,
    Service1RadarSupabasePersistenceAdapterV1,
)
from pymia.smartpyme.service_1_tenant_identity_contract_v1 import (
    build_service_1_tenant_identity_contract_v1,
)


_REQUIRED_ENV = ("PYMIA_SUPABASE_URL", "PYMIA_SUPABASE_SERVICE_ROLE_KEY")


def _supabase_ready() -> bool:
    return all(str(os.environ.get(name) or "").strip() for name in _REQUIRED_ENV)


@pytest.mark.skipif(not _supabase_ready(), reason="Supabase RADAR environment is not configured")
def test_consorcios_owner_policy_physical_supabase_roundtrip_and_event() -> None:
    tenant_id = f"tenant-radar-e2e-{uuid.uuid4().hex[:12]}"
    policy_ref = f"policy-{uuid.uuid4().hex[:12]}"
    identity = build_service_1_tenant_identity_contract_v1(
        tenant_id=tenant_id,
        case_id=f"case-{uuid.uuid4().hex[:12]}",
        cliente_id="cliente-radar-e2e",
        owner_actor_id="owner-radar-e2e",
        owner_actor_role="OWNER",
        source_system_ref="assisted-web",
        source_context_ref="consorcios-radar-owner-policy",
        workbook_ref="workbook-radar-e2e",
    )
    store = Service1RadarSupabasePersistenceAdapterV1.from_environment()

    policy = persist_consorcios_radar_owner_policy_v1(
        identity_contract=identity,
        owner_request={
            "policy_ref": policy_ref,
            "observable_ref": OBS_DEBT_EQUIVALENT_PERIODS,
            "enabled": True,
            "operator": OP_GTE,
            "comparison_value": "2",
            "communication_level": COMM_ALERT,
            "confirmed_by_owner": True,
        },
        policy_store=store,
    )
    loaded = store.load_policy(tenant_id=tenant_id, policy_ref=policy_ref)
    assert loaded == policy

    result = evaluate_collection_aging_from_normalized_tables_v1(
        normalized_tables=[
            {
                "sheet_name": "Expensas",
                "rows": [
                    {
                        "unidad_funcional": "UF-E2E",
                        "saldo_anterior": 300,
                        "expensa_mes": 100,
                    }
                ],
            }
        ]
    )
    observation = project_collection_aging_to_radar_v1(computation_result=result)[0]
    events = evaluate_consorcios_radar_observation_with_owner_policy_v1(
        identity_contract=identity,
        observation=observation,
        policy_store=store,
    )
    assert len(events) == 1
    assert events[0].tenant_id == tenant_id
    assert events[0].policy_ref == policy_ref
    assert events[0].communication_level == COMM_ALERT

    # Cleanup the physical smoke row so the test does not leave tenant data behind.
    store._client.table(RADAR_POLICIES_TABLE).delete().eq("tenant_id", tenant_id).eq(
        "policy_ref", policy_ref
    ).execute()
