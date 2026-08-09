from __future__ import annotations

from types import SimpleNamespace

import pytest

from pymia.smartpyme.service_1_owner_confirmation_event_v1 import (
    build_service_1_owner_confirmation_event_v1,
)
from pymia.smartpyme.service_1_supabase_persistence_v1 import (
    OWNER_CONFIRMATIONS_TABLE,
    SEMANTIC_CONTRACTS_TABLE,
    SUPABASE_SERVICE_ROLE_KEY_ENV,
    SUPABASE_URL_ENV,
    Service1SupabasePersistenceAdapterV1,
    Service1SupabasePersistenceErrorV1,
    load_service_1_supabase_config_v1,
)
from pymia.smartpyme.service_1_tenant_identity_contract_v1 import (
    build_service_1_tenant_identity_contract_v1,
)
from pymia.smartpyme.service_1_tenant_semantic_contract_v1 import (
    build_service_1_tenant_semantic_contract_v1,
)


class _Query:
    def __init__(self, table_name: str, calls: list[tuple], response_data: list[dict]):
        self.table_name = table_name
        self.calls = calls
        self.response_data = response_data

    def upsert(self, payload, **kwargs):
        self.calls.append((self.table_name, "upsert", payload, kwargs))
        return self

    def select(self, columns):
        self.calls.append((self.table_name, "select", columns))
        return self

    def eq(self, column, value):
        self.calls.append((self.table_name, "eq", column, value))
        return self

    def limit(self, value):
        self.calls.append((self.table_name, "limit", value))
        return self

    def execute(self):
        self.calls.append((self.table_name, "execute"))
        return SimpleNamespace(data=self.response_data)


class _Client:
    def __init__(self, responses: dict[str, list[dict]]):
        self.calls: list[tuple] = []
        self.responses = responses

    def table(self, table_name: str):
        self.calls.append((table_name, "table"))
        return _Query(table_name, self.calls, self.responses[table_name])


def _artifacts():
    identity = build_service_1_tenant_identity_contract_v1(
        tenant_id="tenant-acme",
        cliente_id="cliente-001",
        case_id="case-001",
        owner_actor_id="owner-001",
        owner_actor_role="OWNER",
        source_system_ref="xlsx_upload",
        source_context_ref="service1-assisted-web",
        workbook_ref="ventas.xlsx",
    )
    event = build_service_1_owner_confirmation_event_v1(
        case_id="case-001",
        file_ref="ventas.xlsx",
        region_ref=None,
        sheet_ref="Hoja1",
        column_ref="saldo",
        question_ref="q-001",
        owner_answer="saldo pendiente de cobro",
        confirmation_scope="FREE_TEXT_MEANING",
        corrected_meaning="saldo pendiente de cobro",
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
        source_column_name="Saldo",
        normalized_column_ref="saldo",
        owner_confirmation_event=event,
    )
    return event, contract


def test_config_uses_pymia_scoped_environment_names_only():
    config = load_service_1_supabase_config_v1(
        {
            SUPABASE_URL_ENV: "https://example.supabase.co",
            SUPABASE_SERVICE_ROLE_KEY_ENV: "secret-value-not-logged",
        }
    )
    assert config.url == "https://example.supabase.co"
    assert config.service_role_key == "secret-value-not-logged"


@pytest.mark.parametrize("missing", [SUPABASE_URL_ENV, SUPABASE_SERVICE_ROLE_KEY_ENV])
def test_config_fails_closed_when_required_value_is_missing(missing):
    values = {
        SUPABASE_URL_ENV: "https://example.supabase.co",
        SUPABASE_SERVICE_ROLE_KEY_ENV: "secret-value-not-logged",
    }
    values.pop(missing)
    with pytest.raises(Service1SupabasePersistenceErrorV1, match=missing):
        load_service_1_supabase_config_v1(values)


def test_adapter_persists_owner_event_before_semantic_contract():
    event, contract = _artifacts()
    client = _Client(
        {
            OWNER_CONFIRMATIONS_TABLE: [
                {"confirmation_event_ref": contract.confirmation_event_ref}
            ],
            SEMANTIC_CONTRACTS_TABLE: [{"contract_id": contract.contract_id}],
        }
    )
    adapter = Service1SupabasePersistenceAdapterV1(client)

    assert adapter(event, contract) is True

    upserts = [call for call in client.calls if len(call) > 1 and call[1] == "upsert"]
    assert upserts[0][0] == OWNER_CONFIRMATIONS_TABLE
    assert upserts[1][0] == SEMANTIC_CONTRACTS_TABLE
    owner_payload = upserts[0][2]
    contract_payload = upserts[1][2]
    assert owner_payload["tenant_id"] == "tenant-acme"
    assert owner_payload["cliente_id"] == "cliente-001"
    assert owner_payload["owner_actor_id"] == "owner-001"
    assert contract_payload["tenant_id"] == "tenant-acme"
    assert contract_payload["confirmation_event_ref"] == contract.confirmation_event_ref


def test_adapter_never_rewrites_tenant_from_cliente():
    event, contract = _artifacts()
    client = _Client(
        {
            OWNER_CONFIRMATIONS_TABLE: [
                {"confirmation_event_ref": contract.confirmation_event_ref}
            ],
            SEMANTIC_CONTRACTS_TABLE: [{"contract_id": contract.contract_id}],
        }
    )
    adapter = Service1SupabasePersistenceAdapterV1(client)
    adapter(event, contract)

    upserts = [call for call in client.calls if len(call) > 1 and call[1] == "upsert"]
    for call in upserts:
        payload = call[2]
        assert payload["tenant_id"] == "tenant-acme"
        assert payload["cliente_id"] == "cliente-001"
        assert payload["tenant_id"] != payload["cliente_id"]
