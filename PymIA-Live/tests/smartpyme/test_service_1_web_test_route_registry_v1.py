from __future__ import annotations

from pathlib import Path

import pytest

from pymia.smartpyme.service_1_web_test_route_registry_v1 import (
    ALLOWED_WEB_TEST_ROUTE_IDS,
    BLOCKED_WEB_TEST_ROUTE_IDS,
    REQUIRED_WEB_TEST_ROUTE_FIELDS,
    assert_service_1_web_test_route_allowed_v1,
    get_service_1_web_test_route_v1,
    is_service_1_web_test_route_allowed_v1,
    list_service_1_web_test_routes_v1,
)


def test_lists_exactly_five_allowed_routes() -> None:
    routes = list_service_1_web_test_routes_v1()

    assert [route["route_id"] for route in routes] == list(ALLOWED_WEB_TEST_ROUTE_IDS)
    assert len(routes) == 5


def test_each_route_has_required_fields_in_stable_order() -> None:
    for route in list_service_1_web_test_routes_v1():
        assert tuple(route.keys()) == REQUIRED_WEB_TEST_ROUTE_FIELDS


def test_each_route_is_sandbox_only_and_human_review_required() -> None:
    for route in list_service_1_web_test_routes_v1():
        assert route["runtime_authorized"] is False, route["route_id"]
        assert route["production_allowed"] is False, route["route_id"]
        assert route["human_review_required"] is True, route["route_id"]
        assert route["status"] == "READY_FOR_SANDBOX_REHEARSAL"


def test_real_client_data_is_blocked_by_default_for_every_route() -> None:
    for route in list_service_1_web_test_routes_v1():
        assert "REAL_CLIENT_DATA" in route["blocked_data_modes"], route["route_id"]
        assert "REAL_CLIENT_DATA" not in route["allowed_data_modes"], route["route_id"]


def test_allowed_routes_have_artifacts_runner_and_forbidden_claims() -> None:
    for route in list_service_1_web_test_routes_v1():
        assert route["runner_ref"].startswith("run_"), route["route_id"]
        assert route["expected_artifacts"], route["route_id"]
        assert route["forbidden_claims"], route["route_id"]


def test_get_route_returns_copy_not_mutable_registry_reference() -> None:
    route = assert_service_1_web_test_route_allowed_v1("excel_treatment_lab_sandbox")
    route["expected_artifacts"].append("mutated.xlsx")

    fresh_route = assert_service_1_web_test_route_allowed_v1("excel_treatment_lab_sandbox")

    assert "mutated.xlsx" not in fresh_route["expected_artifacts"]


def test_known_allowed_routes_are_allowed() -> None:
    for route_id in ALLOWED_WEB_TEST_ROUTE_IDS:
        assert is_service_1_web_test_route_allowed_v1(route_id) is True
        assert get_service_1_web_test_route_v1(route_id) is not None


def test_blocked_route_ids_are_not_exposed() -> None:
    exposed_route_ids = {route["route_id"] for route in list_service_1_web_test_routes_v1()}

    for route_id in BLOCKED_WEB_TEST_ROUTE_IDS:
        assert route_id not in exposed_route_ids
        assert is_service_1_web_test_route_allowed_v1(route_id) is False
        assert get_service_1_web_test_route_v1(route_id) is None


def test_mercado_pago_route_is_not_exposed() -> None:
    exposed_route_ids = {route["route_id"] for route in list_service_1_web_test_routes_v1()}

    assert "mercado_pago_reconciliation" not in exposed_route_ids
    assert "mercado_pago_reconciliation_sandbox" not in exposed_route_ids
    assert is_service_1_web_test_route_allowed_v1("mercado_pago_reconciliation_sandbox") is False


def test_servicio_2_route_is_not_exposed() -> None:
    exposed_route_ids = {route["route_id"] for route in list_service_1_web_test_routes_v1()}

    assert "servicio_2_diagnostic" not in exposed_route_ids
    assert "servicio_2_diagnostic_sandbox" not in exposed_route_ids
    assert is_service_1_web_test_route_allowed_v1("servicio_2_diagnostic") is False


def test_unknown_route_is_blocked() -> None:
    assert is_service_1_web_test_route_allowed_v1("unknown_route") is False
    assert get_service_1_web_test_route_v1("unknown_route") is None

    with pytest.raises(ValueError, match="Blocked or unknown"):
        assert_service_1_web_test_route_allowed_v1("unknown_route")


def test_blank_route_is_blocked() -> None:
    assert is_service_1_web_test_route_allowed_v1("   ") is False
    assert get_service_1_web_test_route_v1("   ") is None


def test_first_aid_rehearsal_does_not_accept_anonymized_candidate_mode() -> None:
    route = assert_service_1_web_test_route_allowed_v1("first_aid_synthetic_delivery_rehearsal")

    assert route["allowed_data_modes"] == ["SYNTHETIC_FIXTURE", "MANUAL_METADATA"]
    assert "ANONYMIZED_REHEARSAL_CANDIDATE" in route["blocked_data_modes"]


def test_excel_treatment_lab_route_links_current_completion_slice() -> None:
    route = assert_service_1_web_test_route_allowed_v1("excel_treatment_lab_sandbox")

    assert route["runner_ref"] == "run_excel_treatment_lab_completion_slice_v1"
    assert "excel_treatment_lab_review_packet.xlsx" in route["expected_artifacts"]
    assert "real_workbook_normalized" in route["forbidden_claims"]


def test_registry_module_has_no_io_web_runtime_or_llm_dependencies() -> None:
    module_path = Path(__file__).parents[2] / "pymia" / "smartpyme" / "service_1_web_test_route_registry_v1.py"
    source = module_path.read_text(encoding="utf-8")

    forbidden_fragments = (
        "openpyxl",
        "pandas",
        "Path(",
        "open(",
        "read_text(",
        "write_text(",
        "from pathlib",
        "requests",
        "httpx",
        "FastAPI",
        "flask",
        "django",
        "streamlit",
        "subprocess",
        "import openai",
        "from openai",
        "import langchain",
        "from langchain",
        "vertical_slice",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source
