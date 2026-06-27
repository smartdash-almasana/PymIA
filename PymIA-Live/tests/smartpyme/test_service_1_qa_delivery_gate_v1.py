"""
Tests for Service 1 QA Delivery Gate.
"""
from __future__ import annotations

import copy

import pytest


def _build_complete_packet() -> dict:
    """Build a complete valid packet with all required artifacts."""
    return {
        "schema_version": "1.0",
        "service_name": "SERVICE_1",
        "source_channel": "cli",
        "asset": {
            "asset_id": "asset_abc123",
            "filename": "cafeteria_abc.xlsx",
            "declared_mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "size_bytes": 12345,
            "source": "path",
        },
        "file_intake": {
            "file_intake_id": "intake_001",
            "support": {"status": "SUPPORTED"},
            "runtime_authorized": False,
        },
        "taskspec_patch": {
            "next_allowed_action": "send_to_xlsx_document_ingestion",
            "runtime_authorized": False,
        },
        "owner_response": {
            "next_owner_action": "confirm_columns",
            "runtime_authorized": False,
        },
        "owner_message": "Respuesta inicial de Servicio 1.\n\nPróximo paso: Confirmar columnas.",
        "runtime_authorized": False,
        "detected_structure": {
            "schema_version": "1.0",
            "service_name": "SERVICE_1",
            "source_path_basename": "cafeteria_abc.xlsx",
            "workbook": {
                "sheet_count": 1,
                "sheets": [
                    {
                        "name": "Datos",
                        "max_row": 10,
                        "max_column": 4,
                        "headers": ["Producto", "Cantidad", "Precio", "Total"],
                        "empty_header_count": 0,
                        "sample_rows_count": 9,
                    }
                ],
            },
            "warnings": [],
            "runtime_authorized": False,
        },
        "column_confirmation_packet": {
            "packet_type": "COLUMN_CONFIRMATION",
            "questions": [
                {
                    "question": "¿Qué significa la columna 'Producto'?",
                    "column_name": "Producto",
                }
            ],
            "runtime_authorized": False,
        },
        "case_delivery_manifest": {
            "service_name": "SERVICE_1",
            "case_id": "case_001",
            "case_dir": ".tmp/service_1_cases/case_001",
            "files_written": ["owner_message.md", "operator_packet.json"],
            "runtime_authorized": False,
        },
    }


# ---------------------------------------------------------------------------
# 1. Packet completo devuelve status PASS
# ---------------------------------------------------------------------------


def test_complete_packet_returns_pass() -> None:
    """Complete packet with all artifacts → status PASS."""
    from pymia.smartpyme.service_1_qa_delivery_gate_v1 import (
        evaluate_service_1_qa_delivery_gate_v1,
    )

    packet = _build_complete_packet()
    result = evaluate_service_1_qa_delivery_gate_v1(packet)

    assert result["status"] == "PASS"
    assert result["service_name"] == "SERVICE_1"
    assert result["gate_type"] == "QA_DELIVERY_GATE"
    assert result["runtime_authorized"] is False
    assert result["checks_passed"] == result["checks_total"]


# ---------------------------------------------------------------------------
# 2. Packet sin owner_message devuelve BLOCKED
# ---------------------------------------------------------------------------


def test_packet_without_owner_message_returns_blocked() -> None:
    """Packet without owner_message → status BLOCKED."""
    from pymia.smartpyme.service_1_qa_delivery_gate_v1 import (
        evaluate_service_1_qa_delivery_gate_v1,
    )

    packet = _build_complete_packet()
    del packet["owner_message"]

    result = evaluate_service_1_qa_delivery_gate_v1(packet)

    assert result["status"] == "BLOCKED"
    assert any(c["check_id"] == "qa_003" and c["status"] == "FAIL" for c in result["checks"])
    assert len(result["blockers"]) > 0


# ---------------------------------------------------------------------------
# 3. Packet con runtime_authorized=True en cualquier nivel devuelve BLOCKED
# ---------------------------------------------------------------------------


def test_packet_with_runtime_authorized_true_returns_blocked() -> None:
    """Packet with runtime_authorized=True at any level → status BLOCKED."""
    from pymia.smartpyme.service_1_qa_delivery_gate_v1 import (
        evaluate_service_1_qa_delivery_gate_v1,
    )

    # Top level True
    packet_top = _build_complete_packet()
    packet_top["runtime_authorized"] = True
    result_top = evaluate_service_1_qa_delivery_gate_v1(packet_top)
    assert result_top["status"] == "BLOCKED"

    # Nested True
    packet_nested = _build_complete_packet()
    packet_nested["taskspec_patch"]["runtime_authorized"] = True
    result_nested = evaluate_service_1_qa_delivery_gate_v1(packet_nested)
    assert result_nested["status"] == "BLOCKED"

    # Deeply nested True
    packet_deep = _build_complete_packet()
    packet_deep["detected_structure"]["runtime_authorized"] = True
    result_deep = evaluate_service_1_qa_delivery_gate_v1(packet_deep)
    assert result_deep["status"] == "BLOCKED"


# ---------------------------------------------------------------------------
# 4. Packet sin detected_structure para XLSX devuelve BLOCKED
# ---------------------------------------------------------------------------


def test_packet_without_detected_structure_for_xlsx_returns_blocked() -> None:
    """XLSX packet without detected_structure → status BLOCKED."""
    from pymia.smartpyme.service_1_qa_delivery_gate_v1 import (
        evaluate_service_1_qa_delivery_gate_v1,
    )

    packet = _build_complete_packet()
    # Simulate XLSX by having column_confirmation but no detected_structure
    del packet["detected_structure"]

    result = evaluate_service_1_qa_delivery_gate_v1(packet)

    assert result["status"] == "BLOCKED"
    assert any(c["check_id"] == "qa_004" and c["status"] == "FAIL" for c in result["checks"])


