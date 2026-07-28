"""
SCN offline chain integration test.

Validates the full offline contractual chain:
    EvidenceCandidate -> KernelRequest -> OperationalAuditResult -> RenderContract

This test is purely static/offline. It does NOT execute Hermes, PymIA kernel,
Boundary Layer runtime, Output Gateway, or any real runtime. It asserts
continuity of references, tenant consistency, guardrail preservation, and
sovereign boundary enforcement across all stages using plain dict fixtures.

Related:
- docs/hermes/HERMES_LOCAL_SCN_OFFLINE_CHAIN_AUDIT_RESULT.md
- evidence sandbox: .tmp/hermes-scn-local/evidence/scn_offline_chain_001.audit.md
"""


def _evidence_candidate():
    return {
        "schema_version": "draft-local-sandbox",
        "evidence_id": "evidence_candidate_001",
        "tenant_id": "tenant_sandbox_demo",
        "conversation_id": "sandbox_conversation_na_draft",
        "source_type": "synthetic",
        "source_origin": "offline_static_transform",
        "collected_by": "system",
        "collected_at": "2026-05-25T00:00:00Z",
        "raw_content_hash": "sha256:sandbox_draft_placeholder_hash_not_computed",
        "payload": {
            "source_case_id": "scn_synthetic_001",
            "source": "synthetic_sandbox",
            "runtime": "none",
            "hermes_executed": False,
            "channel": "sandbox",
            "input_message": "No me cierra la caja y quiero saber qué evidencia necesitás.",
            "attachments": [],
            "claims": [],
            "requested_evidence": [
                {
                    "id": "req_cash_001",
                    "kind": "cash_reconciliation_evidence",
                    "reason": "El usuario declara un descuadre de caja, pero no aporta datos verificables.",
                    "required": True,
                }
            ],
            "forbidden_inferences": [
                "No diagnosticar causa del descuadre.",
                "No afirmar faltante, robo, error contable ni problema operativo sin evidencia.",
                "No crear findings.",
                "No inferir montos, responsables ni periodo.",
            ],
            "expected_behavior": {
                "hermes_may_create_findings": False,
                "must_request_evidence": True,
                "must_not_diagnose": True,
                "must_fail_closed_if_invalid": True,
            },
            "sovereign_boundary": {
                "pymia_computes": True,
                "hermes_renders_only": True,
                "hermes_may_create_findings": False,
            },
            "status": "draft_not_runtime_validated",
        },
        "provenance": {
            "source_case_id": "scn_synthetic_001",
            "transform": "offline_static",
            "sandbox": "hermes-scn-local",
            "derived_from": "synthetic_input_001.json",
            "draft_source": "evidence_candidate_001.draft.json",
            "hermes_executed": False,
        },
        "confidence": 0,
        "hermes_notes": {
            "role": "context_only",
            "diagnostic_authority": False,
            "runtime": "none",
            "notes": "Offline canonical EvidenceCandidate generated from synthetic sandbox draft. Hermes was not executed.",
        },
    }


def _kernel_request(evidence_candidate):
    return {
        "request_id": "kernel_request_001",
        "schema_version": "scn.kernel_request.v1",
        "tenant_id": evidence_candidate["tenant_id"],
        "evidence_refs": [evidence_candidate["evidence_id"]],
        "requested_by": "boundary_layer",
        "conversation_context_ref": evidence_candidate["conversation_id"],
        "intent": "evaluate_cash_reconciliation_evidence",
        "hermes_executed": False,
    }


def _operational_audit_result(evidence_candidate):
    forbidden = evidence_candidate["payload"]["forbidden_inferences"]
    return {
        "schema_version": "scn.operational_audit_result.v1",
        "result_id": "operational_audit_result_001",
        "tenant_id": evidence_candidate["tenant_id"],
        "status": "pending_data",
        "findings": [],
        "evidence_used": [evidence_candidate["evidence_id"]],
        "missing_evidence": [
            "Cierre de caja del periodo en cuestión.",
            "Detalle de ventas por canal (POS / e-commerce).",
            "Conciliación bancaria del periodo.",
            "Reporte de diferencias del sistema contable.",
            "Justificación documental de ajustes manuales.",
        ],
        "forbidden_inferences": list(forbidden),
        "allowed_rendering": {
            "must_not_diagnose": True,
            "must_not_create_findings": True,
        },
        "audit_trail_ref": "audit-trail-offline-001",
        "sovereign_mark": {
            "issuer": "pymia-sandbox",
            "mark_type": "offline_chain_draft",
            "mark_value": "scn_synthetic_001_draft",
        },
        "created_at": "2026-05-25T00:00:00Z",
    }


