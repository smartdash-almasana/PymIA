from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_microservice_activation_contract_v1 import (
    build_service_1_microservice_activation_contract_v1,
)


def _activation_input(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "microservice_id": "file_intake",
        "requested_capability": "file_intake_result",
        "runtime_requested": False,
        "human_review_present": False,
    }
    data.update(overrides)
    return data


def test_file_intake_activation_allowed_without_human_review() -> None:
    result = build_service_1_microservice_activation_contract_v1(_activation_input())

    assert result["status"] == "ACTIVATION_ALLOWED"
    assert result["activation_allowed"] is True
    assert result["activated_microservice"] == "file_intake"
    assert result["runtime_authorized"] is False
    assert result["human_review_required"] is False
    assert result["required_human_actions"] == []


def test_accounting_contract_activation_allowed_only_with_human_review() -> None:
    result = build_service_1_microservice_activation_contract_v1(
        _activation_input(
            microservice_id="accounting_contracts",
            requested_capability="contract_review_report",
            human_review_present=True,
        )
    )

    assert result["status"] == "ACTIVATION_ALLOWED"
    assert result["activation_allowed"] is True
    assert result["human_review_required"] is True
    assert result["required_human_actions"] == ["maintain_human_review"]


def test_non_dict_input_is_invalid() -> None:
    result = build_service_1_microservice_activation_contract_v1("bad")  # type: ignore[arg-type]

    assert result["status"] == "INVALID_INPUT"
    assert result["activation_allowed"] is False
    assert result["blocked_reason"] == "activation_input_must_be_dict"


def test_missing_required_fields_blocks_activation() -> None:
    data = _activation_input()
    del data["requested_capability"]

    result = build_service_1_microservice_activation_contract_v1(data)

    assert result["status"] == "MISSING_REQUIRED_FIELDS"
    assert result["activation_allowed"] is False
    assert "requested_capability" in result["blocked_reason"]


def test_unknown_microservice_blocks_activation() -> None:
    result = build_service_1_microservice_activation_contract_v1(
        _activation_input(microservice_id="tax_liquidation")
    )

    assert result["status"] == "UNKNOWN_MICROSERVICE"
    assert result["activation_allowed"] is False
    assert result["next_allowed_action"] == "select_supported_service_1_microservice"


def test_out_of_scope_chatbot_blocks_activation() -> None:
    result = build_service_1_microservice_activation_contract_v1(
        _activation_input(microservice_id="chatbot", requested_capability="free_chat", human_review_present=True)
    )

    assert result["status"] == "BLOCKED_BY_REGISTRY"
    assert result["activation_allowed"] is False
    assert result["next_allowed_action"] == "keep_microservice_blocked"


def test_missing_dependencies_block_activation() -> None:
    result = build_service_1_microservice_activation_contract_v1(
        _activation_input(
            microservice_id="bank_reconciliation_basic",
            requested_capability="reconciliation_scope_summary",
            human_review_present=True,
            available_microservices=["file_intake"],
        )
    )

    assert result["status"] == "BLOCKED_BY_DEPENDENCIES"
    assert result["activation_allowed"] is False
    assert "accounting_contracts" in result["blocked_reason"]
    assert result["next_allowed_action"] == "complete_microservice_dependencies"


def test_runtime_request_blocks_even_when_microservice_exists() -> None:
    result = build_service_1_microservice_activation_contract_v1(
        _activation_input(runtime_requested=True)
    )

    assert result["status"] == "BLOCKED_BY_RUNTIME_REQUEST"
    assert result["activation_allowed"] is False
    assert result["runtime_authorized"] is False
    assert result["next_allowed_action"] == "request_non_runtime_activation"


def test_missing_human_review_blocks_human_review_required_microservice() -> None:
    result = build_service_1_microservice_activation_contract_v1(
        _activation_input(
            microservice_id="xlsx_delivery",
            requested_capability="operational_xlsx_draft",
            human_review_present=False,
        )
    )

    assert result["status"] == "BLOCKED_BY_MISSING_HUMAN_REVIEW"
    assert result["activation_allowed"] is False
    assert result["required_human_actions"] == ["assign_human_review"]


def test_blocked_capability_blocks_activation() -> None:
    result = build_service_1_microservice_activation_contract_v1(
        _activation_input(
            microservice_id="bank_reconciliation_basic",
            requested_capability="conciliacion_bancaria_cerrada",
            human_review_present=True,
        )
    )

    assert result["status"] == "BLOCKED_BY_FORBIDDEN_CAPABILITY"
    assert result["activation_allowed"] is False
    assert result["blocked_reason"] == "forbidden_capability:conciliacion_bancaria_cerrada"


def test_finality_terms_block_activation_even_if_not_exact_registry_term() -> None:
    result = build_service_1_microservice_activation_contract_v1(
        _activation_input(
            microservice_id="owner_output",
            requested_capability="resultado contable final",
            human_review_present=True,
        )
    )

    assert result["status"] == "BLOCKED_BY_FORBIDDEN_CAPABILITY"
    assert result["activation_allowed"] is False
    assert result["blocked_reason"] == "forbidden_capability:finality_or_external_runtime_request"


def test_service_2_activation_is_blocked_by_registry() -> None:
    result = build_service_1_microservice_activation_contract_v1(
        _activation_input(microservice_id="servicio_2_diagnostic", requested_capability="diagnostico_integral_pyme")
    )

    assert result["status"] == "BLOCKED_BY_REGISTRY"
    assert result["activation_allowed"] is False
    assert result["activated_microservice"] is None


def test_module_has_no_io_xlsx_parser_api_or_llm_dependencies() -> None:
    module_path = Path(__file__).parents[2] / "pymia" / "smartpyme" / "service_1_microservice_activation_contract_v1.py"
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
        "import openai",
        "from openai",
        "import langchain",
        "from langchain",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source


def test_vertical_slice_was_not_imported_or_referenced() -> None:
    module_path = Path(__file__).parents[2] / "pymia" / "smartpyme" / "service_1_microservice_activation_contract_v1.py"
    source = module_path.read_text(encoding="utf-8")

    assert "vertical_slice" not in source
