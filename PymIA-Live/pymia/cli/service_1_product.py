from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_canonical_ingestion_output_from_owner_confirmation_v1,
)
from pymia.smartpyme.service_1_product_pipeline_v1 import (
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
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object")
    return payload


def _load_tool_requests(path: str | Path) -> list[dict[str, Any]]:
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"tool requests file not found: {resolved}")
    payload = json.loads(resolved.read_text(encoding="utf-8"))
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
    sheet_name: str = "sheet1",
) -> dict[str, Any]:
    source = Path(xlsx_path)
    if not source.exists():
        raise FileNotFoundError(f"XLSX file not found: {source}")

    boundary = build_service_1_web_column_confirmation_intake_boundary_v1(
        local_xlsx_path=source,
    )
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

    product = run_service_1_product_pipeline_v1(
        ingestion_output=connector["ingestion_output"],
        tool_requests=tool_requests,
        output_dir=output_dir,
        sheet_name=sheet_name,
        owner_answers=semantic_owner_answers,
    )
    return {
        "schema_version": "SERVICE_1_PRODUCT_ENTRYPOINT_V1",
        "status": product.get("status"),
        "blocked_reason": product.get("blocked_reason"),
        "boundary": boundary,
        "connector": connector,
        "product_pipeline": product,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Canonical Service 1 product CLI")
    parser.add_argument("--xlsx", required=True)
    parser.add_argument("--owner-column-answers", required=True)
    parser.add_argument("--semantic-owner-answers", default=None)
    parser.add_argument("--tool-requests", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--sheet-name", default="sheet1")
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
        tool_requests = _load_tool_requests(args.tool_requests)
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        result = run_service_1_product_entrypoint_v1(
            xlsx_path=args.xlsx,
            owner_column_answers=owner_column_answers,
            semantic_owner_answers=semantic_owner_answers,
            tool_requests=tool_requests,
            output_dir=output_dir,
            sheet_name=args.sheet_name,
        )
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCKED", "blocked_reason": str(exc)}, ensure_ascii=False))
        return 2

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.result_json:
        target = Path(args.result_json)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0 if result.get("status") == STATUS_READY else 2


if __name__ == "__main__":
    raise SystemExit(main())
