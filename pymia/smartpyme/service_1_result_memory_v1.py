"""F13 tenant-scoped longitudinal memory for governed Service 1 ResultSets.

This module persists no data by itself. It defines the immutable snapshot that a
persistence adapter may append after F9. It never recalculates, reinterprets,
or upgrades an analytical result and it grants no runtime authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
import hashlib
import json
from types import MappingProxyType
from typing import Any, Final, Mapping

from pymia.contracts.formula_contract import SUPPORTED_FORMULAS
from pymia.smartpyme.service_1_analysis_math_execution_v1 import SCHEMA_VERSION as F8_SCHEMA_VERSION
from pymia.smartpyme.service_1_analysis_result_projection_v1 import (
    INTEGRITY_SCOPE_RESULT_SET,
    Service1AnalysisResultProjectionV1,
)
from pymia.smartpyme.service_1_computability_v1 import Service1GovernedAnalysisInputV1
from pymia.smartpyme.service_1_tenant_identity_contract_v1 import Service1TenantIdentityContractV1

SCHEMA_VERSION: Final[str] = "SERVICE_1_RESULT_MEMORY_RECORD_V1"
PERIOD_SCHEMA_VERSION: Final[str] = "SERVICE_1_RESULT_MEMORY_PERIOD_V1"
ARTIFACT_KIND: Final[str] = "GOVERNED_RESULT_SET"
MATH_RUNTIME_VERSION_KEY: Final[str] = "__analysis_math_runtime__"

_AUTHORITY_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
    "analysis_execution_authorized",
    "automatic_reuse_authorized",
)


class Service1ResultMemoryErrorV1(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _blocked(code: str, detail: str) -> Service1ResultMemoryErrorV1:
    return Service1ResultMemoryErrorV1(code, detail)


def _required(value: object, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise _blocked("RESULT_MEMORY_INVALID", f"{field_name} is required")
    return text


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _freeze_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze_json(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(item) for item in value)
    return value


def _thaw_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


def _date(value: str, field_name: str) -> str:
    text = _required(value, field_name)
    try:
        parsed = date.fromisoformat(text)
    except ValueError as exc:
        raise _blocked("RESULT_MEMORY_INVALID_PERIOD", f"{field_name} must be YYYY-MM-DD") from exc
    return parsed.isoformat()


def _executed_at(value: str | None) -> str:
    raw = value or datetime.now(timezone.utc).isoformat()
    try:
        parsed = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError as exc:
        raise _blocked("RESULT_MEMORY_INVALID_EXECUTED_AT", "executed_at must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise _blocked("RESULT_MEMORY_INVALID_EXECUTED_AT", "executed_at must be timezone-aware")
    return parsed.astimezone(timezone.utc).isoformat()


def _result_set_canonical_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    required = (
        "schema_version",
        "case_id",
        "analysis_id",
        "analysis_kind",
        "grain",
        "groups",
        "source_sheet_refs",
        "relationship_refs",
        "applied_filters",
        "provenance",
    )
    if any(key not in payload for key in required):
        raise _blocked("RESULT_MEMORY_INVALID_RESULT_SET", "result_set payload is incomplete")
    return {key: _thaw_json(payload[key]) for key in required}


def _verify_result_set_integrity(payload: Mapping[str, Any], expected_digest: str) -> None:
    integrity = payload.get("integrity")
    if not isinstance(integrity, Mapping):
        raise _blocked("RESULT_MEMORY_INVALID_RESULT_SET", "result_set integrity is required")
    digest = str(integrity.get("digest") or "").strip()
    scope = str(integrity.get("scope") or "").strip()
    if scope != INTEGRITY_SCOPE_RESULT_SET or digest != expected_digest:
        raise _blocked("RESULT_MEMORY_RESULT_SET_DRIFT", "result_set integrity identity does not match")
    if _sha256(_result_set_canonical_payload(payload)) != expected_digest:
        raise _blocked("RESULT_MEMORY_RESULT_SET_DRIFT", "result_set canonical payload digest does not match")


@dataclass(frozen=True)
class Service1ResultMemoryPeriodV1:
    period_ref: str
    start_date: str
    end_date: str
    basis_ref: str
    source_refs: tuple[str, ...]
    schema_version: str = PERIOD_SCHEMA_VERSION

    def __post_init__(self) -> None:
        start = _date(self.start_date, "start_date")
        end = _date(self.end_date, "end_date")
        if start > end:
            raise _blocked("RESULT_MEMORY_INVALID_PERIOD", "start_date cannot be after end_date")
        object.__setattr__(self, "start_date", start)
        object.__setattr__(self, "end_date", end)
        object.__setattr__(self, "period_ref", _required(self.period_ref, "period_ref"))
        object.__setattr__(self, "basis_ref", _required(self.basis_ref, "basis_ref"))
        refs = tuple(dict.fromkeys(_required(value, "period source_ref") for value in self.source_refs))
        if not refs:
            raise _blocked("RESULT_MEMORY_INVALID_PERIOD", "period source_refs are required")
        object.__setattr__(self, "source_refs", refs)
        if self.schema_version != PERIOD_SCHEMA_VERSION:
            raise _blocked("RESULT_MEMORY_INVALID_PERIOD", "invalid period schema version")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "period_ref": self.period_ref,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "basis_ref": self.basis_ref,
            "source_refs": list(self.source_refs),
        }


@dataclass(frozen=True)
class Service1ResultMemoryRecordV1:
    memory_record_id: str
    identity_contract_id: str
    tenant_id: str
    cliente_id: str | None
    case_id: str
    analysis_id: str
    period: Service1ResultMemoryPeriodV1
    grain: Mapping[str, Any]
    formula_versions: Mapping[str, str]
    result_set: Mapping[str, Any]
    result_set_integrity_digest: str
    evidence_refs: tuple[str, ...]
    owner_evidence_refs: tuple[str, ...]
    executed_at: str
    artifact_ref: str
    artifact: Mapping[str, Any]
    provenance: Mapping[str, Any] = field(default_factory=lambda: {"source": "F13_GOVERNED_RESULT_MEMORY"})
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in (
            "memory_record_id",
            "identity_contract_id",
            "tenant_id",
            "case_id",
            "analysis_id",
            "result_set_integrity_digest",
            "artifact_ref",
        ):
            object.__setattr__(self, name, _required(getattr(self, name), name))
        if self.cliente_id is not None:
            object.__setattr__(self, "cliente_id", _required(self.cliente_id, "cliente_id"))
        if not isinstance(self.period, Service1ResultMemoryPeriodV1):
            raise _blocked("RESULT_MEMORY_INVALID", "period must be Service1ResultMemoryPeriodV1")
        if not isinstance(self.grain, Mapping) or not self.grain:
            raise _blocked("RESULT_MEMORY_INVALID", "grain is required")
        if not isinstance(self.formula_versions, Mapping) or not self.formula_versions:
            raise _blocked("RESULT_MEMORY_INVALID", "formula_versions are required")
        formula_versions = {
            _required(key, "formula version key"): _required(value, "formula version")
            for key, value in self.formula_versions.items()
        }
        if MATH_RUNTIME_VERSION_KEY not in formula_versions:
            raise _blocked("RESULT_MEMORY_INVALID", "math runtime version is required")
        object.__setattr__(self, "formula_versions", MappingProxyType(formula_versions))
        if not isinstance(self.result_set, Mapping):
            raise _blocked("RESULT_MEMORY_INVALID_RESULT_SET", "result_set must be a mapping")
        result_set_payload = _thaw_json(self.result_set)
        _verify_result_set_integrity(result_set_payload, self.result_set_integrity_digest)
        if str(result_set_payload.get("case_id") or "") != self.case_id:
            raise _blocked("RESULT_MEMORY_IDENTITY_DRIFT", "result_set case_id mismatch")
        if str(result_set_payload.get("analysis_id") or "") != self.analysis_id:
            raise _blocked("RESULT_MEMORY_IDENTITY_DRIFT", "result_set analysis_id mismatch")
        if _thaw_json(result_set_payload.get("grain")) != _thaw_json(self.grain):
            raise _blocked("RESULT_MEMORY_GRAIN_DRIFT", "result_set grain mismatch")
        object.__setattr__(self, "result_set", _freeze_json(result_set_payload))
        object.__setattr__(self, "grain", _freeze_json(dict(self.grain)))
        evidence_refs = tuple(dict.fromkeys(_required(value, "evidence_ref") for value in self.evidence_refs))
        owner_refs = tuple(dict.fromkeys(_required(value, "owner_evidence_ref") for value in self.owner_evidence_refs))
        if not evidence_refs:
            raise _blocked("RESULT_MEMORY_INVALID", "evidence_refs are required")
        if not owner_refs:
            raise _blocked("RESULT_MEMORY_INVALID", "owner_evidence_refs are required")
        object.__setattr__(self, "evidence_refs", evidence_refs)
        object.__setattr__(self, "owner_evidence_refs", owner_refs)
        object.__setattr__(self, "executed_at", _executed_at(self.executed_at))
        if self.artifact_ref != f"resultset:sha256:{self.result_set_integrity_digest}":
            raise _blocked("RESULT_MEMORY_ARTIFACT_DRIFT", "artifact_ref must identify the F9 ResultSet digest")
        if not isinstance(self.artifact, Mapping):
            raise _blocked("RESULT_MEMORY_INVALID", "artifact must be a mapping")
        artifact = dict(self.artifact)
        if (
            artifact.get("kind") != ARTIFACT_KIND
            or artifact.get("ref") != self.artifact_ref
            or artifact.get("integrity_digest") != self.result_set_integrity_digest
        ):
            raise _blocked("RESULT_MEMORY_ARTIFACT_DRIFT", "artifact identity mismatch")
        object.__setattr__(self, "artifact", _freeze_json(artifact))
        if not isinstance(self.provenance, Mapping) or dict(self.provenance) != {"source": "F13_GOVERNED_RESULT_MEMORY"}:
            raise _blocked("RESULT_MEMORY_INVALID", "provenance must use the closed F13 projection")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))
        if self.schema_version != SCHEMA_VERSION:
            raise _blocked("RESULT_MEMORY_INVALID", "invalid result memory schema version")
        if self.memory_record_id != _memory_record_id(self):
            raise _blocked("RESULT_MEMORY_IDENTITY_DRIFT", "memory_record_id does not match canonical snapshot identity")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "memory_record_id": self.memory_record_id,
            "identity_contract_id": self.identity_contract_id,
            "tenant_id": self.tenant_id,
            "cliente_id": self.cliente_id,
            "case_id": self.case_id,
            "analysis_id": self.analysis_id,
            "period": self.period.to_dict(),
            "grain": _thaw_json(self.grain),
            "formula_versions": dict(self.formula_versions),
            "result_set": _thaw_json(self.result_set),
            "result_set_integrity_digest": self.result_set_integrity_digest,
            "evidence_refs": list(self.evidence_refs),
            "owner_evidence_refs": list(self.owner_evidence_refs),
            "executed_at": self.executed_at,
            "artifact_ref": self.artifact_ref,
            "artifact": _thaw_json(self.artifact),
            "provenance": dict(self.provenance),
            **{flag: False for flag in _AUTHORITY_FLAGS},
        }


def _memory_identity_payload_values(
    *,
    identity_contract_id: str,
    tenant_id: str,
    cliente_id: str | None,
    case_id: str,
    analysis_id: str,
    period: Service1ResultMemoryPeriodV1,
    grain: Mapping[str, Any],
    formula_versions: Mapping[str, str],
    result_set_integrity_digest: str,
    evidence_refs: tuple[str, ...] | list[str],
    owner_evidence_refs: tuple[str, ...] | list[str],
    artifact_ref: str,
) -> dict[str, Any]:
    return {
        "identity_contract_id": identity_contract_id,
        "tenant_id": tenant_id,
        "cliente_id": cliente_id,
        "case_id": case_id,
        "analysis_id": analysis_id,
        "period": period.to_dict(),
        "grain": _thaw_json(grain),
        "formula_versions": dict(formula_versions),
        "result_set_integrity_digest": result_set_integrity_digest,
        "evidence_refs": list(evidence_refs),
        "owner_evidence_refs": list(owner_evidence_refs),
        "artifact_ref": artifact_ref,
    }


def _memory_identity_payload(record: Service1ResultMemoryRecordV1) -> dict[str, Any]:
    return _memory_identity_payload_values(
        identity_contract_id=record.identity_contract_id,
        tenant_id=record.tenant_id,
        cliente_id=record.cliente_id,
        case_id=record.case_id,
        analysis_id=record.analysis_id,
        period=record.period,
        grain=record.grain,
        formula_versions=record.formula_versions,
        result_set_integrity_digest=record.result_set_integrity_digest,
        evidence_refs=record.evidence_refs,
        owner_evidence_refs=record.owner_evidence_refs,
        artifact_ref=record.artifact_ref,
    )


def _memory_record_id(record: Service1ResultMemoryRecordV1) -> str:
    return f"s1rm_{_sha256(_memory_identity_payload(record))}"


def _formula_versions(result_projection: Service1AnalysisResultProjectionV1) -> dict[str, str]:
    refs: list[str] = []
    for group in result_projection.result_set.groups:
        for measure in group.measures.values():
            if measure.formula_ref and measure.formula_ref not in refs:
                refs.append(measure.formula_ref)
    versions = {MATH_RUNTIME_VERSION_KEY: F8_SCHEMA_VERSION}
    for ref in refs:
        definition = SUPPORTED_FORMULAS.get(ref)
        if definition is None:
            raise _blocked("RESULT_MEMORY_FORMULA_VERSION_MISSING", f"formula version not governed: {ref}")
        versions[ref] = definition.formula_version
    return versions


def _compact_evidence_refs(result_projection: Service1AnalysisResultProjectionV1) -> tuple[str, ...]:
    refs: list[str] = []
    for group in result_projection.result_set.groups:
        for measure in group.measures.values():
            for raw in measure.source_refs:
                compact = str(raw).split("@", 1)[0].strip()
                if compact and compact not in refs:
                    refs.append(compact)
    for ref in result_projection.result_set.relationship_refs:
        if ref not in refs:
            refs.append(ref)
    return tuple(refs)


def build_service_1_result_memory_record_v1(
    *,
    identity_contract: Service1TenantIdentityContractV1,
    governed_analysis_input: Service1GovernedAnalysisInputV1,
    result_projection: Service1AnalysisResultProjectionV1,
    period: Service1ResultMemoryPeriodV1,
    owner_evidence_refs: tuple[str, ...] | list[str],
    executed_at: str | None = None,
) -> Service1ResultMemoryRecordV1:
    if not isinstance(identity_contract, Service1TenantIdentityContractV1):
        raise TypeError("identity_contract must be Service1TenantIdentityContractV1")
    if not isinstance(governed_analysis_input, Service1GovernedAnalysisInputV1):
        raise TypeError("governed_analysis_input must be Service1GovernedAnalysisInputV1")
    if not isinstance(result_projection, Service1AnalysisResultProjectionV1):
        raise TypeError("result_projection must be Service1AnalysisResultProjectionV1")
    if not isinstance(period, Service1ResultMemoryPeriodV1):
        raise TypeError("period must be Service1ResultMemoryPeriodV1")
    result_set = result_projection.result_set
    if identity_contract.case_id != governed_analysis_input.case_id or result_set.case_id != identity_contract.case_id:
        raise _blocked("RESULT_MEMORY_IDENTITY_DRIFT", "tenant, P8, and F9 case identities must match")
    if governed_analysis_input.analysis_plan.analysis_id != result_set.analysis_id:
        raise _blocked("RESULT_MEMORY_IDENTITY_DRIFT", "P8 and F9 analysis identities must match")
    if governed_analysis_input.grain.to_dict() != result_set.grain.to_dict():
        raise _blocked("RESULT_MEMORY_GRAIN_DRIFT", "P8 and F9 grain must match")
    digest = result_set.integrity.digest
    result_set_payload = result_set.to_dict()
    _verify_result_set_integrity(result_set_payload, digest)
    artifact_ref = f"resultset:sha256:{digest}"
    formula_versions = _formula_versions(result_projection)
    evidence_refs = _compact_evidence_refs(result_projection)
    owner_refs = tuple(owner_evidence_refs)
    grain = result_set.grain.to_dict()
    memory_id = f"s1rm_{_sha256(_memory_identity_payload_values(
        identity_contract_id=identity_contract.identity_contract_id,
        tenant_id=identity_contract.tenant_id,
        cliente_id=identity_contract.cliente_id,
        case_id=identity_contract.case_id,
        analysis_id=result_set.analysis_id,
        period=period,
        grain=grain,
        formula_versions=formula_versions,
        result_set_integrity_digest=digest,
        evidence_refs=evidence_refs,
        owner_evidence_refs=owner_refs,
        artifact_ref=artifact_ref,
    ))}"
    return Service1ResultMemoryRecordV1(
        memory_record_id=memory_id,
        identity_contract_id=identity_contract.identity_contract_id,
        tenant_id=identity_contract.tenant_id,
        cliente_id=identity_contract.cliente_id,
        case_id=identity_contract.case_id,
        analysis_id=result_set.analysis_id,
        period=period,
        grain=grain,
        formula_versions=formula_versions,
        result_set=result_set_payload,
        result_set_integrity_digest=digest,
        evidence_refs=evidence_refs,
        owner_evidence_refs=owner_refs,
        executed_at=_executed_at(executed_at),
        artifact_ref=artifact_ref,
        artifact={
            "kind": ARTIFACT_KIND,
            "ref": artifact_ref,
            "schema_version": result_set.schema_version,
            "integrity_digest": digest,
        },
        provenance={"source": "F13_GOVERNED_RESULT_MEMORY"},
        schema_version=SCHEMA_VERSION,
    )


def service_1_result_memory_record_from_mapping_v1(payload: Mapping[str, Any]) -> Service1ResultMemoryRecordV1:
    if not isinstance(payload, Mapping):
        raise TypeError("payload must be a mapping")
    period_payload = payload.get("period")
    if not isinstance(period_payload, Mapping):
        raise _blocked("RESULT_MEMORY_INVALID_PERIOD", "period payload is required")
    period = Service1ResultMemoryPeriodV1(
        period_ref=str(period_payload.get("period_ref") or ""),
        start_date=str(period_payload.get("start_date") or ""),
        end_date=str(period_payload.get("end_date") or ""),
        basis_ref=str(period_payload.get("basis_ref") or ""),
        source_refs=tuple(period_payload.get("source_refs") or ()),
        schema_version=str(period_payload.get("schema_version") or PERIOD_SCHEMA_VERSION),
    )
    return Service1ResultMemoryRecordV1(
        memory_record_id=str(payload.get("memory_record_id") or ""),
        identity_contract_id=str(payload.get("identity_contract_id") or ""),
        tenant_id=str(payload.get("tenant_id") or ""),
        cliente_id=(str(payload.get("cliente_id")) if payload.get("cliente_id") is not None else None),
        case_id=str(payload.get("case_id") or ""),
        analysis_id=str(payload.get("analysis_id") or ""),
        period=period,
        grain=dict(payload.get("grain") or {}),
        formula_versions=dict(payload.get("formula_versions") or {}),
        result_set=dict(payload.get("result_set") or {}),
        result_set_integrity_digest=str(payload.get("result_set_integrity_digest") or ""),
        evidence_refs=tuple(payload.get("evidence_refs") or ()),
        owner_evidence_refs=tuple(payload.get("owner_evidence_refs") or ()),
        executed_at=str(payload.get("executed_at") or ""),
        artifact_ref=str(payload.get("artifact_ref") or ""),
        artifact=dict(payload.get("artifact") or {}),
        provenance=dict(payload.get("provenance") or {}),
        schema_version=str(payload.get("schema_version") or ""),
    )


__all__ = [
    "SCHEMA_VERSION",
    "PERIOD_SCHEMA_VERSION",
    "ARTIFACT_KIND",
    "MATH_RUNTIME_VERSION_KEY",
    "Service1ResultMemoryErrorV1",
    "Service1ResultMemoryPeriodV1",
    "Service1ResultMemoryRecordV1",
    "build_service_1_result_memory_record_v1",
    "service_1_result_memory_record_from_mapping_v1",
]
