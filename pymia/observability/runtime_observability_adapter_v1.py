"""Small, fail-safe runtime observability seam.

The default adapter is deliberately a no-op.  This module owns the technical
boundary for future exporters while keeping business payloads out of runtime
telemetry.
"""

from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Iterator, Mapping, Protocol

OPERATION_NAME = "pymia.ingestion.xlsx"
PROFILE_OPERATION_NAME = "pymia.workbook.profile"

ALLOWED_ATTRIBUTE_KEYS = frozenset(
    {
        "operation.name",
        "operation.status",
        "workbook.size_bucket",
        "workbook.sheet_count_bucket",
        "workbook.column_count_bucket",
        "workbook.relationship_count_bucket",
        "error.classification",
    }
)
_BUCKET_KEYS = frozenset(
    {
        "workbook.size_bucket",
        "workbook.sheet_count_bucket",
        "workbook.column_count_bucket",
        "workbook.relationship_count_bucket",
    }
)
_OPERATION_ATTRIBUTE_KEYS = {
    OPERATION_NAME: frozenset(
        {
            "operation.name",
            "operation.status",
            "workbook.size_bucket",
            "workbook.sheet_count_bucket",
            "workbook.column_count_bucket",
            "error.classification",
        }
    ),
    PROFILE_OPERATION_NAME: frozenset(
        {
            "operation.name",
            "operation.status",
            "workbook.column_count_bucket",
            "workbook.relationship_count_bucket",
            "error.classification",
        }
    ),
}
_ALLOWED_STATUSES = frozenset(
    {
        "BLOCKED",
        "NEEDS_EVIDENCE",
        "NEEDS_OWNER_CONFIRMATION",
        "READY",
        "CONFIRMED_BINDINGS",
        "PERSISTED",
        "PERSISTENCE_ERROR",
        "WORKBOOK_PROFILE_READY",
    }
)
_ALLOWED_ERROR_CLASSIFICATIONS = frozenset(
    {
        "BLOCKED_RESULT",
        "OS_ERROR",
        "TIMEOUT",
        "TYPE_ERROR",
        "UNCLASSIFIED_ERROR",
        "VALUE_ERROR",
    }
)
_BUCKET_VALUES = frozenset(
    {
        "unknown",
        "0",
        "1-10",
        "11-50",
        "51-200",
        ">200",
        "<1MiB",
        "1-10MiB",
        "10-25MiB",
        ">25MiB",
    }
)


def size_bucket(size_bytes: int | None) -> str:
    """Return a bounded size label without retaining the size or source name."""
    if size_bytes is None or size_bytes < 0:
        return "unknown"
    if size_bytes <= 1024 * 1024:
        return "<1MiB"
    if size_bytes <= 10 * 1024 * 1024:
        return "1-10MiB"
    if size_bytes <= 25 * 1024 * 1024:
        return "10-25MiB"
    return ">25MiB"


def count_bucket(count: int | None) -> str:
    """Return a bounded count label."""
    if count is None or count < 0:
        return "unknown"
    if count == 0:
        return "0"
    if count <= 10:
        return "1-10"
    if count <= 50:
        return "11-50"
    if count <= 200:
        return "51-200"
    return ">200"


def classify_error(error: BaseException) -> str:
    """Map an exception to a closed taxonomy, never exposing its message."""
    if isinstance(error, TimeoutError):
        return "TIMEOUT"
    if isinstance(error, OSError):
        return "OS_ERROR"
    if isinstance(error, TypeError):
        return "TYPE_ERROR"
    if isinstance(error, ValueError):
        return "VALUE_ERROR"
    return "UNCLASSIFIED_ERROR"


def _validate_attributes(
    attributes: Mapping[str, Any] | None,
    *,
    allowed_keys: frozenset[str] = ALLOWED_ATTRIBUTE_KEYS,
    operation_name: str | None = None,
) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in (attributes or {}).items():
        if key not in allowed_keys:
            raise ValueError(f"attribute not allowlisted: {key}")
        if key == "operation.name" and operation_name is not None and value != operation_name:
            raise ValueError("operation.name is fixed")
        if key == "operation.status" and value not in _ALLOWED_STATUSES:
            raise ValueError("operation.status is not allowlisted")
        if key == "error.classification" and value not in _ALLOWED_ERROR_CLASSIFICATIONS:
            raise ValueError("error.classification is not allowlisted")
        if key in _BUCKET_KEYS and value not in _BUCKET_VALUES:
            raise ValueError(f"unbounded bucket value for {key}")
        if not isinstance(value, str):
            raise ValueError(f"attribute values must be strings: {key}")
        normalized[key] = value
    return normalized


@dataclass(frozen=True)
class Observation:
    operation_name: str
    status: str
    duration_ms: float
    attributes: dict[str, str]


class ObservationHandle(Protocol):
    def end(
        self,
        *,
        status: str,
        attributes: Mapping[str, Any] | None = None,
        error_classification: str | None = None,
    ) -> Observation | None: ...


