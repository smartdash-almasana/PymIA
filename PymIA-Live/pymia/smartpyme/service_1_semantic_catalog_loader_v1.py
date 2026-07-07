from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Final, Literal


SCHEMA_VERSION: Final[str] = "SERVICE_1_SEMANTIC_CATALOG_LOADER_V1"
SERVICE_NAME: Final[str] = "SERVICE_1"

STATUS_CATALOGS_LOADED: Final[str] = "CATALOGS_LOADED"
STATUS_CATALOGS_PARTIALLY_LOADED: Final[str] = "CATALOGS_PARTIALLY_LOADED"
STATUS_BLOCKED_FORMULA_CATALOG_MISSING: Final[str] = "BLOCKED_FORMULA_CATALOG_MISSING"
STATUS_BLOCKED_PATHOLOGY_CATALOG_MISSING: Final[str] = "BLOCKED_PATHOLOGY_CATALOG_MISSING"
STATUS_BLOCKED_INVALID_FORMULA_CATALOG: Final[str] = "BLOCKED_INVALID_FORMULA_CATALOG"
STATUS_BLOCKED_INVALID_PATHOLOGY_CATALOG: Final[str] = "BLOCKED_INVALID_PATHOLOGY_CATALOG"

ALLOWED_STATUSES: Final[tuple[str, ...]] = (
    STATUS_CATALOGS_LOADED,
    STATUS_CATALOGS_PARTIALLY_LOADED,
    STATUS_BLOCKED_FORMULA_CATALOG_MISSING,
    STATUS_BLOCKED_PATHOLOGY_CATALOG_MISSING,
    STATUS_BLOCKED_INVALID_FORMULA_CATALOG,
    STATUS_BLOCKED_INVALID_PATHOLOGY_CATALOG,
)

SemanticCatalogLoadStatusV1 = Literal[
    "CATALOGS_LOADED",
    "CATALOGS_PARTIALLY_LOADED",
    "BLOCKED_FORMULA_CATALOG_MISSING",
    "BLOCKED_PATHOLOGY_CATALOG_MISSING",
    "BLOCKED_INVALID_FORMULA_CATALOG",
    "BLOCKED_INVALID_PATHOLOGY_CATALOG",
]

_FORMULA_FIELDS: Final[tuple[str, ...]] = (
    "formula_id",
    "pathology_code",
    "required_variables",
    "required_evidence",
    "expression",
    "calculation_state",
    "interpretation",
)

_PATHOLOGY_FIELDS: Final[tuple[str, ...]] = (
    "pathology_code",
    "name",
    "description",
    "symptoms",
    "required_evidence",
    "formula_refs",
)


def _required_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string")
    return value.strip()


def _clean_text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _clean_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    values = value if isinstance(value, (list, tuple, set)) else (value,)
    cleaned: list[str] = []
    for item in values:
        text = _clean_text(item)
        if text:
            cleaned.append(text)
    return tuple(cleaned)


def _clean_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _validate_status(value: str) -> SemanticCatalogLoadStatusV1:
    value = _required_text(value, field_name="status")
    if value not in ALLOWED_STATUSES:
        raise ValueError(f"status must be one of: {', '.join(ALLOWED_STATUSES)}")
    return value  # type: ignore[return-value]


def _fail_closed_flag(value: bool, *, field_name: str) -> bool:
    if value is not False:
        raise ValueError(f"{field_name} must remain False in {SCHEMA_VERSION}")
    return False


def _entry_label(entry: dict[str, Any], *, id_key: str, index: int) -> str:
    identifier = _clean_text(entry.get(id_key))
    return identifier or f"index:{index}"


def _missing_fields(entry: dict[str, Any], *, fields: tuple[str, ...], id_key: str, index: int) -> tuple[str, ...]:
    label = _entry_label(entry, id_key=id_key, index=index)
    missing: list[str] = []
    for field_name in fields:
        value = entry.get(field_name)
        if value is None or value == "" or value == [] or value == {}:
            missing.append(f"{label}.{field_name}")
    return tuple(missing)


