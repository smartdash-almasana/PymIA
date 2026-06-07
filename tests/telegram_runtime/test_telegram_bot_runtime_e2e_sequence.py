from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from pymia.orchestration.state_storage import load_state
from pymia.smartpyme.evidence_requirement import create_evidence_requirement
from pymia.smartpyme.intake import create_intake_record
from pymia.telegram_bot_runtime import (
    _route_document_with_evidence_gate,
    route_text_message,
)
from pymia.telegram_document_handler import DocumentResult
from pymia.telegram_runtime import SENTINEL


REPO_ROOT = Path(__file__).resolve().parents[2]
WHOLESALE_FIXTURE = REPO_ROOT / "prueba_excels" / "distribuidora_mayorista_compleja.xlsx"


def _complete_distribution_profile(tmp_path: Path, monkeypatch, chat_id: str) -> tuple[str, dict]:
    monkeypatch.setenv("PYMIA_TELEGRAM_STATE_BASE_DIR", str(tmp_path))

    first_reply = route_text_message(
        "Hola, tengo una distribuidora y no me cierra la caja.",
        chat_id=chat_id,
    )
    assert "nombre y apellido" in first_reply.lower()

    answers = [
        "Roque Perez",
        "Distribuidora Don Roque",
        "4",
        "distribuidora mayorista",
        "3",
        "6,7,2",
        "1",
        "2",
        "2",
        "3",
        "1,2,6,7",
        "Dueño",
        "+5491122334455",
        "roque@example.com",
    ]

    reply = first_reply
    for answer in answers:
        reply = route_text_message(answer, chat_id=chat_id)

    state = load_state("telegram", chat_id, tmp_path)
    assert state is not None
    return reply, state.progressive_context


def test_post_ficha_routing_has_no_duplicate_evidence_types(tmp_path, monkeypatch) -> None:
    reply, progressive_context = _complete_distribution_profile(
        tmp_path, monkeypatch, "tg-e2e-001"
    )

    assert "Ya tengo la ficha inicial." in reply
    post_ficha_routing = progressive_context["post_ficha_routing"]
    evidence_requests = post_ficha_routing["evidence_requests"]
    evidence_types = [item["evidence_type"] for item in evidence_requests]
    assert len(evidence_types) == len(set(evidence_types))

    visible_lines = [
        line.strip()
        for line in reply.splitlines()
        if line.strip() and line.strip()[0].isdigit() and ". " in line
    ]
    assert len(visible_lines) == len(set(visible_lines))
    assert reply.count("LIQ_001") <= 1


def test_intake_merges_formula_ids_for_same_evidence_type() -> None:
    duplicate_requirements = [
        create_evidence_requirement(
            requirement_id="req_a",
            tenant_id="tenant-test",
            intake_id="intake-test",
            hypothesis_id="hyp-test",
            evidence_type="excel_ventas_costos",
            description="Req formula A",
            required_fields=["fecha", "monto"],
            reason="A",
            blocks_analysis=True,
            priority=1,
            telegram_message="A",
            formula_id="FORM_A",
            formula_ids=["FORM_A"],
        ),
        create_evidence_requirement(
            requirement_id="req_b",
            tenant_id="tenant-test",
            intake_id="intake-test",
            hypothesis_id="hyp-test",
            evidence_type="excel_ventas_costos",
            description="Req formula B",
            required_fields=["producto", "fecha"],
            reason="B",
            blocks_analysis=True,
            priority=1,
            telegram_message="B",
            formula_id="FORM_B",
            formula_ids=["FORM_B"],
        ),
    ]

    with patch(
        "pymia.smartpyme.intake.derive_evidence_requirements_from_formulas",
        return_value=duplicate_requirements,
    ):
        record = create_intake_record(
            tenant_id="tenant-test",
            raw_text="mi margen es dudoso y hago copia manual en excel",
        )

    matching = [
        req for req in record.evidence_requests if req.evidence_type == "excel_ventas_costos"
    ]
    assert len(matching) == 1
    request = matching[0]
    assert request.formula_ids == ["FORM_A", "FORM_B"]
    assert request.formula_id == "FORM_A"
    assert request.required_fields == [
        "producto",
        "venta_neta",
        "costo_directo",
        "fecha",
        "monto",
    ]


def test_telegram_e2e_sequence_ficha_to_evidence_gate_no_duplicates(tmp_path, monkeypatch) -> None:
    reply, progressive_context = _complete_distribution_profile(
        tmp_path, monkeypatch, "tg-e2e-002"
    )

    post_ficha_routing = progressive_context["post_ficha_routing"]
    evidence_requests = post_ficha_routing["evidence_requests"]
    evidence_types = [item["evidence_type"] for item in evidence_requests]
    assert len(evidence_types) == len(set(evidence_types))
    assert reply.count("LIQ_001") <= 1

    doc_result = DocumentResult(
        text=(
            f"{SENTINEL} Documento recibido: {WHOLESALE_FIXTURE.name}. "
            "Ya lo guarde y podes pedirme el analisis cuando quieras."
        ),
        mode="received",
        file_path=str(WHOLESALE_FIXTURE),
    )
    with patch("pymia.telegram_bot_runtime.handle_document", return_value=doc_result):
        upload_reply = _route_document_with_evidence_gate(
            "fake-token",
            "file-1",
            WHOLESALE_FIXTURE.name,
            "tg-e2e-002",
        )

    assert "Documento recibido" in upload_reply
    assert "Recibí el Excel" in upload_reply or "Documento recibido" in upload_reply
    assert WHOLESALE_FIXTURE.name in upload_reply
    assert "Lo que pude rescatar" in upload_reply
    assert "Lo que todavía no queda claro" in upload_reply
    assert "Para avanzar" in upload_reply
    lowered = upload_reply.lower()
    assert "diagnóstico" not in lowered
    assert "diagnostico" not in lowered
    assert "margen" not in lowered
    assert "excel_caja_banco" not in lowered
    assert "ventas_del_periodo" not in lowered
    assert "cobranzas_del_periodo" not in lowered
    assert "liq_001" not in lowered

    state = load_state("telegram", "tg-e2e-002", tmp_path)
    assert state is not None
    assert state.progressive_context.get("evidence_records")
    assert state.progressive_context["post_ficha_readiness"]["readiness_state"] in {
        "READY_FOR_ANALYSIS",
        "NEEDS_EVIDENCE",
    }
