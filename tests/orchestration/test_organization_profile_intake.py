from __future__ import annotations

import json
from pathlib import Path

from pymia.orchestration.organization_profile_intake import (
    answer_organization_profile_question,
    get_organization_profile_questions,
    get_procedural_orientation,
    start_organization_profile_intake,
)


def test_orientation_contains_key_procedural_rules() -> None:
    text = get_procedural_orientation().lower()
    assert "expresarte libremente" in text
    assert "subir documentacion" in text
    assert "nombre, fecha y hora" in text
    assert "archivo documental" in text
    assert "analisis/reportes" in text
    assert "no se hace todo junto" in text


def test_start_returns_first_question_and_initial_context() -> None:
    result = start_organization_profile_intake({})
    questions = get_organization_profile_questions()
    assert result.completed is False
    assert result.next_question_id == questions[0].id
    assert "organization_profile" in result.updated_progressive_context
    assert result.updated_progressive_context["organization_profile"] == {}
    assert result.updated_progressive_context["organization_profile_status"] == "IN_PROGRESS"


def test_answer_advances_one_question_at_a_time_and_stores_answers() -> None:
    context = {}
    started = start_organization_profile_intake(context)
    questions = get_organization_profile_questions()

    after_first = answer_organization_profile_question(started.updated_progressive_context, "PyME")
    assert after_first.completed is False
    assert after_first.next_question_id == questions[1].id
    assert after_first.updated_progressive_context["organization_profile"]["business_type"] == "PyME"


def test_input_context_is_not_mutated() -> None:
    original = {"organization_profile": {}}
    snapshot = json.loads(json.dumps(original))
    _ = start_organization_profile_intake(original)
    assert original == snapshot

    _ = answer_organization_profile_question(original, "PyME")
    assert original == snapshot


def test_full_flow_completes_and_invites_document_upload() -> None:
    result = start_organization_profile_intake({})
    questions = get_organization_profile_questions()
    answers = [
        "PyME",
        "Textil",
        "Fabrico productos",
        "Pequena",
        "6-20",
        "Medio",
        "Mixto",
        "Planillas",
        "Stock",
        "Rentabilidad",
        "Medio",
        "Excel ventas",
        "Si, ahora",
    ]
    assert len(answers) == len(questions)

    for answer in answers:
        result = answer_organization_profile_question(result.updated_progressive_context, answer)

    assert result.completed is True
    assert result.next_question_id is None
    assert "subi documentacion" in result.reply_text.lower()


def test_output_is_json_serializable() -> None:
    result = start_organization_profile_intake({})
    json.dumps(result.updated_progressive_context)
    json.dumps(
        {
            "reply_text": result.reply_text,
            "completed": result.completed,
            "next_question_id": result.next_question_id,
            "decision_trail_entry": result.decision_trail_entry,
        }
    )


def test_source_has_no_forbidden_imports() -> None:
    source = Path("pymia/orchestration/organization_profile_intake.py").read_text(encoding="utf-8").lower()
    assert "telegram" not in source
    assert "smartpyme" not in source
    assert "hermes" not in source
    assert "langgraph" not in source
