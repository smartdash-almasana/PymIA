import importlib
import json
from pathlib import Path

from pymia.smartpyme.service_1_pathology_shadow_artifact_v1 import (
    build_service_1_pathology_shadow_artifact_v1,
)


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "pymia"
    / "smartpyme"
    / "service_1_pathology_shadow_artifact_v1.py"
)


FORBIDDEN_IMPORT_TOKENS = (
    "openai",
    "anthropic",
    "langchain",
    "langgraph",
    "requests",
    "httpx",
    "fastapi",
    "fasthtml",
    "storage",
    "vertical_pipeline",
    "pipeline_registration",
    "operator_delivery_package",
    "human_review",
    "release_gate",
    "bank_reconciliation",
    "mercado_pago",
    "invoice_collection",
    "accounting_workpaper",
)


def minimal_catalog_fixture(status="DRAFT_CANONICAL_CANDIDATE"):
    return {
        "catalogo_patologias_smartpyme_v0": {
            "version": "0.1",
            "estado": status,
            "dominios": {
                "rentabilidad": [
                    {
                        "id": "REN_001",
                        "nombre": "margen_invisible",
                        "descripcion": "El negocio factura pero no sabe qué productos, clientes o canales dejan ganancia real.",
                        "sintomas": ["vende mucho pero no gana"],
                        "senales_anamnesis": ["vendo pero no sé si gano"],
                        "datos_minimos": [
                            "precio_venta",
                            "costo_unitario",
                            "comisiones",
                        ],
                        "formulas_asociadas": [
                            "Margen bruto por producto",
                            "Margen neto",
                        ],
                    }
                ]
            },
        }
    }


def assert_no_effect_safety_line(payload):
    assert payload["runtime_decision"] == "NO_EFFECT"
    assert payload["diagnosis_authorized"] is False
    assert payload["routing_authorized"] is False
    assert payload["tool_selection_authorized"] is False
    assert payload["delivery_modification_authorized"] is False


def test_off_flag_skips_with_no_effect_payload():
    payload = build_service_1_pathology_shadow_artifact_v1(
        case_id="CASE-001",
        catalog_snapshot=minimal_catalog_fixture(),
        feature_flag_state="OFF",
        owner_pain_text="vendo pero no sé si gano",
    )

    assert payload["status"] == "SKIPPED"
    assert payload["blocked_reason"] == "FEATURE_FLAG_OFF"
    assert payload["candidate_count"] == 0
    assert payload["detected_candidates"] == []
    assert_no_effect_safety_line(payload)


def test_shadow_only_matching_owner_pain_generates_candidate():
    payload = build_service_1_pathology_shadow_artifact_v1(
        case_id="CASE-001",
        catalog_snapshot=minimal_catalog_fixture(),
        feature_flag_state="SHADOW_ONLY",
        owner_pain_text="vendo pero no sé si gano",
    )

    assert payload["status"] == "GENERATED"
    assert payload["blocked_reason"] is None
    assert payload["candidate_count"] == 1
    candidate = payload["detected_candidates"][0]
    assert candidate["pathology_id"] == "REN_001"
    assert candidate["name"] == "margen_invisible"
    assert candidate["domain"] == "rentabilidad"
    assert candidate["confidence"] == "candidate"
    assert "vendo pero no sé si gano" in candidate["matched_signals"]
    assert "precio_venta" in candidate["missing_evidence"]
    assert "costo_unitario" in candidate["missing_evidence"]
    assert "Margen bruto por producto" in candidate["suggested_formulas"]
    assert candidate["source_catalog_status"] == "DRAFT_CANONICAL_CANDIDATE"
    assert_no_effect_safety_line(payload)


def test_shadow_only_non_matching_owner_pain_returns_no_candidates():
    payload = build_service_1_pathology_shadow_artifact_v1(
        case_id="CASE-001",
        catalog_snapshot=minimal_catalog_fixture(),
        feature_flag_state="SHADOW_ONLY",
        owner_pain_text="quiero ordenar los nombres de clientes duplicados",
    )

    assert payload["status"] == "NO_CANDIDATES"
    assert payload["blocked_reason"] is None
    assert payload["candidate_count"] == 0
    assert payload["detected_candidates"] == []
    assert_no_effect_safety_line(payload)


def test_shadow_only_without_signals_blocks():
    payload = build_service_1_pathology_shadow_artifact_v1(
        case_id="CASE-001",
        catalog_snapshot=minimal_catalog_fixture(),
        feature_flag_state="SHADOW_ONLY",
        owner_pain_text=None,
        anamnesis_signals=[],
        case_metadata={},
        available_evidence_refs=[],
    )

    assert payload["status"] == "BLOCKED"
    assert payload["blocked_reason"] == "NO_SIGNALS_AVAILABLE"
    assert payload["candidate_count"] == 0
    assert_no_effect_safety_line(payload)