def _load_catalog_entries(catalog_path: str | Path, *, list_key: str) -> tuple[dict[str, Any], ...]:
    path = Path(catalog_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(str(path))
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        entries = payload
    elif isinstance(payload, dict):
        entries = payload.get(list_key)
    else:
        raise ValueError("catalog root must be a dict or list")
    if not isinstance(entries, list):
        raise ValueError(f"catalog must contain a list at {list_key}")
    if any(not isinstance(entry, dict) for entry in entries):
        raise ValueError(f"{list_key} entries must be objects")
    return tuple(dict(entry) for entry in entries)


@dataclass(frozen=True)
class Service1NormalizedFormulaCatalogEntryV1:
    formula_id: str
    pathology_code: str
    required_variables: tuple[str, ...]
    required_evidence: tuple[str, ...]
    expression: str
    calculation_state: str
    interpretation: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "formula_id", _clean_text(self.formula_id))
        object.__setattr__(self, "pathology_code", _clean_text(self.pathology_code))
        object.__setattr__(self, "required_variables", _clean_tuple(self.required_variables))
        object.__setattr__(self, "required_evidence", _clean_tuple(self.required_evidence))
        object.__setattr__(self, "expression", _clean_text(self.expression))
        object.__setattr__(self, "calculation_state", _clean_text(self.calculation_state))
        object.__setattr__(self, "interpretation", _clean_text(self.interpretation))
        object.__setattr__(self, "metadata", _clean_dict(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1NormalizedPathologyCatalogEntryV1:
    pathology_code: str
    name: str
    description: str
    symptoms: tuple[str, ...]
    required_evidence: tuple[str, ...]
    formula_refs: tuple[str, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "pathology_code", _clean_text(self.pathology_code))
        object.__setattr__(self, "name", _clean_text(self.name))
        object.__setattr__(self, "description", _clean_text(self.description))
        object.__setattr__(self, "symptoms", _clean_tuple(self.symptoms))
        object.__setattr__(self, "required_evidence", _clean_tuple(self.required_evidence))
        object.__setattr__(self, "formula_refs", _clean_tuple(self.formula_refs))
        object.__setattr__(self, "metadata", _clean_dict(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Service1SemanticCatalogLoadResultV1:
    schema_version: str
    service_name: str
    status: SemanticCatalogLoadStatusV1
    formula_entries: tuple[Service1NormalizedFormulaCatalogEntryV1, ...]
    pathology_entries: tuple[Service1NormalizedPathologyCatalogEntryV1, ...]
    formula_count: int
    pathology_count: int
    missing_formula_fields: tuple[str, ...]
    missing_pathology_fields: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    runtime_authorized: bool
    tool_execution_authorized: bool
    delivery_authorized: bool
    diagnosis_generated: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "schema_version", _required_text(self.schema_version, field_name="schema_version"))
        object.__setattr__(self, "service_name", _required_text(self.service_name, field_name="service_name"))
        object.__setattr__(self, "status", _validate_status(self.status))
        object.__setattr__(self, "formula_entries", tuple(self.formula_entries or ()))
        object.__setattr__(self, "pathology_entries", tuple(self.pathology_entries or ()))
        object.__setattr__(self, "formula_count", int(self.formula_count))
        object.__setattr__(self, "pathology_count", int(self.pathology_count))
        object.__setattr__(self, "missing_formula_fields", _clean_tuple(self.missing_formula_fields))
        object.__setattr__(self, "missing_pathology_fields", _clean_tuple(self.missing_pathology_fields))
        object.__setattr__(self, "blocked_reasons", _clean_tuple(self.blocked_reasons))
        object.__setattr__(self, "runtime_authorized", _fail_closed_flag(self.runtime_authorized, field_name="runtime_authorized"))
        object.__setattr__(self, "tool_execution_authorized", _fail_closed_flag(self.tool_execution_authorized, field_name="tool_execution_authorized"))
        object.__setattr__(self, "delivery_authorized", _fail_closed_flag(self.delivery_authorized, field_name="delivery_authorized"))
        object.__setattr__(self, "diagnosis_generated", _fail_closed_flag(self.diagnosis_generated, field_name="diagnosis_generated"))
        object.__setattr__(self, "metadata", _clean_dict(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_formula_entry(entry: dict[str, Any]) -> Service1NormalizedFormulaCatalogEntryV1:
    metadata = {
        key: value
        for key, value in entry.items()
        if key not in _FORMULA_FIELDS
    }
    return Service1NormalizedFormulaCatalogEntryV1(
        formula_id=_clean_text(entry.get("formula_id")),
        pathology_code=_clean_text(entry.get("pathology_code")),
        required_variables=_clean_tuple(entry.get("required_variables")),
        required_evidence=_clean_tuple(entry.get("required_evidence")),
        expression=_clean_text(entry.get("expression")),
        calculation_state=_clean_text(entry.get("calculation_state")),
        interpretation=_clean_text(entry.get("interpretation")),
        metadata=metadata,
    )


def _normalize_pathology_entry(entry: dict[str, Any]) -> Service1NormalizedPathologyCatalogEntryV1:
    metadata = {
        key: value
        for key, value in entry.items()
        if key not in _PATHOLOGY_FIELDS
    }
    return Service1NormalizedPathologyCatalogEntryV1(
        pathology_code=_clean_text(entry.get("pathology_code")),
        name=_clean_text(entry.get("name")),
        description=_clean_text(entry.get("description")),
        symptoms=_clean_tuple(entry.get("symptoms")),
        required_evidence=_clean_tuple(entry.get("required_evidence")),
        formula_refs=_clean_tuple(entry.get("formula_refs")),
        metadata=metadata,
    )


def load_service_1_formula_catalog_v1(
    catalog_path: str | Path,
) -> tuple[Service1NormalizedFormulaCatalogEntryV1, ...]:
    entries = _load_catalog_entries(catalog_path, list_key="formulas")
    return tuple(_normalize_formula_entry(entry) for entry in entries)


def load_service_1_pathology_catalog_v1(
    catalog_path: str | Path,
) -> tuple[Service1NormalizedPathologyCatalogEntryV1, ...]:
    entries = _load_catalog_entries(catalog_path, list_key="pathologies")
    return tuple(_normalize_pathology_entry(entry) for entry in entries)


def _blocked_result(
    *,
    status: SemanticCatalogLoadStatusV1,
    blocked_reason: str,
    formula_entries: tuple[Service1NormalizedFormulaCatalogEntryV1, ...] = (),
    pathology_entries: tuple[Service1NormalizedPathologyCatalogEntryV1, ...] = (),
    missing_formula_fields: tuple[str, ...] = (),
    missing_pathology_fields: tuple[str, ...] = (),
    metadata: dict[str, Any] | None = None,
) -> Service1SemanticCatalogLoadResultV1:
    return Service1SemanticCatalogLoadResultV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        formula_entries=formula_entries,
        pathology_entries=pathology_entries,
        formula_count=len(formula_entries),
        pathology_count=len(pathology_entries),
        missing_formula_fields=missing_formula_fields,
        missing_pathology_fields=missing_pathology_fields,
        blocked_reasons=(blocked_reason,),
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        metadata=dict(metadata or {}),
    )


def build_service_1_semantic_catalog_load_result_v1(
    *,
    formula_catalog_path: str | Path,
    pathology_catalog_path: str | Path,
    metadata: dict[str, Any] | None = None,
) -> Service1SemanticCatalogLoadResultV1:
    metadata_dict = dict(metadata or {})
    try:
        raw_formula_entries = _load_catalog_entries(formula_catalog_path, list_key="formulas")
    except FileNotFoundError:
        return _blocked_result(
            status=STATUS_BLOCKED_FORMULA_CATALOG_MISSING,
            blocked_reason="formula_catalog_missing",
            metadata=metadata_dict,
        )
    except Exception as exc:
        return _blocked_result(
            status=STATUS_BLOCKED_INVALID_FORMULA_CATALOG,
            blocked_reason=f"invalid_formula_catalog:{exc}",
            metadata=metadata_dict,
        )

    formula_entries = tuple(_normalize_formula_entry(entry) for entry in raw_formula_entries)
    missing_formula_fields = tuple(
        item
        for index, entry in enumerate(raw_formula_entries)
        for item in _missing_fields(entry, fields=_FORMULA_FIELDS, id_key="formula_id", index=index)
    )

    try:
        raw_pathology_entries = _load_catalog_entries(pathology_catalog_path, list_key="pathologies")
    except FileNotFoundError:
        return _blocked_result(
            status=STATUS_BLOCKED_PATHOLOGY_CATALOG_MISSING,
            blocked_reason="pathology_catalog_missing",
            formula_entries=formula_entries,
            missing_formula_fields=missing_formula_fields,
            metadata=metadata_dict,
        )
    except Exception as exc:
        return _blocked_result(
            status=STATUS_BLOCKED_INVALID_PATHOLOGY_CATALOG,
            blocked_reason=f"invalid_pathology_catalog:{exc}",
            formula_entries=formula_entries,
            missing_formula_fields=missing_formula_fields,
            metadata=metadata_dict,
        )

    pathology_entries = tuple(_normalize_pathology_entry(entry) for entry in raw_pathology_entries)
    missing_pathology_fields = tuple(
        item
        for index, entry in enumerate(raw_pathology_entries)
        for item in _missing_fields(entry, fields=_PATHOLOGY_FIELDS, id_key="pathology_code", index=index)
    )

    status = (
        STATUS_CATALOGS_PARTIALLY_LOADED
        if missing_formula_fields or missing_pathology_fields
        else STATUS_CATALOGS_LOADED
    )
    return Service1SemanticCatalogLoadResultV1(
        schema_version=SCHEMA_VERSION,
        service_name=SERVICE_NAME,
        status=status,
        formula_entries=formula_entries,
        pathology_entries=pathology_entries,
        formula_count=len(formula_entries),
        pathology_count=len(pathology_entries),
        missing_formula_fields=missing_formula_fields,
        missing_pathology_fields=missing_pathology_fields,
        blocked_reasons=(),
        runtime_authorized=False,
        tool_execution_authorized=False,
        delivery_authorized=False,
        diagnosis_generated=False,
        metadata=metadata_dict,
    )


__all__ = [
    "SCHEMA_VERSION",
    "SERVICE_NAME",
    "STATUS_CATALOGS_LOADED",
    "STATUS_CATALOGS_PARTIALLY_LOADED",
    "STATUS_BLOCKED_FORMULA_CATALOG_MISSING",
    "STATUS_BLOCKED_PATHOLOGY_CATALOG_MISSING",
    "STATUS_BLOCKED_INVALID_FORMULA_CATALOG",
    "STATUS_BLOCKED_INVALID_PATHOLOGY_CATALOG",
    "ALLOWED_STATUSES",
    "Service1NormalizedFormulaCatalogEntryV1",
    "Service1NormalizedPathologyCatalogEntryV1",
    "Service1SemanticCatalogLoadResultV1",
    "load_service_1_formula_catalog_v1",
    "load_service_1_pathology_catalog_v1",
    "build_service_1_semantic_catalog_load_result_v1",
]
