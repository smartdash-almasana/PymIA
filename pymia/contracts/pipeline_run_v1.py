from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


PipelineRunStatus = Literal["COMPLETED", "BLOCKED", "FAILED"]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class PipelineRunRecord(BaseModel):
    run_id: str = Field(default_factory=lambda: f"run_{uuid.uuid4().hex}")
    tenant_id: str
    intake_id: str
    pipeline_name: str
    pipeline_version: str
    pipeline_module: str
    entrypoint: str
    service_name: str
    started_at: str = Field(default_factory=utc_now_iso)
    completed_at: str | None = None
    input_hash: str
    evidence_ids: list[str] = Field(default_factory=list)
    steps_executed: list[str] = Field(default_factory=list)
    output_artifact_id: str | None = None
    output_hash: str | None = None
    status: PipelineRunStatus
    error_code: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


def build_pipeline_run_record(
    *,
    tenant_id: str,
    intake_id: str,
    message: str,
    evidence_ids: list[str],
    status: PipelineRunStatus,
    output_payload: dict[str, Any],
    steps_executed: list[str],
) -> PipelineRunRecord:
    return PipelineRunRecord(
        tenant_id=tenant_id,
        intake_id=intake_id,
        pipeline_name="vertical_pipeline_evidence_spine",
        pipeline_version="v1",
        pipeline_module="pymia.application.vertical_pipeline",
        entrypoint="build_pipeline",
        service_name="vertical_pipeline",
        completed_at=utc_now_iso(),
        input_hash=hashlib.sha256(message.encode("utf-8")).hexdigest(),
        evidence_ids=evidence_ids,
        steps_executed=steps_executed,
        output_artifact_id="owner_facing_markdown",
        output_hash=canonical_hash(output_payload),
        status=status,
        metadata={"case_id_alias": intake_id, "channel": "cli"},
    )


__all__ = ["PipelineRunRecord", "PipelineRunStatus", "build_pipeline_run_record", "canonical_hash"]
