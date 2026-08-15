from __future__ import annotations

from io import BytesIO
from pathlib import Path

from openpyxl import Workbook

from pymia.smartpyme.service_1_deterministic_semantic_proposal_provider_v1 import (
    build_service_1_deterministic_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_unconfirmed_canonical_ingestion_output_v1,
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
