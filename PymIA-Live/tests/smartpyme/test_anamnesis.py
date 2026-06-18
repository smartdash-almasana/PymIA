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
    assert payload["business_taxonomy"]["industria"] == "desconocido"
    assert payload["business_taxonomy"]["modelo_comercial"] == "desconocido"
    assert payload["business_taxonomy"]["canales_venta"] == []
    assert payload["business_taxonomy"]["maneja_stock"] is None
    assert payload["business_taxonomy"]["produce"] is None
    assert payload["business_taxonomy"]["presta_servicios"] is None
    assert payload["business_taxonomy"]["dolores_declarados"] == []
    assert payload["business_taxonomy"]["documentos_disponibles"] == []
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
        produce=False,
        presta_servicios=False,
        dolores_declarados=["stock parado", "incertidumbre de margen"],
        documentos_disponibles=["planilla de ventas"],
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
    assert payload["business_taxonomy"]["produce"] is False
    assert payload["business_taxonomy"]["presta_servicios"] is False
    assert payload["business_taxonomy"]["dolores_declarados"] == ["stock parado", "incertidumbre de margen"]
    assert payload["business_taxonomy"]["documentos_disponibles"] == ["planilla de ventas"]
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


def test_anamnesis_record_persists_taxonomic_intake_minimum() -> None:
    record = create_anamnesis_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        raw_owner_message="No se si gano con este canal.",
        business_taxonomy={
            "empresa_tipo": "comercio",
            "industria": "retail",
            "modelo_comercial": "b2c",
            "canales_venta": ["local", "whatsapp"],
            "maneja_stock": True,
            "produce": False,
            "presta_servicios": False,
            "areas_criticas": ["margen"],
            "dolores_declarados": ["no se si gano"],
            "documentos_disponibles": ["ventas.xlsx"],
        },
    )

    payload = record.to_dict()

    assert payload["business_taxonomy"] == {
        "empresa_tipo": "comercio",
        "industria": "retail",
        "modelo_comercial": "b2c",
        "canales_venta": ["local", "whatsapp"],
        "areas_criticas": ["margen"],
        "maneja_stock": True,
        "produce": False,
        "presta_servicios": False,
        "dolores_declarados": ["no se si gano"],
        "documentos_disponibles": ["ventas.xlsx"],
        "produce_revende_o_servicio": None,
    }


def test_anamnesis_defaults_unknown_and_none_without_crash() -> None:
    record = create_anamnesis_record(
        tenant_id="tenant_demo",
        intake_id="intake_demo",
        raw_owner_message="Necesito ordenar el negocio.",
        business_taxonomy={"empresa_tipo": "servicios"},
    )

    payload = record.to_dict()["business_taxonomy"]

    assert payload["empresa_tipo"] == "servicios"
    assert payload["industria"] == "desconocido"
    assert payload["modelo_comercial"] == "desconocido"
    assert payload["canales_venta"] == []
    assert payload["areas_criticas"] == []
    assert payload["maneja_stock"] is None
    assert payload["produce"] is None
    assert payload["presta_servicios"] is None
    assert payload["dolores_declarados"] == []
    assert payload["documentos_disponibles"] == []
