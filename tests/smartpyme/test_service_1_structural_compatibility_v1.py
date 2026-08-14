from __future__ import annotations

from copy import deepcopy

from pymia.smartpyme.service_1_owner_confirmation_event_v1 import (
    build_service_1_owner_confirmation_event_v1,
)
from pymia.smartpyme.service_1_structural_compatibility_v1 import (
    STATUS_COMPATIBLE_HINT,
    STATUS_LEGACY_UNVERIFIED_HINT,
    STATUS_OBSOLETE_HINT,
    build_service_1_structural_signature_v1,
    classify_service_1_structural_compatibility_v1,
    select_service_1_compatible_tenant_memory_hints_v1,
)
from pymia.smartpyme.service_1_tenant_semantic_contract_v1 import (
    build_service_1_tenant_semantic_contract_v1,
    service_1_tenant_semantic_contract_from_mapping_v1,
)
from pymia.smartpyme.service_1_tenant_semantic_contract_store_v1 import (
    append_service_1_tenant_semantic_contract_v1,
    list_service_1_tenant_semantic_contracts_v1,
)
from pymia.smartpyme.service_1_workbook_profiler_v1 import SCHEMA_VERSION as PROFILE_SCHEMA


def _profile() -> dict:
    return {
        "schema_version": PROFILE_SCHEMA,
        "service_name": "SERVICE_1",
        "status": "WORKBOOK_PROFILE_READY",
        "blocked_reason": None,
        "case_id": "case-sem7",
        "source_file_ref": "cafeteria.xlsx",
        "sheet_names": ["Ventas", "Productos"],
        "column_count": 3,
        "relationship_count": 1,
        "columns": [
            {
                "column_ref": "Ventas.ProductoID",
                "sheet_name": "Ventas",
                "column_name": "ProductoID",
                "normalized_header": "productoid",
                "inferred_type": "text",
                "row_count": 100,
                "non_null_count": 100,
                "null_count": 0,
                "null_ratio": 0.0,
                "cardinality": 20,
                "unique_ratio": 0.2,
                "uniqueness_class": "NON_UNIQUE",
                "candidate_primary_key": False,
            },
            {
                "column_ref": "Productos.ProductoID",
                "sheet_name": "Productos",
                "column_name": "ProductoID",
                "normalized_header": "productoid",
                "inferred_type": "text",
                "row_count": 20,
                "non_null_count": 20,
                "null_count": 0,
                "null_ratio": 0.0,
                "cardinality": 20,
                "unique_ratio": 1.0,
                "uniqueness_class": "UNIQUE",
                "candidate_primary_key": True,
            },
            {
                "column_ref": "Ventas.Cantidad",
                "sheet_name": "Ventas",
                "column_name": "Cantidad",
                "normalized_header": "cantidad",
                "inferred_type": "number",
                "row_count": 100,
                "non_null_count": 100,
                "null_count": 0,
                "null_ratio": 0.0,
                "cardinality": 8,
                "unique_ratio": 0.08,
                "uniqueness_class": "NON_UNIQUE",
                "candidate_primary_key": False,
            },
        ],
        "relationships": [
            {
                "relationship_ref": "Ventas.ProductoID->Productos.ProductoID",
                "left_column_ref": "Ventas.ProductoID",
                "right_column_ref": "Productos.ProductoID",
                "relationship_kind": "MANY_TO_ONE",
                "same_normalized_header": True,
                "left_value_coverage": 1.0,
                "right_value_coverage": 1.0,
                "candidate_foreign_key": True,
                "candidate_primary_key_ref": "Productos.ProductoID",
                "intersection_cardinality": 20,
            }
        ],
        "evidence_registry": {},
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _signature(profile: dict | None = None, column_ref: str = "Ventas.ProductoID"):
    return build_service_1_structural_signature_v1(
        workbook_profile=profile or _profile(),
        column_ref=column_ref,
        source_system_ref="xlsx_upload",
        source_context_ref="ventas_productos_v1",
    )


def _tenant_contract_with_signature():
    signature = _signature().to_dict()
    event = build_service_1_owner_confirmation_event_v1(
        case_id="case-sem7",
        file_ref="cafeteria.xlsx",
        region_ref=None,
        sheet_ref="Ventas",
        column_ref="ProductoID",
        question_ref="dialogue:product-id",
        owner_answer="ACCEPT",
        proposed_role="product_id",
        proposed_variable="product_id",
        confirmed_role="product_id",
        confirmation_scope="SEMANTIC_ROLE",
        timestamp="2026-08-14T14:00:00+00:00",
        provenance={"producer": "sem7-test"},
    )
    return build_service_1_tenant_semantic_contract_v1(
        tenant_id="tenant-a",
        cliente_id=None,
        owner_actor_id="owner-a",
        owner_actor_role="PYME_OWNER",
        source_system_ref="xlsx_upload",
        source_context_ref="ventas_productos_v1",
        workbook_ref="cafeteria.xlsx",
        expected_case_id="case-sem7",
        expected_sheet_ref="Ventas",
        expected_question_ref="dialogue:product-id",
        source_column_name="ProductoID",
        normalized_column_ref="productoid",
        owner_confirmation_event=event,
        inferred_data_type="text",
        structural_signature=signature,
    )


def test_sem7_volume_changes_do_not_invalidate_stable_signature() -> None:
    historical = _signature()
    current_profile = deepcopy(_profile())
    sales = current_profile["columns"][0]
    sales.update(
        {
            "row_count": 1000,
            "non_null_count": 1000,
            "cardinality": 200,
            "unique_ratio": 0.2,
        }
    )
    current_profile["relationships"][0]["intersection_cardinality"] = 200
    current = _signature(current_profile)

    result = classify_service_1_structural_compatibility_v1(
        historical_signature=historical,
        current_signature=current,
    )

    assert result["status"] == STATUS_COMPATIBLE_HINT
    assert result["changed_fields"] == []
    assert result["automatic_reuse_authorized"] is False
    assert result["semantic_rebind_authorized"] is False


def test_sem7_uniqueness_or_key_role_change_marks_memory_obsolete() -> None:
    historical = _signature()
    current_profile = deepcopy(_profile())
    current_profile["columns"][0]["uniqueness_class"] = "UNIQUE"
    current_profile["columns"][0]["candidate_primary_key"] = True
    current = _signature(current_profile)

    result = classify_service_1_structural_compatibility_v1(
        historical_signature=historical,
        current_signature=current,
    )

    assert result["status"] == STATUS_OBSOLETE_HINT
    assert {"uniqueness_class", "key_role"}.intersection(result["changed_fields"])


def test_sem7_relationship_shape_change_marks_memory_obsolete() -> None:
    historical = _signature()
    current_profile = deepcopy(_profile())
    current_profile["relationships"] = []
    current_profile["relationship_count"] = 0
    current = _signature(current_profile)

    result = classify_service_1_structural_compatibility_v1(
        historical_signature=historical,
        current_signature=current,
    )

    assert result["status"] == STATUS_OBSOLETE_HINT
    assert "relationship_shape" in result["changed_fields"]
    assert "key_role" in result["changed_fields"]


def test_sem7_missing_historical_signature_is_legacy_unverified_only() -> None:
    result = classify_service_1_structural_compatibility_v1(
        historical_signature=None,
        current_signature=_signature(),
    )
    assert result["status"] == STATUS_LEGACY_UNVERIFIED_HINT
    assert result["automatic_reuse_authorized"] is False


def test_sem7_selector_separates_compatible_obsolete_and_legacy_memory() -> None:
    profile = _profile()
    sales_signature = _signature(profile).to_dict()
    product_signature = _signature(profile, "Productos.ProductoID").to_dict()
    stale_product = dict(product_signature)
    stale_product["uniqueness_class"] = "NON_UNIQUE"
    # Rebuild a valid stale signature from a structurally changed profile.
    stale_profile = deepcopy(profile)
    stale_profile["columns"][1]["uniqueness_class"] = "NON_UNIQUE"
    stale_profile["columns"][1]["candidate_primary_key"] = False
    stale_profile["relationships"] = []
    stale_profile["relationship_count"] = 0
    stale_product = _signature(stale_profile, "Productos.ProductoID").to_dict()

    rows = [
        {
            "tenant_id": "tenant-a",
            "source_system_ref": "xlsx_upload",
            "source_context_ref": "ventas_productos_v1",
            "sheet_ref": "Ventas",
            "source_column_name": "ProductoID",
            "contract_id": "c1",
            "mapping_series_id": "m1",
            "revision": 2,
            "confirmed_role": "product_id",
            "confirmed_variable": "product_id",
            "structural_signature": sales_signature,
        },
        {
            "tenant_id": "tenant-a",
            "source_system_ref": "xlsx_upload",
            "source_context_ref": "ventas_productos_v1",
            "sheet_ref": "Productos",
            "source_column_name": "ProductoID",
            "contract_id": "c2",
            "mapping_series_id": "m2",
            "revision": 1,
            "confirmed_role": "product_id",
            "confirmed_variable": "product_id",
            "structural_signature": stale_product,
        },
        {
            "tenant_id": "tenant-a",
            "source_system_ref": "xlsx_upload",
            "source_context_ref": "ventas_productos_v1",
            "sheet_ref": "Ventas",
            "source_column_name": "Cantidad",
            "contract_id": "legacy",
            "mapping_series_id": "m3",
            "revision": 1,
            "confirmed_role": "quantity",
            "confirmed_variable": "volume_sold",
        },
    ]

    result = select_service_1_compatible_tenant_memory_hints_v1(
        tenant_id="tenant-a",
        source_system_ref="xlsx_upload",
        source_context_ref="ventas_productos_v1",
        workbook_profile=profile,
        memory_rows=rows,
    )

    assert result["compatible_hint_count"] == 1
    assert result["obsolete_hint_count"] == 1
    assert result["legacy_unverified_hint_count"] == 1
    assert result["compatible_hints"][0]["column_ref"] == "Ventas.ProductoID"
    assert result["obsolete_hints"][0]["column_ref"] == "Productos.ProductoID"
    assert result["legacy_unverified_hints"][0]["column_ref"] == "Ventas.Cantidad"
    assert result["automatic_reuse_authorized"] is False


def test_sem7_tenant_contract_roundtrips_signature_and_legacy_payload_still_loads() -> None:
    signature = _signature().to_dict()
    event = build_service_1_owner_confirmation_event_v1(
        case_id="case-sem7",
        file_ref="cafeteria.xlsx",
        region_ref=None,
        sheet_ref="Ventas",
        column_ref="ProductoID",
        question_ref="dialogue:product-id",
        owner_answer="ACCEPT",
        proposed_role="product_id",
        proposed_variable="product_id",
        confirmed_role="product_id",
        confirmation_scope="SEMANTIC_ROLE",
        timestamp="2026-08-14T14:00:00+00:00",
        provenance={"producer": "sem7-test"},
    )
    contract = build_service_1_tenant_semantic_contract_v1(
        tenant_id="tenant-a",
        cliente_id=None,
        owner_actor_id="owner-a",
        owner_actor_role="PYME_OWNER",
        source_system_ref="xlsx_upload",
        source_context_ref="ventas_productos_v1",
        workbook_ref="cafeteria.xlsx",
        expected_case_id="case-sem7",
        expected_sheet_ref="Ventas",
        expected_question_ref="dialogue:product-id",
        source_column_name="ProductoID",
        normalized_column_ref="productoid",
        owner_confirmation_event=event,
        inferred_data_type="text",
        structural_signature=signature,
    )

    payload = contract.to_dict()
    restored = service_1_tenant_semantic_contract_from_mapping_v1(payload)
    assert restored.structural_signature is not None
    assert restored.structural_signature["signature_id"] == signature["signature_id"]
    assert restored.automatic_reuse_authorized is False

    legacy_payload = dict(payload)
    legacy_payload.pop("structural_signature")
    legacy = service_1_tenant_semantic_contract_from_mapping_v1(legacy_payload)
    assert legacy.structural_signature is None
    assert legacy.automatic_reuse_authorized is False


def test_sem7_store_roundtrip_preserves_structural_signature(tmp_path) -> None:
    contract = _tenant_contract_with_signature()
    result = append_service_1_tenant_semantic_contract_v1(
        base_dir=tmp_path,
        tenant_id="tenant-a",
        contract=contract,
    )
    assert result.status == "TENANT_SEMANTIC_CONTRACT_RECORDED"

    loaded = list_service_1_tenant_semantic_contracts_v1(
        base_dir=tmp_path,
        tenant_id="tenant-a",
    )
    assert len(loaded) == 1
    assert loaded[0].structural_signature is not None
    assert (
        loaded[0].structural_signature["signature_id"]
        == contract.structural_signature["signature_id"]
    )
    assert loaded[0].automatic_reuse_authorized is False
    assert loaded[0].semantic_rebind_authorized is False