# ---------------------------------------------------------------------------
# 5. Packet sin column_confirmation_packet para XLSX devuelve BLOCKED
# ---------------------------------------------------------------------------


def test_packet_without_column_confirmation_for_xlsx_returns_blocked() -> None:
    """XLSX packet without column_confirmation_packet → status BLOCKED."""
    from pymia.smartpyme.service_1_qa_delivery_gate_v1 import (
        evaluate_service_1_qa_delivery_gate_v1,
    )

    packet = _build_complete_packet()
    del packet["column_confirmation_packet"]

    result = evaluate_service_1_qa_delivery_gate_v1(packet)

    assert result["status"] == "BLOCKED"
    assert any(c["check_id"] == "qa_005" and c["status"] == "FAIL" for c in result["checks"])


# ---------------------------------------------------------------------------
# 6. Packet sin case_delivery_manifest devuelve BLOCKED
# ---------------------------------------------------------------------------


def test_packet_without_case_delivery_manifest_returns_blocked() -> None:
    """Packet without case_delivery_manifest → status BLOCKED."""
    from pymia.smartpyme.service_1_qa_delivery_gate_v1 import (
        evaluate_service_1_qa_delivery_gate_v1,
    )

    packet = _build_complete_packet()
    del packet["case_delivery_manifest"]

    result = evaluate_service_1_qa_delivery_gate_v1(packet)

    assert result["status"] == "BLOCKED"
    assert any(c["check_id"] == "qa_007" and c["status"] == "FAIL" for c in result["checks"])


# ---------------------------------------------------------------------------
# 7. No muta packet original
# ---------------------------------------------------------------------------


def test_does_not_mutate_original_packet() -> None:
    """Gate evaluation must not mutate the original packet."""
    from pymia.smartpyme.service_1_qa_delivery_gate_v1 import (
        evaluate_service_1_qa_delivery_gate_v1,
    )

    packet = _build_complete_packet()
    original = copy.deepcopy(packet)

    evaluate_service_1_qa_delivery_gate_v1(packet)

    assert packet == original


# ---------------------------------------------------------------------------
# 8. No expone diagnosis/accounting_result/recommendation fuerte
# ---------------------------------------------------------------------------


def test_does_not_expose_forbidden_keys() -> None:
    """Packet with forbidden keys → status BLOCKED."""
    from pymia.smartpyme.service_1_qa_delivery_gate_v1 import (
        evaluate_service_1_qa_delivery_gate_v1,
    )

    # Test diagnosis
    packet_diag = _build_complete_packet()
    packet_diag["diagnosis"] = {"some": "data"}
    result_diag = evaluate_service_1_qa_delivery_gate_v1(packet_diag)
    assert result_diag["status"] == "BLOCKED"

    # Test accounting_result
    packet_acct = _build_complete_packet()
    packet_acct["accounting_result"] = {"margins": []}
    result_acct = evaluate_service_1_qa_delivery_gate_v1(packet_acct)
    assert result_acct["status"] == "BLOCKED"

    # Test strong recommendation
    packet_rec = _build_complete_packet()
    packet_rec["owner_message"] = "Debes urgentemente corregir los precios."
    result_rec = evaluate_service_1_qa_delivery_gate_v1(packet_rec)
    assert result_rec["status"] == "BLOCKED"


# ---------------------------------------------------------------------------
# 9. No importa módulos prohibidos
# ---------------------------------------------------------------------------


def test_does_not_import_forbidden_modules(tmp_path) -> None:
    """Module must not import forbidden modules."""
    import ast
    from pathlib import Path

    module_path = Path(__file__).parent.parent.parent / "pymia" / "smartpyme" / "service_1_qa_delivery_gate_v1.py"
    source = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    forbidden = {
        "pymia.smartpyme.vertical_pipeline",
        "pymia.smartpyme.service_1_boundary_chain_v1",
        "pymia.smartpyme.service_1_fsm_decision_patch_v1",
        "pymia.smartpyme.service_1_pipeline_v1",
        "pymia.smartpyme.service_1_owner_answer_reentry_v1",
        "pymia.smartpyme.service_1_owner_answer_reentry_persistence_v1",
        "pymia.smartpyme.service_1_case_reentry_read_model_v1",
        "openai",
        "chatbot",
    }

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)

    for mod in forbidden:
        assert mod not in imports, f"Module imports forbidden module: {mod}"


# ---------------------------------------------------------------------------
# Additional tests
# ---------------------------------------------------------------------------


def test_returns_required_schema_fields() -> None:
    """Result must have all required schema fields."""
    from pymia.smartpyme.service_1_qa_delivery_gate_v1 import (
        evaluate_service_1_qa_delivery_gate_v1,
    )

    packet = _build_complete_packet()
    result = evaluate_service_1_qa_delivery_gate_v1(packet)

    assert "schema_version" in result
    assert "service_name" in result
    assert "gate_type" in result
    assert "status" in result
    assert "runtime_authorized" in result
    assert "checks" in result
    assert "warnings" in result
    assert "blockers" in result


def test_checks_have_required_fields() -> None:
    """Each check must have check_id, label, status, required."""
    from pymia.smartpyme.service_1_qa_delivery_gate_v1 import (
        evaluate_service_1_qa_delivery_gate_v1,
    )

    packet = _build_complete_packet()
    result = evaluate_service_1_qa_delivery_gate_v1(packet)

    for check in result["checks"]:
        assert "check_id" in check
        assert "label" in check
        assert "status" in check
        assert "required" in check
        assert check["status"] in ("PASS", "FAIL")
