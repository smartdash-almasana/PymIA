from __future__ import annotations

from pathlib import Path

import pytest

from pymia.contracts.column_confirmation_v1 import CalculationRelevance, ColumnConfirmationEntry, ColumnConfirmationMatrix, ConfirmationStatus
from pymia.smartpyme.service_1_aligned_owner_prompt_display_packet_v1 import (
    DISPLAY_STATUS_BLOCKED,
    DISPLAY_STATUS_EMPTY,
    DISPLAY_STATUS_READY,
    SCHEMA_VERSION,
    build_service_1_aligned_owner_prompt_display_packet_v1,
)
from pymia.smartpyme.service_1_column_confirmation_owner_prompt_batch_v1 import build_service_1_column_confirmation_owner_prompt_batch_v1
from pymia.smartpyme.service_1_owner_prompt_batch_to_question_bundle_alignment_v1 import align_service_1_owner_prompt_batch_to_question_bundle_v1
from pymia.smartpyme.service_1_question_bundle_v1 import build_service_1_question_bundle_v1


def _entry(column_name: str, role: str, *, status: ConfirmationStatus = ConfirmationStatus.PENDING_OWNER_CONFIRMATION) -> ColumnConfirmationEntry:
    relevance = CalculationRelevance.CANTIDADES if role == "cantidad" else CalculationRelevance.VENTAS
    return ColumnConfirmationEntry(
        original_column_name=column_name,
        sheet_name="Ventas",
        sample_values=[100, 200],
        inferred_type="number",
        suggested_semantic_role=role,
        calculation_relevance=relevance,
        confirmation_status=status,
        owner_question=f"La columna {column_name} confirma {role}?",
    )


def _matrix(entries: list[ColumnConfirmationEntry]) -> ColumnConfirmationMatrix:
    return ColumnConfirmationMatrix(file_name="ventas.xlsx", entries=entries)


def _alignment(matrix: ColumnConfirmationMatrix):
    bundle = build_service_1_question_bundle_v1(
        case_id="case-1",
        tenant_id="tenant-1",
        intake_id="intake-1",
        run_id="run-1",
        column_confirmation_matrix=matrix.model_dump(mode="json"),
    )
    batch = build_service_1_column_confirmation_owner_prompt_batch_v1(matrix=matrix)
    return align_service_1_owner_prompt_batch_to_question_bundle_v1(
        question_bundle=bundle,
        owner_prompt_batch=batch,
    )


def test_builds_ready_display_packet_from_alignment() -> None:
    packet = build_service_1_aligned_owner_prompt_display_packet_v1(
        alignment=_alignment(_matrix([_entry("Total", "venta_total")])),
    )

    assert packet.schema_version == SCHEMA_VERSION
    assert packet.display_status == DISPLAY_STATUS_READY
    assert packet.blocked_reason is None
    assert packet.total_items == 1
    item = packet.items[0]
    assert item.display_index == 1
    assert item.question_ref.startswith("service_1:column_confirmation_matrix:")
    assert item.target_ref == "file:ventas.xlsx:sheet:Ventas:column:Total"
    assert item.display_title == "Pregunta 1: confirmar columna Total"
    assert "Dueño, revisé tu Excel" in item.prompt_text
    assert item.allowed_owner_responses == ("SÍ", "NO", "TU_RESPUESTA")
    assert "question_ref" in item.operator_note


def test_packet_is_acceptance_chain_matrix_to_bundle_batch_alignment_display() -> None:
    matrix = _matrix([_entry("Total", "venta_total"), _entry("Cantidad", "cantidad")])
    alignment = _alignment(matrix)
    packet = build_service_1_aligned_owner_prompt_display_packet_v1(alignment=alignment)

    assert alignment.aligned_prompts_count == 2
    assert packet.display_status == DISPLAY_STATUS_READY
    assert packet.total_items == 2
    assert [item.display_index for item in packet.items] == [1, 2]
    assert all(item.question_ref for item in packet.items)
    assert all(item.prompt_text for item in packet.items)


def test_empty_alignment_returns_empty_display_packet() -> None:
    matrix = _matrix([_entry("Total", "venta_total", status=ConfirmationStatus.CONFIRMED)])
    packet = build_service_1_aligned_owner_prompt_display_packet_v1(alignment=_alignment(matrix))

    assert packet.display_status == DISPLAY_STATUS_EMPTY
    assert packet.blocked_reason == "NO_ALIGNED_PROMPTS_TO_DISPLAY"
    assert packet.total_items == 0
    assert packet.items == ()


def test_blocked_alignment_returns_blocked_display_packet() -> None:
    matrix = _matrix([_entry("Total", "venta_total")])
    empty_bundle = build_service_1_question_bundle_v1(
        case_id="case-1",
        tenant_id="tenant-1",
        intake_id="intake-1",
        run_id="run-1",
    )
    batch = build_service_1_column_confirmation_owner_prompt_batch_v1(matrix=matrix)
    alignment = align_service_1_owner_prompt_batch_to_question_bundle_v1(
        question_bundle=empty_bundle,
        owner_prompt_batch=batch,
    )

    packet = build_service_1_aligned_owner_prompt_display_packet_v1(alignment=alignment)

    assert packet.display_status == DISPLAY_STATUS_BLOCKED
    assert packet.blocked_reason == "NO_PROMPTS_WITH_QUESTION_REF"
    assert packet.total_items == 0
    assert packet.unaligned_prompt_targets == ("file:ventas.xlsx:sheet:Ventas:column:Total",)


def test_metadata_flags_and_to_dict_are_stable() -> None:
    packet = build_service_1_aligned_owner_prompt_display_packet_v1(
        alignment=_alignment(_matrix([_entry("Total", "venta_total")])) ,
        metadata={"delivery_surface": "operator_cli"},
    )

    assert packet.metadata == {"delivery_surface": "operator_cli"}
    assert packet.runtime_authorized is False
    assert packet.owner_confirmation_required is True
    assert packet.reexecution_authorized is False
    assert packet.recalculation_authorized is False
    assert packet.persistence_authorized is False
    assert packet.items[0].metadata["delivery_surface"] == "operator_cli"
    assert packet.items[0].runtime_authorized is False
    assert packet.items[0].owner_confirmation_required is True
    data = packet.to_dict()
    assert isinstance(data["items"], list)
    assert data["owner_confirmation_required"] is True
    assert data["items"][0]["owner_confirmation_required"] is True
    assert data["items"][0]["allowed_owner_responses"] == ["SÍ", "NO", "TU_RESPUESTA"]


def test_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="alignment"):
        build_service_1_aligned_owner_prompt_display_packet_v1(alignment="bad")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="metadata"):
        build_service_1_aligned_owner_prompt_display_packet_v1(
            alignment=_alignment(_matrix([_entry("Total", "venta_total")])) ,
            metadata="bad",  # type: ignore[arg-type]
        )


def test_module_does_not_depend_on_io_ingestion_or_runtime() -> None:
    source = Path("pymia/smartpyme/service_1_aligned_owner_prompt_display_packet_v1.py").read_text(encoding="utf-8")
    assert "openpyxl" not in source
    assert "pandas" not in source
    assert "curate_xlsx_document" not in source
    assert "DocumentCurator" not in source
    assert "vertical_pipeline" not in source
    assert "storage" not in source
