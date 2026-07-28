from pathlib import Path

from openpyxl import Workbook

from pymia.faithful_operator import OperatorPhase, handle_owner_message, receive_excel_and_build_candidate


def _make_operational_excel(path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "ventas"
    sheet.append(["fecha", "producto", "cantidad", "precio", "costo"])
    sheet.append(["2026-06-01", "producto-a", 3, 120, 70])
    workbook.save(path)


def test_owner_message_requests_evidence_without_diagnosis() -> None:
    state = handle_owner_message(
        "Vendo más pero no me queda plata.",
        tenant_id="cafeteria_abc",
    )

    assert state.current_state == OperatorPhase.EVIDENCE_REQUESTED
    assert state.tenant_id == "cafeteria_abc"
    assert state.intake_id.startswith("intake_")
    assert state.evidence_requested == ["ventas", "costos", "productos", "periodo"]
    assert "todavía no puedo afirmar la causa" in state.next_question
    assert "Excel" in state.next_question
    assert "la causa es" not in state.next_question.lower()


def test_owner_message_preserves_existing_intake_id() -> None:
    state = handle_owner_message(
        "Tengo una fábrica y no me cierra la caja.",
        tenant_id="fabrica_industrial",
        intake_id="intake_fabrica_industrial_001",
    )

    assert state.current_state == OperatorPhase.EVIDENCE_REQUESTED
    assert state.intake_id == "intake_fabrica_industrial_001"
    assert state.problem_summary == "Tengo una fábrica y no me cierra la caja."


def test_blank_owner_message_blocks_honestly() -> None:
    state = handle_owner_message("   ", tenant_id="tenant_empty")

    assert state.current_state == OperatorPhase.BLOCKED
    assert state.blocked_reason == "empty_owner_message"
    assert state.evidence_requested == []
    assert "Necesito que me cuentes" in state.next_question


def test_intake_id_is_deterministic_for_same_input() -> None:
    first = handle_owner_message("No sé si mis productos dejan margen.", tenant_id="distribuidora")
    second = handle_owner_message("No sé si mis productos dejan margen.", tenant_id="distribuidora")

    assert first.intake_id == second.intake_id


def test_full_local_flow_executes_spine_and_waits_for_owner_confirmation(tmp_path: Path) -> None:
    excel_path = tmp_path / "ventas.xlsx"
    storage_dir = tmp_path / "storage"
    _make_operational_excel(excel_path)

    initial = handle_owner_message(
        "Vendo más pero no me queda plata.",
        tenant_id="cafeteria_abc",
    )
    final = receive_excel_and_build_candidate(initial, excel_path, storage_dir=storage_dir)

    assert initial.current_state == OperatorPhase.EVIDENCE_REQUESTED
    assert initial.evidence_requested == ["ventas", "costos", "productos", "periodo"]
    assert final.current_state == OperatorPhase.OWNER_CONFIRMATION_PENDING
    assert final.intake_id == initial.intake_id
    assert final.evidence_id is not None
    assert final.evidence_hash is not None
    assert final.run_id is not None
    assert final.output_hash is not None
    assert final.evidence_hash != final.output_hash
    assert final.candidate_response is not None
    assert "Estado:" in final.candidate_response
    assert f"Evidence ID: {final.evidence_id}" in final.candidate_response
    assert f"Evidence SHA-256: {final.evidence_hash}" in final.candidate_response
    assert f"Run ID: {final.run_id}" in final.candidate_response
    assert f"Output hash: {final.output_hash}" in final.candidate_response
    assert "Resultado candidato" in final.candidate_response
    assert "Próxima pregunta:" in final.candidate_response
    assert "la causa es" not in final.candidate_response.lower()
    assert (storage_dir / "cafeteria_abc" / "evidences.jsonl").exists()
    assert (storage_dir / "cafeteria_abc" / "pipeline_runs.jsonl").exists()


def test_excel_processing_blocks_when_file_is_missing(tmp_path: Path) -> None:
    initial = handle_owner_message("Vendo más pero no me queda plata.", tenant_id="tenant_missing")
    final = receive_excel_and_build_candidate(initial, tmp_path / "missing.xlsx")

    assert final.current_state == OperatorPhase.BLOCKED
    assert final.blocked_reason == "evidence_file_not_found"
    assert final.run_id is None
    assert final.output_hash is None


def test_faithful_operator_has_no_forbidden_tooling_imports() -> None:
    source = Path("pymia/faithful_operator.py").read_text(encoding="utf-8").lower()

    for forbidden in ["langgraph", "subprocess", "telegram", "hermes", "openai", "requests", "httpx"]:
        assert forbidden not in source
