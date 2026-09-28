import os
from pathlib import Path

import pytest

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
from pymia.smartpyme.service_1_pydantic_ai_column_semantic_provider_v1 import (
    semantic_provider_from_environment_v1,
)


@pytest.mark.live
def test_real_taller_workbook_reaches_confirmable_dialogue_with_configured_llm() -> None:
    if not os.getenv("PYMIA_SEMANTIC_LLM_MODEL", "").strip():
        pytest.skip("PYMIA_SEMANTIC_LLM_MODEL is not configured")
    root = Path(__file__).resolve().parents[2]
    fixture = root / "prueba_excels" / "taller_mecanico_lubricar_srl.xlsx"
    intake = build_service_1_web_column_confirmation_intake_boundary_v1(
        uploaded_xlsx_bytes=fixture.read_bytes(),
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
        provider=semantic_provider_from_environment_v1(),
    )

    assert result.get("status") == STATUS_OWNER_DIALOGUE_REQUIRED, result
    assert list(result.get("owner_questions") or []), result
