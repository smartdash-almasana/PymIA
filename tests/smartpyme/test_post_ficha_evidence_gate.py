from pymia.smartpyme.post_ficha_evidence_gate import (
    apply_post_ficha_evidence_turn,
    is_post_ficha_evidence_input,
    parse_post_ficha_evidence_input,
)


def _base_context() -> dict:
    return {
        "post_ficha_routing": {
            "intake_id": "intake_test_001",
            "evidence_requests": [
                {
                    "request_id": "req_1",
                    "evidence_type": "sales_records",
                    "description": "Ventas",
                    "reason": "Contrastar",
                    "status": "REQUESTED",
                    "hypothesis_id": "hyp_1",
                    "enables_classification": "excel_diagnostic",
                },
                {
                    "request_id": "req_2",
                    "evidence_type": "price_list",
                    "description": "Lista",
                    "reason": "Contrastar",
                    "status": "REQUESTED",
                    "hypothesis_id": "hyp_1",
                },
            ],
        }
    }


def test_parse_valid_evidence_input() -> None:
    source_kind, evidence_type, source_ref = parse_post_ficha_evidence_input(
        "EVIDENCE::uploaded_file::sales_records::ventas.xlsx"
    )
    assert source_kind == "uploaded_file"
    assert evidence_type == "sales_records"
    assert source_ref == "ventas.xlsx"
    assert is_post_ficha_evidence_input("EVIDENCE::uploaded_file::x::y")


def test_fields_metadata_is_persisted_normalized_and_deduplicated() -> None:
    out, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text=(
            "EVIDENCE::uploaded_file::sales_records::ventas.xlsx"
            "::FIELDS= period, amount,period "
        ),
        previous_context=None,
        updated_context=_base_context(),
    )
    record = out["evidence_records"][0]
    assert record["metadata"] == {"fields": ["period", "amount"]}


def test_input_without_fields_preserves_empty_metadata() -> None:
    out, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::sales_records::ventas.xlsx",
        previous_context=None,
        updated_context=_base_context(),
    )
    assert out["evidence_records"][0]["metadata"] == {}


def test_parse_invalid_evidence_input_fail_closed() -> None:
    try:
        parse_post_ficha_evidence_input("EVIDENCE::uploaded_file::missing_ref")
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "Formato inválido" in str(exc)


def test_rejects_invalid_source_kind() -> None:
    try:
        apply_post_ficha_evidence_turn(
            tenant_id="t1",
            message_text="EVIDENCE::magic_kind::sales_records::ventas.xlsx",
            previous_context=None,
            updated_context=_base_context(),
        )
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "source_kind" in str(exc)


def test_rejects_missing_post_ficha_routing() -> None:
    try:
        apply_post_ficha_evidence_turn(
            tenant_id="t1",
            message_text="EVIDENCE::uploaded_file::sales_records::ventas.xlsx",
            previous_context=None,
            updated_context={},
        )
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "post_ficha_routing" in str(exc)


def test_updates_request_and_calculates_readiness_with_idempotency() -> None:
    ctx = _base_context()
    out1, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::sales_records::ventas.xlsx",
        previous_context=None,
        updated_context=ctx,
    )
    assert len(out1["evidence_records"]) == 1
    assert out1["post_ficha_readiness"]["readiness_state"] == "NEEDS_EVIDENCE"
    assert out1["post_ficha_routing"]["evidence_requests"][0]["hypothesis_id"] == "hyp_1"

    out2, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::sales_records::ventas.xlsx",
        previous_context=out1,
        updated_context=out1,
    )
    assert len(out2["evidence_records"]) == 1

    out3, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::price_list::precios.xlsx",
        previous_context=out2,
        updated_context=out2,
    )
    assert out3["post_ficha_readiness"]["readiness_state"] == "READY_FOR_ANALYSIS"
    assert out3["post_ficha_readiness"]["ready_for_analysis"] is True


def test_non_blocking_request_does_not_prevent_readiness() -> None:
    ctx = _base_context()
    ctx["post_ficha_routing"]["evidence_requests"].append(
        {
            "request_id": "req_optional",
            "evidence_type": "optional_context",
            "description": "Deseable",
            "reason": "Amplía contexto",
            "status": "REQUESTED",
            "hypothesis_id": "hyp_1",
            "blocks_analysis": False,
        }
    )
    out1, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::sales_records::ventas.xlsx",
        previous_context=None,
        updated_context=ctx,
    )
    out2, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::price_list::precios.xlsx",
        previous_context=out1,
        updated_context=out1,
    )
    readiness = out2["post_ficha_readiness"]
    assert readiness["readiness_state"] == "READY_FOR_ANALYSIS"
    assert readiness["ready_for_analysis"] is True
    assert readiness["requested_count"] == 2
    assert readiness["missing_evidence_types"] == []


