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
