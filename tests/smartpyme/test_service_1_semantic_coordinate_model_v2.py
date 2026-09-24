from __future__ import annotations

import json
from pathlib import Path

import pytest

from pymia.smartpyme.service_1_semantic_coordinate_model_v2 import (
    AXES,
    Service1BusinessStructureProfileV2,
    Service1SemanticCoordinateV2,
    infer_service_1_semantic_coordinate_v2,
    load_service_1_semantic_coordinate_taxonomy_v2,
    render_service_1_semantic_coordinate_owner_proposal_v2,
)


ROOT = Path(__file__).resolve().parents[2]
TAXONOMY_PATH = ROOT / "docs" / "current" / "SERVICE_1_C2_SEMANTIC_COORDINATE_TAXONOMY_V2.json"


def _c(field_ref: str, **kwargs: object) -> Service1SemanticCoordinateV2:
    return Service1SemanticCoordinateV2(field_ref=field_ref, confidence=0.9, **kwargs).validate_against(
        load_service_1_semantic_coordinate_taxonomy_v2()
    )


def test_taxonomy_is_multidimensional_and_structural_not_vertical_specific() -> None:
    taxonomy = load_service_1_semantic_coordinate_taxonomy_v2()
    assert tuple(taxonomy.axes) == AXES
    assert "gastronomy" in taxonomy.business_families
    assert "services" in taxonomy.business_families
    assert "technical_service" in taxonomy.operating_archetypes
    raw = TAXONOMY_PATH.read_text(encoding="utf-8").casefold()
    for forbidden in ("taller_mecanico", "lubricentro", "cafeteria", "constructora", "mayorista"):
        assert forbidden not in raw


def test_same_measure_can_exist_many_times_with_different_context() -> None:
    labor_margin = _c(
        "ORDENES_TRABAJO.margen_mano_obra",
        measure="margin",
        object="labor",
        process="service_delivery",
        state="actual",
        grain="work_order",
        scope="event",
        unit="currency",
        aggregation="sum",
    )
    parts_margin = _c(
        "ORDENES_TRABAJO.margen_repuestos",
        measure="margin",
        object="part",
        process="sale",
        state="actual",
        grain="work_order",
        scope="event",
        unit="currency",
        aggregation="sum",
    )
    assert labor_margin.measure == parts_margin.measure == "margin"
    assert labor_margin.object != parts_margin.object
    assert labor_margin.process != parts_margin.process


def test_same_cost_and_identifier_families_do_not_collapse() -> None:
    labor_cost = _c(
        "ORDENES_TRABAJO.costo_mano_obra",
        measure="cost",
        object="labor",
        process="service_delivery",
        grain="work_order",
        scope="event",
        unit="currency",
        aggregation="sum",
    )
    part_cost = _c(
        "PRODUCTOS_STOCK.costo_unitario",
        measure="cost",
        object="part",
        process="inventory_management",
        grain="product",
        scope="unit",
        unit="currency",
        aggregation="average",
    )
    order_id = _c(
        "ORDENES_TRABAJO.orden_id",
        entity="work_order",
        grain="work_order",
        identity="identifier",
    )
    customer_id = _c(
        "CLIENTES.cliente_id",
        entity="customer",
        grain="customer",
        identity="identifier",
    )
    assert labor_cost.measure == part_cost.measure == "cost"
    assert labor_cost.object != part_cost.object
    assert order_id.identity == customer_id.identity == "identifier"
    assert order_id.entity != customer_id.entity


def test_four_business_structures_use_the_same_taxonomy() -> None:
    taxonomy = load_service_1_semantic_coordinate_taxonomy_v2()

    cafeteria = Service1BusinessStructureProfileV2(
        family="gastronomy",
        archetypes=("direct_sale", "production_by_recipe", "sale_with_inventory"),
        processes=("sale", "production", "inventory_management"),
        objects=("ingredient", "finished_product", "labor", "inventory"),
    ).validate_against(taxonomy)

    technical_service = Service1BusinessStructureProfileV2(
        family="services",
        archetypes=("technical_service", "service_by_order", "service_with_materials"),
        processes=("service_delivery", "sale", "inventory_management", "collection"),
        objects=("labor", "part", "service", "inventory"),
    ).validate_against(taxonomy)

    construction = Service1BusinessStructureProfileV2(
        family="construction",
        archetypes=("project_based", "service_with_materials"),
        processes=("project_execution", "billing", "collection", "budgeting"),
        objects=("material", "labor", "equipment", "subcontract"),
    ).validate_against(taxonomy)

    wholesale = Service1BusinessStructureProfileV2(
        family="commerce",
        archetypes=("sale_with_inventory",),
        processes=("purchase", "sale", "inventory_management", "collection"),
        objects=("product", "inventory", "money"),
    ).validate_against(taxonomy)

    assert {cafeteria.family, technical_service.family, construction.family, wholesale.family} == {
        "gastronomy",
        "services",
        "construction",
        "commerce",
    }


