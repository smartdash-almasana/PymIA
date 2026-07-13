from __future__ import annotations

from pymia.smartpyme.owner_facing_report import build_owner_facing_report


def _base_payload(*, operational_status: str) -> dict:
    return {
        "operational_audit_result": {
            "tenant_id": "tenant_demo",
            "status": operational_status,
            "evidence_used": ["excel_file_readable"],
            "missing_evidence": [],
        },
        "render_contract": {
            "tenant_id": "tenant_demo",
            "summary": "Resumen trazable",
            "blocked_message": "",
            "next_questions": ["Pregunta siguiente"],
            "next_steps": ["Paso siguiente"],
            "references": ["stdout"],
            "forbidden_inferences": ["No inferir diagnóstico"],
        },
        "delivery_package": {
            "tenant_id": "tenant_demo",
            "intake_id": "intake_demo",
            "status": "DELIVERED",
            "summary": "Resumen delivery",
            "output_refs": ["stdout"],
            "warnings": ["Slice local; no es canal productivo."],
        },
    }


def test_owner_facing_report_uses_declarative_candidate_warning():
    payload = _base_payload(operational_status="candidate")
    report = build_owner_facing_report(**payload)
    assert "Estado candidato: el resultado sigue siendo no confirmado." in report.limit_warnings


def test_owner_facing_report_uses_declarative_blocked_warning():
    payload = _base_payload(operational_status="blocked")
    payload["delivery_package"]["status"] = "BLOCKED"
    report = build_owner_facing_report(**payload)
    assert "Estado bloqueado o incompleto: falta evidencia para avanzar." in report.limit_warnings


def test_owner_facing_report_uses_declarative_pending_data_warning():
    payload = _base_payload(operational_status="pending_data")
    report = build_owner_facing_report(**payload)
    assert "Estado bloqueado o incompleto: falta evidencia para avanzar." in report.limit_warnings
