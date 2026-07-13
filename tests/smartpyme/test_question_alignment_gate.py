from pathlib import Path

from pymia.smartpyme.question_alignment_gate import (
    AXIS_CAJA_LIQUIDEZ,
    AXIS_DESCONOCIDO,
    AXIS_STOCK_REPOSICION,
    AXIS_VENTAS_MARGEN,
    align_next_question,
    detect_owner_axis,
    detect_question_axis,
    load_question_alignment_rules,
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


def test_question_alignment_rules_json_loads_valid_contract():
    contract_path = Path(__file__).resolve().parents[2] / "pymia" / "contracts" / "question_alignment_v1.json"
    assert contract_path.exists()

    rules = load_question_alignment_rules()
    assert rules["schema_version"] == "1.0"
    assert rules["status"] == "ACTIVE"
    assert AXIS_CAJA_LIQUIDEZ in rules["owner_keywords"]
    assert rules["formula_prefix_axis"]["LIQ"] == AXIS_CAJA_LIQUIDEZ
    assert rules["pathology_axis"]["INV_001"] == AXIS_STOCK_REPOSICION
    assert {
        "owner_axis": AXIS_CAJA_LIQUIDEZ,
        "question_axis": AXIS_STOCK_REPOSICION,
        "status": "MISALIGNED",
    } in rules["misalignment_rules"]
    assert "misaligned_reconduction" in rules["copy_templates"]
    assert "misaligned_technical_reference" in rules["copy_templates"]


# --- detect_question_axis ---

def test_question_axis_from_formula_prefix():
    assert detect_question_axis({"formula_id": "LIQ_001"}) == AXIS_CAJA_LIQUIDEZ
    assert detect_question_axis({"formula_id": "INV_001"}) == AXIS_STOCK_REPOSICION


def test_question_axis_from_pathology_code():
    assert detect_question_axis({"pathology_code": "LIQ_002"}) == AXIS_CAJA_LIQUIDEZ


def test_question_axis_unknown_for_unmapped():
    assert detect_question_axis({"formula_id": "OPE_001"}) == AXIS_DESCONOCIDO


def test_question_alignment_uses_declarative_rules(monkeypatch):
    monkeypatch.setattr(
        "pymia.smartpyme.question_alignment_gate.load_question_alignment_rules",
        lambda: {
            "owner_keywords": {
                AXIS_CAJA_LIQUIDEZ: ["tesoreria urgente"],
            },
            "formula_prefix_axis": {
                "TES": AXIS_STOCK_REPOSICION,
            },
            "pathology_axis": {},
            "misalignment_rules": [
                {
                    "owner_axis": AXIS_CAJA_LIQUIDEZ,
                    "question_axis": AXIS_STOCK_REPOSICION,
                    "status": "MISALIGNED",
                }
            ],
            "copy_templates": {
                "misaligned_reconduction": "Reconducir {declared_axis} antes de {question_axis}.",
                "misaligned_technical_reference": "Referencia {declared_axis}/{question_axis}",
                "no_candidates_reference": "sin candidatos para evaluar",
            },
        },
    )

    result = align_next_question(
        "tesoreria urgente",
        [{
            "formula_id": "TES_001",
            "pathology_code": "",
            "next_audit_questions": ["¿Podés compartir el dato técnico?"],
        }],
    )

    assert detect_owner_axis("tesoreria urgente") == AXIS_CAJA_LIQUIDEZ
    assert detect_question_axis({"formula_id": "TES_001"}) == AXIS_STOCK_REPOSICION
    assert result["status"] == "MISALIGNED"
    assert result["final_question_text"] == "Reconducir caja_liquidez antes de stock_reposicion."
    assert result["technical_reference"] == "Referencia caja_liquidez/stock_reposicion"


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


def test_caja_message_uses_declarative_reconduction_copy():
    result = align_next_question("no me cierra la caja", [_stock_candidate()])
    assert "caja/liquidez" in result["final_question_text"]
    assert "pregunta técnica sobre stock" in result["final_question_text"]
    assert result["technical_reference"] == "Referencia técnica: reconducción_axis_caja_liquidez"
