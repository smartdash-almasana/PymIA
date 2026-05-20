from __future__ import annotations

import sys
from pathlib import Path

from pymia.audit_result.builder import build_operational_audit_result
from pymia.contracts.evidence_v1 import StructuredEvidence
from pymia.narrative.extract_evidence import extract_evidence_pool
from pymia.narrative.grounding_validator import validate_grounding
from pymia.narrative.report_generator_v2 import build_narrative_report_v2

REPO_ROOT = Path(__file__).resolve().parents[2]
CONVERSA_DIR = REPO_ROOT / "conversa-engine"
if str(CONVERSA_DIR) not in sys.path:
    sys.path.insert(0, str(CONVERSA_DIR))

from operational_audit_router import route_operational_audit_message  # noqa: E402


def _audit_result_with_routes():
    evidence = StructuredEvidence(
        tenant_id="tenant-router",
        document_type="xlsx_operational_evidence",
        source="xlsx_upload",
        file_name="router_test.xlsx",
        computed_variables={"ventas_total": 1000.0, "costos_total": 600.0},
        metadata={
            "sheet_reports": {"ventas": "OK", "compras": "OK", "stock": "OK"},
            "signals": [
                {
                    "signal_id": "S1",
                    "signal_type": "caja_tensionada",
                    "severity": "ALTA",
                    "description": "Hay tensión de caja.",
                },
                {
                    "signal_id": "S2",
                    "signal_type": "margen_bajo",
                    "severity": "CRÍTICA",
                    "description": "Margen bajo.",
                },
                {
                    "signal_id": "S3",
                    "signal_type": "sobrestock",
                    "severity": "MEDIA",
                    "description": "Sobrestock.",
                },
            ],
        },
    )
    pool = extract_evidence_pool(evidence)
    report = build_narrative_report_v2(pool)
    grounding = validate_grounding(report, pool)
    return build_operational_audit_result(
        evidence=evidence,
        report=report,
        grounding=grounding,
        audit_id="audit-router",
    )


def test_route_caja_maps_to_liq() -> None:
    audit = _audit_result_with_routes()
    decision = route_operational_audit_message("quiero entender caja", audit)
    assert decision.pathology_code is not None
    assert decision.pathology_code.startswith("LIQ_")


def test_route_margen_maps_to_ren() -> None:
    audit = _audit_result_with_routes()
    decision = route_operational_audit_message("quiero mejorar margen", audit)
    assert decision.pathology_code is not None
    assert decision.pathology_code.startswith("REN_")


def test_route_stock_maps_to_inv() -> None:
    audit = _audit_result_with_routes()
    decision = route_operational_audit_message("quiero ordenar stock", audit)
    assert decision.pathology_code is not None
    assert decision.pathology_code.startswith("INV_")


def test_ambiguous_message_returns_options() -> None:
    audit = _audit_result_with_routes()
    decision = route_operational_audit_message("quiero profundizar", audit)
    assert decision.pathology_code is None
    assert decision.options


def test_no_raw_payload_fields_for_router() -> None:
    audit = _audit_result_with_routes()
    payload = audit.model_dump(mode="json", by_alias=True)
    forbidden = {"tables", "raw_tables", "normalized_tables", "kernel_output"}
    assert forbidden.isdisjoint(payload.keys())
