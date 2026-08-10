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

    def order(self, column, **kwargs):
        self.calls.append((self.table_name, "order", column, kwargs))
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


def test_adapter_lists_owner_confirmation_memory_scoped_to_tenant():
    client = _Client(
        {
            OWNER_CONFIRMATIONS_TABLE: [
                {
                    "confirmation_event_ref": "evt-1",
                    "tenant_id": "tenant-acme",
                    "sheet_ref": "Ventas",
                    "column_ref": "venta_total",
                    "question_ref": "q-1",
                    "owner_answer": "sold_amount",
                    "confirmed_at": "2026-08-09T20:00:00Z",
                }
            ],
            SEMANTIC_CONTRACTS_TABLE: [],
        }
    )
    adapter = Service1SupabasePersistenceAdapterV1(client)

    rows = adapter.list_owner_confirmation_memory("tenant-acme")

    assert len(rows) == 1
    assert rows[0]["tenant_id"] == "tenant-acme"
    assert rows[0]["owner_answer"] == "sold_amount"
    assert (OWNER_CONFIRMATIONS_TABLE, "eq", "tenant_id", "tenant-acme") in client.calls
    assert any(call[1] == "order" and call[2] == "confirmed_at" for call in client.calls)


def test_adapter_blocks_cross_tenant_memory_response():
    client = _Client(
        {
            OWNER_CONFIRMATIONS_TABLE: [
                {
                    "confirmation_event_ref": "evt-foreign",
                    "tenant_id": "tenant-other",
                    "sheet_ref": "Ventas",
                    "column_ref": "venta_total",
                    "question_ref": "q-foreign",
                    "owner_answer": "sold_amount",
                    "confirmed_at": "2026-08-09T20:00:00Z",
                }
            ],
            SEMANTIC_CONTRACTS_TABLE: [],
        }
    )
    adapter = Service1SupabasePersistenceAdapterV1(client)

    with pytest.raises(Service1SupabasePersistenceErrorV1, match="crossed tenant boundary"):
        adapter.list_owner_confirmation_memory("tenant-acme")


def test_load_current_semantic_contract_is_tenant_and_series_scoped():
    _event_value, contract = _artifacts()
    client = _Client(
        {
            OWNER_CONFIRMATIONS_TABLE: [],
            SEMANTIC_CONTRACTS_TABLE: [
                {
                    "tenant_id": contract.tenant_id,
                    "revision": contract.revision,
                    "contract_id": contract.contract_id,
                    "contract_payload": contract.to_dict(),
                }
            ],
        }
    )
    adapter = Service1SupabasePersistenceAdapterV1(client)

    loaded = adapter.load_current_semantic_contract(
        "tenant-acme",
        "xlsx_upload",
        "service1-assisted-web",
        "Hoja1",
        "Saldo",
    )

    assert loaded is not None
    assert loaded.contract_id == contract.contract_id
    eq_calls = [call for call in client.calls if len(call) > 1 and call[1] == "eq"]
    assert (SEMANTIC_CONTRACTS_TABLE, "eq", "tenant_id", "tenant-acme") in eq_calls
    assert (SEMANTIC_CONTRACTS_TABLE, "eq", "sheet_ref", "Hoja1") in eq_calls
    assert (SEMANTIC_CONTRACTS_TABLE, "eq", "source_column_name", "Saldo") in eq_calls


def test_load_current_semantic_contract_blocks_cross_tenant_payload():
    _event_value, contract = _artifacts()
    client = _Client(
        {
            OWNER_CONFIRMATIONS_TABLE: [],
            SEMANTIC_CONTRACTS_TABLE: [
                {
                    "tenant_id": "tenant-other",
                    "revision": contract.revision,
                    "contract_id": contract.contract_id,
                    "contract_payload": contract.to_dict(),
                }
            ],
        }
    )
    adapter = Service1SupabasePersistenceAdapterV1(client)

    with pytest.raises(Service1SupabasePersistenceErrorV1, match="crossed tenant boundary"):
        adapter.load_current_semantic_contract(
            "tenant-acme",
            "xlsx_upload",
            "service1-assisted-web",
            "Hoja1",
            "Saldo",
        )


def test_load_current_semantic_contract_blocks_ambiguous_latest_revision():
    first_event, first = _artifacts()
    event_a = build_service_1_owner_confirmation_event_v1(
        case_id=first.case_id,
        file_ref=first.workbook_ref,
        region_ref=None,
        sheet_ref=first.sheet_ref,
        column_ref=first.normalized_column_ref,
        question_ref=first.question_ref,
        owner_answer="saldo pendiente confirmado otra vez",
        confirmation_scope="FREE_TEXT_MEANING",
        corrected_meaning="saldo pendiente confirmado otra vez",
        timestamp="2026-08-09T20:10:00+00:00",
    )
    event_b = build_service_1_owner_confirmation_event_v1(
        case_id=first.case_id,
        file_ref=first.workbook_ref,
        region_ref=None,
        sheet_ref=first.sheet_ref,
        column_ref=first.normalized_column_ref,
        question_ref=first.question_ref,
        owner_answer="saldo pendiente confirmado nuevamente",
        confirmation_scope="FREE_TEXT_MEANING",
        corrected_meaning="saldo pendiente confirmado nuevamente",
        timestamp="2026-08-09T20:11:00+00:00",
    )
    second_a = build_service_1_tenant_semantic_contract_v1(
        tenant_id=first.tenant_id,
        cliente_id=first.cliente_id,
        owner_actor_id=first.owner_actor_id,
        owner_actor_role=first.owner_actor_role,
        source_system_ref=first.source_system_ref,
        source_context_ref=first.source_context_ref,
        workbook_ref=first.workbook_ref,
        expected_case_id=first.case_id,
        expected_sheet_ref=first.sheet_ref,
        expected_question_ref=first.question_ref,
        source_column_name=first.source_column_name,
        normalized_column_ref=first.normalized_column_ref,
        owner_confirmation_event=event_a,
        revision=2,
        supersedes_contract=first,
    )
    second_b = build_service_1_tenant_semantic_contract_v1(
        tenant_id=first.tenant_id,
        cliente_id=first.cliente_id,
        owner_actor_id=first.owner_actor_id,
        owner_actor_role=first.owner_actor_role,
        source_system_ref=first.source_system_ref,
        source_context_ref=first.source_context_ref,
        workbook_ref=first.workbook_ref,
        expected_case_id=first.case_id,
        expected_sheet_ref=first.sheet_ref,
        expected_question_ref=first.question_ref,
        source_column_name=first.source_column_name,
        normalized_column_ref=first.normalized_column_ref,
        owner_confirmation_event=event_b,
        revision=2,
        supersedes_contract=first,
    )
    client = _Client(
        {
            OWNER_CONFIRMATIONS_TABLE: [],
            SEMANTIC_CONTRACTS_TABLE: [
                {"tenant_id": first.tenant_id, "revision": 2, "contract_id": second_a.contract_id, "contract_payload": second_a.to_dict()},
                {"tenant_id": first.tenant_id, "revision": 2, "contract_id": second_b.contract_id, "contract_payload": second_b.to_dict()},
            ],
        }
    )
    adapter = Service1SupabasePersistenceAdapterV1(client)

    with pytest.raises(Service1SupabasePersistenceErrorV1, match="revision is ambiguous"):
        adapter.load_current_semantic_contract(
            first.tenant_id,
            first.source_system_ref,
            first.source_context_ref,
            first.sheet_ref,
            first.source_column_name,
        )
