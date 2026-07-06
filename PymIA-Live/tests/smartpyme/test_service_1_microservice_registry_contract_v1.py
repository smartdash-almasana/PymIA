from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_microservice_registry_contract_v1 import (
    REQUIRED_REGISTRY_OUTPUT_FIELDS,
    SUPPORTED_MICROSERVICES,
    build_service_1_microservice_registry_contract_v1,
)


def test_file_intake_registry_entry_is_valid_without_human_review_requirement() -> None:
    result = build_service_1_microservice_registry_contract_v1({"microservice_id": "file_intake"})

    assert result["status"] == "VALID"
    assert result["microservice_id"] == "file_intake"
    assert result["state"] == "IMPLEMENTED_VALIDATED"
    assert result["runtime_authorized"] is False
    assert result["human_review_required"] is False
    assert result["missing_dependencies"] == []
    assert result["next_allowed_action"] == "use_as_intake_boundary"


def test_owner_release_action_gate_registry_entry_declares_manifest_and_audit_dependencies() -> None:
    result = build_service_1_microservice_registry_contract_v1({"microservice_id": "owner_release_action_gate"})

    assert result["status"] == "VALID"
    assert result["state"] == "IMPLEMENTED_VALIDATED"
    assert result["dependencies"] == ["case_folder_manifest", "delivery_manifest_audit"]
    assert result["human_review_required"] is True
    assert "chatbot_autonomo" in result["blocked_capabilities"]
    assert "final_accounting_claim" in result["blocked_capabilities"]


def test_accounting_contracts_registry_entry_is_contract_only_and_blocks_final_accounting() -> None:
    result = build_service_1_microservice_registry_contract_v1({"microservice_id": "accounting_contracts"})

    assert result["status"] == "VALID"
    assert result["state"] == "CONTRACT_ONLY"
    assert result["runtime_authorized"] is False
    assert result["human_review_required"] is True
    assert "conciliacion_definitiva" in result["blocked_capabilities"]
    assert "asientos_automaticos" in result["blocked_capabilities"]


def test_bank_reconciliation_is_blocked_when_dependencies_are_not_available() -> None:
    result = build_service_1_microservice_registry_contract_v1(
        {
            "microservice_id": "bank_reconciliation_basic",
            "available_microservices": ["file_intake"],
        }
    )

    assert result["status"] == "BLOCKED_BY_DEPENDENCIES"
    assert result["missing_dependencies"] == ["accounting_contracts", "xlsx_delivery"]
    assert result["next_allowed_action"] == "complete_microservice_dependencies"
    assert result["runtime_authorized"] is False


def test_delivery_manifest_audit_is_valid_when_case_folder_manifest_dependency_is_available() -> None:
    result = build_service_1_microservice_registry_contract_v1(
        {
            "microservice_id": "delivery_manifest_audit",
            "available_microservices": ["case_folder_manifest"],
        }
    )

    assert result["status"] == "VALID"
    assert result["dependencies"] == ["case_folder_manifest"]
    assert result["missing_dependencies"] == []
    assert result["next_allowed_action"] == "audit_delivery_manifest"


def test_chatbot_is_explicitly_blocked_as_out_of_scope() -> None:
    result = build_service_1_microservice_registry_contract_v1({"microservice_id": "chatbot"})

    assert result["status"] == "BLOCKED_MICROSERVICE"
    assert result["state"] == "OUT_OF_SCOPE"
    assert result["runtime_authorized"] is False
    assert result["next_allowed_action"] == "keep_microservice_blocked"


def test_servicio_2_diagnostic_is_explicitly_out_of_scope() -> None:
    result = build_service_1_microservice_registry_contract_v1({"microservice_id": "servicio_2_diagnostic"})

    assert result["status"] == "BLOCKED_MICROSERVICE"
    assert result["state"] == "OUT_OF_SCOPE"
    assert "diagnostico_integral_pyme" in result["blocked_capabilities"]


def test_unknown_microservice_is_rejected() -> None:
    result = build_service_1_microservice_registry_contract_v1({"microservice_id": "tax_liquidation"})

    assert result["status"] == "UNKNOWN_MICROSERVICE"
    assert result["microservice_id"] == "tax_liquidation"
    assert result["next_allowed_action"] == "select_supported_service_1_microservice"
    assert result["runtime_authorized"] is False


def test_invalid_input_is_rejected() -> None:
    result = build_service_1_microservice_registry_contract_v1("not-a-dict")  # type: ignore[arg-type]

    assert result["status"] == "INVALID_INPUT"
    assert result["microservice_id"] is None
    assert result["next_allowed_action"] == "provide_registry_input_dict"
    assert result["human_review_required"] is True


def test_blank_microservice_id_is_invalid() -> None:
    result = build_service_1_microservice_registry_contract_v1({"microservice_id": ""})

    assert result["status"] == "INVALID_INPUT"
    assert result["next_allowed_action"] == "provide_microservice_id"


def test_all_supported_entries_are_runtime_authorized_false() -> None:
    for microservice_id in SUPPORTED_MICROSERVICES:
        result = build_service_1_microservice_registry_contract_v1({"microservice_id": microservice_id})
        assert result["runtime_authorized"] is False, microservice_id


def test_all_registry_results_have_required_output_fields() -> None:
    for microservice_id in SUPPORTED_MICROSERVICES:
        result = build_service_1_microservice_registry_contract_v1({"microservice_id": microservice_id})
        assert tuple(result.keys()) == REQUIRED_REGISTRY_OUTPUT_FIELDS


def test_core_microservices_are_registered() -> None:
    expected = {
        "file_intake",
        "first_aid_triage",
        "excel_treatment_lab",
        "exceland_bridge",
        "owner_output",
        "xlsx_delivery",
        "accounting_contracts",
        "bank_reconciliation_basic",
        "mercado_pago_reconciliation_basic",
        "invoice_collection_matching_basic",
        "supplier_purchase_review_basic",
        "accounting_workpaper",
        "case_folder_manifest",
        "delivery_manifest_audit",
        "owner_release_action_gate",
    }

    assert expected.issubset(set(SUPPORTED_MICROSERVICES))


def test_registry_module_has_no_io_xlsx_parser_api_or_llm_dependencies() -> None:
    module_path = Path(__file__).parents[2] / "pymia" / "smartpyme" / "service_1_microservice_registry_contract_v1.py"
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
        "import llama",
        "from llama",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source


def test_vertical_slice_was_not_imported_or_referenced() -> None:
    module_path = Path(__file__).parents[2] / "pymia" / "smartpyme" / "service_1_microservice_registry_contract_v1.py"
    source = module_path.read_text(encoding="utf-8")

    assert "vertical_slice" not in source
