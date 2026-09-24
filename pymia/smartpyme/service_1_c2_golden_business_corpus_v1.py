"""Servicio 1 — F11 Golden Business Corpus evaluator.

Validates the non-normative multi-business C2 corpus against real physical XLSX
through the canonical intake/profile/context chain. It does not call an LLM,
reparse XLSX outside canonical intake, calculate business results, or grant any
authority. Expected V2 coordinates are checked only against the governed V2
taxonomy; they remain Golden evidence, not runtime truth.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final

from pymia.smartpyme.service_1_owner_confirmation_to_canonical_ingestion_output_v1 import (
    build_service_1_unconfirmed_canonical_ingestion_output_v1,
)
from pymia.smartpyme.service_1_semantic_coordinate_model_v2 import (
    AXES,
    load_service_1_semantic_coordinate_taxonomy_v2,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1,
)
from pymia.smartpyme.service_1_workbook_profiler_v1 import build_service_1_workbook_profile_v1
from pymia.smartpyme.service_1_workbook_semantic_context_v1 import (
    STATUS_READY as WORKBOOK_CONTEXT_READY,
    build_service_1_workbook_semantic_context_v1,
)

SCHEMA_VERSION: Final[str] = "SERVICE_1_C2_GOLDEN_BUSINESS_CORPUS_F11_EVALUATION_V1"
STATUS_READY: Final[str] = "GOLDEN_BUSINESS_CORPUS_READY"
STATUS_BLOCKED: Final[str] = "BLOCKED"
AUTHORITY: Final[str] = "EVIDENCE_ONLY"


def default_service_1_c2_golden_business_corpus_path_v1() -> Path:
    return Path(__file__).resolve().parents[2] / "docs" / "current" / "SERVICE_1_C2_GOLDEN_BUSINESS_CORPUS_F11_V1.json"


def evaluate_service_1_c2_golden_business_corpus_v1(
    *,
    corpus_path: str | Path | None = None,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    path = Path(corpus_path) if corpus_path is not None else default_service_1_c2_golden_business_corpus_path_v1()
    try:
        corpus = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return _blocked("CORPUS_UNREADABLE", detail=type(exc).__name__)
    if not isinstance(corpus, Mapping) or corpus.get("schema_version") != "SERVICE_1_C2_GOLDEN_BUSINESS_CORPUS_F11_V1":
        return _blocked("CORPUS_SCHEMA_INVALID")
    if corpus.get("authority") != AUTHORITY:
        return _blocked("CORPUS_AUTHORITY_INVALID")
    cases = corpus.get("cases")
    if not isinstance(cases, list) or len(cases) < 5:
        return _blocked("CORPUS_CASES_INSUFFICIENT")

    taxonomy = load_service_1_semantic_coordinate_taxonomy_v2()
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[2]
    results: list[dict[str, Any]] = []
    safe_unknown_count = 0

    for raw_case in cases:
        if not isinstance(raw_case, Mapping):
            return _blocked("CORPUS_CASE_INVALID")
        case_id = str(raw_case.get("case_id") or "").strip()
        workbook_rel = str(raw_case.get("workbook") or "").strip()
        sheet_name = str(raw_case.get("sheet") or "").strip()
        if not case_id or not workbook_rel or not sheet_name:
            return _blocked("CORPUS_CASE_IDENTITY_INVALID", detail=case_id or None)
        workbook_path = root / workbook_rel
        if not workbook_path.is_file():
            return _blocked("CORPUS_WORKBOOK_MISSING", detail=workbook_rel)

        intake = build_service_1_web_column_confirmation_intake_boundary_v1(
            uploaded_xlsx_bytes=workbook_path.read_bytes(),
            uploaded_filename=workbook_path.name,
            sheet_name=sheet_name,
        )
        if intake.get("status") == "BLOCKED":
            return _blocked("CANONICAL_INTAKE_BLOCKED", detail={"case_id": case_id, "reason": intake.get("blocked_reason")})
        canonical = build_service_1_unconfirmed_canonical_ingestion_output_v1(owner_question_packet=intake)
        if canonical.get("status") == "BLOCKED":
            return _blocked("CANONICAL_INGESTION_BLOCKED", detail={"case_id": case_id, "reason": canonical.get("blocked_reason")})
        profile = build_service_1_workbook_profile_v1(ingestion_output=canonical["ingestion_output"])
        if profile.get("status") == "BLOCKED":
            return _blocked("WORKBOOK_PROFILE_BLOCKED", detail={"case_id": case_id, "reason": profile.get("blocked_reason")})
        context = build_service_1_workbook_semantic_context_v1(workbook_profile=profile)
        if context.get("status") != WORKBOOK_CONTEXT_READY:
            return _blocked("WORKBOOK_CONTEXT_BLOCKED", detail={"case_id": case_id, "reason": context.get("blocked_reason")})

        tables = {str(item.get("sheet_name") or ""): item for item in context.get("tables") or [] if isinstance(item, Mapping)}
        table = tables.get(sheet_name)
        if not isinstance(table, Mapping):
            return _blocked("GOLDEN_SHEET_NOT_IN_CONTEXT", detail={"case_id": case_id, "sheet": sheet_name})
        physical_columns = {str(item.get("column_name") or "").strip() for item in table.get("columns") or [] if isinstance(item, Mapping)}

        expected_columns = raw_case.get("expected_columns") or {}
        if not isinstance(expected_columns, Mapping):
            return _blocked("EXPECTED_COLUMNS_INVALID", detail=case_id)
        for column_name, coordinates in expected_columns.items():
            if str(column_name) not in physical_columns:
                return _blocked("GOLDEN_COLUMN_MISSING", detail={"case_id": case_id, "column": column_name})
            if not isinstance(coordinates, Mapping) or not coordinates:
                return _blocked("GOLDEN_COORDINATES_INVALID", detail={"case_id": case_id, "column": column_name})
            for axis, value in coordinates.items():
                if axis not in AXES or str(value) not in taxonomy.allowed(str(axis)):
                    return _blocked("GOLDEN_COORDINATE_OUTSIDE_TAXONOMY", detail={"case_id": case_id, "column": column_name, "axis": axis, "value": value})

        safe_unknowns = [str(item) for item in (raw_case.get("safe_unknown_columns") or []) if str(item).strip()]
        if any(column not in physical_columns for column in safe_unknowns):
            return _blocked("SAFE_UNKNOWN_COLUMN_MISSING", detail=case_id)
        safe_unknown_count += len(safe_unknowns)
        results.append({
            "case_id": case_id,
            "sheet": sheet_name,
            "physical_column_count": len(physical_columns),
            "golden_coordinate_columns": len(expected_columns),
            "safe_unknown_columns": safe_unknowns,
            "canonical_context_ready": True,
        })

    invariants = corpus.get("global_invariants") or {}
    if not isinstance(invariants, Mapping) or any(invariants.get(flag) is not False for flag in (
        "runtime_authorized", "tool_execution_authorized", "product_ready", "delivery_authorized", "automatic_reuse_authorized"
    )):
        return _blocked("CORPUS_SAFETY_INVARIANTS_INVALID")

    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_READY,
        "blocked_reason": None,
        "authority": AUTHORITY,
        "case_count": len(results),
        "golden_coordinate_column_count": sum(item["golden_coordinate_columns"] for item in results),
        "safe_unknown_column_count": safe_unknown_count,
        "cases": results,
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "automatic_reuse_authorized": False,
    }


def _blocked(reason: str, *, detail: Any = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "blocked_reason": reason,
        "detail": detail,
        "authority": AUTHORITY,
        "case_count": 0,
        "golden_coordinate_column_count": 0,
        "safe_unknown_column_count": 0,
        "cases": [],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "automatic_reuse_authorized": False,
    }


__all__ = [
    "AUTHORITY", "SCHEMA_VERSION", "STATUS_BLOCKED", "STATUS_READY",
    "default_service_1_c2_golden_business_corpus_path_v1",
    "evaluate_service_1_c2_golden_business_corpus_v1",
]
