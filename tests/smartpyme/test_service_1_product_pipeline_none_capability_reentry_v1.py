from __future__ import annotations

from io import BytesIO
from pathlib import Path

from openpyxl import Workbook

from pymia.smartpyme.service_1_deterministic_semantic_proposal_provider_v1 import (
    build_service_1_deterministic_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_unconfirmed_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_product_execution_contracts_v1 import (
    Service1ProductExecutionDependenciesV1,
    WorkbookSemanticContinueRequestV1,
    WorkbookSemanticStartRequestV1,
)
from pymia.smartpyme.service_1_product_pipeline_v1 import (
    STATUS_NEEDS_OWNER,
    STATUS_READY,
    run_service_1_product_pipeline_v1,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)


def _ingestion_output() -> dict:
    stream = BytesIO()
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Ventas"
    sheet.append(["ProductoID", "Cantidad"])
    sheet.append(["P001", 1])
    sheet.append(["P002", 2])
    workbook.save(stream)

    intake = build_service_1_web_column_confirmation_intake_boundary_v1(
        uploaded_xlsx_bytes=stream.getvalue(),
        uploaded_filename="none-capability-reentry.xlsx",
        include_all_sheets=True,
    )
    assert intake["status"] != "BLOCKED", intake
    canonical = build_service_1_unconfirmed_canonical_ingestion_output_v1(
        owner_question_packet=intake,
    )
    assert canonical["status"] != "BLOCKED", canonical
    return canonical["ingestion_output"]


def _run(request, output_dir: Path) -> dict:
    return run_service_1_product_pipeline_v1(
        request,
        dependencies=Service1ProductExecutionDependenciesV1(
            output_dir=output_dir,
            semantic_provider=build_service_1_deterministic_semantic_proposal_v1,
            semantic_owner_actor_id="owner-1",
            semantic_owner_actor_role="OWNER",
        ),
    )


def test_none_capability_owner_reentry_reaches_ready_without_context_mismatch(tmp_path: Path) -> None:
    ingestion_output = _ingestion_output()
    first = _run(
        WorkbookSemanticStartRequestV1(
            ingestion_output=ingestion_output,
            requested_capability=None,
        ),
        tmp_path,
    )

    assert first["status"] == STATUS_NEEDS_OWNER, first
    assert first["semantic_assistance_state"]["requested_capability"] is None
    responses = [
        {"decision_id": item["decision_id"], "action": "ACCEPT"}
        for item in first["owner_questions"]
    ]
    second = _run(
        WorkbookSemanticContinueRequestV1(
            ingestion_output=ingestion_output,
            requested_capability=None,
            semantic_assistance_state=first["semantic_assistance_state"],
            semantic_dialogue_responses=responses,
        ),
        tmp_path,
    )

    assert second["status"] == STATUS_READY, second
    assert second["blocked_reason"] != "ASSISTED_SEMANTIC_STATE_CONTEXT_MISMATCH"
    assert second["semantic_assistance_state"]["requested_capability"] is None

    legacy_state = dict(first["semantic_assistance_state"])
    legacy_state["requested_capability"] = ""
    legacy_second = _run(
        WorkbookSemanticContinueRequestV1(
            ingestion_output=ingestion_output,
            requested_capability=None,
            semantic_assistance_state=legacy_state,
            semantic_dialogue_responses=responses,
        ),
        tmp_path,
    )

    assert legacy_second["status"] == STATUS_READY, legacy_second
    assert legacy_second["semantic_assistance_state"]["requested_capability"] is None


def test_empty_capability_is_canonicalized_to_none_at_product_root(tmp_path: Path) -> None:
    ingestion_output = _ingestion_output()
    first = _run(
        WorkbookSemanticStartRequestV1(
            ingestion_output=ingestion_output,
            requested_capability="",
        ),
        tmp_path,
    )

    assert first["status"] == STATUS_NEEDS_OWNER, first
    assert first["semantic_assistance_state"]["requested_capability"] is None
