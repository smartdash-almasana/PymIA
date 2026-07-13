from __future__ import annotations

from pymia.smartpyme.service_1_pathology_anamnesis_triage_contract_v1 import (
    PATHOLOGY_LIQ_001,
    PATHOLOGY_REN_001,
    STATUS_EVIDENCE_REQUIRED,
    STATUS_OWNER_CONFIRMATION_REQUIRED,
    SCHEMA_VERSION,
    SERVICE_NAME,
    build_service_1_anamnesis_triage_decision_v1,
    create_service_1_anamnesis_record_v1,
    detect_service_1_pathology_candidates_v1,
)


def test_creates_anamnesis_with_owner_narrative() -> None:
    record = create_service_1_anamnesis_record_v1(
        case_id="case:s1:001",
        owner_ref="owner:pyme:001",
        tenant_ref="tenant:pyme:001",
        raw_owner_narrative="Vendo mucho pero no sé si gano porque no tengo claro el costo y el precio.",
        business_period_reference="2026-06",
        declared_data_sources=["ventas.xlsx"],
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
        available_data_fields=["precio", "costo", "cantidad"],
    )

    assert record.schema_version == SCHEMA_VERSION
    assert record.service_name == SERVICE_NAME
    assert record.raw_owner_narrative.startswith("Vendo mucho")
    assert record.runtime_authorized is False


def test_detects_ren_001_when_margin_cost_price_appear() -> None:
    record = create_service_1_anamnesis_record_v1(
        case_id="case:s1:002",
        owner_ref="owner:pyme:001",
        tenant_ref="tenant:pyme:001",
        raw_owner_narrative="No veo el margen real porque tengo precio, costo y no sé si gano.",
        business_period_reference="2026-06",
        declared_data_sources=["rentabilidad.xlsx"],
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
        available_data_fields=["precio", "costo", "cantidad_vendida"],
    )

    candidates = detect_service_1_pathology_candidates_v1(record, available_data_fields=["precio", "costo", "cantidad_vendida"])

    assert candidates
    assert candidates[0].pathology_code == PATHOLOGY_REN_001


def test_ventas_alone_does_not_activate_liq_001() -> None:
    record = create_service_1_anamnesis_record_v1(
        case_id="case:s1:liq:weak",
        owner_ref="owner:pyme:001",
        tenant_ref="tenant:pyme:001",
        raw_owner_narrative="Tengo ventas, pero todavía no ordené nada más.",
        business_period_reference="2026-06",
        declared_data_sources=["ventas.xlsx"],
        column_meaning_confirmations=["ventas=importe vendido"],
        available_data_fields=["ventas"],
    )

    candidates = detect_service_1_pathology_candidates_v1(record, available_data_fields=["ventas"])

    assert all(candidate.pathology_code != PATHOLOGY_LIQ_001 for candidate in candidates)


def test_costo_alone_does_not_activate_ren_001() -> None:
    record = create_service_1_anamnesis_record_v1(
        case_id="case:s1:ren:weak",
        owner_ref="owner:pyme:001",
        tenant_ref="tenant:pyme:001",
        raw_owner_narrative="Sólo tengo una referencia de costo.",
        business_period_reference="2026-06",
        declared_data_sources=["costos.xlsx"],
        column_meaning_confirmations=["costo=costo unitario"],
        available_data_fields=["costo"],
    )

    candidates = detect_service_1_pathology_candidates_v1(record, available_data_fields=["costo"])

    assert all(candidate.pathology_code != PATHOLOGY_REN_001 for candidate in candidates)


def test_detects_liq_001_when_sales_collections_cash_appear() -> None:
    record = create_service_1_anamnesis_record_v1(
        case_id="case:s1:003",
        owner_ref="owner:pyme:001",
        tenant_ref="tenant:pyme:001",
        raw_owner_narrative="Tengo ventas pero los cobros no entran en caja y no veo la plata.",
        business_period_reference="2026-06",
        declared_data_sources=["cobranzas.xlsx"],
        column_meaning_confirmations=["ventas=importe vendido", "cobros=importe cobrado"],
        available_data_fields=["ventas", "cobros", "saldo"],
    )

    candidates = detect_service_1_pathology_candidates_v1(record, available_data_fields=["ventas", "cobros", "saldo"])

    assert candidates
    assert candidates[0].pathology_code == PATHOLOGY_LIQ_001