def test_uncontracted_promotion_states_are_blocked():
    for state in ("ADVISORY", "ROUTING_CANDIDATE", "ACTIVE"):
        payload = build_service_1_pathology_shadow_artifact_v1(
            case_id="CASE-001",
            catalog_snapshot=minimal_catalog_fixture(),
            feature_flag_state=state,
            owner_pain_text="vendo pero no sé si gano",
        )

        assert payload["status"] == "BLOCKED"
        assert payload["blocked_reason"] == "FEATURE_FLAG_STATE_UNCONTRACTED"
        assert payload["candidate_count"] == 0
        assert_no_effect_safety_line(payload)


def test_missing_catalog_blocks():
    payload = build_service_1_pathology_shadow_artifact_v1(
        case_id="CASE-001",
        catalog_snapshot={},
        feature_flag_state="SHADOW_ONLY",
        owner_pain_text="vendo pero no sé si gano",
    )

    assert payload["status"] == "BLOCKED"
    assert payload["blocked_reason"] == "CATALOG_MISSING"
    assert payload["candidate_count"] == 0
    assert_no_effect_safety_line(payload)


def test_unsupported_catalog_status_blocks():
    payload = build_service_1_pathology_shadow_artifact_v1(
        case_id="CASE-001",
        catalog_snapshot=minimal_catalog_fixture(status="ACTIVE"),
        feature_flag_state="SHADOW_ONLY",
        owner_pain_text="vendo pero no sé si gano",
    )

    assert payload["status"] == "BLOCKED"
    assert payload["blocked_reason"] == "CATALOG_STATUS_UNSUPPORTED"
    assert payload["candidate_count"] == 0
    assert_no_effect_safety_line(payload)


def test_missing_case_id_blocks():
    payload = build_service_1_pathology_shadow_artifact_v1(
        case_id="",
        catalog_snapshot=minimal_catalog_fixture(),
        feature_flag_state="SHADOW_ONLY",
        owner_pain_text="vendo pero no sé si gano",
    )

    assert payload["status"] == "BLOCKED"
    assert payload["blocked_reason"] == "CASE_ID_MISSING"
    assert payload["candidate_count"] == 0
    assert_no_effect_safety_line(payload)


def test_draft_catalog_candidate_never_authorizes_diagnosis_or_routing():
    payload = build_service_1_pathology_shadow_artifact_v1(
        case_id="CASE-001",
        catalog_snapshot=minimal_catalog_fixture(),
        feature_flag_state="SHADOW_ONLY",
        owner_pain_text="vendo pero no sé si gano",
    )

    assert payload["status"] == "GENERATED"
    assert_no_effect_safety_line(payload)
    assert payload["detected_candidates"][0]["confidence"] == "candidate"


def test_missing_evidence_and_formulas_are_catalog_passthrough_only():
    payload = build_service_1_pathology_shadow_artifact_v1(
        case_id="CASE-001",
        catalog_snapshot=minimal_catalog_fixture(),
        feature_flag_state="SHADOW_ONLY",
        owner_pain_text="vendo pero no sé si gano",
    )

    candidate = payload["detected_candidates"][0]
    assert candidate["missing_evidence"] == [
        "precio_venta",
        "costo_unitario",
        "comisiones",
    ]
    assert candidate["suggested_formulas"] == [
        "Margen bruto por producto",
        "Margen neto",
    ]
    assert candidate["suggested_skills"] == []
    assert payload["missing_evidence_global"] == [
        "precio_venta",
        "costo_unitario",
        "comisiones",
    ]


def test_output_is_json_serializable():
    payload = build_service_1_pathology_shadow_artifact_v1(
        case_id="CASE-001",
        catalog_snapshot=minimal_catalog_fixture(),
        feature_flag_state="SHADOW_ONLY",
        owner_pain_text="vendo pero no sé si gano",
        metadata={"operator_ref": "OP-001"},
    )

    json.dumps(payload, sort_keys=True)


def test_module_does_not_import_forbidden_runtime_dependencies():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in FORBIDDEN_IMPORT_TOKENS:
        assert forbidden not in source


def test_module_imports_cleanly():
    module = importlib.import_module(
        "pymia.smartpyme.service_1_pathology_shadow_artifact_v1"
    )
    assert hasattr(module, "build_service_1_pathology_shadow_artifact_v1")
