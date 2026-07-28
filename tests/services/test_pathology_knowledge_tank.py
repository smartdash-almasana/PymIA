from pymia.contracts.pathology_contract import PathologySeverity
from pymia.services.pathology_knowledge_tank import LocalPathologyKnowledgeTank


def test_local_pathology_tank_loads_rules_declaratively():
    tank = LocalPathologyKnowledgeTank()
    definition = tank.get_definition("margen_bruto_negativo")
    assert definition is not None
    assert definition.formula_id == "margen_bruto"
    assert definition.severity == PathologySeverity.HIGH
    assert definition.suggested_action == "Revisar costos o precios de venta."

    metadata = tank.get_metadata("margen_bruto_negativo")
    assert metadata.get("source") == "local_chip1"
    assert metadata.get("category") == "rentabilidad"
    assert metadata.get("requires_formula") is True

    evaluator = tank.get_evaluator("margen_bruto_negativo")
    assert evaluator is not None

    unknown_definition = tank.get_definition("UNKNOWN")
    assert unknown_definition is None

    unknown_evaluator = tank.get_evaluator("UNKNOWN")
    assert unknown_evaluator is None
