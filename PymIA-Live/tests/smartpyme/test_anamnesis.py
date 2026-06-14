from __future__ import annotations

import pytest

from pymia.smartpyme.anamnesis import (
    ANAMNESIS_STATUS_DRAFT,
    ANAMNESIS_STATUS_READY_FOR_EVIDENCE,
    BusinessTaxonomy,
    create_anamnesis_record,
)


def test_create_anamnesis_record_defaults_to_unknown_taxonomy() -> None:
    record = create_anamnesis_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        raw_owner_message="Vendemos mucho pero no se cuanto queda limpio.",
    )

    payload = record.to_dict()

    assert record.tenant_id == "tenant_demo"
    assert record.intake_id == "intake_demo"
    assert record.status == ANAMNESIS_STATUS_DRAFT
    assert record.raw_owner_message == "Vendemos mucho pero no se cuanto queda limpio."
    assert payload["business_taxonomy"]["empresa_tipo"] == "desconocido"
    assert payload["declared_pains"] == []
    assert payload["owner_hypotheses"] == []
    assert record.anamnesis_id.startswith("anamnesis_")


def test_create_anamnesis_record_accepts_taxonomy_and_lists() -> None:
    taxonomy = BusinessTaxonomy(
        empresa_tipo="comercio",
        industria="retail",
        modelo_comercial="b2c",
        canales_venta=["local", "whatsapp"],
        areas_criticas=["margen", "stock"],
        maneja_stock=True,
        produce_revende_o_servicio="revende",
    )

    record = create_anamnesis_record(
        tenant_id="tenant_retail",
        intake_id="intake_retail",
        raw_owner_message="Tengo stock parado y no se si gano por producto.",
        business_taxonomy=taxonomy,
        declared_pains=["stock parado", "incertidumbre de margen"],
        owner_hypotheses=["precios desactualizados"],
        declared_documents=["planilla de ventas"],
        requested_documents=["costos unitarios"],
        status=ANAMNESIS_STATUS_READY_FOR_EVIDENCE,
        metadata={"source": "assisted_intake"},
    )

    payload = record.to_dict()

    assert payload["business_taxonomy"]["empresa_tipo"] == "comercio"
    assert payload["business_taxonomy"]["maneja_stock"] is True
    assert payload["declared_pains"] == ["stock parado", "incertidumbre de margen"]
    assert payload["owner_hypotheses"] == ["precios desactualizados"]
    assert payload["declared_documents"] == ["planilla de ventas"]
    assert payload["requested_documents"] == ["costos unitarios"]
    assert payload["metadata"] == {"source": "assisted_intake"}


def test_create_anamnesis_record_rejects_missing_owner_message() -> None:
    with pytest.raises(ValueError, match="raw_owner_message"):
        create_anamnesis_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            raw_owner_message="",
        )


def test_create_anamnesis_record_rejects_unknown_taxonomy_fields() -> None:
    with pytest.raises(ValueError, match="unknown fields"):
        create_anamnesis_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            raw_owner_message="Necesito ordenar mi negocio.",
            business_taxonomy={"empresa_tipo": "servicios", "campo_invalido": "x"},
        )
