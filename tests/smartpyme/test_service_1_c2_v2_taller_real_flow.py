from pathlib import Path

from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_unconfirmed_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_assisted_semantic_product_wiring_v1 import (
    STATUS_OWNER_DIALOGUE_REQUIRED,
    run_service_1_assisted_semantic_initial_v1,
)
from pymia.smartpyme.service_1_deterministic_semantic_proposal_provider_v1 import (
    build_service_1_deterministic_semantic_proposal_v1,
)


def test_real_taller_workbook_reaches_confirmable_c2_v2_dialogue() -> None:
    root = Path(__file__).resolve().parents[2]
    fixture = root / "prueba_excels" / "taller_mecanico_lubricar_srl.xlsx"
    content = fixture.read_bytes()
    intake = build_service_1_web_column_confirmation_intake_boundary_v1(
        uploaded_xlsx_bytes=content,
        uploaded_filename=fixture.name,
        include_all_sheets=True,
    )
    assert intake.get("status") != "BLOCKED", intake
    canonical = build_service_1_unconfirmed_canonical_ingestion_output_v1(
        owner_question_packet=intake,
    )
    assert canonical.get("status") != "BLOCKED", canonical

    result = run_service_1_assisted_semantic_initial_v1(
        ingestion_output=canonical["ingestion_output"],
        requested_capability=None,
        provider=build_service_1_deterministic_semantic_proposal_v1,
    )

    assert result.get("status") == STATUS_OWNER_DIALOGUE_REQUIRED, result
    questions = list(result.get("owner_questions") or [])
    assert questions, result
    assert all(str(item.get("decision_id") or "").strip() for item in questions)
    rendered = "\n".join(str(item.get("presentation_text") or "") for item in questions)
    assert "horas_mano_obra como la hora de la operación" not in rendered
    assert "valor_hora como la hora de la operación" not in rendered
    assert "costo_hora_real como la hora de la operación" not in rendered
    assert "cliente asociado a la operación" in rendered
    assert "forma o medio de pago" in rendered
    assert "existencia actual disponible" in rendered
    assert "nivel mínimo de stock definido" in rendered

    validated_packet = result.get("validated_packet") or {}
    compression = validated_packet.get("semantic_compression") or {}
    assert compression.get("status") == "SEMANTIC_COMPRESSION_READY", compression
    assert compression.get("authority") == "CONTEXT_ONLY", compression
    assert compression.get("runtime_authorized") is False, compression
    assert all(unit.get("traceability_complete") for unit in compression.get("semantic_units") or []), compression
    semantic_unit_questions = [
        item for item in questions
        if str(item.get("decision_id") or "").startswith("dialogue:semantic-unit:")
    ]
    assert semantic_unit_questions, result
    assert all(item.get("proposal_refs") for item in semantic_unit_questions)
    assert all(item.get("column_refs") for item in semantic_unit_questions)

    validated_by_id = {
        str(item.get("decision_id") or ""): item
        for item in validated_packet.get("decisions") or []
        if isinstance(item, dict)
    }
    for question in questions:
        proposal_refs = [str(ref) for ref in question.get("proposal_refs") or []]
        if question.get("decision_kind") != "SEMANTIC_GROUP":
            continue
        assert len(question.get("column_refs") or []) < 10, question
        clusters = set()
        for proposal_ref in proposal_refs:
            semantic = validated_by_id[proposal_ref].get("compositional_semantic") or {}
            clusters.add(
                (
                    semantic.get("process"),
                    semantic.get("object"),
                    semantic.get("entity"),
                )
            )
        assert len(clusters) == 1, question
