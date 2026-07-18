from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_canonical_ingestion_output_from_owner_confirmation_v1,
)
from pymia.smartpyme.service_1_product_pipeline_v1 import (
    STATUS_COMPUTATION_PLAN_READY,
    STATUS_READY,
    run_service_1_product_pipeline_v1,
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


def _load_tool_requests(path: str | Path) -> list[dict[str, Any]]:
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"tool requests file not found: {resolved}")
    payload = json.loads(resolved.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("tool requests must be a non-empty JSON list")
    return payload


def run_service_1_product_entrypoint_v1(
    *,
    xlsx_path: str | Path,
    owner_column_answers: dict[str, Any],
    semantic_owner_answers: dict[str, Any] | None,
    tool_requests: list[dict[str, Any]],
    output_dir: str | Path,
    sheet_name: str | None = None,
    sheet_names: list[str] | tuple[str, ...] | None = None,
    include_all_sheets: bool = False,
    requested_capability: str | None = None,
    deliver_result: bool = False,
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

    ingestion_output = dict(connector["ingestion_output"])
    normalized_tables = boundary.get("normalized_tables")
    if isinstance(normalized_tables, list):
        ingestion_output["normalized_tables"] = normalized_tables

    product = run_service_1_product_pipeline_v1(
        ingestion_output=ingestion_output,
        tool_requests=tool_requests,
        output_dir=output_dir,
        sheet_name=sheet_name or "sheet1",
        owner_answers=semantic_owner_answers,
        requested_capability=requested_capability,
        deliver_result=deliver_result,
    )
    return {
        "schema_version": "SERVICE_1_PRODUCT_ENTRYPOINT_V1",
        "status": product.get("status"),
        "blocked_reason": product.get("blocked_reason"),
        "boundary": boundary,
        "connector": connector,
        "product_pipeline": product,
    }


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
    parser.add_argument("--tool-requests", default=None)
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
        if bool(args.tool_requests) == bool(args.requested_capability):
            raise ValueError("provide exactly one of --tool-requests or --requested-capability")
        if args.deliver_result and not args.requested_capability:
            raise ValueError("--deliver-result requires --requested-capability")
        tool_requests = _load_tool_requests(args.tool_requests) if args.tool_requests else []
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        selected_sheet_names = tuple(args.sheet_name or ())
        selected_sheet_name = selected_sheet_names[0] if len(selected_sheet_names) == 1 else None
        result = run_service_1_product_entrypoint_v1(
            xlsx_path=args.xlsx,
            owner_column_answers=owner_column_answers,
            semantic_owner_answers=semantic_owner_answers,
            tool_requests=tool_requests,
            output_dir=output_dir,
            sheet_name=selected_sheet_name,
            sheet_names=selected_sheet_names if len(selected_sheet_names) > 1 else None,
            include_all_sheets=bool(args.all_sheets),
            requested_capability=args.requested_capability,
            deliver_result=bool(args.deliver_result),
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
