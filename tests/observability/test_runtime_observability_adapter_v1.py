from __future__ import annotations

import pytest

from pymia.observability.runtime_observability_adapter_v1 import (
    InMemoryObservabilityAdapter,
    NoOpObservabilityAdapter,
    OPERATION_NAME,
    classify_error,
    get_runtime_observability_adapter,
    observability_adapter_scope,
)


def test_default_adapter_is_noop() -> None:
    adapter = get_runtime_observability_adapter()
    assert isinstance(adapter, NoOpObservabilityAdapter)
    handle = adapter.start_operation(OPERATION_NAME)
    assert handle.end(status="READY") is None


def test_in_memory_adapter_records_bounded_observation() -> None:
    adapter = InMemoryObservabilityAdapter()
    with observability_adapter_scope(adapter):
        handle = get_runtime_observability_adapter().start_operation(
            OPERATION_NAME,
            attributes={"workbook.size_bucket": "1-10MiB"},
        )
        handle.end(
            status="NEEDS_OWNER_CONFIRMATION",
            attributes={
                "workbook.sheet_count_bucket": "1-10",
                "workbook.column_count_bucket": "11-50",
            },
        )

    assert len(adapter.observations) == 1
    observation = adapter.observations[0]
    assert observation.operation_name == OPERATION_NAME
    assert observation.status == "NEEDS_OWNER_CONFIRMATION"
    assert adapter.outcomes["NEEDS_OWNER_CONFIRMATION"] == 1
    assert set(observation.attributes) <= {
        "operation.name",
        "operation.status",
        "workbook.size_bucket",
        "workbook.sheet_count_bucket",
        "workbook.column_count_bucket",
        "error.classification",
    }


@pytest.mark.parametrize(
    "attributes",
    [
        {"tenant_id": "tenant-secret"},
        {"case_id": "case-secret"},
        {"workbook.filename": "client.xlsx"},
        {"raw_xlsx_bytes": "payload"},
        {"workbook.size_bucket": "client.xlsx"},
    ],
)
def test_forbidden_or_unbounded_attributes_are_rejected(attributes: dict[str, str]) -> None:
    adapter = InMemoryObservabilityAdapter()
    with pytest.raises(ValueError):
        adapter.start_operation(OPERATION_NAME, attributes=attributes)
    assert adapter.observations == []


def test_profile_operation_has_separate_attribute_allowlist() -> None:
    from pymia.observability.runtime_observability_adapter_v1 import PROFILE_OPERATION_NAME

    adapter = InMemoryObservabilityAdapter()
    profile = adapter.start_operation(PROFILE_OPERATION_NAME)
    profile.end(
        status="WORKBOOK_PROFILE_READY",
        attributes={
            "workbook.column_count_bucket": "1-10",
            "workbook.relationship_count_bucket": "0",
        },
    )
    assert adapter.observations[0].operation_name == PROFILE_OPERATION_NAME
    with pytest.raises(ValueError):
        adapter.start_operation(
            PROFILE_OPERATION_NAME,
            attributes={"workbook.size_bucket": "<1MiB"},
        )


def test_error_classification_does_not_include_exception_message() -> None:
    error = ValueError("tenant-secret and raw workbook content")
    assert classify_error(error) == "VALUE_ERROR"
    assert "tenant-secret" not in classify_error(error)

