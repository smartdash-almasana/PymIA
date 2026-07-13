import pytest

from pymia.contracts.pathology_contract import PathologyFinding, PathologySeverity, PathologyStatus
from pymia.services.pathology_adapters import (
    PathologyAdapterError,
    pathology_finding_to_finding_record,
)


def test_adapter_converts_active_pathology_to_finding_record():
    pathology = PathologyFinding(
        cliente_id="pyme_A",
        pathology_id="REN_001",
        formula_result_id="fr1",
        formula_id="REN_001_margen_neto_real",
        status=PathologyStatus.ACTIVE,
        severity=PathologySeverity.HIGH,
        suggested_action="Revisar costos, impuestos o precios.",
        source_refs=["ventas:1", "costos:1", "impuestos:1"],
        explanation="Margen neto real negativo.",
        metadata={"measured_difference": {"REN_001_margen_neto_real": -10.0}},
    )

    finding = pathology_finding_to_finding_record(pathology)

    assert finding.entity == "pyme_A"
    assert finding.finding_type == "REN_001"
    assert finding.evidence_used == ["ventas:1", "costos:1", "impuestos:1"]
    assert finding.compared_sources == ["ventas:1", "costos:1", "impuestos:1"]
    assert finding.measured_difference == {"REN_001_margen_neto_real": -10.0}


def test_adapter_blocks_without_source_refs():
    pathology = PathologyFinding(
        cliente_id="pyme_A",
        pathology_id="REN_001",
        formula_result_id="fr1",
        formula_id="REN_001_margen_neto_real",
        status=PathologyStatus.ACTIVE,
        severity=PathologySeverity.HIGH,
        source_refs=[],
        explanation="Margen neto real negativo.",
    )

    with pytest.raises(PathologyAdapterError, match="SOURCE_REFS_REQUIRED"):
        pathology_finding_to_finding_record(pathology)


def test_adapter_blocks_not_detected_pathology():
    pathology = PathologyFinding(
        cliente_id="pyme_A",
        pathology_id="REN_001",
        formula_result_id="fr1",
        formula_id="REN_001_margen_neto_real",
        status=PathologyStatus.NOT_DETECTED,
        source_refs=["ventas:1"],
        explanation="No detectada.",
    )

    with pytest.raises(PathologyAdapterError, match="ONLY_ACTIVE_PATHOLOGIES_CAN_BECOME_FINDINGS"):
        pathology_finding_to_finding_record(pathology)
