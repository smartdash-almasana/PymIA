from __future__ import annotations

import pymia.smartpyme.service_1_workbook_profiler_v1 as profiler_module
from pymia.observability.runtime_observability_adapter_v1 import (
    InMemoryObservabilityAdapter,
    OPERATION_NAME,
    PROFILE_OPERATION_NAME,
    observability_adapter_scope,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1 as build_intake,
)
from pymia.smartpyme.service_1_workbook_profiler_v1 import (
    STATUS_BLOCKED,
    STATUS_READY,
    build_service_1_workbook_profile_v1,
)


def _valid_ingestion_output() -> dict:
    return {
        "workbook_context": {"case_id": "case-secret", "workbook_ref": "workbook-ref"},
        "provenance": {"source_file_ref": "client.xlsx"},
        "column_refs": [
            {
                "field_id": "field-1",
                "question_id": "question-1",
                "sheet_name": "Ventas",
                "column_name": "Cantidad",
                "normalized_column_name": "cantidad",
            }
        ],
        "normalized_tables": [
            {
                "status": "OK",
                "sheet_name": "Ventas",
                "headers": ["Cantidad"],
                "normalized_headers": ["cantidad"],
                "rows": [{"cantidad": "1"}, {"cantidad": "2"}],
            }
        ],
        "runtime_authorized": False,
    }


def test_success_emits_profile_operation_and_real_buckets() -> None:
    adapter = InMemoryObservabilityAdapter()
    with observability_adapter_scope(adapter):
        profile = build_service_1_workbook_profile_v1(
            ingestion_output=_valid_ingestion_output()
        )

    assert profile["status"] == STATUS_READY
    assert len(adapter.observations) == 1
    observation = adapter.observations[0]
    assert observation.operation_name == PROFILE_OPERATION_NAME
    assert observation.status == STATUS_READY
    assert observation.attributes["workbook.column_count_bucket"] == "1-10"
    assert observation.attributes["workbook.relationship_count_bucket"] == "0"
    assert "workbook.size_bucket" not in observation.attributes


def test_blocked_profile_emits_blocked_status_without_changing_result() -> None:
    adapter = InMemoryObservabilityAdapter()
    with observability_adapter_scope(adapter):
        profile = build_service_1_workbook_profile_v1(ingestion_output={})

    assert profile["status"] == STATUS_BLOCKED
    assert adapter.observations[0].operation_name == PROFILE_OPERATION_NAME
    assert adapter.observations[0].status == STATUS_BLOCKED
    assert adapter.observations[0].attributes["error.classification"] == "BLOCKED_RESULT"


def test_profile_adapter_failure_preserves_product_result_and_exception(monkeypatch) -> None:
    class ExplodingAdapter:
        def start_operation(self, *_args, **_kwargs):
            raise RuntimeError("telemetry raw secret")

    expected = build_service_1_workbook_profile_v1(ingestion_output={})
    with observability_adapter_scope(ExplodingAdapter()):
        actual = build_service_1_workbook_profile_v1(ingestion_output={})
    assert actual == expected

    class ExplodingEndHandle:
        def end(self, *_args, **_kwargs):
            raise RuntimeError("telemetry raw secret")

    class ExplodingEndAdapter:
        def start_operation(self, *_args, **_kwargs):
            return ExplodingEndHandle()

    with observability_adapter_scope(ExplodingEndAdapter()):
        assert build_service_1_workbook_profile_v1(ingestion_output={}) == expected

    def raise_product_error(**_kwargs):
        raise ValueError("product secret must remain original")

    monkeypatch.setattr(profiler_module, "_profile_column", raise_product_error)
    product_error_adapter = InMemoryObservabilityAdapter()
    try:
        with observability_adapter_scope(product_error_adapter):
            build_service_1_workbook_profile_v1(ingestion_output=_valid_ingestion_output())
    except ValueError as error:
        assert str(error) == "product secret must remain original"
    else:
        raise AssertionError("expected original product exception")
    serialized = repr(product_error_adapter.observations)
    assert product_error_adapter.observations[0].attributes["error.classification"] == "VALUE_ERROR"
    assert "product secret" not in serialized


def test_ingestion_and_profile_operations_are_separate() -> None:
    adapter = InMemoryObservabilityAdapter()
    with observability_adapter_scope(adapter):
        build_intake()
        build_service_1_workbook_profile_v1(ingestion_output={})

    assert [item.operation_name for item in adapter.observations] == [
        OPERATION_NAME,
        PROFILE_OPERATION_NAME,
    ]
    assert adapter.operation_outcomes[(OPERATION_NAME, "BLOCKED")] == 1
    assert adapter.operation_outcomes[(PROFILE_OPERATION_NAME, "BLOCKED")] == 1
    ingestion_attrs = adapter.observations[0].attributes
    profile_attrs = adapter.observations[1].attributes
    assert "workbook.relationship_count_bucket" not in ingestion_attrs
    assert "workbook.size_bucket" not in profile_attrs


def test_profile_observation_contains_no_sensitive_names_or_raw_messages() -> None:
    adapter = InMemoryObservabilityAdapter()
    with observability_adapter_scope(adapter):
        build_service_1_workbook_profile_v1(ingestion_output=_valid_ingestion_output())

    serialized = repr(adapter.observations)
    assert "Ventas" not in serialized
    assert "Cantidad" not in serialized
    assert "case-secret" not in serialized
    assert "client.xlsx" not in serialized
    assert "product secret" not in serialized

