from pathlib import Path

from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_unconfirmed_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_workbook_profiler_v1 import build_service_1_workbook_profile_v1
from pymia.smartpyme.service_1_workbook_semantic_context_v1 import (
    build_service_1_workbook_semantic_context_v1,
)
from pymia.smartpyme.service_1_assisted_semantic_product_wiring_v1 import (
    run_service_1_assisted_semantic_initial_v1,
)
from pymia.smartpyme.service_1_deterministic_semantic_proposal_provider_v1 import (
    build_service_1_deterministic_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_semantic_knowledge_context_v1 import (
    AUTHORITY_CONTEXT_ONLY,
    BUSINESS_CATALOG_SOURCE,
    STATUS_READY,
    load_service_1_business_semantic_knowledge_v1,
    retrieve_service_1_semantic_knowledge_v1,
)


def _workbook_context(fixture_name: str):
    root = Path(__file__).resolve().parents[2]
    fixture = root / "prueba_excels" / fixture_name
    intake = build_service_1_web_column_confirmation_intake_boundary_v1(
        uploaded_xlsx_bytes=fixture.read_bytes(),
        uploaded_filename=fixture.name,
        include_all_sheets=True,
    )
    canonical = build_service_1_unconfirmed_canonical_ingestion_output_v1(
        owner_question_packet=intake,
    )
    profile = build_service_1_workbook_profile_v1(
        ingestion_output=canonical["ingestion_output"],
    )
    return build_service_1_workbook_semantic_context_v1(workbook_profile=profile)


def test_catalog_is_explicit_context_only_and_provenanced() -> None:
    catalog = load_service_1_business_semantic_knowledge_v1()
    assert catalog["status"] == STATUS_READY, catalog
    assert len(catalog["knowledge_items"]) > 50
    assert catalog["source_registry"] == [
        {
            "source_ref": BUSINESS_CATALOG_SOURCE,
            "classification": "LEXICAL_REFERENCE_ONLY",
            "authority": AUTHORITY_CONTEXT_ONLY,
        }
    ]
    assert all(item["authority"] == AUTHORITY_CONTEXT_ONLY for item in catalog["knowledge_items"])
    assert all(item["source_ref"] == BUSINESS_CATALOG_SOURCE for item in catalog["knowledge_items"])
    assert catalog["runtime_authorized"] is False
    assert catalog["delivery_authorized"] is False


def test_real_taller_retrieves_bounded_business_knowledge_without_deciding_semantics() -> None:
    workbook = _workbook_context("taller_mecanico_lubricar_srl.xlsx")
    result = retrieve_service_1_semantic_knowledge_v1(workbook_semantic_context=workbook)

    assert result["status"] == STATUS_READY, result
    assert result["authority"] == AUTHORITY_CONTEXT_ONLY
    assert result["retrieval_scoped"] is True
    assert 0 < result["retrieved_item_count"] < result["catalog_item_count"]
    assert result["runtime_authorized"] is False

    labels = {item["label"] for item in result["retrieved_knowledge"]}
    assert "orden_de_trabajo" in labels
    assert "mano_de_obra" in labels
    assert "costo" in labels
    assert "stock_actual" in labels or "stock" in labels
    assert "medio_de_pago" in labels
    assert "tarifa_horaria" in labels or "precio" in labels
    assert all(item["authority"] == AUTHORITY_CONTEXT_ONLY for item in result["retrieved_knowledge"])
    assert result["retrieval_evidence"]


def test_non_taller_workbook_retrieves_different_context_without_vertical_switch() -> None:
    taller = retrieve_service_1_semantic_knowledge_v1(
        workbook_semantic_context=_workbook_context("taller_mecanico_lubricar_srl.xlsx")
    )
    cafeteria = retrieve_service_1_semantic_knowledge_v1(
        workbook_semantic_context=_workbook_context("cafeteria_abc.xlsx")
    )

    assert cafeteria["status"] == STATUS_READY, cafeteria
    taller_ids = {item["knowledge_id"] for item in taller["retrieved_knowledge"]}
    cafeteria_ids = {item["knowledge_id"] for item in cafeteria["retrieved_knowledge"]}
    assert taller_ids != cafeteria_ids
    cafeteria_labels = {item["label"] for item in cafeteria["retrieved_knowledge"]}
    assert {"producto", "cantidad", "precio", "costo"}.intersection(cafeteria_labels)
    assert cafeteria["authority"] == AUTHORITY_CONTEXT_ONLY


def test_productive_provider_payload_includes_scoped_semantic_knowledge() -> None:
    root = Path(__file__).resolve().parents[2]
    fixture = root / "prueba_excels" / "taller_mecanico_lubricar_srl.xlsx"
    intake = build_service_1_web_column_confirmation_intake_boundary_v1(
        uploaded_xlsx_bytes=fixture.read_bytes(),
        uploaded_filename=fixture.name,
        include_all_sheets=True,
    )
    canonical = build_service_1_unconfirmed_canonical_ingestion_output_v1(
        owner_question_packet=intake,
    )
    captured = {}

    def provider(payload):
        captured.update(payload)
        return build_service_1_deterministic_semantic_proposal_v1(payload)

    result = run_service_1_assisted_semantic_initial_v1(
        ingestion_output=canonical["ingestion_output"],
        requested_capability=None,
        provider=provider,
    )

    assert result.get("status") != "BLOCKED", result
    knowledge = captured.get("semantic_knowledge_context")
    assert isinstance(knowledge, dict)
    assert knowledge.get("status") == STATUS_READY
    assert knowledge.get("authority") == AUTHORITY_CONTEXT_ONLY
    assert knowledge.get("retrieval_scoped") is True
    assert knowledge.get("retrieved_knowledge")