def test_received_request_without_required_metadata_is_not_satisfied() -> None:
    ctx = _base_context()
    ctx["post_ficha_routing"]["evidence_requests"] = [
        {
            "request_id": "req_required",
            "evidence_type": "sales_records",
            "description": "Ventas",
            "reason": "Contrastar",
            "status": "REQUESTED",
            "hypothesis_id": "hyp_1",
            "blocks_analysis": True,
            "required_fields": ["period", "amount"],
        }
    ]
    out, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::sales_records::ventas.xlsx",
        previous_context=None,
        updated_context=ctx,
    )
    request = out["post_ficha_routing"]["evidence_requests"][0]
    readiness = out["post_ficha_readiness"]
    assert request["status"] == "RECEIVED"
    assert readiness["readiness_state"] == "NEEDS_EVIDENCE"
    assert readiness["received_count"] == 1
    assert readiness["satisfied_count"] == 0


def test_declared_required_metadata_marks_request_satisfied() -> None:
    ctx = _base_context()
    ctx["post_ficha_routing"]["evidence_requests"] = [
        {
            "request_id": "req_required",
            "evidence_type": "sales_records",
            "description": "Ventas",
            "reason": "Contrastar",
            "status": "REQUESTED",
            "hypothesis_id": "hyp_1",
            "blocks_analysis": True,
            "required_fields": ["period", "amount"],
        }
    ]
    out, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::sales_records::ventas.xlsx",
        previous_context=None,
        updated_context=ctx,
        evidence_metadata={"period": "2026-01", "amount": 1000},
    )
    request = out["post_ficha_routing"]["evidence_requests"][0]
    readiness = out["post_ficha_readiness"]
    assert request["status"] == "SATISFIED"
    assert readiness["readiness_state"] == "READY_FOR_ANALYSIS"
    assert readiness["received_count"] == 1
    assert readiness["satisfied_count"] == 1


def test_fields_suffix_marks_request_satisfied_without_file_reading() -> None:
    ctx = _base_context()
    ctx["post_ficha_routing"]["evidence_requests"] = [
        {
            "request_id": "req_required",
            "evidence_type": "sales_records",
            "description": "Ventas",
            "reason": "Contrastar",
            "status": "REQUESTED",
            "hypothesis_id": "hyp_1",
            "blocks_analysis": True,
            "required_fields": ["period", "amount"],
        }
    ]
    out, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text=(
            "EVIDENCE::uploaded_file::sales_records::does-not-exist.xlsx"
            "::FIELDS=period,amount"
        ),
        previous_context=None,
        updated_context=ctx,
    )
    assert out["evidence_records"][0]["metadata"] == {"fields": ["period", "amount"]}
    assert out["post_ficha_routing"]["evidence_requests"][0]["status"] == "SATISFIED"
    assert out["post_ficha_readiness"]["ready_for_analysis"] is True


def test_incomplete_fields_suffix_leaves_request_received() -> None:
    ctx = _base_context()
    ctx["post_ficha_routing"]["evidence_requests"] = [
        {
            "request_id": "req_required",
            "evidence_type": "sales_records",
            "description": "Ventas",
            "reason": "Contrastar",
            "status": "REQUESTED",
            "hypothesis_id": "hyp_1",
            "blocks_analysis": True,
            "required_fields": ["period", "amount"],
        }
    ]
    out, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::sales_records::ventas.xlsx::FIELDS=period",
        previous_context=None,
        updated_context=ctx,
    )
    assert out["post_ficha_routing"]["evidence_requests"][0]["status"] == "RECEIVED"
    assert out["post_ficha_readiness"]["readiness_state"] == "NEEDS_EVIDENCE"


def test_idempotent_resend_merges_declared_fields() -> None:
    ctx = _base_context()
    ctx["post_ficha_routing"]["evidence_requests"] = [
        {
            "request_id": "req_required",
            "evidence_type": "sales_records",
            "description": "Ventas",
            "reason": "Contrastar",
            "status": "REQUESTED",
            "hypothesis_id": "hyp_1",
            "blocks_analysis": True,
            "required_fields": ["period", "amount"],
        }
    ]
    out1, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::sales_records::ventas.xlsx::FIELDS=period",
        previous_context=None,
        updated_context=ctx,
    )
    out2, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::sales_records::ventas.xlsx::FIELDS=amount",
        previous_context=out1,
        updated_context=out1,
    )
    assert len(out2["evidence_records"]) == 1
    assert out2["evidence_records"][0]["metadata"] == {"fields": ["period", "amount"]}
    assert out2["post_ficha_routing"]["evidence_requests"][0]["status"] == "SATISFIED"


