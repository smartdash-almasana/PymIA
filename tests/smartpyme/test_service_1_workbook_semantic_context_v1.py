from pathlib import Path

from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_unconfirmed_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_workbook_profiler_v1 import build_service_1_workbook_profile_v1
from pymia.smartpyme.service_1_workbook_semantic_context_v1 import (
    STATUS_READY,
    build_service_1_workbook_semantic_context_v1,
)


def test_real_taller_builds_table_first_llm_context_with_structural_evidence() -> None:
    root = Path(__file__).resolve().parents[2]
    fixture = root / "prueba_excels" / "taller_mecanico_lubricar_srl.xlsx"
    intake = build_service_1_web_column_confirmation_intake_boundary_v1(
        uploaded_xlsx_bytes=fixture.read_bytes(),
        uploaded_filename=fixture.name,
        include_all_sheets=True,
    )
    canonical = build_service_1_unconfirmed_canonical_ingestion_output_v1(
        owner_question_packet=intake,
    )
    profile = build_service_1_workbook_profile_v1(
        ingestion_output=canonical["ingestion_output"],
    )
    context = build_service_1_workbook_semantic_context_v1(workbook_profile=profile)

    assert context["status"] == STATUS_READY, context
    assert context["sheet_count"] == 3
    assert context["column_count"] >= 20
    assert context["runtime_authorized"] is False
    tables = {table["sheet_name"]: table for table in context["tables"]}
    assert {"ORDENES_TRABAJO", "PRODUCTOS_STOCK", "CLIENTES"}.issubset(tables)

    order_columns = {item["column_name"]: item for item in tables["ORDENES_TRABAJO"]["columns"]}
    for required in ("orden_id", "horas_mano_obra", "valor_hora", "costo_mano_obra"):
        assert required in order_columns
        column = order_columns[required]
        assert "inferred_type" in column
        assert "sample_values" in column
        assert "cardinality" in column
        assert "unique_ratio" in column
        assert "candidate_primary_key" in column

    assert order_columns["orden_id"]["sample_values"], order_columns["orden_id"]
    assert context["relationships"] == profile["relationships"] or context["relationship_count"] == len(profile["relationships"])
