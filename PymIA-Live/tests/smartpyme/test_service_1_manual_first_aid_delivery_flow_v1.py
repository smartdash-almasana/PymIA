from __future__ import annotations

import inspect
import os
import tempfile
from pathlib import Path

import pytest

from pymia.smartpyme.first_aid_tool_result_v1 import (
    build_first_aid_tool_result_v1,
    build_missing_inputs_tool_result_v1,
)
from pymia.smartpyme.service_1_manual_first_aid_delivery_flow_v1 import (
    SERVICE_NAME,
    build_service_1_manual_first_aid_delivery_flow_v1,
)


def _ok_result(
    tool_ref: str,
    computed_results: dict[str, object] | None = None,
) -> dict[str, object]:
    return build_first_aid_tool_result_v1(
        tool_ref=tool_ref,
        status="OK",
        inputs_used={"input": tool_ref},
        computed_results=computed_results or {"result": 1},
        limitations=[f"Limitation for {tool_ref}."],
        owner_summary=f"Summary for {tool_ref}.",
        technical_notes=["Deterministic math only."],
    )


def _missing_result(tool_ref: str, missing: list[str]) -> dict[str, object]:
    return build_missing_inputs_tool_result_v1(
        tool_ref=tool_ref,
        missing_inputs=missing,
        owner_summary=f"Missing inputs for {tool_ref}.",
        inputs_used={"input": tool_ref},
    )


def test_flow_with_single_ok_result() -> None:
    tool_result = _ok_result("tool_a", {"result": 42})

    with tempfile.TemporaryDirectory() as tmpdir:
        flow_result = build_service_1_manual_first_aid_delivery_flow_v1(
            tool_results=[tool_result],
            output_dir=tmpdir,
        )

    assert flow_result["schema_version"] == "1.0"
    assert flow_result["service_name"] == SERVICE_NAME
    assert flow_result["delivery_count"] == 1
    assert flow_result["tool_refs"] == ["tool_a"]
    assert flow_result["statuses"] == ["OK"]
    assert flow_result["runtime_authorized"] is False


def test_flow_with_multiple_results() -> None:
    first = _ok_result("tool_a", {"result": 1})
    second = _ok_result("tool_b", {"result": 2})

    with tempfile.TemporaryDirectory() as tmpdir:
        flow_result = build_service_1_manual_first_aid_delivery_flow_v1(
            tool_results=[first, second],
            output_dir=tmpdir,
        )

    assert flow_result["delivery_count"] == 2
    assert flow_result["tool_refs"] == ["tool_a", "tool_b"]
    assert flow_result["statuses"] == ["OK", "OK"]
    assert len(flow_result["deliveries"]) == 2


def test_generates_xlsx_files() -> None:
    tool_result = _ok_result("test_tool", {"result": 1})

    with tempfile.TemporaryDirectory() as tmpdir:
        flow_result = build_service_1_manual_first_aid_delivery_flow_v1(
            tool_results=[tool_result],
            output_dir=tmpdir,
        )

        xlsx_path = Path(tmpdir) / "first_aid_test_tool.xlsx"
        assert xlsx_path.exists()
        assert xlsx_path.stat().st_size > 0
        assert flow_result["deliveries"][0]["output_path"] == str(xlsx_path.resolve())


def test_uses_aggregate_and_preserves_aggregate_id() -> None:
    tool_result = _ok_result("tool_a", {"result": 1})

    with tempfile.TemporaryDirectory() as tmpdir:
        first = build_service_1_manual_first_aid_delivery_flow_v1(
            tool_results=[tool_result],
            output_dir=tmpdir,
        )
        second = build_service_1_manual_first_aid_delivery_flow_v1(
            tool_results=[tool_result],
            output_dir=tmpdir,
        )

    assert first["aggregate_id"] == second["aggregate_id"]
    assert first["aggregate_id"].startswith("first_aid_delivery_aggregate_v1:")


def test_summary_text_includes_tool_ref_and_status() -> None:
    tool_result = _ok_result("tool_a", {"result": 1})

    with tempfile.TemporaryDirectory() as tmpdir:
        flow_result = build_service_1_manual_first_aid_delivery_flow_v1(
            tool_results=[tool_result],
            output_dir=tmpdir,
        )

    assert "tool_a" in flow_result["summary_text"]
    assert "OK" in flow_result["summary_text"]
    assert "1" in flow_result["summary_text"]


def test_summary_text_includes_missing_inputs() -> None:
    tool_result = _missing_result("tool_a", ["input_x", "input_y"])
    ok_result = _ok_result("tool_b", {"result": 1})

    with tempfile.TemporaryDirectory() as tmpdir:
        flow_result = build_service_1_manual_first_aid_delivery_flow_v1(
            tool_results=[tool_result, ok_result],
            output_dir=tmpdir,
        )

    assert "Faltantes detectados" in flow_result["summary_text"]
    assert "input_x" in flow_result["summary_text"]
    assert "input_y" in flow_result["summary_text"]


def test_preserves_limitations() -> None:
    tool_result = _ok_result("tool_a", {"result": 1})

    with tempfile.TemporaryDirectory() as tmpdir:
        flow_result = build_service_1_manual_first_aid_delivery_flow_v1(
            tool_results=[tool_result],
            output_dir=tmpdir,
        )

    assert "Limitation for tool_a." in flow_result["summary_text"]
    assert "Limitaciones principales" in flow_result["summary_text"]


def test_rejects_empty_list() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(ValueError, match="requires at least one tool result"):
            build_service_1_manual_first_aid_delivery_flow_v1(
                tool_results=[],
                output_dir=tmpdir,
            )


def test_rejects_runtime_authorized_result() -> None:
    tool_result = _ok_result("tool_a", {"result": 1})
    tool_result["runtime_authorized"] = True

    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(ValueError, match="does not accept runtime_authorized=True"):
            build_service_1_manual_first_aid_delivery_flow_v1(
                tool_results=[tool_result],
                output_dir=tmpdir,
            )


def test_rejects_nonexistent_output_dir() -> None:
    tool_result = _ok_result("tool_a", {"result": 1})

    with pytest.raises(FileNotFoundError, match="Output directory does not exist"):
        build_service_1_manual_first_aid_delivery_flow_v1(
            tool_results=[tool_result],
            output_dir="/nonexistent/path/for/test",
        )


def test_does_not_import_concrete_tools() -> None:
    import pymia.smartpyme.service_1_manual_first_aid_delivery_flow_v1 as module

    source = inspect.getsource(module)

    assert "first_aid_precio_margen_basico_v1" not in source
    assert "first_aid_caja_diaria_triage_v1" not in source
    assert "first_aid_stock_alertas_basicas_v1" not in source
    assert "run_" not in source


def test_does_not_depend_on_pipeline_fsm_llm_chatbot_document_ingestion_or_excelsystems() -> None:
    import pymia.smartpyme.service_1_manual_first_aid_delivery_flow_v1 as module

    source = inspect.getsource(module)

    assert "vertical_pipeline" not in source
    assert "fsm" not in source.lower()
    assert "llm" not in source.lower()
    assert "chatbot" not in source.lower()
    assert "document_ingestion" not in source
    assert "exceland" not in source.lower()


def test_does_not_execute_tools_or_recalculate_results() -> None:
    import pymia.smartpyme.service_1_manual_first_aid_delivery_flow_v1 as module

    source = inspect.getsource(module)

    assert "first_aid_tool_result_v1" in source
    assert "run_first_aid" not in source
