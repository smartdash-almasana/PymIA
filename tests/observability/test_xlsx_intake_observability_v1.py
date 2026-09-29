from __future__ import annotations

from pathlib import Path

from pymia.observability.runtime_observability_adapter_v1 import (
    InMemoryObservabilityAdapter,
    OPERATION_NAME,
    observability_adapter_scope,
)
from pymia.smartpyme.service_1_web_column_confirmation_intake_boundary_v1 import (
    build_service_1_web_column_confirmation_intake_boundary_v1 as build_intake,
)


_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "smartpyme" / "ventas_costos_margen.xlsx"


def test_success_emits_only_bounded_observation() -> None:
    adapter = InMemoryObservabilityAdapter()
    with observability_adapter_scope(adapter):
        packet = build_intake(local_xlsx_path=_FIXTURE)

    assert packet["status"] == "NEEDS_OWNER_CONFIRMATION"
    assert len(adapter.observations) == 1
    observation = adapter.observations[0]
    assert observation.operation_name == OPERATION_NAME
    assert observation.status == "NEEDS_OWNER_CONFIRMATION"
    assert observation.attributes["operation.name"] == OPERATION_NAME
    assert "error.classification" not in observation.attributes


def test_blocked_path_emits_closed_blocked_status() -> None:
    adapter = InMemoryObservabilityAdapter()
    with observability_adapter_scope(adapter):
        packet = build_intake()

    assert packet["status"] == "BLOCKED"
    assert len(adapter.observations) == 1
    observation = adapter.observations[0]
    assert observation.status == "BLOCKED"
    assert observation.attributes["error.classification"] == "BLOCKED_RESULT"


def test_failing_telemetry_adapter_cannot_change_product_result() -> None:
    class ExplodingAdapter:
        def start_operation(self, *_args, **_kwargs):
            raise RuntimeError("telemetry must not escape")

    expected = build_intake()
    with observability_adapter_scope(ExplodingAdapter()):
        actual = build_intake()

    assert actual == expected


def test_failing_telemetry_end_cannot_change_product_result() -> None:
    class ExplodingHandle:
        def end(self, *_args, **_kwargs):
            raise RuntimeError("telemetry must not escape")

    class AdapterWithExplodingEnd:
        def start_operation(self, *_args, **_kwargs):
            return ExplodingHandle()

    expected = build_intake()
    with observability_adapter_scope(AdapterWithExplodingEnd()):
        actual = build_intake()

    assert actual == expected


def test_telemetry_does_not_capture_source_or_tenant_data() -> None:
    adapter = InMemoryObservabilityAdapter()
    with observability_adapter_scope(adapter):
        build_intake(local_xlsx_path=_FIXTURE)

    serialized = repr(adapter.observations)
    assert _FIXTURE.name not in serialized
    assert "tenant" not in serialized.lower()
    assert "case_" not in serialized
    assert "column_name" not in serialized

