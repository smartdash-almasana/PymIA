from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


PrimaryCaseFileStatus = Literal["draft", "sealed", "superseded"]
AuthorizationStatus = Literal["owner_consents", "operator_assumes", "pending"]
PrimaryCaseFileSchemaVersion = Literal["1.0"]

_IMMUTABLE_WHEN_SEALED = {
    "pcf_id",
    "tenant_id",
    "case_id",
    "operator_id",
    "owner_ref",
    "business_ref",
    "period",
    "problem_statement",
    "scope",
    "authorization",
    "initial_evidence_refs",
    "schema_version",
    "created_at",
    "sealed_at",
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PrimaryCaseFileError(ValueError):
    """Raised when PrimaryCaseFile lifecycle invariants are violated."""


class PrimaryCasePeriod(BaseModel):
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def validate_period_order(self) -> "PrimaryCasePeriod":
        if self.end < self.start:
            raise ValueError("period.end must be greater than or equal to period.start")
        return self


class PrimaryCaseAuthorization(BaseModel):
    status: AuthorizationStatus


class PrimaryCaseFile(BaseModel):
    """Minimal sealed case boundary contract.

    PrimaryCaseFile is a pure contract artifact. It does not create case_id,
    attach evidence, persist state, run formulas, diagnose, render owner-facing
    output, or open a case lifecycle.
    """

    pcf_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    operator_id: str = Field(min_length=1)
    owner_ref: str = Field(min_length=1)
    business_ref: str = Field(min_length=1)
    period: PrimaryCasePeriod
    problem_statement: str = Field(min_length=1)
    scope: str = Field(min_length=1)
    authorization: PrimaryCaseAuthorization
    status: PrimaryCaseFileStatus = "draft"
    initial_evidence_refs: list[str] = Field(default_factory=list)
    schema_version: PrimaryCaseFileSchemaVersion = "1.0"
    created_at: datetime = Field(default_factory=_utcnow)
    sealed_at: datetime | None = None
    superseded_by: str | None = None

    @field_validator(
        "pcf_id",
        "tenant_id",
        "case_id",
        "operator_id",
        "owner_ref",
        "business_ref",
        "problem_statement",
        "scope",
        mode="before",
    )
    @classmethod
    def _strip_required_string(cls, value: Any) -> Any:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                raise ValueError("field must not be empty")
            return stripped
        return value

    @field_validator("initial_evidence_refs", mode="after")
    @classmethod
    def _validate_evidence_refs(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in value:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("initial_evidence_refs must contain non-empty strings")
            cleaned.append(item.strip())
        return cleaned

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "status", None) == "sealed" and name in _IMMUTABLE_WHEN_SEALED:
            raise TypeError("sealed PrimaryCaseFile is immutable")
        super().__setattr__(name, value)

    def seal(self, *, sealed_at: datetime | None = None) -> "PrimaryCaseFile":
        if self.status != "draft":
            raise PrimaryCaseFileError("only draft PrimaryCaseFile can be sealed")
        return self.model_copy(
            update={
                "status": "sealed",
                "sealed_at": sealed_at or _utcnow(),
            }
        )

    def is_sealed(self) -> bool:
        return self.status == "sealed"

    def supersede(self, new_pcf_id: str) -> "PrimaryCaseFile":
        if self.status != "sealed":
            raise PrimaryCaseFileError("only sealed PrimaryCaseFile can be superseded")
        if not isinstance(new_pcf_id, str) or not new_pcf_id.strip():
            raise PrimaryCaseFileError("new_pcf_id must be a non-empty string")
        return self.model_copy(
            update={
                "status": "superseded",
                "superseded_by": new_pcf_id.strip(),
            }
        )


__all__ = [
    "AuthorizationStatus",
    "PrimaryCaseAuthorization",
    "PrimaryCaseFile",
    "PrimaryCaseFileError",
    "PrimaryCaseFileSchemaVersion",
    "PrimaryCaseFileStatus",
    "PrimaryCasePeriod",
]
