from __future__ import annotations

from pymia.smartpyme.service_1_xlsx_first_product_entrypoint_v1 import (
    STATUS_NEXT_OWNER_QUESTION,
    build_service_1_xlsx_first_product_entrypoint_v1,
)


def test_case_001_documents_current_semantic_evidence_binding_gap() -> None:
    """Characterization test: this freezes the current defect, not the desired product behavior.

    CASE_001 has observed XLSX columns and owner declarations that should eventually feed a
    Semantic Evidence Binding layer. Today, those signals remain flat strings, so the
    XLSX-first entrypoint stops at triage and repeats the segmentation question.
    """
    result = build_service_1_xlsx_first_product_entrypoint_v1(
        case_id="case:s1:case-001:semantic-binding-gap",
        tenant_id="tenant:synthetic-owner-001",
        intake_id="intake:case-001",
        run_id="run:case-001-semantic-binding-gap",
        owner_ref="owner:synthetic-pyme-001",
        raw_owner_narrative=(
            "Vendo bastante, pero no me queda claro si estoy ganando.\n"
            "Tengo una planilla de ventas de junio 2026.\n"
            "Quiero saber si hay algo raro."
        ),
        business_period_reference="2026-06",
        declared_data_sources=["CASE_001_ventas_junio_2026_margin_leak.xlsx"],
        available_data_fields=[
            "fecha",
            "comprobante",
            "producto_codigo",
            "producto",
            "categoria",
            "cantidad",
            "precio_unitario",
            "costo_unitario",
            "canal",
            "venta_total",
        ],
        input_values={
            "fecha": "2026-06-01",
            "comprobante": "A-0001",
            "producto_codigo": "SKU-001",
            "producto": "Producto A",
            "categoria": "Categoria A",
            "cantidad": 10,
            "precio_unitario": 100,
            "costo_unitario": 60,
            "canal": "local",
            "venta_total": 1000,
        },
        column_meaning_confirmations=[
            "fecha=fecha de venta",
            "comprobante=identificador de comprobante",
            "producto_codigo=código de producto",
            "producto=producto vendido",
            "categoria=categoría comercial",
            "cantidad=cantidad vendida",
            "precio_unitario=precio unitario de venta",
            "costo_unitario=costo unitario del producto",
            "canal=canal de venta",
            "venta_total=importe total de venta",
            "owner_answer_001=La columna producto identifica el producto vendido.",
            "owner_answer_001=La columna categoria agrupa el tipo de producto.",
            "owner_answer_001=La columna canal indica por dónde se vendió: local, web, mayorista o marketplace.",
        ],
        metadata={
            "characterization": "SERVICE_1_SEMANTIC_EVIDENCE_BINDING_GAP_V1",
            "ground_truth_used": False,
        },
    )

    assert result.status == STATUS_NEXT_OWNER_QUESTION
    assert result.selected_primary_pathology == "SAL_001"
    assert result.allowed_computation_ref is None
    assert result.delivery_package_candidate is None
    assert result.next_owner_question == "¿Qué columnas separan producto, canal o categoría?"

    # The current chain stops at triage. No semantic binding, allowed-computation,
    # evidence-readiness, computation-plan, dry-run, owner-view, policy, or package
    # step is reached from this CASE_001-shaped payload.
    assert result.trace == {"triage_entrypoint_status": "BUILT"}
    assert "allowed_computation_candidate_status" not in result.trace
    assert "evidence_readiness_gate_status" not in result.trace
    assert "dry_run_status" not in result.trace

    assert result.runtime_authorized is False
    assert result.reexecution_authorized is False
    assert result.recalculation_authorized is False
    assert result.delivery_authorized is False
