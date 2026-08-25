from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Mapping

from pydantic import BaseModel

from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_canonical_ingestion_output_from_owner_confirmation_v1,
)
from pymia.smartpyme.service_1_product_pipeline_v1 import (
    STATUS_COMPUTATION_PLAN_READY,
    STATUS_READY,
    run_service_1_product_pipeline_v1,
)
from pymia.smartpyme.service_1_product_execution_contracts_v1 import (
    Service1ProductExecutionDependenciesV1,
    WorkbookSemanticContinueRequestV1,
    WorkbookSemanticStartRequestV1,
)
from pymia.smartpyme.service_1_deterministic_semantic_proposal_provider_v1 import (
    build_service_1_deterministic_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)


def _load_json_object(path: str | Path, *, label: str) -> dict[str, Any]:
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"{label} file not found: {resolved}")
    payload = json.loads(resolved.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object")
    return payload


def run_service_1_product_entrypoint_v1(
    *,
    xlsx_path: str | Path,
    owner_column_answers: dict[str, Any],
    semantic_owner_answers: dict[str, Any] | None,
    output_dir: str | Path,
    sheet_name: str | None = None,
    sheet_names: list[str] | tuple[str, ...] | None = None,
    include_all_sheets: bool = False,
    requested_capability: str | None = None,
    deliver_result: bool = False,
    semantic_owner_actor_id: str | None = None,
    semantic_owner_actor_role: str | None = None,
) -> dict[str, Any]:
    source = Path(xlsx_path)
    if not source.exists():
        raise FileNotFoundError(f"XLSX file not found: {source}")

    boundary = build_service_1_web_column_confirmation_intake_boundary_v1(
        local_xlsx_path=source,
        sheet_name=sheet_name,
        sheet_names=sheet_names,
        include_all_sheets=include_all_sheets,
    )
    if boundary.get("status") != "NEEDS_OWNER_CONFIRMATION":
        return {
            "schema_version": "SERVICE_1_PRODUCT_ENTRYPOINT_V1",
            "status": "BLOCKED",
            "blocked_reason": boundary.get("blocked_reason") or "CANONICAL_INTAKE_BLOCKED",
            "boundary": boundary,
            "connector": None,
            "product_pipeline": None,
        }

    if not owner_column_answers and boundary.get("owner_questions"):
        return {
            "schema_version": "SERVICE_1_PRODUCT_ENTRYPOINT_V1",
            "status": "NEEDS_OWNER_CONFIRMATION",
            "blocked_reason": None,
            "boundary": boundary,
            "connector": None,
            "product_pipeline": None,
        }

    connector = build_service_1_canonical_ingestion_output_from_owner_confirmation_v1(
        owner_question_packet=boundary,
        owner_answers=owner_column_answers,
    )
    if connector.get("status") != "INGESTION_OUTPUT_READY":
        return {
            "schema_version": "SERVICE_1_PRODUCT_ENTRYPOINT_V1",
            "status": "BLOCKED",
            "blocked_reason": connector.get("blocked_reason") or "CANONICAL_INGESTION_BLOCKED",
            "boundary": boundary,
            "connector": connector,
            "product_pipeline": None,
        }

    ingestion_output = connector["ingestion_output"]

    dependencies = Service1ProductExecutionDependenciesV1(
        output_dir=output_dir,
        semantic_provider=build_service_1_deterministic_semantic_proposal_v1,
        semantic_owner_actor_id=semantic_owner_actor_id,
        semantic_owner_actor_role=semantic_owner_actor_role,
    )
    if semantic_owner_answers is None:
        product = run_service_1_product_pipeline_v1(
            WorkbookSemanticStartRequestV1(
                ingestion_output=ingestion_output,
                requested_capability=requested_capability,
                deliver_result=deliver_result,
            ),
            dependencies=dependencies,
        )
    else:
        initial_product = run_service_1_product_pipeline_v1(
            WorkbookSemanticStartRequestV1(
                ingestion_output=ingestion_output,
                requested_capability=requested_capability,
                deliver_result=deliver_result,
            ),
            dependencies=dependencies,
        )
        if initial_product.get("status") != "NEEDS_OWNER_CONFIRMATION":
            product = initial_product
        else:
            semantic_state = initial_product.get("semantic_assistance_state")
            if not isinstance(semantic_state, dict):
                product = {
                    "status": "BLOCKED",
                    "blocked_reason": "SEMANTIC_ASSISTANCE_STATE_REQUIRED",
                }
            else:
                request = WorkbookSemanticContinueRequestV1(
                    ingestion_output=ingestion_output,
                    requested_capability=requested_capability,
                    semantic_assistance_state=semantic_state,
                    semantic_dialogue_responses=_semantic_dialogue_responses(
                        initial_product.get("owner_questions") or (),
                        semantic_owner_answers,
                    ),
                    deliver_result=deliver_result,
                )
                product = run_service_1_product_pipeline_v1(
                    request,
                    dependencies=dependencies,
                )
    return {
        "schema_version": "SERVICE_1_PRODUCT_ENTRYPOINT_V1",
        "status": product.get("status"),
        "blocked_reason": product.get("blocked_reason"),
        "boundary": boundary,
        "connector": connector,
        "product_pipeline": product,
    }


def _semantic_dialogue_responses(
    questions: Any,
    owner_answers: Mapping[str, Any],
) -> tuple[dict[str, Any], ...]:
    """Translate explicit CLI owner answers into SEM-8 dialogue commands."""
    if not isinstance(owner_answers, Mapping):
        return ()
    responses: list[dict[str, Any]] = []
    for question in questions if isinstance(questions, (list, tuple)) else ():
        if not isinstance(question, Mapping):
            continue
        answer = None
        found = False
        for key in (
            question.get("decision_id"),
            question.get("question_id"),
            question.get("field_id"),
            question.get("column_name"),
        ):
            if key is not None and str(key).strip() in owner_answers:
                answer = owner_answers[str(key).strip()]
                found = True
                break
        if not found:
            continue
        option_id = ""
        correction_text = None
        action = "ACCEPT"
        if isinstance(answer, Mapping):
            option_id = str(answer.get("option_id") or "").strip()
            correction_text = answer.get("correction_text") or answer.get("free_text")
            action = str(answer.get("action") or "").strip().upper() or action
        else:
            option_id = str(answer or "").strip()
        if option_id.upper() in {"IGNORE", "IGNORED_NOT_RELEVANT", "SKIP"}:
            action = "SKIP"
        response = {
            "decision_id": str(question.get("decision_id") or "").strip(),
            "action": action,
        }
        if option_id:
            response["option_id"] = option_id
        if correction_text is not None:
            response["correction_text"] = str(correction_text)
        responses.append(response)
    return tuple(responses)


def _json_default(value: Any) -> Any:
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return to_dict()
    if isinstance(value, BaseModel):
        model_dump = getattr(value, "model_dump", None)
        if callable(model_dump):
            return model_dump(mode="json")
        return value.dict()
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Canonical Service 1 product CLI")
    parser.add_argument("--xlsx", required=True)
    parser.add_argument("--owner-column-answers", required=True)
    parser.add_argument("--semantic-owner-answers", default=None)
    parser.add_argument("--semantic-owner-actor-id", default=None)
    parser.add_argument("--semantic-owner-actor-role", default=None)
    parser.add_argument("--requested-capability", default=None)
    parser.add_argument(
        "--deliver-result",
        action="store_true",
        help="Generate the bounded XLSX result for a supported requested capability.",
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--sheet-name",
        action="append",
        default=None,
        help="Worksheet to ingest; repeat to select multiple sheets.",
    )
    parser.add_argument(
        "--all-sheets",
        action="store_true",
        help="Ingest every non-empty worksheet in workbook order.",
    )
    parser.add_argument("--result-json", default=None)
    args = parser.parse_args(argv)

    try:
        owner_column_answers = _load_json_object(
            args.owner_column_answers, label="owner column answers"
        )
        semantic_owner_answers = (
            _load_json_object(args.semantic_owner_answers, label="semantic owner answers")
            if args.semantic_owner_answers
            else None
        )
        if not args.requested_capability:
            raise ValueError("--requested-capability is required")
        if args.deliver_result and not args.requested_capability:
            raise ValueError("--deliver-result requires --requested-capability")
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        selected_sheet_names = tuple(args.sheet_name or ())
        selected_sheet_name = selected_sheet_names[0] if len(selected_sheet_names) == 1 else None
        result = run_service_1_product_entrypoint_v1(
            xlsx_path=args.xlsx,
            owner_column_answers=owner_column_answers,
            semantic_owner_answers=semantic_owner_answers,
            output_dir=output_dir,
            sheet_name=selected_sheet_name,
            sheet_names=selected_sheet_names if len(selected_sheet_names) > 1 else None,
            include_all_sheets=bool(args.all_sheets),
            requested_capability=args.requested_capability,
            deliver_result=bool(args.deliver_result),
            semantic_owner_actor_id=args.semantic_owner_actor_id,
            semantic_owner_actor_role=args.semantic_owner_actor_role,
        )
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCKED", "blocked_reason": str(exc)}, ensure_ascii=False))
        return 2

    payload = json.dumps(result, ensure_ascii=False, indent=2, default=_json_default)
    if args.result_json:
        target = Path(args.result_json)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0 if result.get("status") in {STATUS_READY, STATUS_COMPUTATION_PLAN_READY} else 2


if __name__ == "__main__":
    raise SystemExit(main())
