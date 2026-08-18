from __future__ import annotations

from io import BytesIO
from pathlib import Path

from openpyxl import Workbook

from pymia.smartpyme.service_1_deterministic_semantic_proposal_provider_v1 import (
    build_service_1_deterministic_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_assisted_semantic_product_wiring_v1 import (
    STATUS_CONFIRMED as SEM8_CONFIRMED,
    STATUS_OWNER_DIALOGUE_FOLLOWUP as SEM8_FOLLOWUP,
    STATUS_OWNER_DIALOGUE_REQUIRED as SEM8_OWNER_REQUIRED,
    revise_service_1_assisted_semantic_decision_v1,
    run_service_1_assisted_semantic_initial_v1,
    run_service_1_assisted_semantic_reentry_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_unconfirmed_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_assisted_web_semantic_reception_v1 import (
    Service1SemanticReceptionWebApplicationV1,
    build_service_1_post_semantic_analysis_discovery_v1,
)
from pymia.smartpyme.service_1_product_pipeline_v1 import (
    STATUS_BLOCKED,
    STATUS_COMPUTATION_PLAN_READY,
    STATUS_NEEDS_OWNER,
    run_service_1_product_pipeline_v1,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)


def _xlsx_bytes(sheets: dict[str, tuple[list[str], list[list[object]]]]) -> bytes:
    stream = BytesIO()
    workbook = Workbook()
    first = True
    for sheet_name, (headers, rows) in sheets.items():
        if first:
            sheet = workbook.active
            sheet.title = sheet_name
            first = False
        else:
            sheet = workbook.create_sheet(sheet_name)
        sheet.append(headers)
        for row in rows:
            sheet.append(row)
    workbook.save(stream)
    return stream.getvalue()


def _ingestion(filename: str, content: bytes) -> dict:
    intake = build_service_1_web_column_confirmation_intake_boundary_v1(
        uploaded_xlsx_bytes=content,
        uploaded_filename=filename,
        include_all_sheets=True,
    )
    assert intake["status"] != "BLOCKED"
    canonical = build_service_1_unconfirmed_canonical_ingestion_output_v1(
        owner_question_packet=intake
    )
    assert canonical["status"] != "BLOCKED"
    return canonical["ingestion_output"]


def _candidate_for_variable(payload: dict, column_ref: str, variable_name: str) -> dict:
    sheet_name, column_name = column_ref.split(".", 1)
    for hypothesis in payload["deterministic_hypotheses"]:
        if (
            str(hypothesis.get("sheet_name") or "") != sheet_name
            or str(hypothesis.get("column_name") or "") != column_name
        ):
            continue
        for candidate in hypothesis.get("candidate_meanings") or []:
            if str(candidate.get("variable_name") or "") == variable_name:
                return dict(candidate)
    raise AssertionError(f"deterministic candidate not found: {column_ref} -> {variable_name}")


def _proposal_from_assignments(payload: dict, assignments: dict[str, str], *, include_relation: bool = False) -> dict:
    concepts = []
    for index, (column_ref, variable_name) in enumerate(assignments.items(), start=1):
        candidate = _candidate_for_variable(payload, column_ref, variable_name)
        concepts.append(
            {
                "proposal_id": f"concept:{index}:{column_ref}",
                "target_column_refs": [column_ref],
                "semantic_role": candidate["semantic_role"],
                "variable_name": candidate["variable_name"],
                "confidence": 0.95,
                "rationale": "deterministic hypothesis plus workbook structure",
                "evidence_refs": [f"ev:column:{column_ref}:type"],
            }
        )

    all_refs = {str(item["column_ref"]) for item in payload["workbook_profile"]["columns"]}
    irrelevant = sorted(all_refs - set(assignments))
    relationships = []
    if include_relation:
        relation = next(
            item
            for item in payload["workbook_profile"]["relationships"]
            if item["left_column_ref"] == "Ventas.ProductoID"
            and item["right_column_ref"] == "Productos.ProductoID"
        )
        relationships.append(
            {
                "relationship_id": "relationship:ventas-productos",
                "left_column_ref": relation["left_column_ref"],
                "right_column_ref": relation["right_column_ref"],
                "relationship_type": relation["relationship_kind"],
                "confidence": 0.98,
                "rationale": "cross-sheet key overlap",
                "evidence_refs": [
                    "ev:relationship:Ventas.ProductoID->Productos.ProductoID:overlap"
                ],
            }
        )

    return {
        "schema_version": "SERVICE_1_LLM_SEMANTIC_PROPOSAL_V1",
        "concept_proposals": concepts,
        "relationship_proposals": relationships,
        "duplicate_semantics": [],
        "irrelevant_refs": irrelevant,
        "material_ambiguities": [],
    }


def _accept_all(initial_packet: dict) -> list[dict[str, str]]:
    return [
        {"decision_id": str(item["decision_id"]), "action": "ACCEPT"}
        for item in initial_packet["owner_questions"]
    ]


def test_sem8_workbook_first_calls_existing_provider_with_full_allowed_roles() -> None:
    ingestion = _ingestion(
        "caja_workbook_first.xlsx",
        _xlsx_bytes(
            {
                "Caja": (
                    ["SaldoInicial", "CobrosEsperados", "PagosEsperados"],
                    [[1000, 400, 250]],
                )
            }
        ),
    )
    provider_calls: list[dict] = []

    def provider(payload: dict) -> dict:
        provider_calls.append(payload)
        assert payload["requested_capability"] is None
        assert payload["capability_relevant_roles"] == payload["allowed_semantic_roles"]
        return _proposal_from_assignments(
            payload,
            {
                "Caja.SaldoInicial": "initial_balance",
                "Caja.CobrosEsperados": "expected_collections",
                "Caja.PagosEsperados": "expected_payments",
            },
        )

    initial = run_service_1_assisted_semantic_initial_v1(
        ingestion_output=ingestion,
        requested_capability=None,
        provider=provider,
        atomic_confirmation=True,
    )

    assert initial["status"] == SEM8_OWNER_REQUIRED
    assert initial["requested_capability"] is None
    assert len(provider_calls) == 1
    assert initial["interpreter_packet"]["proposal"].concept_proposals
    assert len(initial["owner_questions"]) == 1
    assert set(initial["owner_questions"][0]["column_refs"]) == {
        "Caja.SaldoInicial",
        "Caja.CobrosEsperados",
        "Caja.PagosEsperados",
    }
    assert all(
        initial[flag] is False
        for flag in (
            "runtime_authorized",
            "tool_execution_authorized",
            "product_ready",
            "delivery_authorized",
            "diagnosis_generated",
        )
    )


def test_web_upload_without_capability_starts_workbook_first_semantic_reception(tmp_path: Path) -> None:
    provider_calls: list[dict] = []

    def provider(payload: dict) -> dict:
        provider_calls.append(payload)
        return _proposal_from_assignments(
            payload,
            {
                "Ventas.Descuento": "discount",
                "Ventas.PrecioUnitario": "sale_price",
            },
        )

    app = Service1SemanticReceptionWebApplicationV1(
        output_dir=tmp_path,
        semantic_provider=provider,
    )
    status, page = app.receive_xlsx(
        session_id="workbook-first-web",
        filename="ventas_workbook_first.xlsx",
        content=_xlsx_bytes(
            {
                "Ventas": (
                    ["Descuento", "PrecioUnitario"],
                    [[0.1, 100]],
                )
            }
        ),
        selected_launch_review=None,
    )
    state = app.session("workbook-first-web")

    assert status == 200
    assert state.ingestion_output is not None
    assert len(provider_calls) == 1
    assert provider_calls[0]["requested_capability"] is None
    assert state.semantic_assistance_state["status"] == SEM8_OWNER_REQUIRED
    assert len(state.semantic_questions) == 1
    assert set(state.semantic_questions[0]["column_refs"]) == {
        "Ventas.Descuento",
        "Ventas.PrecioUnitario",
    }
    assert "Descuento" in page
    assert "PrecioUnitario" in page
    assert "¿Qué querés que PymIA te devuelva?" not in page


def test_web_workbook_first_owner_accept_reenters_and_opens_menu(tmp_path: Path) -> None:
    def provider(payload: dict) -> dict:
        return _proposal_from_assignments(
            payload,
            {
                "Ventas.Descuento": "discount",
                "Promos.Descuento": "discount",
            },
        )

    app = Service1SemanticReceptionWebApplicationV1(
        output_dir=tmp_path,
        semantic_provider=provider,
    )
    status, _page = app.receive_xlsx(
        session_id="workbook-first-owner-reentry",
        filename="discount_workbook_first.xlsx",
        content=_xlsx_bytes(
            {
                "Ventas": (["Descuento"], [[0.1]]),
                "Promos": (["Descuento"], [[5]]),
            }
        ),
        selected_launch_review=None,
    )
    state = app.session("workbook-first-owner-reentry")
    assert status == 200
    assert len(state.semantic_questions) == 1
    decision_id = state.semantic_questions[0]["decision_id"]
    assert set(state.semantic_questions[0]["column_refs"]) == {
        "Ventas.Descuento",
        "Promos.Descuento",
    }

    status, page = app.confirm_meanings(
        session_id="workbook-first-owner-reentry",
        fields={f"action_{decision_id}": "ACCEPT"},
    )

    assert status == 200
    assert state.semantic_dialogue_responses[decision_id] == {
        "decision_id": decision_id,
        "action": "ACCEPT",
    }
    assert len(state.semantic_dialogue_responses) == 1
    assert state.semantic_questions == []
    assert state.semantic_assistance_state["status"] == SEM8_CONFIRMED
    assert "¿Qué querés que PymIA te devuelva?" in page


def test_web_workbook_first_owner_confirmation_is_durable_before_analysis_menu(tmp_path: Path) -> None:
    recorded = []

    def persist(event, contract):
        recorded.append((event, contract))
        return True

    def provider(payload: dict) -> dict:
        return _proposal_from_assignments(
            payload,
            {
                "Ventas.Descuento": "discount",
                "Ventas.PrecioUnitario": "sale_price",
            },
        )

    app = Service1SemanticReceptionWebApplicationV1(
        output_dir=tmp_path,
        semantic_provider=provider,
        persist_tenant_confirmation=persist,
        require_tenant_persistence=True,
    )
    app.bind_tenant_identity(
        session_id="workbook-first-durable",
        tenant_id="tenant-f0",
        cliente_id="client-f0",
        owner_actor_id="owner-f0",
        owner_actor_role="OWNER",
    )
    status, _page = app.receive_xlsx(
        session_id="workbook-first-durable",
        filename="ventas_workbook_first_durable.xlsx",
        content=_xlsx_bytes(
            {
                "Ventas": (
                    ["Descuento", "PrecioUnitario"],
                    [[0.1, 100]],
                )
            }
        ),
        selected_launch_review=None,
    )
    state = app.session("workbook-first-durable")
    assert status == 200
    assert recorded == []
    decision_id = state.semantic_questions[0]["decision_id"]

    status, page = app.confirm_meanings(
        session_id="workbook-first-durable",
        fields={f"action_{decision_id}": "ACCEPT"},
    )

    assert status == 200
    assert state.semantic_assistance_state["status"] == SEM8_CONFIRMED
    assert "¿Qué querés que PymIA te devuelva?" in page
    assert recorded
    for event, contract in recorded:
        assert event.case_id == contract.case_id
        assert event.file_ref == "ventas_workbook_first_durable.xlsx"
        assert contract.tenant_id == "tenant-f0"
        assert contract.cliente_id == "client-f0"
        assert contract.owner_actor_id == "owner-f0"
        assert contract.owner_actor_role == "OWNER"
        assert contract.workbook_ref == "ventas_workbook_first_durable.xlsx"
        assert contract.confirmation_event_ref


def test_web_workbook_first_clear_semantics_require_one_grouped_owner_confirmation_before_menu(tmp_path: Path) -> None:
    provider_calls: list[dict] = []

    def provider(payload: dict) -> dict:
        provider_calls.append(payload)
        return _proposal_from_assignments(
            payload,
            {
                "Caja.SaldoInicial": "initial_balance",
                "Caja.CobrosEsperados": "expected_collections",
                "Caja.PagosEsperados": "expected_payments",
            },
        )

    app = Service1SemanticReceptionWebApplicationV1(
        output_dir=tmp_path,
        semantic_provider=provider,
    )
    status, page = app.receive_xlsx(
        session_id="workbook-first-zero-questions",
        filename="caja_workbook_first.xlsx",
        content=_xlsx_bytes(
            {
                "Caja": (
                    ["SaldoInicial", "CobrosEsperados", "PagosEsperados"],
                    [[1000, 400, 250]],
                )
            }
        ),
        selected_launch_review=None,
    )
    state = app.session("workbook-first-zero-questions")

    assert status == 200
    assert len(provider_calls) == 1
    assert state.semantic_assistance_state is not None
    assert state.semantic_assistance_state["status"] == SEM8_OWNER_REQUIRED
    assert len(state.semantic_questions) == 1
    assert set(state.semantic_questions[0]["column_refs"]) == {
        "Caja.SaldoInicial",
        "Caja.CobrosEsperados",
        "Caja.PagosEsperados",
    }
    assert "¿Qué querés que PymIA te devuelva?" not in page

    decision_id = state.semantic_questions[0]["decision_id"]
    status, page = app.confirm_meanings(
        session_id="workbook-first-zero-questions",
        fields={f"action_{decision_id}": "ACCEPT"},
    )
    assert status == 200
    assert state.semantic_questions == []
    assert state.semantic_assistance_state["status"] == SEM8_CONFIRMED
    assert state.semantic_assistance_state["semantic_run"]["status"] == "CONFIRMED_BINDINGS"
    discovery = build_service_1_post_semantic_analysis_discovery_v1(
        confirmed_bindings=state.semantic_assistance_state["semantic_run"]
    )
    assert discovery["status"] == "READY"
    assert [item["launch_ref"] for item in discovery["available"]] == ["working_capital"]
    assert {item["launch_ref"] for item in discovery["blocked"]} == {
        "sold_vs_collected_gap",
        "net_margin_real",
    }
    assert 'name="review_working_capital"' in page
    assert 'name="review_sold_vs_collected_gap"' not in page
    assert 'name="review_net_margin_real"' not in page
    assert "Análisis que necesitan más datos" in page
    assert "¿Qué querés que PymIA te devuelva?" in page

    confirmed_run = state.semantic_assistance_state["semantic_run"]
    original_events = list(
        (confirmed_run.get("owner_loop_packet") or {}).get("owner_confirmation_events") or []
    )
    status, result_page = app.run_review(
        session_id="workbook-first-zero-questions",
        requested_capability="working_capital",
    )
    assert status == 200
    assert len(provider_calls) == 1
    assert state.semantic_questions == []
    assert "Esto entendí de tu Excel" not in result_page
    service_packet = state.last_review_result
    assert service_packet["service_ref"] == "working_capital"
    assert "projected_closing_cash_balance" in service_packet["computed_components"]
    assert service_packet["component_packets"]
    for component in service_packet["component_packets"].values():
        semantic_run = component.get("semantic_run") or {}
        assert semantic_run.get("status") == "CONFIRMED_BINDINGS"
        assert list(semantic_run.get("owner_confirmation_events") or []) == original_events


def test_post_discovery_blocked_selection_does_not_reopen_semantics_or_execute(tmp_path: Path) -> None:
    provider_calls: list[dict] = []

    def provider(payload: dict) -> dict:
        provider_calls.append(payload)
        return _proposal_from_assignments(
            payload,
            {
                "Caja.SaldoInicial": "initial_balance",
                "Caja.CobrosEsperados": "expected_collections",
                "Caja.PagosEsperados": "expected_payments",
            },
        )

    app = Service1SemanticReceptionWebApplicationV1(
        output_dir=tmp_path,
        semantic_provider=provider,
    )
    status, _page = app.receive_xlsx(
        session_id="post-discovery-blocked",
        filename="caja_only.xlsx",
        content=_xlsx_bytes(
            {
                "Caja": (
                    ["SaldoInicial", "CobrosEsperados", "PagosEsperados"],
                    [[1000, 400, 250]],
                )
            }
        ),
        selected_launch_review=None,
    )
    state = app.session("post-discovery-blocked")
    assert status == 200
    decision_id = state.semantic_questions[0]["decision_id"]
    status, menu = app.confirm_meanings(
        session_id="post-discovery-blocked",
        fields={f"action_{decision_id}": "ACCEPT"},
    )
    assert status == 200
    assert len(provider_calls) == 1
    assert 'name="review_sold_vs_collected_gap"' not in menu

    confirmed_before = state.semantic_assistance_state["semantic_run"]
    status, blocked_page = app.run_review(
        session_id="post-discovery-blocked",
        requested_capability="sold_vs_collected_gap",
    )
    assert status == 200
    assert len(provider_calls) == 1
    assert state.semantic_assistance_state["semantic_run"] is confirmed_before
    assert state.semantic_questions == []
    assert 'name="review_sold_vs_collected_gap"' not in blocked_page
    assert "Falta información" in blocked_page


def test_real_cafeteria_upload_reaches_deterministic_semantic_provider_without_capability(tmp_path: Path) -> None:
    workbook_path = Path(__file__).resolve().parents[2] / "prueba_excels" / "cafeteria_abc.xlsx"
    assert workbook_path.is_file()
    provider_calls: list[dict] = []

    def deterministic_fallback(payload: dict) -> dict:
        provider_calls.append(payload)
        return build_service_1_deterministic_semantic_proposal_v1(payload)

    app = Service1SemanticReceptionWebApplicationV1(
        output_dir=tmp_path,
        semantic_provider=deterministic_fallback,
    )
    status, page = app.receive_xlsx(
        session_id="real-cafeteria-workbook-first",
        filename=workbook_path.name,
        content=workbook_path.read_bytes(),
        selected_launch_review=None,
    )
    state = app.session("real-cafeteria-workbook-first")

    assert status == 200
    assert state.ingestion_output is not None
    assert len(provider_calls) == 1
    assert provider_calls[0]["requested_capability"] is None
    assert provider_calls[0]["capability_relevant_roles"] == provider_calls[0]["allowed_semantic_roles"]
    proposal = state.semantic_assistance_state["interpreter_packet"]["proposal"]
    assert proposal.concept_proposals
    assert state.semantic_questions
    assert "¿Qué querés que PymIA te devuelva?" not in page

    steps = 0
    while state.semantic_questions:
        steps += 1
        assert steps <= 20
        decision_id = state.semantic_questions[0]["decision_id"]
        status, page = app.confirm_meanings(
            session_id="real-cafeteria-workbook-first",
            fields={f"action_{decision_id}": "ACCEPT"},
        )
        assert status == 200

    assert steps < len(proposal.concept_proposals)
    assert state.semantic_assistance_state["status"] == SEM8_CONFIRMED
    assert state.semantic_assistance_state["semantic_run"]["status"] == "CONFIRMED_BINDINGS"
    discovery = build_service_1_post_semantic_analysis_discovery_v1(
        confirmed_bindings=state.semantic_assistance_state["semantic_run"]
    )
    assert discovery["status"] == "READY"
    assert discovery["available"] == []
    assert {item["launch_ref"] for item in discovery["blocked"]} == {
        "sold_vs_collected_gap",
        "net_margin_real",
        "working_capital",
    }
    assert all(item["missing_evidence"] for item in discovery["blocked"])
    assert all(item["why_needed"] for item in discovery["blocked"])
    for item in discovery["available"]:
        assert f'name="review_{item["launch_ref"]}"' in page
    for item in discovery["blocked"]:
        assert f'name="review_{item["launch_ref"]}"' not in page
        assert item["name"] in page
    assert "¿Qué querés que PymIA te devuelva?" in page


def test_post_semantic_discovery_fails_closed_without_confirmed_bindings() -> None:
    discovery = build_service_1_post_semantic_analysis_discovery_v1(
        confirmed_bindings={}
    )
    assert discovery["status"] == "BLOCKED"
    assert discovery["blocked_reason"] == "CONFIRMED_BINDINGS_REQUIRED"
    assert discovery["available"] == []
    assert discovery["runtime_authorized"] is False
    assert discovery["tool_execution_authorized"] is False
    assert discovery["delivery_authorized"] is False


def test_sem8_explicit_assisted_route_without_provider_fails_closed(tmp_path: Path) -> None:
    ingestion = _ingestion(
        "caja.xlsx",
        _xlsx_bytes(
            {
                "Caja": (
                    ["SaldoInicial", "CobrosEsperados", "PagosEsperados"],
                    [[1000, 400, 250]],
                )
            }
        ),
    )

    packet = run_service_1_product_pipeline_v1(
        ingestion_output=ingestion,
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="projected_closing_cash_balance",
        use_assisted_semantics=True,
    )

    assert packet["status"] == STATUS_BLOCKED
    assert packet["blocked_reason"] == "BLOCK_SEM8_INTERPRETER_FAILED"
    state = packet["semantic_assistance_state"]
    assert state["interpreter_packet"]["blocked_reason"] == "BLOCK_LLM_PROVIDER_MISSING"
    assert packet["computation_executed"] is False


def test_sem8_invented_column_is_blocked_before_owner_and_execution(tmp_path: Path) -> None:
    ingestion = _ingestion(
        "caja.xlsx",
        _xlsx_bytes(
            {
                "Caja": (
                    ["SaldoInicial", "CobrosEsperados", "PagosEsperados"],
                    [[1000, 400, 250]],
                )
            }
        ),
    )

    def provider(_payload: dict) -> dict:
        return {
            "schema_version": "SERVICE_1_LLM_SEMANTIC_PROPOSAL_V1",
            "concept_proposals": [
                {
                    "proposal_id": "invented",
                    "target_column_refs": ["Caja.NoExiste"],
                    "semantic_role": "initial_balance",
                    "variable_name": "initial_balance",
                    "confidence": 0.99,
                    "rationale": "invalid on purpose",
                    "evidence_refs": [],
                }
            ],
            "relationship_proposals": [],
            "duplicate_semantics": [],
            "irrelevant_refs": [],
            "material_ambiguities": [],
        }

    packet = run_service_1_product_pipeline_v1(
        ingestion_output=ingestion,
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="projected_closing_cash_balance",
        semantic_provider=provider,
        use_assisted_semantics=True,
    )

    assert packet["status"] == STATUS_BLOCKED
    assert packet["blocked_reason"] == "BLOCK_SEM8_VALIDATOR_FAILED"
    state = packet["semantic_assistance_state"]
    assert state["validated_packet"]["blocked_reason"] == "BLOCKED_COLUMN_REF_NOT_FOUND"
    assert packet["semantic_bindings_confirmed"] is False
    assert packet["computation_executed"] is False


def test_sem8_composite_scope_reuses_one_owner_state_only_for_declared_component_capabilities(tmp_path: Path) -> None:
    ingestion = _ingestion(
        "capital_trabajo.xlsx",
        _xlsx_bytes(
            {
                "CapitalTrabajo": (
                    [
                        "saldo_inicial",
                        "cobros_esperados",
                        "pagos_esperados",
                        "cuentas_por_cobrar",
                        "ventas_periodo",
                        "dias_periodo",
                        "activo_corriente",
                        "pasivo_corriente",
                    ],
                    [[1000, 2500, 1800, 3000, 9000, 30, 15000, 10000]],
                )
            }
        ),
    )

    scope = (
        "projected_closing_cash_balance",
        "dso",
        "current_ratio",
    )
    initial = run_service_1_product_pipeline_v1(
        ingestion_output=ingestion,
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="working_capital",
        semantic_provider=build_service_1_deterministic_semantic_proposal_v1,
        semantic_scope_capabilities=scope,
        use_assisted_semantics=True,
    )
    assert initial["status"] == STATUS_NEEDS_OWNER
    state = initial["semantic_assistance_state"]
    assert tuple(state["semantic_scope_capabilities"]) == scope

    dso = run_service_1_product_pipeline_v1(
        ingestion_output=ingestion,
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="dso",
        semantic_assistance_state=state,
        semantic_dialogue_responses=_accept_all(initial),
        semantic_owner_actor_id="owner-1",
        semantic_owner_actor_role="OWNER",
        use_assisted_semantics=True,
    )
    assert dso["status"] == STATUS_COMPUTATION_PLAN_READY
    assert dso["computation_result"]["status"] == "EVALUATED"

    outside_scope = run_service_1_product_pipeline_v1(
        ingestion_output=ingestion,
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="net_margin_real",
        semantic_assistance_state=state,
        semantic_dialogue_responses=_accept_all(initial),
        semantic_owner_actor_id="owner-1",
        semantic_owner_actor_role="OWNER",
        use_assisted_semantics=True,
    )
    assert outside_scope["status"] == STATUS_BLOCKED
    assert outside_scope["blocked_reason"] == "ASSISTED_SEMANTIC_STATE_CONTEXT_MISMATCH"


def test_sem8_assisted_route_reuses_exact_state_and_executes_existing_deterministic_capability(tmp_path: Path) -> None:
    ingestion = _ingestion(
        "caja.xlsx",
        _xlsx_bytes(
            {
                "Caja": (
                    ["SaldoInicial", "CobrosEsperados", "PagosEsperados"],
                    [[1000, 400, 250]],
                )
            }
        ),
    )
    provider_calls = 0

    def provider(payload: dict) -> dict:
        nonlocal provider_calls
        provider_calls += 1
        assignments = {
            "Caja.SaldoInicial": "initial_balance",
            "Caja.CobrosEsperados": "expected_collections",
            "Caja.PagosEsperados": "expected_payments",
        }
        return _proposal_from_assignments(payload, assignments)

    initial = run_service_1_product_pipeline_v1(
        ingestion_output=ingestion,
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="projected_closing_cash_balance",
        semantic_provider=provider,
        use_assisted_semantics=True,
    )
    assert initial["status"] == STATUS_NEEDS_OWNER
    assert provider_calls == 1
    assert len(initial["owner_questions"]) == 1
    state = initial["semantic_assistance_state"]

    confirmed = run_service_1_product_pipeline_v1(
        ingestion_output=ingestion,
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="projected_closing_cash_balance",
        semantic_assistance_state=state,
        semantic_dialogue_responses=_accept_all(initial),
        semantic_owner_actor_id="owner-1",
        semantic_owner_actor_role="OWNER",
        use_assisted_semantics=True,
    )

    assert provider_calls == 1, "owner reentry must not recall the LLM"
    assert confirmed["status"] == STATUS_COMPUTATION_PLAN_READY
    assert confirmed["semantic_bindings_confirmed"] is True
    assert confirmed["computation_executed"] is True
    assert confirmed["computation_result"]["status"] == "EVALUATED"
    assert confirmed["computation_result"]["computed"]["projected_closing_balance"] == 1150.0
    semantic = confirmed["semantic_run"]
    assert len(semantic["owner_confirmation_events"]) == 3
    assert all(event["confirmed_by_owner"] is True for event in semantic["owner_confirmation_events"])
    assert confirmed["runtime_authorized"] is False
    assert confirmed["delivery_authorized"] is False


def test_sem8_cafeteria_reaches_confirmed_bindings_with_one_relationship_question_and_no_llm_recall(tmp_path: Path) -> None:
    ingestion = _ingestion(
        "cafeteria.xlsx",
        _xlsx_bytes(
            {
                "Ventas": (
                    [
                        "VentaID",
                        "Fecha",
                        "Hora",
                        "SucursalID",
                        "ProductoID",
                        "Cantidad",
                        "PrecioUnitario",
                        "MetodoPago",
                        "CanalVenta",
                        "Descuento",
                        "Empleado",
                    ],
                    [
                        ["V0001", "2026-01-01", "07:15:44", "S001", "P008", 1, 60, "Tarjeta", "Llevar", 0, "Carlos"],
                        ["V0002", "2026-01-01", "07:37:24", "S004", "P008", 2, 60, "Débito", "Llevar", 0.1, "Fernanda"],
                    ],
                ),
                "Sucursales": (
                    ["SucursalID", "Sucursal", "Ciudad"],
                    [["S001", "Centro", "Querétaro"], ["S004", "Roma Norte", "CDMX"]],
                ),
                "Productos": (
                    ["ProductoID", "Producto", "Categoria", "Costo", "Precio"],
                    [["P008", "Latte", "Café", 28, 60], ["P013", "Americano", "Café", 18, 45]],
                ),
            }
        ),
    )
    provider_calls = 0

    def provider(payload: dict) -> dict:
        nonlocal provider_calls
        provider_calls += 1
        assignments = {
            "Ventas.ProductoID": "product_id",
            "Productos.ProductoID": "product_id",
            "Ventas.Cantidad": "volume_sold",
            "Ventas.PrecioUnitario": "sale_price",
            "Ventas.Descuento": "discount",
            "Productos.Costo": "cost",
        }
        return _proposal_from_assignments(payload, assignments, include_relation=True)

    initial = run_service_1_product_pipeline_v1(
        ingestion_output=ingestion,
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="net_margin_real",
        semantic_provider=provider,
        use_assisted_semantics=True,
    )

    assert initial["status"] == STATUS_NEEDS_OWNER
    assert provider_calls == 1
    questions = initial["owner_questions"]
    relationship_questions = [item for item in questions if item["decision_kind"] == "RELATIONSHIP"]
    assert len(relationship_questions) == 1
    assert relationship_questions[0]["relationship_refs"] == [
        "Ventas.ProductoID->Productos.ProductoID"
    ]
    assert len(questions) == 2
    assert initial["semantic_assistance_state"]["dialogue_plan"]["zero_duplicate_questions"] is True
    assert initial["semantic_assistance_state"]["dialogue_plan"]["zero_irrelevant_questions"] is True

    confirmed = run_service_1_product_pipeline_v1(
        ingestion_output=ingestion,
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="net_margin_real",
        semantic_assistance_state=initial["semantic_assistance_state"],
        semantic_dialogue_responses=_accept_all(initial),
        semantic_owner_actor_id="owner-cafeteria",
        semantic_owner_actor_role="OWNER",
        use_assisted_semantics=True,
    )

    assert provider_calls == 1
    assert confirmed["semantic_bindings_confirmed"] is True
    semantic = confirmed["semantic_run"]
    assert len(semantic["owner_relationship_confirmation_events"]) == 1
    relation = semantic["owner_relationship_confirmation_events"][0]
    assert relation["left_column_ref"] == "ProductoID"
    assert relation["right_column_ref"] == "ProductoID"
    assert relation["confirmed_by_owner"] is True
    assert confirmed["runtime_authorized"] is False
    assert confirmed["tool_execution_authorized"] is False
    # The derived-evidence engine must not guess whether a non-zero discount is
    # a percentage or an amount. It surfaces one explicit owner unit question.
    assert confirmed["status"] == STATUS_NEEDS_OWNER
    assert confirmed["computation_executed"] is False
    assert confirmed["blocked_reason"] == "DISCOUNT_UNIT_CONFIRMATION_REQUIRED"
    assert confirmed["derived_evidence"]["status"] == "DERIVED_EVIDENCE_NEEDS_EVIDENCE"
    assert len(confirmed["owner_questions"]) == 1
    assert confirmed["owner_questions"][0]["question_kind"] == "UNIT_MEANING"
    assert confirmed["semantic_assistance_state"]["status"] == "CONFIRMED_BINDINGS"


def test_sem8_cafeteria_with_explicit_period_taxes_executes_ren001_through_derived_evidence_and_kernel(tmp_path: Path) -> None:
    ingestion = _ingestion(
        "cafeteria_with_taxes.xlsx",
        _xlsx_bytes(
            {
                "Ventas": (
                    ["VentaID", "ProductoID", "Cantidad", "PrecioUnitario"],
                    [
                        ["V0001", "P008", 1, 60],
                        ["V0002", "P008", 2, 60],
                    ],
                ),
                "Productos": (
                    ["ProductoID", "Costo"],
                    [["P008", 28], ["P013", 18]],
                ),
                "Resumen": (
                    ["impuestos_periodo"],
                    [[20]],
                ),
            }
        ),
    )
    provider_calls = 0

    def provider(payload: dict) -> dict:
        nonlocal provider_calls
        provider_calls += 1
        assignments = {
            "Ventas.ProductoID": "product_id",
            "Productos.ProductoID": "product_id",
            "Ventas.Cantidad": "volume_sold",
            "Ventas.PrecioUnitario": "sale_price",
            "Productos.Costo": "cost",
            "Resumen.impuestos_periodo": "taxes",
        }
        return _proposal_from_assignments(payload, assignments, include_relation=True)

    initial = run_service_1_product_pipeline_v1(
        ingestion_output=ingestion,
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="net_margin_real",
        semantic_provider=provider,
        use_assisted_semantics=True,
    )
    assert initial["status"] == STATUS_NEEDS_OWNER
    assert provider_calls == 1

    confirmed = run_service_1_product_pipeline_v1(
        ingestion_output=ingestion,
        tool_requests=[],
        output_dir=tmp_path,
        requested_capability="net_margin_real",
        semantic_assistance_state=initial["semantic_assistance_state"],
        semantic_dialogue_responses=_accept_all(initial),
        semantic_owner_actor_id="owner-cafeteria",
        semantic_owner_actor_role="OWNER",
        use_assisted_semantics=True,
    )

    assert provider_calls == 1
    assert confirmed["status"] == STATUS_COMPUTATION_PLAN_READY
    assert confirmed["semantic_bindings_confirmed"] is True
    assert confirmed["computation_executed"] is True
    assert confirmed["derived_evidence"]["status"] == "DERIVED_EVIDENCE_READY"
    assert confirmed["derived_evidence"]["derived_variables"]["sale_price"]["value"] == 180.0
    assert confirmed["derived_evidence"]["derived_variables"]["costs"]["value"] == 84.0

    bindings = confirmed["governed_computation_input"]["source_bindings"]
    assert bindings["sale_price"]["source_kind"] == "DERIVED_EVIDENCE"
    assert bindings["costs"]["source_kind"] == "DERIVED_EVIDENCE"
    assert bindings["taxes"] == "impuestos_periodo"

    result = confirmed["computation_result"]
    assert result["status"] == "EVALUATED"
    assert result["inputs"] == {"sale_price": 180.0, "costs": 84.0, "taxes": 20.0}
    assert result["computed"]["net_margin_amount"] == 76.0
    assert round(result["computed"]["net_margin_percentage"], 6) == round((76.0 / 180.0) * 100.0, 6)
    assert result["computed"]["total_outflows"] == 104.0
    assert confirmed["runtime_authorized"] is False
    assert confirmed["delivery_authorized"] is False


def test_sem8_atomic_dialogue_accepts_followup_state_across_multiple_owner_turns() -> None:
    ingestion = _ingestion(
        "caja_atomic.xlsx",
        _xlsx_bytes(
            {
                "Caja": (
                    ["SaldoInicial", "CobrosEsperados", "PagosEsperados"],
                    [[1000, 400, 250]],
                )
            }
        ),
    )

    def provider(payload: dict) -> dict:
        return _proposal_from_assignments(
            payload,
            {
                "Caja.SaldoInicial": "initial_balance",
                "Caja.CobrosEsperados": "expected_collections",
                "Caja.PagosEsperados": "expected_payments",
            },
        )

    initial = run_service_1_assisted_semantic_initial_v1(
        ingestion_output=ingestion,
        requested_capability="projected_closing_cash_balance",
        provider=provider,
        atomic_confirmation=True,
    )
    assert initial["status"] == SEM8_OWNER_REQUIRED
    assert len(initial["owner_questions"]) == 3

    q1, q2, q3 = initial["owner_questions"]
    r1 = {"decision_id": q1["decision_id"], "action": "ACCEPT"}
    r2 = {"decision_id": q2["decision_id"], "action": "ACCEPT"}
    r3 = {"decision_id": q3["decision_id"], "action": "ACCEPT"}

    follow1 = run_service_1_assisted_semantic_reentry_v1(
        previous_state=initial,
        owner_responses=[r1],
        owner_actor_id="owner-atomic",
        owner_actor_role="OWNER",
    )
    assert follow1["status"] == SEM8_FOLLOWUP
    assert len(follow1["owner_questions"]) == 2

    follow2 = run_service_1_assisted_semantic_reentry_v1(
        previous_state=follow1,
        owner_responses=[r1, r2],
        owner_actor_id="owner-atomic",
        owner_actor_role="OWNER",
    )
    assert follow2["status"] == SEM8_FOLLOWUP
    assert len(follow2["owner_questions"]) == 1

    confirmed = run_service_1_assisted_semantic_reentry_v1(
        previous_state=follow2,
        owner_responses=[r1, r2, r3],
        owner_actor_id="owner-atomic",
        owner_actor_role="OWNER",
    )
    assert confirmed["status"] == SEM8_CONFIRMED
    evidence = confirmed["owner_evidence_packet"]
    assert evidence["owner_confirmation_event_count"] == 3
    assert confirmed["runtime_authorized"] is False
    assert confirmed["delivery_authorized"] is False


def test_sem8_owner_correction_revision_stays_proposal_until_owner_accepts() -> None:
    ingestion = _ingestion(
        "caja_correction.xlsx",
        _xlsx_bytes(
            {
                "Caja": (
                    ["SaldoInicial", "CobrosEsperados", "PagosEsperados"],
                    [[1000, 400, 250]],
                )
            }
        ),
    )

    def provider(payload: dict) -> dict:
        return _proposal_from_assignments(
            payload,
            {
                "Caja.SaldoInicial": "initial_balance",
                "Caja.CobrosEsperados": "expected_collections",
                "Caja.PagosEsperados": "expected_payments",
            },
        )

    initial = run_service_1_assisted_semantic_initial_v1(
        ingestion_output=ingestion,
        requested_capability="projected_closing_cash_balance",
        provider=provider,
        atomic_confirmation=True,
    )
    current = initial["owner_questions"][0]
    proposal_ref = current["proposal_refs"][0]
    validated = next(
        item
        for item in initial["validated_packet"]["decisions"]
        if item["decision_id"] == proposal_ref
    )

    revised = revise_service_1_assisted_semantic_decision_v1(
        previous_state=initial,
        decision_id=current["decision_id"],
        semantic_role=validated["semantic_role"],
        variable_name=validated["variable_name"],
        owner_correction_text="Este dato es el saldo inicial con el que arrancamos el período.",
    )

    assert revised["status"] == SEM8_OWNER_REQUIRED
    assert len(revised["owner_questions"]) == 1
    assert revised["owner_evidence_packet"] is None
    assert revised["semantic_run"] is None
    assert revised["runtime_authorized"] is False
    assert revised["delivery_authorized"] is False


def test_web_correction_impuestos_periodo_revises_then_fails_closed_if_capability_semantics_no_longer_match(tmp_path: Path) -> None:
    """Regression for semantic-revise plus downstream fail-closed capability semantics."""
    ingestion = _ingestion(
        "impuestos_periodo_correction.xlsx",
        _xlsx_bytes(
            {
                "Resumen": (
                    ["ventas_periodo", "costos_periodo", "impuestos_periodo"],
                    [[180, 84, 20]],
                )
            }
        ),
    )

    def initial_provider(payload: dict) -> dict:
        return _proposal_from_assignments(
            payload,
            {
                "Resumen.ventas_periodo": "sale_price",
                "Resumen.costos_periodo": "costs",
                "Resumen.impuestos_periodo": "taxes",
            },
        )

    initial = run_service_1_assisted_semantic_initial_v1(
        ingestion_output=ingestion,
        requested_capability="net_margin_real",
        provider=initial_provider,
        atomic_confirmation=True,
    )
    assert initial["status"] == SEM8_OWNER_REQUIRED

    tax_question = next(
        item
        for item in initial["owner_questions"]
        if item.get("column_refs") == ["Resumen.impuestos_periodo"]
    )
    tax_decision_id = str(tax_question["decision_id"])

    class _AssistProvider:
        def __call__(self, _payload):
            raise AssertionError("semantic classification must not rerun during correction")

        def assist(self, payload):
            assert payload["interaction_mode"] == "CORRECTION"
            assert payload["column_refs"] == ["Resumen.impuestos_periodo"]
            allowed = {
                (item["semantic_role"], item["variable_name"])
                for item in payload["allowed_role_variable_pairs"]
            }
            assert allowed == {
                ("period_taxes_total", "taxes"),
                ("tax_amount", "taxes"),
                ("period_sales_total", "sale_price"),
            }
            return {
                "response_text": "Entiendo que es el impuesto de este registro, no el total del período.",
                "suggested_semantic_role": "tax_amount",
                "suggested_variable_name": "taxes",
                "suggestion_reason": "Owner described a row-level tax amount.",
            }

    app = Service1SemanticReceptionWebApplicationV1(
        output_dir=tmp_path,
        semantic_provider=_AssistProvider(),
    )
    state = app.session("tax-revise")
    state.ingestion_output = ingestion
    state.selected_launch_review = "net_margin_real"
    state.semantic_assistance_state = initial
    state.semantic_questions = [tax_question]
    state.semantic_dialogue_responses = {
        str(item["decision_id"]): {
            "decision_id": str(item["decision_id"]),
            "action": "ACCEPT",
        }
        for item in initial["owner_questions"]
        if str(item["decision_id"]) != tax_decision_id
    }
    actual_allowed = {
        (item["semantic_role"], item["variable_name"])
        for item in app._allowed_role_variable_pairs(
            initial,
            column_refs=["Resumen.impuestos_periodo"],
        )
    }
    assert actual_allowed == {
        ("period_taxes_total", "taxes"),
        ("tax_amount", "taxes"),
        ("period_sales_total", "sale_price"),
    }

    status, page = app.semantic_assist(
        session_id="tax-revise",
        fields={
            "decision_id": tax_decision_id,
            "assistant_message": "Esta columna representa el importe de impuestos de cada registro, no el total de impuestos del período.",
            "correction_mode": "1",
        },
    )
    assert status == 200
    assert state.semantic_chat_suggestions[tax_decision_id] == {
        "semantic_role": "tax_amount",
        "variable_name": "taxes",
        "reason": "Owner described a row-level tax amount.",
        "owner_text": "Esta columna representa el importe de impuestos de cada registro, no el total de impuestos del período.",
    }
    assert "Propuesta revisada" in page

    status, page = app.semantic_revise(
        session_id="tax-revise",
        fields={"decision_id": tax_decision_id},
    )
    assert status == 200
    assert state.semantic_assistance_state["status"] == SEM8_OWNER_REQUIRED
    assert state.semantic_assistance_state["owner_evidence_packet"] is None
    assert state.semantic_assistance_state["runtime_authorized"] is False
    assert state.semantic_questions[0]["decision_id"] == tax_decision_id
    assert tax_decision_id not in state.semantic_chat_suggestions
    assert "Confirmala" in page

    status, page = app.confirm_meanings(
        session_id="tax-revise",
        fields={f"action_{tax_decision_id}": "ACCEPT"},
    )
    assert status == 200
    assert state.last_review_result is not None
    assert state.last_review_result["status"] == STATUS_BLOCKED
    assert state.last_review_result["blocked_reason"] == "COMPONENT_SEMANTICS_REQUIRED"
    assert state.last_review_result["semantic_bindings_confirmed"] is True
    assert state.last_review_result["computation_executed"] is False
    assert state.last_review_result["runtime_authorized"] is False
    assert state.last_review_result["delivery_authorized"] is False


def test_sem8_owner_can_skip_one_atomic_column_without_fabricating_semantic_evidence() -> None:
    ingestion = _ingestion(
        "caja_skip.xlsx",
        _xlsx_bytes(
            {
                "Caja": (
                    ["SaldoInicial", "CobrosEsperados", "PagosEsperados"],
                    [[1000, 400, 250]],
                )
            }
        ),
    )

    def provider(payload: dict) -> dict:
        return _proposal_from_assignments(
            payload,
            {
                "Caja.SaldoInicial": "initial_balance",
                "Caja.CobrosEsperados": "expected_collections",
                "Caja.PagosEsperados": "expected_payments",
            },
        )

    initial = run_service_1_assisted_semantic_initial_v1(
        ingestion_output=ingestion,
        requested_capability="projected_closing_cash_balance",
        provider=provider,
        atomic_confirmation=True,
    )
    assert initial["status"] == SEM8_OWNER_REQUIRED

    responses = []
    skipped_ref = None
    for question in initial["owner_questions"]:
        refs = list(question.get("column_refs") or [])
        assert len(refs) == 1
        action = "SKIP" if refs[0].endswith("PagosEsperados") else "ACCEPT"
        if action == "SKIP":
            skipped_ref = refs[0]
        responses.append({"decision_id": question["decision_id"], "action": action})

    confirmed = run_service_1_assisted_semantic_reentry_v1(
        previous_state=initial,
        owner_responses=responses,
        owner_actor_id="owner-skip",
        owner_actor_role="OWNER",
    )

    assert skipped_ref is not None
    assert confirmed["status"] == SEM8_CONFIRMED
    evidence = confirmed["owner_evidence_packet"]
    assert evidence["owner_confirmation_event_count"] == 2
    assert evidence["owner_scope_exclusions"] == [skipped_ref]
    assert all(
        event.get("column_ref") != "PagosEsperados"
        for event in evidence["owner_confirmation_events"]
    )
    assert confirmed["runtime_authorized"] is False
    assert confirmed["delivery_authorized"] is False
