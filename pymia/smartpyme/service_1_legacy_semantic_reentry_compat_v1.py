"""Explicit legacy semantic-reentry compatibility boundary for Servicio 1.

This module preserves the historical owner_answers contract for non-SEM8 callers
without making it part of the canonical product-root authority. It owns no
semantic rules, no P8 authority, no execution and no delivery.
"""
from __future__ import annotations

from typing import Any

from pymia.smartpyme.service_1_deterministic_semantic_pipeline_v1 import (
    STATUS_OWNER_QUESTIONS,
    run_initial_pass,
    run_owner_reentry,
)


def resolve_service_1_legacy_semantic_run_v1(
    *,
    ingestion_output: Any,
    sheet_name: str,
    owner_answers: Any = None,
) -> dict[str, Any]:
    """Resolve the historical semantic flow outside canonical product authority."""
    semantic_run = run_initial_pass(
        ingestion_output=ingestion_output,
        sheet_name=sheet_name,
    )
    if semantic_run.get("status") != STATUS_OWNER_QUESTIONS:
        return semantic_run
    if not isinstance(owner_answers, dict) or not owner_answers:
        return semantic_run
    return run_owner_reentry(
        previous_run=semantic_run,
        owner_answers=owner_answers,
    )


def run_service_1_product_pipeline_with_legacy_owner_answers_v1(
    *,
    ingestion_output: Any,
    tool_requests: Any,
    output_dir: Any,
    sheet_name: str = "sheet1",
    owner_answers: Any = None,
    **product_kwargs: Any,
) -> dict[str, Any]:
    """Compatibility entrypoint for historical callers; canonical root stays reentry-free."""
    from pymia.smartpyme.service_1_product_pipeline_v1 import run_service_1_product_pipeline_v1

    semantic_run_override = resolve_service_1_legacy_semantic_run_v1(
        ingestion_output=ingestion_output,
        sheet_name=sheet_name,
        owner_answers=owner_answers,
    )
    return run_service_1_product_pipeline_v1(
        ingestion_output=ingestion_output,
        tool_requests=tool_requests,
        output_dir=output_dir,
        sheet_name=sheet_name,
        semantic_run_override=semantic_run_override,
        **product_kwargs,
    )


__all__ = [
    "resolve_service_1_legacy_semantic_run_v1",
    "run_service_1_product_pipeline_with_legacy_owner_answers_v1",
]
