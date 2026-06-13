from pymia.smartpyme.question_alignment_gate import (
    AXIS_CAJA_LIQUIDEZ,
    AXIS_COSTOS_PROVEEDORES,
    AXIS_DESCONOCIDO,
    AXIS_STOCK_REPOSICION,
    AXIS_VENTAS_MARGEN,
    align_next_question,
    detect_owner_axis,
    detect_question_axis,
)


def _caja_candidate() -> dict:
    return {
        "formula_id": "LIQ_001",
        "pathology_code": "LIQ_001",
        "next_audit_questions": ["¿Podés enviarnos el saldo inicial de caja y banco?"],
    }


def _stock_candidate() -> dict:
    return {
        "formula_id": "INV_001",
        "pathology_code": "INV_001",
        "next_audit_questions": ["¿Podés compartir los tiempos de reposición de proveedores?"],
    }


def _costos_candidate() -> dict:
    return {
        "formula_id": "REN_001",
        "pathology_code": "REN_001",
        "next_audit_questions": ["¿Podés detallar los costos directos de tus productos?"],
    }


# --- detect_owner_axis ---

def test_owner_axis_detects_caja_liquidez():
    assert detect_owner_axis("no me cierra la caja") == AXIS_CAJA_LIQUIDEZ


def test_owner_axis_detects_ventas_margen():
    assert detect_owner_axis("vendo mucho pero no me queda margen") == AXIS_VENTAS_MARGEN


def test_owner_axis_returns_unknown_for_empty():
    assert detect_owner_axis("") == AXIS_DESCONOCIDO


def test_owner_axis_returns_unknown_for_ambiguous():
    assert detect_owner_axis("quiero analizar mi negocio") == AXIS_DESCONOCIDO


# --- detect_question_axis ---

def test_question_axis_from_formula_prefix():
    assert detect_question_axis({"formula_id": "LIQ_001"}) == AXIS_CAJA_LIQUIDEZ
    assert detect_question_axis({"formula_id": "INV_001"}) == AXIS_STOCK_REPOSICION


def test_question_axis_from_pathology_code():
    assert detect_question_axis({"pathology_code": "LIQ_002"}) == AXIS_CAJA_LIQUIDEZ


def test_question_axis_unknown_for_unmapped():
    assert detect_question_axis({"formula_id": "OPE_001"}) == AXIS_DESCONOCIDO


# --- align_next_question ---

def test_caja_message_stock_candidate_is_misaligned():
    result = align_next_question("no me cierra la caja", [_stock_candidate()])
    assert result["status"] == "MISALIGNED"
    assert result["declared_axis"] == AXIS_CAJA_LIQUIDEZ
    assert result["question_axis"] == AXIS_STOCK_REPOSICION


def test_caja_message_caja_candidate_is_aligned():
    result = align_next_question("no me cierra la caja", [_caja_candidate()])
    assert result["status"] == "ALIGNED"
    assert result["declared_axis"] == AXIS_CAJA_LIQUIDEZ
    assert result["question_axis"] == AXIS_CAJA_LIQUIDEZ


def test_ventas_margen_to_costos_is_aligned():
    result = align_next_question("vendo mucho pero no me queda margen", [_costos_candidate()])
    assert result["status"] == "ALIGNED"


def test_empty_message_returns_unknown():
    result = align_next_question("", [_stock_candidate()])
    assert result["status"] == "UNKNOWN"


def test_ambiguous_message_returns_unknown():
    result = align_next_question("quiero analizar mi negocio", [_stock_candidate()])
    assert result["status"] == "UNKNOWN"


def test_no_candidates_returns_unknown():
    result = align_next_question("no me cierra la caja", [])
    assert result["status"] == "UNKNOWN"
    assert result["question_axis"] == AXIS_DESCONOCIDO


def test_caja_message_carries_question_text():
    result = align_next_question("no me cierra la caja", [_stock_candidate()])
    assert "reposición" in result["final_question_text"]
    assert result["technical_reference"] == "INV_001"