class RuntimeObservabilityAdapter(Protocol):
    def start_operation(
        self,
        operation_name: str,
        *,
        attributes: Mapping[str, Any] | None = None,
    ) -> ObservationHandle: ...


class _Handle:
    def __init__(
        self,
        adapter: "InMemoryObservabilityAdapter",
        operation_name: str,
        attributes: dict[str, str],
        allowed_keys: frozenset[str],
    ) -> None:
        self._adapter = adapter
        self._operation_name = operation_name
        self._attributes = attributes
        self._allowed_keys = allowed_keys
        self._started_at = perf_counter()
        self._ended = False

    def end(
        self,
        *,
        status: str,
        attributes: Mapping[str, Any] | None = None,
        error_classification: str | None = None,
    ) -> Observation | None:
        if self._ended:
            return None
        self._ended = True
        merged = dict(self._attributes)
        merged.update(
            _validate_attributes(
                attributes,
                allowed_keys=self._allowed_keys,
                operation_name=self._operation_name,
            )
        )
        merged["operation.status"] = status
        if error_classification is not None:
            merged["error.classification"] = error_classification
        merged = _validate_attributes(
            merged,
            allowed_keys=self._allowed_keys,
            operation_name=self._operation_name,
        )
        observation = Observation(
            operation_name=self._operation_name,
            status=status,
            duration_ms=(perf_counter() - self._started_at) * 1000.0,
            attributes=merged,
        )
        self._adapter.observations.append(observation)
        self._adapter.outcomes[status] += 1
        self._adapter.operation_outcomes[(self._operation_name, status)] += 1
        return observation


class NoOpObservabilityAdapter:
    """Default adapter: accepts valid bounded observations and stores nothing."""

    def start_operation(
        self,
        operation_name: str,
        *,
        attributes: Mapping[str, Any] | None = None,
    ) -> ObservationHandle:
        _, allowed_keys = _validate_operation(operation_name, attributes)
        return _NoOpHandle(operation_name=operation_name, allowed_keys=allowed_keys)


class _NoOpHandle:
    def __init__(self, *, operation_name: str, allowed_keys: frozenset[str]) -> None:
        self._operation_name = operation_name
        self._allowed_keys = allowed_keys

    def end(
        self,
        *,
        status: str,
        attributes: Mapping[str, Any] | None = None,
        error_classification: str | None = None,
    ) -> None:
        _validate_attributes(
            {"operation.status": status, **(attributes or {})},
            allowed_keys=self._allowed_keys,
            operation_name=self._operation_name,
        )
        if error_classification is not None:
            _validate_attributes(
                {"error.classification": error_classification},
                allowed_keys=self._allowed_keys,
                operation_name=self._operation_name,
            )
        return None


class InMemoryObservabilityAdapter:
    """Deterministic test double for asserting emitted telemetry."""

    def __init__(self) -> None:
        self.observations: list[Observation] = []
        self.outcomes: Counter[str] = Counter()
        self.operation_outcomes: Counter[tuple[str, str]] = Counter()

    def start_operation(
        self,
        operation_name: str,
        *,
        attributes: Mapping[str, Any] | None = None,
    ) -> ObservationHandle:
        normalized, allowed_keys = _validate_operation(operation_name, attributes)
        return _Handle(self, operation_name, normalized, allowed_keys)


def _validate_operation(
    operation_name: str,
    attributes: Mapping[str, Any] | None,
) -> tuple[dict[str, str], frozenset[str]]:
    allowed_keys = _OPERATION_ATTRIBUTE_KEYS.get(operation_name)
    if allowed_keys is None:
        raise ValueError(f"unsupported operation: {operation_name}")
    normalized = _validate_attributes(
        attributes,
        allowed_keys=allowed_keys,
        operation_name=operation_name,
    )
    normalized["operation.name"] = operation_name
    return normalized, allowed_keys


_DEFAULT_ADAPTER = NoOpObservabilityAdapter()
_CURRENT_ADAPTER: ContextVar[RuntimeObservabilityAdapter] = ContextVar(
    "pymia_runtime_observability_adapter",
    default=_DEFAULT_ADAPTER,
)


def get_runtime_observability_adapter() -> RuntimeObservabilityAdapter:
    return _CURRENT_ADAPTER.get()


@contextmanager
def observability_adapter_scope(adapter: RuntimeObservabilityAdapter) -> Iterator[None]:
    token = _CURRENT_ADAPTER.set(adapter)
    try:
        yield
    finally:
        _CURRENT_ADAPTER.reset(token)


__all__ = [
    "ALLOWED_ATTRIBUTE_KEYS",
    "InMemoryObservabilityAdapter",
    "NoOpObservabilityAdapter",
    "Observation",
    "OPERATION_NAME",
    "PROFILE_OPERATION_NAME",
    "classify_error",
    "count_bucket",
    "get_runtime_observability_adapter",
    "observability_adapter_scope",
    "size_bucket",
]