# --- Integración con document_parser_front ---

import ast
from unittest.mock import patch, MagicMock
from pymia.smartpyme.parsed_document_metadata import PARSE_STATUS_FAILED

# 1. Si input trae FIELDS=..., no se invoca parse_document_to_metadata.
@patch("pymia.smartpyme.post_ficha_evidence_gate.parse_document_to_metadata")
def test_fields_suffix_skips_document_parser_front(mock_parse):
    ctx = _base_context()
    apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text=(
            "EVIDENCE::uploaded_file::sales_records::ventas.xlsx"
            "::FIELDS=period,amount"
        ),
        previous_context=None,
        updated_context=ctx,
    )
    mock_parse.assert_not_called()

# 2. Si no trae FIELDS y source_ref es local existente, EvidenceRecord.metadata recibe ParsedDocumentMetadata.to_dict().
@patch("pymia.smartpyme.post_ficha_evidence_gate.Path.exists")
@patch("pymia.smartpyme.post_ficha_evidence_gate.parse_document_to_metadata")
def test_document_parser_front_enriches_metadata_if_no_fields(mock_parse, mock_exists):
    mock_exists.return_value = True
    mock_metadata = MagicMock()
    mock_metadata.to_dict.return_value = {"file_type": "xlsx", "fields": ["ventas"]}
    mock_parse.return_value = mock_metadata
    
    ctx = _base_context()
    out, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::sales_records::ventas.xlsx",
        previous_context=None,
        updated_context=ctx,
    )
    
    mock_parse.assert_called_once()
    assert out["evidence_records"][0]["metadata"]["file_type"] == "xlsx"
    assert out["evidence_records"][0]["metadata"]["fields"] == ["ventas"]

# 3. Si parser parsea OK y fields cubren required_fields, request pasa a SATISFIED.
@patch("pymia.smartpyme.post_ficha_evidence_gate.Path.exists")
@patch("pymia.smartpyme.post_ficha_evidence_gate.parse_document_to_metadata")
def test_document_parser_front_satisfies_request_if_fields_cover_required(mock_parse, mock_exists):
    mock_exists.return_value = True
    mock_metadata = MagicMock()
    mock_metadata.to_dict.return_value = {"file_type": "pdf", "fields": ["period", "amount"]}
    mock_parse.return_value = mock_metadata
    
    ctx = _base_context()
    ctx["post_ficha_routing"]["evidence_requests"] = [
        {
            "request_id": "req_required",
            "evidence_type": "sales_records",
            "status": "REQUESTED",
            "blocks_analysis": True,
            "required_fields": ["period", "amount"],
        }
    ]
    
    out, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::sales_records::ventas.pdf",
        previous_context=None,
        updated_context=ctx,
    )
    
    assert out["post_ficha_routing"]["evidence_requests"][0]["status"] == "SATISFIED"
    assert out["post_ficha_readiness"]["readiness_state"] == "READY_FOR_ANALYSIS"

# 4. Si parser parsea pero faltan required_fields, queda RECEIVED / NEEDS_EVIDENCE.
@patch("pymia.smartpyme.post_ficha_evidence_gate.Path.exists")
@patch("pymia.smartpyme.post_ficha_evidence_gate.parse_document_to_metadata")
def test_document_parser_front_leaves_received_if_fields_missing(mock_parse, mock_exists):
    mock_exists.return_value = True
    mock_metadata = MagicMock()
    mock_metadata.to_dict.return_value = {"file_type": "docx", "fields": ["period"]}
    mock_parse.return_value = mock_metadata
    
    ctx = _base_context()
    ctx["post_ficha_routing"]["evidence_requests"] = [
        {
            "request_id": "req_required",
            "evidence_type": "sales_records",
            "status": "REQUESTED",
            "blocks_analysis": True,
            "required_fields": ["period", "amount"],
        }
    ]
    
    out, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::sales_records::ventas.docx",
        previous_context=None,
        updated_context=ctx,
    )
    
    assert out["post_ficha_routing"]["evidence_requests"][0]["status"] == "RECEIVED"
    assert out["post_ficha_readiness"]["readiness_state"] == "NEEDS_EVIDENCE"

