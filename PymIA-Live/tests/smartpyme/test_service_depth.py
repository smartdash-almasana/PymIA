from __future__ import annotations

from pymia.smartpyme.service_depth import derive_service_depth


def test_first_aid_by_single_task_request() -> None:
    verdict = derive_service_depth(
        raw_owner_message="Mirame este Excel y sacame algo en limpio.",
        evidence_records=[{"evidence_id": "ev_1", "evidence_type": "xlsx_upload", "status": "REGISTERED"}],
    )

    assert verdict == {
        "level": "FIRST_AID",
        "reason": "single_source_task_request",
        "required_evidence_depth": "single_source",
        "required_case_file_depth": "minimal",
        "next_allowed_action": "run_first_aid_microservice",
    }


def test_first_aid_fallback_conservative() -> None:
    verdict = derive_service_depth(raw_owner_message="Necesito ayuda con un tema.")

    assert verdict["level"] == "FIRST_AID"
    assert verdict["reason"] == "insufficient_signal_for_deeper_diagnosis"
    assert verdict["required_evidence_depth"] == "single_source"
    assert verdict["required_case_file_depth"] == "minimal"
    assert verdict["next_allowed_action"] == "request_minimal_evidence"


def test_deterministic_diagnosis_by_economic_pain_and_cross_source() -> None:
    verdict = derive_service_depth(
        taxonomic_intake={"dolores_declarados": ["vendo pero no me queda plata"]},
        evidence_records=[
            {"evidence_id": "ev_1", "evidence_type": "ventas", "status": "REGISTERED"},
            {"evidence_id": "ev_2", "evidence_type": "costos", "status": "REGISTERED"},
        ],
    )

    assert verdict == {
        "level": "DETERMINISTIC_DIAGNOSIS",
        "reason": "declared_economic_pain_with_cross_source_evidence",
        "required_evidence_depth": "cross_source",
        "required_case_file_depth": "partial",
        "next_allowed_action": "run_deterministic_diagnosis",
    }


def test_deterministic_diagnosis_requests_cross_source_evidence_when_missing() -> None:
    verdict = derive_service_depth(
        taxonomic_intake={"dolores_declarados": ["no me cierra la caja"]},
        evidence_records=[{"evidence_id": "ev_1", "evidence_type": "caja", "status": "REGISTERED"}],
    )

    assert verdict["level"] == "DETERMINISTIC_DIAGNOSIS"
    assert verdict["reason"] == "declared_economic_pain_requires_cross_source_evidence"
    assert verdict["next_allowed_action"] == "request_cross_source_evidence"


def test_organizational_lab_by_systemic_intent() -> None:
    verdict = derive_service_depth(raw_owner_message="Quiero profesionalizar la empresa.")

    assert verdict == {
        "level": "ORGANIZATIONAL_LAB",
        "reason": "declared_lab_intent_requires_onboarding",
        "required_evidence_depth": "longitudinal",
        "required_case_file_depth": "full",
        "next_allowed_action": "request_lab_onboarding_evidence",
    }


def test_organizational_lab_by_multiple_critical_areas() -> None:
    verdict = derive_service_depth(
        taxonomic_intake={
            "areas_criticas": ["margen", "stock", "caja"],
            "dolores_declarados": ["hay varios problemas operativos"],
        },
    )

    assert verdict["level"] == "ORGANIZATIONAL_LAB"
    assert verdict["reason"] == "multi_area_critical_case_requires_lab"
    assert verdict["required_evidence_depth"] == "longitudinal"
    assert verdict["required_case_file_depth"] == "full"
    assert verdict["next_allowed_action"] == "request_lab_onboarding_evidence"


def test_idempotency_same_input_same_verdict() -> None:
    payload = {
        "taxonomic_intake": {"dolores_declarados": ["no se si gano"]},
        "evidence_records": [
            {"evidence_id": "ev_1", "evidence_type": "ventas", "status": "REGISTERED"},
            {"evidence_id": "ev_2", "evidence_type": "costos", "status": "REGISTERED"},
        ],
    }

    assert derive_service_depth(**payload) == derive_service_depth(**payload)


def test_transition_new_evidence_changes_depth() -> None:
    first = derive_service_depth(
        raw_owner_message="Mirame este Excel.",
        evidence_records=[{"evidence_id": "ev_1", "evidence_type": "xlsx_upload", "status": "REGISTERED"}],
    )
    second = derive_service_depth(
        taxonomic_intake={"dolores_declarados": ["no me cierra la caja"]},
        evidence_records=[
            {"evidence_id": "ev_1", "evidence_type": "ventas", "status": "REGISTERED"},
            {"evidence_id": "ev_2", "evidence_type": "banco", "status": "REGISTERED"},
        ],
    )

    assert first["level"] == "FIRST_AID"
    assert second["level"] == "DETERMINISTIC_DIAGNOSIS"


def test_lab_intent_without_evidence_blocks_diagnosis() -> None:
    verdict = derive_service_depth(raw_owner_message="Quiero profesionalizar mi empresa.")

    assert verdict["level"] == "ORGANIZATIONAL_LAB"
    assert verdict["reason"] == "declared_lab_intent_requires_onboarding"
    assert verdict["next_allowed_action"] == "request_lab_onboarding_evidence"
    assert verdict["next_allowed_action"] != "run_deterministic_diagnosis"
