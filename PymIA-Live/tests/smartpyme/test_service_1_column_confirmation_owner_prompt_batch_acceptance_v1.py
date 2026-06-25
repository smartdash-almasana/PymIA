from __future__ import annotations

from openpyxl import Workbook

from tools.document_ingestion import curate_xlsx_document
from pymia.contracts.column_confirmation_v1 import ColumnConfirmationMatrix
from pymia.smartpyme.service_1_column_confirmation_owner_prompt_batch_v1 import (
    build_service_1_column_confirmation_owner_prompt_batch_v1,
)


def _write_xlsx(path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Ventas"
    ws.append(["Producto", "Cantidad", "Venta Total", "Costo Unitario"])
    ws.append(["Remera", 2, 10000, 3000])
    ws.append(["Pantalon", 1, 18000, 7000])
    wb.save(path)


def test_xlsx_curation_matrix_feeds_owner_prompt_batch(tmp_path):
    xlsx_path = tmp_path / "ventas_test.xlsx"
    _write_xlsx(xlsx_path)

    curated = curate_xlsx_document(xlsx_path)
    matrix = curated.report.column_confirmation_matrix

    assert isinstance(matrix, ColumnConfirmationMatrix)
    assert matrix.file_name == "ventas_test.xlsx"
    assert matrix.entries

    batch = build_service_1_column_confirmation_owner_prompt_batch_v1(
        matrix=matrix,
        metadata={"case_id": "acceptance-seam"},
    )

    assert batch.file_name == "ventas_test.xlsx"
    assert batch.total_entries == len(matrix.entries)
    assert batch.actionable_entries_count == len([e for e in matrix.entries if e.is_actionable()])
    assert batch.has_prompts is True
    assert batch.prompts
    assert all(prompt.file_name == "ventas_test.xlsx" for prompt in batch.prompts)
    assert all(prompt.metadata["case_id"] == "acceptance-seam" for prompt in batch.prompts)
    assert all("suggested_semantic_role" not in prompt.owner_prompt.prompt_text for prompt in batch.prompts)


def test_batch_input_is_matrix_not_report(tmp_path):
    xlsx_path = tmp_path / "test.xlsx"
    _write_xlsx(xlsx_path)

    curated = curate_xlsx_document(xlsx_path)
    matrix = curated.report.column_confirmation_matrix

    assert isinstance(matrix, ColumnConfirmationMatrix)

    batch = build_service_1_column_confirmation_owner_prompt_batch_v1(matrix=matrix)
    assert batch.file_name == "test.xlsx"
    assert batch.total_entries > 0


def test_matrix_none_is_not_batch_input():
    assert not isinstance(None, ColumnConfirmationMatrix)