def test_margin_or_gain_plus_cost_or_price_activates_ren_001() -> None:
    record = create_service_1_anamnesis_record_v1(
        case_id="case:s1:ren:strong",
        owner_ref="owner:pyme:001",
        tenant_ref="tenant:pyme:001",
        raw_owner_narrative="Quiero entender la ganancia porque tengo costo y precio pero no veo el margen real.",
        business_period_reference="2026-06",
        declared_data_sources=["rentabilidad.xlsx"],
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
        available_data_fields=["precio", "costo", "cantidad"],
    )

    candidates = detect_service_1_pathology_candidates_v1(record, available_data_fields=["precio", "costo", "cantidad"])

    assert candidates
    assert candidates[0].pathology_code == PATHOLOGY_REN_001


def test_returns_evidence_required_when_minimum_data_is_missing() -> None:
    record = create_service_1_anamnesis_record_v1(
        case_id="case:s1:004",
        owner_ref="owner:pyme:001",
        tenant_ref="tenant:pyme:001",
        raw_owner_narrative="No veo el margen porque tengo precio, costo y ganancia poco clara.",
        business_period_reference="2026-06",
        declared_data_sources=["rentabilidad.xlsx"],
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
        available_data_fields=["precio", "costo"],
    )

    decision = build_service_1_anamnesis_triage_decision_v1(record, available_data_fields=["precio", "costo"])

    assert decision.status == STATUS_EVIDENCE_REQUIRED
    assert decision.runtime_authorized is False
    assert decision.next_allowed_computation == ()


def test_returns_owner_confirmation_required_when_period_columns_or_context_are_missing() -> None:
    record = create_service_1_anamnesis_record_v1(
        case_id="case:s1:005",
        owner_ref="owner:pyme:001",
        tenant_ref="tenant:pyme:001",
        raw_owner_narrative="Tengo ventas y cobros pero la caja no me cierra.",
        business_period_reference=None,
        declared_data_sources=["ventas.xlsx"],
        column_meaning_confirmations=[],
        available_data_fields=["ventas", "cobros", "saldo"],
    )

    decision = build_service_1_anamnesis_triage_decision_v1(record, available_data_fields=["ventas", "cobros", "saldo"])

    assert record.status == STATUS_OWNER_CONFIRMATION_REQUIRED
    assert decision.status == STATUS_OWNER_CONFIRMATION_REQUIRED
    assert decision.owner_confirmation_required is True


def test_never_authorizes_runtime() -> None:
    record = create_service_1_anamnesis_record_v1(
        case_id="case:s1:006",
        owner_ref="owner:pyme:001",
        tenant_ref="tenant:pyme:001",
        raw_owner_narrative="Quiero entender margen con precio, costo y cantidad.",
        business_period_reference="2026-06",
        declared_data_sources=["ventas.xlsx"],
        column_meaning_confirmations=["precio=precio de venta", "costo=costo unitario"],
        available_data_fields=["precio", "costo", "cantidad"],
    )
    candidates = detect_service_1_pathology_candidates_v1(record, available_data_fields=["precio", "costo", "cantidad"])
    decision = build_service_1_anamnesis_triage_decision_v1(record, available_data_fields=["precio", "costo", "cantidad"])

    assert record.runtime_authorized is False
    assert all(candidate.runtime_authorized is False for candidate in candidates)
    assert decision.runtime_authorized is False


def test_primary_dicts_do_not_expose_human_review_fields() -> None:
    record = create_service_1_anamnesis_record_v1(
        case_id="case:s1:007",
        owner_ref="owner:pyme:001",
        tenant_ref="tenant:pyme:001",
        raw_owner_narrative="Tengo ventas y cobros pero la caja no me cierra.",
        business_period_reference="2026-06",
        declared_data_sources=["ventas.xlsx"],
        column_meaning_confirmations=["ventas=importe vendido", "cobros=importe cobrado"],
        available_data_fields=["ventas", "cobros", "saldo"],
        delivery_policy_constraints=["No prometer conciliación definitiva."],
    )
    candidate = detect_service_1_pathology_candidates_v1(record, available_data_fields=["ventas", "cobros", "saldo"])[0]
    decision = build_service_1_anamnesis_triage_decision_v1(record, available_data_fields=["ventas", "cobros", "saldo"])

    assert "human_review_required" not in record.to_dict()
    assert "human_review_gate" not in record.to_dict()
    assert "human_review_required" not in candidate.to_dict()
    assert "human_review_gate" not in candidate.to_dict()
    assert "human_review_required" not in decision.to_dict()
    assert "human_review_gate" not in decision.to_dict()
