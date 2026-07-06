from __future__ import annotations

from pymia.smartpyme.service_1_question_bundle_v1 import (
    ANSWER_TYPE_CONFIRM_COLUMN_ROLE,
    ANSWER_TYPE_FREE_TEXT,
    ANSWER_TYPE_PROVIDE_MISSING_EVIDENCE,
    QUESTION_STATUS_PENDING,
    SCHEMA_VERSION,
    SERVICE_NAME,
    build_service_1_question_bundle_v1,
    build_stable_question_ref,
    create_service_1_question_v1,
)


def test_build_stable_question_ref_prefers_target_ref_over_text() -> None:
    first = build_stable_question_ref(
        source="column_confirmation_matrix",
        target_ref="file:ventas.xlsx:sheet:Ventas:column:MetodoPago",
        text="Texto inicial",
    )
    second = build_stable_question_ref(
        source="column_confirmation_matrix",
        target_ref="file:ventas.xlsx:sheet:Ventas:column:MetodoPago",
        text="Texto cambiado",
    )

    assert first == second
    assert first == "service_1:column_confirmation_matrix:file_ventas_xlsx_sheet_ventas_column_metodopago"


def test_build_stable_question_ref_falls_back_to_text_hash_when_target_missing() -> None:
    first = build_stable_question_ref(source="owner_question", target_ref="", text="Que falta confirmar?")
    second = build_stable_question_ref(source="owner_question", target_ref="", text="Que falta confirmar?")

    assert first == second
    assert first.startswith("service_1:owner_question:text_")


def test_create_question_requires_valid_answer_type() -> None:
    question = create_service_1_question_v1(
        source="owner_question",
        text="Confirmas este dato?",
        target_ref="owner_question:main",
        answer_type=ANSWER_TYPE_FREE_TEXT,
    )

    assert question.status == QUESTION_STATUS_PENDING
    assert question.required is True
    assert question.question_ref == "service_1:owner_question:owner_question_main"


def test_bundle_extracts_column_confirmation_questions_first() -> None:
    bundle = build_service_1_question_bundle_v1(
        case_id="case_1",
        tenant_id="tenant_1",
        intake_id="intake_1",
        run_id="run_1",
        report={
            "owner_question": "Que objetivo queres priorizar?",
            "owner_question_technical_reference": "owner_axis:cash",
        },
        column_confirmation_matrix={
            "file_name": "ventas.xlsx",
            "entries": [
                {
                    "sheet_name": "Ventas",
                    "original_column_name": "MetodoPago",
                    "owner_question": "En la hoja Ventas, la columna MetodoPago indica forma de pago o importe?",
                }
            ],
        },
    )

    assert bundle.schema_version == SCHEMA_VERSION
    assert bundle.service_name == SERVICE_NAME
    assert len(bundle.questions) == 2
    assert bundle.questions[0].answer_type == ANSWER_TYPE_CONFIRM_COLUMN_ROLE
    assert bundle.selected_next_question_ref == bundle.questions[0].question_ref
    assert bundle.runtime_authorized is False
    assert bundle.owner_confirmation_required is True


def test_bundle_extracts_report_next_questions_with_stable_refs() -> None:
    bundle = build_service_1_question_bundle_v1(
        case_id="case_2",
        tenant_id="tenant_1",
        intake_id="intake_1",
        run_id="run_2",
        report={
            "next_questions": [
                {"text": "Cual es el periodo del archivo?", "target_ref": "missing:periodo"},
                "Que columna representa ventas netas?",
            ]
        },
    )

    assert len(bundle.questions) == 2
    assert bundle.questions[0].question_ref == "service_1:next_questions:missing_periodo"
    assert bundle.questions[1].question_ref == "service_1:next_questions:next_question_1"


def test_bundle_extracts_catalog_reconciliation_questions() -> None:
    bundle = build_service_1_question_bundle_v1(
        case_id="case_3",
        tenant_id="tenant_1",
        intake_id="intake_1",
        run_id="run_3",
        structured_summary={
            "catalog_reconciliation": [
                {
                    "formula_id": "PYME044",
                    "pathology_code": "MISSING_INPUTS",
                    "next_audit_questions": ["Cual es el costo unitario?"],
                }
            ]
        },
    )

    assert len(bundle.questions) == 1
    assert bundle.questions[0].answer_type == ANSWER_TYPE_PROVIDE_MISSING_EVIDENCE
    assert bundle.questions[0].target_ref == "catalog:PYME044:MISSING_INPUTS:question:0"
    assert bundle.questions[0].question_ref == "service_1:catalog_reconciliation:catalog_pyme044_missing_inputs_question_0"


def test_bundle_deduplicates_same_computational_target() -> None:
    bundle = build_service_1_question_bundle_v1(
        case_id="case_4",
        tenant_id="tenant_1",
        intake_id="intake_1",
        run_id="run_4",
        report={
            "next_questions": [
                {"text": "Pregunta A", "target_ref": "missing:ventas"},
                {"text": "Pregunta B", "target_ref": "missing:ventas"},
            ]
        },
    )

    assert len(bundle.questions) == 1
    assert bundle.questions[0].text == "Pregunta A"


def test_bundle_is_serializable_for_future_persistence() -> None:
    bundle = build_service_1_question_bundle_v1(
        case_id="case_5",
        tenant_id="tenant_1",
        intake_id="intake_1",
        run_id="run_5",
        report={"owner_question": "Confirmas el objetivo?", "owner_question_technical_reference": "owner_axis:margin"},
    )

    data = bundle.to_dict()

    assert data["schema_version"] == SCHEMA_VERSION
    assert data["questions"][0]["question_ref"] == "service_1:owner_question:owner_axis_margin"
    assert data["selected_next_question_ref"] == data["questions"][0]["question_ref"]
    assert data["owner_confirmation_required"] is True
    assert "human_review_required" not in data


def test_empty_sources_return_empty_bundle_without_authorizing_runtime() -> None:
    bundle = build_service_1_question_bundle_v1(
        case_id="case_6",
        tenant_id="tenant_1",
        intake_id="intake_1",
        run_id="run_6",
    )

    assert bundle.questions == ()
    assert bundle.selected_next_question_ref is None
    assert bundle.runtime_authorized is False
    assert bundle.owner_confirmation_required is True