# 5. Si source_ref no existe, no rompe flujo.
@patch("pymia.smartpyme.post_ficha_evidence_gate.Path.exists")
@patch("pymia.smartpyme.post_ficha_evidence_gate.parse_document_to_metadata")
def test_missing_source_ref_does_not_break_flow(mock_parse, mock_exists):
    mock_exists.return_value = False
    
    ctx = _base_context()
    ctx["post_ficha_routing"]["evidence_requests"] = [
        {
            "request_id": "req_required",
            "evidence_type": "sales_records",
            "status": "REQUESTED",
            "blocks_analysis": True,
            "required_fields": ["period", "amount"],
        }
    ]
    
    out, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::sales_records::missing.xlsx",
        previous_context=None,
        updated_context=ctx,
    )
    
    mock_parse.assert_not_called()
    assert out["post_ficha_routing"]["evidence_requests"][0]["status"] == "RECEIVED"

# 6. Si parser falla, se conserva metadata fail-closed con parse_status=FAILED y warnings.
@patch("pymia.smartpyme.post_ficha_evidence_gate.Path.exists")
@patch("pymia.smartpyme.post_ficha_evidence_gate.parse_document_to_metadata")
def test_document_parser_front_failure_produces_fail_closed_metadata(mock_parse, mock_exists):
    mock_exists.return_value = True
    mock_parse.side_effect = Exception("simulated crash")
    
    ctx = _base_context()
    out, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::sales_records::ventas.xlsx",
        previous_context=None,
        updated_context=ctx,
    )
    
    meta = out["evidence_records"][0]["metadata"]
    assert meta["parse_status"] == PARSE_STATUS_FAILED
    assert any("document_parser_front_error" in w for w in meta["warnings"])

# 7. No se usa xlsx_document_metadata_adapter, docling, tools/excel_evidence.py ni ClinicalConversationalPort.
def test_post_ficha_evidence_gate_ast_rules():
    with open("pymia/smartpyme/post_ficha_evidence_gate.py", "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    forbidden_imports = {
        "xlsx_document_metadata_adapter",
        "docling",
        "excel_evidence",
        "ClinicalConversationalPort",
        "formula",
        "diagnostico",
        "prepare_runtime_execution",
        "RuntimeExecutionCandidate"
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not any(forbidden in alias.name for forbidden in forbidden_imports), f"Forbidden import found: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                assert not any(forbidden in node.module for forbidden in forbidden_imports), f"Forbidden import from found: {node.module}"
            for alias in node.names:
                assert not any(forbidden in alias.name for forbidden in forbidden_imports), f"Forbidden imported name found: {alias.name}"


# --- Proyección de analysis_readiness ---

from pymia.smartpyme.runtime_bridge import prepare_runtime_execution

def test_analysis_readiness_is_projected_and_not_ready_if_missing_evidence():
    ctx = _base_context()
    # base context has 2 requested evidences, so 1 won't be enough
    out, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::sales_records::ventas.xlsx",
        previous_context=None,
        updated_context=ctx,
    )
    assert "analysis_readiness" in out
    ar = out["analysis_readiness"]
    assert "tenant_id" in ar
    assert "intake_id" in ar
    assert "status" in ar
    assert "can_execute" in ar
    assert "runtime_classification" in ar
    assert "matched_evidence_ids" in ar
    assert "warnings" in ar
    assert "audit_notes" in ar
    assert ar["status"] == "NEEDS_EVIDENCE"
    assert ar["can_execute"] is False


def test_analysis_readiness_is_projected_and_ready_if_all_satisfied():
    ctx = _base_context()
    out1, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::sales_records::ventas.xlsx",
        previous_context=None,
        updated_context=ctx,
    )
    out2, _ = apply_post_ficha_evidence_turn(
        tenant_id="t1",
        message_text="EVIDENCE::uploaded_file::price_list::precios.xlsx",
        previous_context=out1,
        updated_context=out1,
    )
    ar = out2["analysis_readiness"]
    assert ar["status"] == "READY_FOR_ANALYSIS"
    assert ar["can_execute"] is True
    # 5. Verify it is consumable by prepare_runtime_execution
    candidate = prepare_runtime_execution(ar)
    assert candidate.intake_id == "intake_test_001"
    assert candidate.tenant_id == "t1"
    assert candidate.can_dispatch is True