def test_representative_coordinates_across_structures_without_new_roles() -> None:
    cases = (
        _c(
            "VENTAS.margen_producto",
            measure="margin",
            object="finished_product",
            process="sale",
            grain="line_item",
            scope="line",
            unit="currency",
            aggregation="sum",
        ),
        _c(
            "ORDENES_TRABAJO.margen_mano_obra",
            measure="margin",
            object="labor",
            process="service_delivery",
            grain="work_order",
            scope="event",
            unit="currency",
            aggregation="sum",
        ),
        _c(
            "OBRAS.costo_material_real",
            measure="cost",
            object="material",
            process="project_execution",
            state="actual",
            grain="project",
            scope="entity",
            unit="currency",
            aggregation="sum",
        ),
        _c(
            "PRODUCTOS.costo_reposicion",
            measure="cost",
            object="product",
            process="purchase",
            state="expected",
            grain="product",
            scope="unit",
            unit="currency",
            aggregation="average",
        ),
    )
    assert [item.measure for item in cases] == ["margin", "margin", "cost", "cost"]


def test_generic_compound_business_headers_preserve_identity_object_and_measure() -> None:
    order_id = infer_service_1_semantic_coordinate_v2(
        "orden_id",
        sheet_name="ORDENES_TRABAJO",
    )
    assert order_id is not None
    assert order_id.identity == "identifier"
    assert order_id.entity == "work_order"
    assert order_id.grain == "work_order"

    labor_cost = infer_service_1_semantic_coordinate_v2(
        "costo_mano_obra",
        sheet_name="ORDENES_TRABAJO",
    )
    assert labor_cost is not None
    assert labor_cost.measure == "cost"
    assert labor_cost.object == "labor"

    hourly_price = infer_service_1_semantic_coordinate_v2(
        "valor_hora",
        sheet_name="ORDENES_TRABAJO",
    )
    assert hourly_price is not None
    assert hourly_price.measure == "price"
    assert hourly_price.measure != "duration"

    labor_hours = infer_service_1_semantic_coordinate_v2(
        "horas_mano_obra",
        sheet_name="ORDENES_TRABAJO",
    )
    assert labor_hours is not None
    assert labor_hours.measure == "duration"
    assert labor_hours.object == "labor"

    order_text = render_service_1_semantic_coordinate_owner_proposal_v2("orden_id", order_id)
    labor_cost_text = render_service_1_semantic_coordinate_owner_proposal_v2("costo_mano_obra", labor_cost)
    assert "identificador de orden de trabajo" in order_text.casefold()
    assert "costo de mano de obra" in labor_cost_text.casefold()


def test_fail_closed_on_unknown_axis_values_and_invalid_identity_composition() -> None:
    taxonomy = load_service_1_semantic_coordinate_taxonomy_v2()
    with pytest.raises(ValueError, match="outside the governed taxonomy"):
        Service1SemanticCoordinateV2(
            field_ref="X.valor",
            measure="invented_vertical_margin",
        ).validate_against(taxonomy)

    with pytest.raises(ValueError, match="identity semantics require an entity"):
        Service1SemanticCoordinateV2(
            field_ref="X.id",
            identity="identifier",
        ).validate_against(taxonomy)

    with pytest.raises(ValueError, match="cannot simultaneously be a measure"):
        Service1SemanticCoordinateV2(
            field_ref="X.id",
            identity="identifier",
            entity="customer",
            measure="quantity",
        ).validate_against(taxonomy)


def test_taxonomy_is_data_driven_and_json_roundtrippable() -> None:
    payload = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))
    assert set(payload["axes"]) == set(AXES)
    assert all(payload["axes"][axis] for axis in AXES)
