from pymia.smartpyme.service_1_assisted_semantic_product_wiring_v1 import (
    BLOCK_INTERPRETER_FAILED,
    run_service_1_assisted_semantic_initial_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_unconfirmed_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)
from pathlib import Path


def test_provider_failure_preserves_safe_interpreter_detail() -> None:
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

    def failing_provider(_payload):
        raise RuntimeError("provider exploded safely")

    result = run_service_1_assisted_semantic_initial_v1(
        ingestion_output=canonical["ingestion_output"],
        requested_capability=None,
        provider=failing_provider,
    )

    assert result["status"] == "BLOCKED"
    assert result["blocked_reason"] == BLOCK_INTERPRETER_FAILED
    assert result["detail"]["interpreter_reason"] == "BLOCK_LLM_PROVIDER_FAILED"
    assert result["detail"]["interpreter_detail"]["exception_type"] == "RuntimeError"
    assert result["detail"]["interpreter_detail"]["exception_message"] == "provider exploded safely"
    assert result["detail"]["interpreter_detail"]["failing_stage"] == "PROVIDER_CALL"
