from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

import pymia.smartpyme.service_1_assisted_web_semantic_reception_v1 as semantic_web

from pymia.smartpyme.service_1_analysis_evidence_preparation_v1 import (
    STATUS_PREPARED,
    build_service_1_analysis_evidence_preparation_v1,
)
from pymia.smartpyme.service_1_analysis_math_execution_v1 import (
    SCHEMA_VERSION as F8_SCHEMA_VERSION,
    STATUS_EVALUATED,
    execute_service_1_analysis_math_v1,
)
from pymia.smartpyme.service_1_analysis_result_projection_v1 import (
    STATUS_READY as F9_STATUS_READY,
    build_service_1_analysis_result_projection_v1,
)
from pymia.smartpyme.service_1_assisted_web_semantic_reception_v1 import (
    Service1SemanticReceptionWebApplicationV1,
)
from pymia.smartpyme.service_1_deterministic_semantic_proposal_provider_v1 import (
    build_service_1_deterministic_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_dynamic_analysis_discovery_v1 import (
    build_service_1_dynamic_analysis_discovery_v1,
)
from pymia.smartpyme.service_1_result_memory_v1 import (
    MATH_RUNTIME_VERSION_KEY,
    Service1ResultMemoryErrorV1,
    service_1_result_memory_record_from_mapping_v1,
)
from pymia.smartpyme.service_1_result_memory_wiring_v1 import (
    build_service_1_result_memory_from_execution_v1,
    derive_service_1_result_memory_period_v1,
)
from pymia.smartpyme.service_1_result_read_boundary_v1 import (
    ResultReadBoundary,
    Service1ResultQueryV1,
)
from pymia.smartpyme.service_1_workbook_logical_model_v1 import (
    build_service_1_workbook_logical_model_v1,
)
from pymia.smartpyme.service_1_supabase_persistence_v1 import (
    ANALYSIS_RESULT_MEMORY_TABLE,
    Service1SupabasePersistenceAdapterV1,
    Service1SupabasePersistenceErrorV1,
)
from pymia.smartpyme.service_1_tenant_identity_contract_v1 import (
    build_service_1_tenant_identity_contract_v1,
)


@pytest.fixture(scope="module")
def f13_execution(tmp_path_factory: pytest.TempPathFactory) -> dict:
    workbook_path = Path(__file__).resolve().parents[2] / "prueba_excels" / "cafeteria_abc.xlsx"
    assert workbook_path.is_file()
    app = Service1SemanticReceptionWebApplicationV1(
        output_dir=tmp_path_factory.mktemp("f13-cafeteria"),
        semantic_provider=build_service_1_deterministic_semantic_proposal_v1,
    )
    session_id = "f13-cafeteria"
    status, _page = app.receive_xlsx(
        session_id=session_id,
        filename=workbook_path.name,
        content=workbook_path.read_bytes(),
        selected_launch_review=None,
    )
    assert status == 200
    state = app.session(session_id)
    steps = 0
    while state.semantic_questions:
        steps += 1
        assert steps <= 30
        question = state.semantic_questions[0]
        status, _page = app.confirm_meanings(
            session_id=session_id,
            fields={f"action_{question['decision_id']}": "ACCEPT"},
        )
        assert status == 200
    semantic_run = state.semantic_assistance_state["semantic_run"]
    assert semantic_run["status"] == "CONFIRMED_BINDINGS"
    discovery = build_service_1_dynamic_analysis_discovery_v1(confirmed_bindings=semantic_run)
    by_id = {item.analysis_id: item for item in discovery.analyses}
    workbook_logical_model = build_service_1_workbook_logical_model_v1(
        ingestion_output=state.ingestion_output,
    )
    assert workbook_logical_model["status"] == "WORKBOOK_LOGICAL_MODEL_READY"

    def execute(analysis_id: str):
        item = by_id[analysis_id]
        governed = item.governed_analysis_input
        assert governed is not None
        prepared = build_service_1_analysis_evidence_preparation_v1(
            case_id=governed.case_id,
            governed_analysis_input=governed,
            ingestion_output=state.ingestion_output,
            d7_workbook_logical_model=workbook_logical_model,
        )
        assert prepared.status == STATUS_PREPARED, prepared.to_dict()
        assert prepared.prepared_evidence is not None
        math = execute_service_1_analysis_math_v1(
            case_id=governed.case_id,
            governed_analysis_input=governed,
            prepared_evidence=prepared.prepared_evidence,
        )
        assert math.status == STATUS_EVALUATED, math.to_dict()
        projection = build_service_1_analysis_result_projection_v1(
            math_result=math.result,
            prepared_evidence=prepared.prepared_evidence,
            currency_code=None,
        )
        assert projection.status == F9_STATUS_READY, projection.to_dict()
        assert projection.projection is not None
        return governed, projection.projection

    case_id = str(state.ingestion_output["workbook_context"]["case_id"])
    identity = build_service_1_tenant_identity_contract_v1(
        tenant_id="tenant-f13",
        cliente_id="cliente-f13",
        case_id=case_id,
        owner_actor_id="owner-f13",
        owner_actor_role="OWNER",
        source_system_ref="xlsx_upload",
        source_context_ref="service1-f13-test",
        workbook_ref=workbook_path.name,
    )
    return {
        "app": app,
        "session_id": session_id,
        "state": state,
        "semantic_run": semantic_run,
        "identity": identity,
        "execute": execute,
    }


def _record(context: dict, analysis_id: str = "sales_total", executed_at: str = "2026-08-18T20:00:00+00:00"):
    governed, projection = context["execute"](analysis_id)
    record = build_service_1_result_memory_from_execution_v1(
        identity_contract=context["identity"],
        governed_analysis_input=governed,
        result_projection=projection,
        semantic_run=context["semantic_run"],
        ingestion_output=context["state"].ingestion_output,
        executed_at=executed_at,
    )
    return governed, projection, record


def test_f13_real_cafeteria_memory_captures_required_longitudinal_contract(f13_execution: dict) -> None:
    governed, projection, record = _record(f13_execution)
    assert record.tenant_id == "tenant-f13"
    assert record.case_id == governed.case_id
    assert record.analysis_id == "sales_total"
    assert record.period.start_date == "2026-01-01"
    assert record.period.end_date == "2026-05-25"
    assert record.period.period_ref == "2026-01-01/2026-05-25"
    assert record.period.source_refs == ("Ventas.Fecha",)
    assert record.grain == projection.result_set.grain.to_dict()
    assert record.formula_versions[MATH_RUNTIME_VERSION_KEY] == F8_SCHEMA_VERSION
    assert record.result_set_integrity_digest == projection.result_set.integrity.digest
    assert record.result_set["integrity"]["digest"] == projection.result_set.integrity.digest
    assert record.evidence_refs
    assert record.owner_evidence_refs
    assert record.artifact_ref == f"resultset:sha256:{projection.result_set.integrity.digest}"
    assert record.artifact["kind"] == "GOVERNED_RESULT_SET"
    assert record.to_dict()["automatic_reuse_authorized"] is False


def test_f13_formula_versions_are_resolved_from_canonical_formula_source(f13_execution: dict) -> None:
    _governed, _projection, record = _record(f13_execution, "product_sales_concentration")
    assert record.formula_versions[MATH_RUNTIME_VERSION_KEY] == F8_SCHEMA_VERSION
    assert record.formula_versions["PYME_033_concentracion_sku"] == "1.0"


def test_f13_snapshot_identity_is_idempotent_across_reexecution_time(f13_execution: dict) -> None:
    _g1, _p1, first = _record(f13_execution, executed_at="2026-08-18T20:00:00+00:00")
    _g2, _p2, second = _record(f13_execution, executed_at="2026-08-19T20:00:00+00:00")
    assert first.memory_record_id == second.memory_record_id
    assert first.executed_at != second.executed_at


def test_r9_result_read_boundary_returns_ready_for_same_tenant_case_and_digest(
    f13_execution: dict,
) -> None:
    _governed, _projection, record = _record(f13_execution)
    boundary = ResultReadBoundary(
        lambda tenant_id, result_id: record
        if tenant_id == record.tenant_id and result_id == record.memory_record_id
        else None
    )
    packet = boundary.read(
        Service1ResultQueryV1(
            tenant_id=record.tenant_id,
            case_id=record.case_id,
            result_id=record.memory_record_id,
            expected_integrity_digest=record.result_set_integrity_digest,
        )
    )
    assert packet["status"] == "READY"
    assert packet["result_set"]["integrity"]["digest"] == (
        record.result_set_integrity_digest
    )


def test_r9_result_read_boundary_blocks_tenant_case_and_integrity_mismatch(
    f13_execution: dict,
) -> None:
    _governed, _projection, record = _record(f13_execution)
    boundary = ResultReadBoundary(lambda _tenant_id, _result_id: record)

    other_tenant = boundary.read(
        Service1ResultQueryV1(
            tenant_id="tenant-other",
            case_id=record.case_id,
            result_id=record.memory_record_id,
            expected_integrity_digest=record.result_set_integrity_digest,
        )
    )
    wrong_case = boundary.read(
        Service1ResultQueryV1(
            tenant_id=record.tenant_id,
            case_id="case-other",
            result_id=record.memory_record_id,
            expected_integrity_digest=record.result_set_integrity_digest,
        )
    )
    wrong_digest = boundary.read(
        Service1ResultQueryV1(
            tenant_id=record.tenant_id,
            case_id=record.case_id,
            result_id=record.memory_record_id,
            expected_integrity_digest="sha256:wrong",
        )
    )

    assert other_tenant["status"] == "BLOCKED"
    assert wrong_case["status"] == "BLOCKED"
    assert wrong_digest["status"] == "BLOCKED"
    assert other_tenant["blocked_reason"] == "TENANT_BOUNDARY_MISMATCH"
    assert wrong_case["blocked_reason"] == "CASE_BOUNDARY_MISMATCH"
    assert wrong_digest["blocked_reason"] == "RESULT_INTEGRITY_MISMATCH"


def test_r9_read_boundary_has_no_execution_dependencies() -> None:
    import inspect

    from pymia.smartpyme import service_1_result_read_boundary_v1 as module

    source = inspect.getsource(module)
    for forbidden in (
        "openpyxl",
        "run_service_1_product_pipeline_v1",
        "run_service_1_governed_analysis_v1",
        "build_service_1_dynamic_analysis_discovery_v1",
        "execute_service_1_analysis_math_v1",
        "build_service_1_analysis_result_projection_v1",
        "semantic_provider",
        "FormulaEngineService",
    ):
        assert forbidden not in source


def test_f13_loader_detects_resultset_tampering(f13_execution: dict) -> None:
    _governed, _projection, record = _record(f13_execution)
    payload = record.to_dict()
    payload["result_set"]["groups"][0]["measures"]["sales"]["value"] += 1
    with pytest.raises(Service1ResultMemoryErrorV1, match="RESULT_MEMORY_RESULT_SET_DRIFT"):
        service_1_result_memory_record_from_mapping_v1(payload)


def test_f13_period_blocks_without_owner_confirmed_date(f13_execution: dict) -> None:
    governed, projection = f13_execution["execute"]("sales_total")
    semantic_run = dict(f13_execution["semantic_run"])
    reentry = dict(semantic_run["reentry_packet"])
    reentry["p6_decisions"] = [
        item
        for item in reentry["p6_decisions"]
        if item.get("approved_role") != "operation_date"
    ]
    semantic_run["reentry_packet"] = reentry
    with pytest.raises(Service1ResultMemoryErrorV1, match="RESULT_MEMORY_PERIOD_EVIDENCE_REQUIRED"):
        derive_service_1_result_memory_period_v1(
            governed_analysis_input=governed,
            result_projection=projection,
            semantic_run=semantic_run,
            ingestion_output=f13_execution["state"].ingestion_output,
        )


def test_f13_web_execution_persists_and_reads_tenant_analysis_history(f13_execution: dict) -> None:
    app = f13_execution["app"]
    state = f13_execution["state"]
    identity = f13_execution["identity"]
    state.tenant_identity_contract = identity
    state.tenant_id = identity.tenant_id
    persisted = []

    def persist(record):
        persisted.append(record)
        return True

    app._persist_result_memory = persist
    app._load_result_memory = lambda tenant_id, analysis_id, limit=100: tuple(
        record
        for record in persisted
        if record.tenant_id == tenant_id and record.analysis_id == analysis_id
    )[:limit]

    status, page = app.run_review(
        session_id=f13_execution["session_id"],
        requested_capability="sales_total",
    )
    assert status == 200
    assert "Resumen del archivo" in page
    packet = state.last_review_result
    assert packet["status"] == "READY"
    assert packet["result_memory"]["status"] == "PERSISTED"
    assert packet["result_memory"]["persisted"] is True
    assert len(persisted) == 1
    assert persisted[0].tenant_id == identity.tenant_id
    assert persisted[0].analysis_id == "sales_total"

    history = app.result_memory_history(
        session_id=f13_execution["session_id"],
        analysis_id="sales_total",
    )
    assert len(history) == 1
    assert history[0]["memory_record_id"] == persisted[0].memory_record_id
    assert history[0]["result_set_integrity_digest"] == persisted[0].result_set_integrity_digest


def test_rc3_restart_lists_and_renders_persisted_resultset_without_xlsx_llm_or_recalculation(
    f13_execution: dict,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _governed, _projection, record = _record(f13_execution)
    list_calls: list[tuple[str, str | None, int]] = []
    load_calls: list[tuple[str, str]] = []
    semantic_calls: list[dict] = []

    def list_memory(tenant_id: str, analysis_id: str | None = None, *, limit: int = 100):
        list_calls.append((tenant_id, analysis_id, limit))
        return (record,)

    def load_memory(tenant_id: str, memory_record_id: str):
        load_calls.append((tenant_id, memory_record_id))
        return record

    def forbidden_semantic_provider(**kwargs):
        semantic_calls.append(dict(kwargs))
        raise AssertionError("semantic provider must not run during F13 reentry")

    def forbidden_product_root(**_kwargs):
        raise AssertionError("product root must not run during F13 reentry")

    monkeypatch.setattr(semantic_web, "run_service_1_product_pipeline_v1", forbidden_product_root)
    app = Service1SemanticReceptionWebApplicationV1(
        output_dir=tmp_path,
        semantic_provider=forbidden_semantic_provider,
        load_result_memory=list_memory,
        load_result_memory_record=load_memory,
    )
    session_id = "rc3-restart"
    app.bind_tenant_identity(
        session_id=session_id,
        tenant_id=record.tenant_id,
        cliente_id=record.cliente_id,
        owner_actor_id="owner-restart",
        owner_actor_role="OWNER",
    )
    state = app.session(session_id)
    assert state.ingestion_output is None
    assert state.semantic_assistance_state is None
    assert state.last_review_result is None

    status, cases_page = app.recent_cases(session_id=session_id)
    assert status == 200
    assert record.memory_record_id in cases_page
    assert record.analysis_id in cases_page
    assert "RESULTADO PERSISTIDO" in cases_page
    assert list_calls == [(record.tenant_id, None, 100)]

    status, result_page = app.open_case(
        session_id=session_id,
        case_ref=record.memory_record_id,
    )
    assert status == 200
    assert "Resumen del archivo" in result_page
    assert record.analysis_id in result_page
    assert load_calls == [(record.tenant_id, record.memory_record_id)]
    assert semantic_calls == []
    assert state.ingestion_output is None
    assert state.semantic_assistance_state is None
    assert state.last_review_result is None


def test_rc3_reentry_passes_exact_persisted_f9_resultset_to_renderer(
    f13_execution: dict,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _governed, _projection, record = _record(f13_execution, "sales_by_product")
    captured: list[dict] = []

    def capture_renderer(results):
        captured.extend(dict(item) for item in results)
        return "RC3_REENTRY_RENDERED"

    monkeypatch.setattr(semantic_web, "render_analysis_result_sets_v1", capture_renderer)
    monkeypatch.setattr(
        semantic_web,
        "run_service_1_product_pipeline_v1",
        lambda **_kwargs: pytest.fail("RC3 reentry recalculated through product root"),
    )
    app = Service1SemanticReceptionWebApplicationV1(
        output_dir=tmp_path,
        semantic_provider=lambda **_kwargs: pytest.fail("RC3 reentry invoked semantic provider"),
        load_result_memory_record=lambda tenant_id, memory_record_id: record,
    )
    session_id = "rc3-exact-resultset"
    app.bind_tenant_identity(
        session_id=session_id,
        tenant_id=record.tenant_id,
        cliente_id=record.cliente_id,
        owner_actor_id="owner-restart",
        owner_actor_role="OWNER",
    )

    status, page = app.open_case(session_id=session_id, case_ref=record.memory_record_id)
    assert status == 200
    assert page == "RC3_REENTRY_RENDERED"
    assert len(captured) == 1
    packet = captured[0]
    assert packet["schema_version"] == "SERVICE_1_F13_RESULT_MEMORY_REENTRY_V1"
    assert packet["analysis_id"] == record.analysis_id
    assert packet["result_set"] == record.to_dict()["result_set"]
    assert packet["result_set"]["integrity"]["digest"] == record.result_set_integrity_digest
    assert packet["result_memory"]["result_set_integrity_digest"] == record.result_set_integrity_digest
    assert packet["runtime_authorized"] is False
    assert packet["tool_execution_authorized"] is False
    assert packet["delivery_authorized"] is False


def test_rc3_reentry_rejects_cross_tenant_result_memory(
    f13_execution: dict,
    tmp_path: Path,
) -> None:
    _governed, _projection, record = _record(f13_execution)
    app = Service1SemanticReceptionWebApplicationV1(
        output_dir=tmp_path,
        semantic_provider=build_service_1_deterministic_semantic_proposal_v1,
        load_result_memory=lambda tenant_id, analysis_id=None, limit=100: (record,),
        load_result_memory_record=lambda tenant_id, memory_record_id: record,
    )
    session_id = "rc3-other-tenant"
    app.bind_tenant_identity(
        session_id=session_id,
        tenant_id="tenant-other",
        cliente_id="cliente-other",
        owner_actor_id="owner-other",
        owner_actor_role="OWNER",
    )

    history_status, history_page = app.recent_cases(session_id=session_id)
    assert history_status == 400
    assert record.memory_record_id not in history_page

    open_status, open_page = app.open_case(
        session_id=session_id,
        case_ref=record.memory_record_id,
    )
    assert open_status == 400
    assert "Resultado listo" not in open_page


def test_rc3_reentry_revalidates_digest_and_blocks_tampered_resultset(
    f13_execution: dict,
    tmp_path: Path,
) -> None:
    _governed, _projection, record = _record(f13_execution)
    tampered = record.to_dict()
    tampered["result_set"]["groups"][0]["measures"]["sales"]["value"] += 1
    app = Service1SemanticReceptionWebApplicationV1(
        output_dir=tmp_path,
        semantic_provider=build_service_1_deterministic_semantic_proposal_v1,
        load_result_memory_record=lambda tenant_id, memory_record_id: tampered,
    )
    session_id = "rc3-tampered"
    app.bind_tenant_identity(
        session_id=session_id,
        tenant_id=record.tenant_id,
        cliente_id=record.cliente_id,
        owner_actor_id="owner-restart",
        owner_actor_role="OWNER",
    )

    status, page = app.open_case(session_id=session_id, case_ref=record.memory_record_id)
    assert status == 400
    assert "validación de identidad e integridad" in page
    assert "Resultado listo" not in page
    assert app.session(session_id).last_review_result is None


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

    def order(self, column, **kwargs):
        self.calls.append((self.table_name, "order", column, kwargs))
        return self

    def limit(self, value):
        self.calls.append((self.table_name, "limit", value))
        return self

    def execute(self):
        self.calls.append((self.table_name, "execute"))
        return SimpleNamespace(data=self.response_data)


class _Client:
    def __init__(self, response_data: list[dict]):
        self.calls: list[tuple] = []
        self.response_data = response_data

    def table(self, table_name: str):
        self.calls.append((table_name, "table"))
        assert table_name == ANALYSIS_RESULT_MEMORY_TABLE
        return _Query(table_name, self.calls, self.response_data)


def test_f13_supabase_adapter_is_append_only_and_tenant_scoped(f13_execution: dict) -> None:
    _governed, _projection, record = _record(f13_execution)
    client = _Client([{"memory_record_id": record.memory_record_id}])
    adapter = Service1SupabasePersistenceAdapterV1(client)
    assert adapter.persist_result_memory(record) is True
    upsert = next(call for call in client.calls if len(call) > 1 and call[1] == "upsert")
    assert upsert[0] == ANALYSIS_RESULT_MEMORY_TABLE
    assert upsert[3] == {"on_conflict": "memory_record_id", "ignore_duplicates": True}
    assert upsert[2]["tenant_id"] == "tenant-f13"
    assert upsert[2]["analysis_id"] == "sales_total"
    assert upsert[2]["record_payload"]["result_set_integrity_digest"] == record.result_set_integrity_digest


def test_f13_supabase_adapter_lists_exact_tenant_analysis_history(f13_execution: dict) -> None:
    _governed, _projection, record = _record(f13_execution)
    client = _Client([
        {
            "tenant_id": record.tenant_id,
            "analysis_id": record.analysis_id,
            "period_start": record.period.start_date,
            "executed_at": record.executed_at,
            "memory_record_id": record.memory_record_id,
            "record_payload": record.to_dict(),
        }
    ])
    adapter = Service1SupabasePersistenceAdapterV1(client)
    rows = adapter.list_result_memory("tenant-f13", "sales_total")
    assert [item.memory_record_id for item in rows] == [record.memory_record_id]
    assert (ANALYSIS_RESULT_MEMORY_TABLE, "eq", "tenant_id", "tenant-f13") in client.calls
    assert (ANALYSIS_RESULT_MEMORY_TABLE, "eq", "analysis_id", "sales_total") in client.calls


def test_f13_supabase_adapter_loads_exact_record_identity(f13_execution: dict) -> None:
    _governed, _projection, record = _record(f13_execution)
    client = _Client([
        {
            "tenant_id": record.tenant_id,
            "memory_record_id": record.memory_record_id,
            "record_payload": record.to_dict(),
        }
    ])
    adapter = Service1SupabasePersistenceAdapterV1(client)
    loaded = adapter.load_result_memory_record(record.tenant_id, record.memory_record_id)
    assert loaded is not None
    assert loaded.memory_record_id == record.memory_record_id
    assert loaded.result_set_integrity_digest == record.result_set_integrity_digest


def test_f13_supabase_adapter_blocks_cross_tenant_history(f13_execution: dict) -> None:
    _governed, _projection, record = _record(f13_execution)
    client = _Client([
        {
            "tenant_id": "tenant-other",
            "analysis_id": record.analysis_id,
            "record_payload": record.to_dict(),
        }
    ])
    adapter = Service1SupabasePersistenceAdapterV1(client)
    with pytest.raises(Service1SupabasePersistenceErrorV1, match="crossed tenant boundary"):
        adapter.list_result_memory("tenant-f13", "sales_total")