def _render_contract(kernel_request, operational_audit_result):
    forbidden = operational_audit_result["forbidden_inferences"]
    return {
        "schema_version": "scn.render_contract.v1",
        "render_id": "render_contract_001",
        "result_ref": operational_audit_result["result_id"],
        "tenant_id": operational_audit_result["tenant_id"],
        "summary": (
            "No hay evidencia suficiente para diagnosticar el descuadre de caja. "
            "Se requiere documentación adicional antes de avanzar."
        ),
        "next_questions": operational_audit_result["missing_evidence"],
        "next_steps": [
            "Adjuntar cierre de caja del periodo.",
            "Adjuntar conciliación bancaria.",
            "Adjuntar detalle de ventas por canal.",
            "Adjuntar reporte de diferencias contables.",
        ],
        "blocked_message": None,
        "forbidden_inferences": list(forbidden),
        "references": [
            operational_audit_result["result_id"],
            kernel_request["evidence_refs"][0],
            kernel_request["request_id"],
        ],
        "allowed_tone": "operational",
        "created_at": "2026-05-25T00:00:00Z",
    }


def test_offline_chain_preserves_references_and_guardrails_across_all_stages():
    evidence_candidate = _evidence_candidate()
    kernel_request = _kernel_request(evidence_candidate)
    operational_audit_result = _operational_audit_result(evidence_candidate)
    render_contract = _render_contract(kernel_request, operational_audit_result)

    expected_tenant = "tenant_sandbox_demo"

    # --- tenant consistency ---
    assert evidence_candidate["tenant_id"] == expected_tenant
    assert kernel_request["tenant_id"] == expected_tenant
    assert operational_audit_result["tenant_id"] == expected_tenant
    assert render_contract["tenant_id"] == expected_tenant

    # --- references continuity ---
    assert evidence_candidate["evidence_id"] in kernel_request["evidence_refs"]
    assert evidence_candidate["evidence_id"] in operational_audit_result["evidence_used"]
    assert render_contract["result_ref"] == operational_audit_result["result_id"]
    assert operational_audit_result["result_id"] in render_contract["references"]
    assert evidence_candidate["evidence_id"] in render_contract["references"]
    assert kernel_request["request_id"] in render_contract["references"]

    # --- evidence candidate guardrails ---
    assert evidence_candidate["payload"]["hermes_executed"] is False
    assert evidence_candidate["payload"]["claims"] == []
    assert evidence_candidate["payload"]["sovereign_boundary"]["hermes_may_create_findings"] is False
    assert evidence_candidate["payload"]["expected_behavior"]["hermes_may_create_findings"] is False
    assert evidence_candidate["payload"]["expected_behavior"]["must_request_evidence"] is True
    assert evidence_candidate["payload"]["expected_behavior"]["must_not_diagnose"] is True
    assert evidence_candidate["payload"]["expected_behavior"]["must_fail_closed_if_invalid"] is True
    assert len(evidence_candidate["payload"]["requested_evidence"]) >= 1
    assert len(evidence_candidate["payload"]["forbidden_inferences"]) >= 1
    assert evidence_candidate["hermes_notes"]["role"] == "context_only"
    assert evidence_candidate["hermes_notes"]["diagnostic_authority"] is False

    # --- kernel request guardrails ---
    assert kernel_request["requested_by"] == "boundary_layer"
    assert kernel_request["hermes_executed"] is False

    # --- operational audit result guardrails ---
    assert operational_audit_result["status"] == "pending_data"
    assert operational_audit_result["findings"] == []
    assert len(operational_audit_result["missing_evidence"]) > 0
    assert operational_audit_result["forbidden_inferences"] == evidence_candidate["payload"]["forbidden_inferences"]
    assert operational_audit_result["allowed_rendering"]["must_not_diagnose"] is True
    assert operational_audit_result["allowed_rendering"]["must_not_create_findings"] is True

    # --- sovereign mark non-empty object ---
    sm = operational_audit_result["sovereign_mark"]
    assert isinstance(sm, dict)
    assert sm["issuer"]
    assert sm["mark_type"]
    assert sm["mark_value"]

    # --- render contract guardrails ---
    assert render_contract["allowed_tone"] == "operational"
    assert render_contract["forbidden_inferences"] == operational_audit_result["forbidden_inferences"]
    assert len(render_contract["next_questions"]) > 0
    assert len(render_contract["next_steps"]) > 0
    assert "findings" not in render_contract

    # --- no diagnostic/causal inference in summary ---
    summary = render_contract["summary"].lower()
    for forbidden_term in [
        "robo",
        "faltante confirmado",
        "error contable confirmado",
        "responsable",
    ]:
        assert forbidden_term not in summary
