from pymia.contracts.formula_contract import FormulaInput
from pymia.contracts.pathology_contract import (
    PathologyEvaluationInput,
    PathologyStatus,
    evaluate_pathology,
)
from pymia.services.formula_engine_service import FormulaEngineService
from pymia.services.pathology_engine_service import PathologyEngineService


def _ren_001_result(sale_price: float, costs: float, taxes: float):
    return FormulaEngineService().calculate(
        "REN_001_margen_neto_real",
        [
            FormulaInput(name="sale_price", value=sale_price, source_refs=["ventas:1"]),
            FormulaInput(name="costs", value=costs, source_refs=["costos:1"]),
            FormulaInput(name="taxes", value=taxes, source_refs=["impuestos:1"]),
        ],
    )


def test_engine_detects_negative_ren_001_margin():
    result = PathologyEngineService().evaluate(
        "REN_001",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr1",
            formula_result=_ren_001_result(1000, 900, 200),
        ),
    )

    assert result.status == PathologyStatus.ACTIVE
    assert result.pathology_id == "REN_001"
    assert result.formula_id == "REN_001_margen_neto_real"
    assert result.cliente_id == "pyme_A"
    assert result.source_refs == ["ventas:1", "costos:1", "impuestos:1"]


def test_engine_not_detected_for_positive_ren_001_margin():
    result = PathologyEngineService().evaluate(
        "REN_001",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr2",
            formula_result=_ren_001_result(1000, 600, 100),
        ),
    )

    assert result.status == PathologyStatus.NOT_DETECTED


def test_engine_wrapper_compatibility():
    result = evaluate_pathology(
        "REN_001",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr3",
            formula_result=_ren_001_result(1000, 900, 200),
        ),
    )

    assert result.status == PathologyStatus.ACTIVE


def test_engine_unknown_pathology_pending_data():
    result = PathologyEngineService().evaluate(
        "unknown",
        PathologyEvaluationInput(
            cliente_id="pyme_A",
            formula_result_id="fr4",
            formula_result=_ren_001_result(1000, 600, 100),
        ),
    )

    assert result.status == PathologyStatus.PENDING_DATA
    assert result.metadata["blocking_reason"] == "PATHOLOGY_NOT_SUPPORTED"
