from __future__ import annotations


def test_known_missing_variables_build_explicit_questions() -> None:
    from pymia.smartpyme.owner_questions_builder import build_owner_questions_bundle

    bundle = build_owner_questions_bundle(
        source_ref="operational_audit_result://missing_evidence",
        missing_evidence=["dias_periodo", "taxes"],
    )

    assert [question.question_text for question in bundle.questions] == [
        "¿Cuál es la cantidad de días del período analizado?",
        "¿Podés informar los impuestos del período analizado?",
    ]
    assert [question.expected_answer_type for question in bundle.questions] == [
        "number",
        "number",
    ]


def test_unknown_missing_variable_builds_safe_fallback_question() -> None:
    from pymia.smartpyme.owner_questions_builder import build_owner_questions_bundle

    bundle = build_owner_questions_bundle(
        source_ref="operational_audit_result://missing_evidence",
        missing_evidence=["saldo_ajustado"],
    )

    assert len(bundle.questions) == 1
    assert bundle.questions[0].question_text == (
        "¿Podés aportar el dato o documento faltante para 'saldo_ajustado'?"
    )
    assert bundle.questions[0].expected_answer_type == "unknown"


def test_builder_deduplicates_repeated_entries() -> None:
    from pymia.smartpyme.owner_questions_builder import build_owner_questions_bundle

    bundle = build_owner_questions_bundle(
        source_ref="render_contract://next_questions",
        missing_evidence=["dias_periodo", "dias_periodo"],
        next_questions=["¿Qué período cubre esta planilla?", "¿Qué período cubre esta planilla?"],
        blocked_message="Falta evidencia para avanzar.",
    )

    assert len(bundle.questions) == 3


def test_builder_preserves_stable_order() -> None:
    from pymia.smartpyme.owner_questions_builder import build_owner_questions_bundle

    bundle = build_owner_questions_bundle(
        source_ref="render_contract://next_questions",
        missing_evidence=["taxes", "dias_periodo"],
        next_questions=["¿Qué período cubre esta planilla?"],
        blocked_message="Falta evidencia para avanzar.",
    )

    assert [question.reason for question in bundle.questions] == [
        "missing_evidence",
        "missing_evidence",
        "next_question",
        "blocked_message",
    ]


def test_builder_generates_deterministic_ids() -> None:
    from pymia.smartpyme.owner_questions_builder import build_owner_questions_bundle

    bundle_a = build_owner_questions_bundle(
        source_ref="render_contract://next_questions",
        missing_evidence=["taxes"],
        next_questions=["¿Qué período cubre esta planilla?"],
        blocked_message="Falta evidencia para avanzar.",
    )
    bundle_b = build_owner_questions_bundle(
        source_ref="render_contract://next_questions",
        missing_evidence=["taxes"],
        next_questions=["¿Qué período cubre esta planilla?"],
        blocked_message="Falta evidencia para avanzar.",
    )

    assert bundle_a.bundle_id == bundle_b.bundle_id
    assert [item.question_id for item in bundle_a.questions] == [
        item.question_id for item in bundle_b.questions
    ]


def test_blocked_message_is_preserved_in_question_metadata() -> None:
    from pymia.smartpyme.owner_questions_builder import build_owner_questions_bundle

    bundle = build_owner_questions_bundle(
        source_ref="render_contract://blocked_message",
        blocked_message="Falta evidencia para avanzar al resultado operativo entregable.",
    )

    assert len(bundle.questions) == 1
    assert bundle.questions[0].reason == "blocked_message"
    assert bundle.questions[0].metadata["blocked_message"] == (
        "Falta evidencia para avanzar al resultado operativo entregable."
    )


def test_next_questions_are_integrated_without_free_narrative() -> None:
    from pymia.smartpyme.owner_questions_builder import build_owner_questions_bundle

    bundle = build_owner_questions_bundle(
        source_ref="render_contract://next_questions",
        next_questions=["¿Qué período cubre esta planilla?", "¿Qué significa la columna ajuste?"],
    )

    assert [question.question_text for question in bundle.questions] == [
        "¿Qué período cubre esta planilla?",
        "¿Qué significa la columna ajuste?",
    ]


def test_owner_questions_bundle_serialization_is_valid() -> None:
    from pymia.smartpyme.owner_questions_builder import build_owner_questions_bundle

    bundle = build_owner_questions_bundle(
        source_ref="operational_audit_result://missing_evidence",
        missing_evidence=["dias_periodo"],
        metadata={"tenant_id": "tenant-1"},
    )

    payload = bundle.model_dump(mode="json")

    assert payload["bundle_id"].startswith("owner_questions_bundle_")
    assert payload["questions"][0]["source_ref"] == "operational_audit_result://missing_evidence"
    assert payload["questions"][0]["required"] is True
    assert payload["metadata"]["tenant_id"] == "tenant-1"
