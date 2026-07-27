from __future__ import annotations

import ast
from pathlib import Path

from pymia.smartpyme.delivery_package import DeliveryPackage, STATUS_BLOCKED, STATUS_READY_TO_DELIVER


def _operational_audit_result(**overrides) -> dict:
    payload = {
        "result_id": "audit-1",
        "tenant_id": "tenant-1",
        "status": "ok",
        "findings": [
            {
                "finding_id": "finding-1",
                "status": "CANDIDATE",
                "summary": "Inventory rotation below threshold.",
            }
        ],
        "evidence_used": ["sheet://ventas", "sheet://costos"],
        "missing_evidence": [],
        "forbidden_inferences": [
            "No inventar evidencia ni variables faltantes.",
            "No agregar findings fuera de DiagnosticCoreResult.",
        ],
        "allowed_rendering": {
            "summary": "Resultado del core materializado para entrega operacional controlada.",
            "next_questions": [],
            "next_steps": ["Revisar referencias antes de cualquier accion."],
            "blocked_message": "",
            "references": ["sheet://ventas", "sheet://costos"],
        },
    }
    payload.update(overrides)
    return payload


def _render_contract(**overrides) -> dict:
    payload = {
        "render_id": "render-1",
        "result_ref": "audit-1",
        "tenant_id": "tenant-1",
        "summary": "Resultado del core materializado para entrega operacional controlada.",
        "next_questions": [],
        "next_steps": ["Revisar referencias antes de cualquier accion."],
        "blocked_message": "",
        "forbidden_inferences": [
            "No inventar evidencia ni variables faltantes.",
            "No agregar findings fuera de DiagnosticCoreResult.",
        ],
        "references": ["sheet://ventas", "sheet://costos"],
    }
    payload.update(overrides)
    return payload


def _delivery_package(**overrides) -> DeliveryPackage:
    payload = DeliveryPackage(
        tenant_id="tenant-1",
        intake_id="intake-1",
        runtime_classification="diagnostic_core_v1",
        output_refs=["C:/tmp/delivery_summary.md", "C:/tmp/render_contract.json"],
        summary="Execution validated and ready to deliver.",
        warnings=["gate warning"],
        reasons=[],
        gate_verdict="PASS",
        status=STATUS_READY_TO_DELIVER,
        created_at="2026-06-09T00:00:00+00:00",
    )
    for key, value in overrides.items():
        setattr(payload, key, value)
    return payload


def test_build_owner_facing_report_for_delivered_result_without_inventing_findings():
    from pymia.smartpyme.owner_facing_report import build_owner_facing_report

    report = build_owner_facing_report(
        operational_audit_result=_operational_audit_result(),
        render_contract=_render_contract(),
        delivery_package=_delivery_package(),
    )

    assert report.status == "DELIVERED"
    assert report.summary == "Resultado del core materializado para entrega operacional controlada."
    assert report.evidence_used == ["sheet://ventas", "sheet://costos"]
    assert report.missing_evidence == []
    assert report.next_questions == []
    assert report.output_refs == ["C:/tmp/delivery_summary.md", "C:/tmp/render_contract.json"]
    assert report.references == ["sheet://ventas", "sheet://costos"]
    assert "findings" not in report.to_dict()


def test_build_owner_facing_report_for_blocked_result_shows_missing_evidence_and_next_questions():
    from pymia.smartpyme.owner_facing_report import build_owner_facing_report

    report = build_owner_facing_report(
        operational_audit_result=_operational_audit_result(
            status="pending_data",
            missing_evidence=["dias_periodo", "taxes"],
        ),
        render_contract=_render_contract(
            summary="PymIA no puede completar este resultado sin evidencia adicional.",
            next_questions=["dias_periodo", "taxes"],
            next_steps=[],
            blocked_message="Falta evidencia para avanzar al resultado operativo entregable.",
        ),
        delivery_package=_delivery_package(
            gate_verdict="BLOCKED",
            status=STATUS_BLOCKED,
            summary="Execution blocked by gate verdict.",
            reasons=["missing evidence"],
        ),
    )

    assert report.status == "BLOCKED"
    assert report.blocked_message == "Falta evidencia para avanzar al resultado operativo entregable."
    assert report.missing_evidence == ["dias_periodo", "taxes"]
    assert report.next_questions == ["dias_periodo", "taxes"]
    assert report.next_steps == []
    assert report.limit_warnings[-1] == "Estado bloqueado o incompleto: falta evidencia para avanzar."


def test_build_owner_facing_report_does_not_elevate_candidate_to_confirmed():
    from pymia.smartpyme.owner_facing_report import build_owner_facing_report

    report = build_owner_facing_report(
        operational_audit_result=_operational_audit_result(status="candidate"),
        render_contract=_render_contract(),
        delivery_package=_delivery_package(),
    )

    assert report.status == "DELIVERED_CANDIDATE"
    assert "confirm" not in report.summary.lower()
    assert report.limit_warnings[-1] == "Estado candidato: el resultado sigue siendo no confirmado."


def test_build_owner_facing_report_is_deterministic():
    from pymia.smartpyme.owner_facing_report import build_owner_facing_report

    report_a = build_owner_facing_report(
        operational_audit_result=_operational_audit_result(status="candidate"),
        render_contract=_render_contract(),
        delivery_package=_delivery_package(),
    )
    report_b = build_owner_facing_report(
        operational_audit_result=_operational_audit_result(status="candidate"),
        render_contract=_render_contract(),
        delivery_package=_delivery_package(),
    )

    assert report_a.to_dict() == report_b.to_dict()


def test_module_does_not_import_forbidden_boundaries_ast():
    source = Path("pymia/smartpyme/owner_facing_report.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    forbidden_prefixes = (
        "pymia.telegram",
        "pymia.audit_result.core_delivery_bridge",
        "pymia.orchestration.graph",
        "tools.document_ingestion",
    )

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith(forbidden_prefixes)
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert not module.startswith(forbidden_prefixes)
