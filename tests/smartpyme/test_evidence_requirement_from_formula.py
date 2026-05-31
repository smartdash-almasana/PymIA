"""
Tests for derive_evidence_requirements_from_formulas.

Verifica:
- import smoke
- derivación básica desde candidate_formula_ids
- lista vacía si no hay formula_ids
- deduplicación por evidence_type
- blocks_analysis=True para CALCULABLE, False para CALCULABLE_CON_SUPUESTOS
- priority derivada de priority_robustez
- formula_id trazable en el requirement
- hypothesis_id propagado
- catálogo inyectable para tests (sin I/O)
- formula_id desconocido ignorado (no crash)
- inputs inválidos levantan ValueError
"""
from __future__ import annotations

import pytest

from pymia.smartpyme.operational_hypothesis import (
    OperationalHypothesis,
    HypothesisStatus,
    derive_evidence_requirements_from_formulas,
)
from pymia.smartpyme.evidence_requirement import EvidenceRequirement
from pymia.contracts.catalogs_v1 import FormulaCatalogEntryV1, FormulaCatalogV1


# ---------------------------------------------------------------------------
# Catálogo mínimo de prueba (inyectado, sin I/O)
# ---------------------------------------------------------------------------

def _make_catalog(formulas: list[dict]) -> FormulaCatalogV1:
    return FormulaCatalogV1(
        catalog_version="test-1.0",
        formulas=[FormulaCatalogEntryV1(**f) for f in formulas],
    )


_FORMULA_LIQ = {
    "formula_id": "LIQ_001_vendido_cobrado",
    "pathology_code": "LIQ_001",
    "name": "Descalce vendido cobrado",
    "expression": "sold_amount - collected_amount",
    "display_expression": "Vendido - Cobrado",
    "category": "liquidez",
    "required_variables": ["sold_amount", "collected_amount"],
    "required_evidence": ["ventas_del_periodo", "cobranzas_del_periodo"],
    "output_unit": "currency",
    "calculation_state": "CALCULABLE",
    "priority_mvp": "alta",
    "priority_robustez": "alta",
    "interpretation": "test",
}

_FORMULA_REN = {
    "formula_id": "REN_001_margen_neto_real",
    "pathology_code": "REN_001",
    "name": "Margen neto real",
    "expression": "((p-c-t)/p)*100",
    "display_expression": "((PV - Costos - Impuestos) / PV) × 100",
    "category": "rentabilidad",
    "required_variables": ["sale_price", "costs", "taxes"],
    "required_evidence": ["ventas_del_periodo", "costos_directos"],  # ventas_del_periodo duplicado
    "output_unit": "percentage",
    "calculation_state": "CALCULABLE_CON_SUPUESTOS",
    "priority_mvp": "alta",
    "priority_robustez": "media",
    "interpretation": "test",
}


def _make_hypothesis(
    *,
    hypothesis_id: str = "hyp_test",
    candidate_formula_ids: list[str] | None = None,
) -> OperationalHypothesis:
    return OperationalHypothesis(
        hypothesis_id=hypothesis_id,
        tenant_id="t1",
        intake_id="intake_test",
        formulation="Hipótesis de prueba",
        source="test",
        domain="liquidez",
        candidate_formula_ids=candidate_formula_ids or [],
    )


# ---------------------------------------------------------------------------
# Import smoke
# ---------------------------------------------------------------------------

class TestImportSmoke:
    def test_import(self):
        from pymia.smartpyme.operational_hypothesis import derive_evidence_requirements_from_formulas  # noqa: F401
        assert callable(derive_evidence_requirements_from_formulas)

    def test_evidence_requirement_has_formula_id(self):
        req = EvidenceRequirement(
            requirement_id="r1",
            tenant_id="t1",
            intake_id="i1",
            hypothesis_id="h1",
            evidence_type="excel_ventas",
            description="desc",
            required_fields=[],
            reason="reason",
            blocks_analysis=True,
            priority=1,
            telegram_message="msg",
            formula_id="LIQ_001_vendido_cobrado",
        )
        assert req.formula_id == "LIQ_001_vendido_cobrado"


# ---------------------------------------------------------------------------
# Casos nominales
# ---------------------------------------------------------------------------

class TestDeriveBasic:
    def test_empty_formula_ids_returns_empty(self):
        hyp = _make_hypothesis(candidate_formula_ids=[])
        result = derive_evidence_requirements_from_formulas(
            hyp, tenant_id="t1", intake_id="i1",
            formula_catalog=_make_catalog([]),
        )
        assert result == []

    def test_single_formula_returns_requirements(self):
        catalog = _make_catalog([_FORMULA_LIQ])
        hyp = _make_hypothesis(candidate_formula_ids=["LIQ_001_vendido_cobrado"])
        result = derive_evidence_requirements_from_formulas(
            hyp, tenant_id="t1", intake_id="i1", formula_catalog=catalog,
        )
        assert len(result) == 2  # ventas_del_periodo + cobranzas_del_periodo
        types = {r.evidence_type for r in result}
        assert types == {"ventas_del_periodo", "cobranzas_del_periodo"}

    def test_returns_list_of_evidence_requirements(self):
        catalog = _make_catalog([_FORMULA_LIQ])
        hyp = _make_hypothesis(candidate_formula_ids=["LIQ_001_vendido_cobrado"])
        result = derive_evidence_requirements_from_formulas(
            hyp, tenant_id="t1", intake_id="i1", formula_catalog=catalog,
        )
        for r in result:
            assert isinstance(r, EvidenceRequirement)


class TestDeduplication:
    def test_duplicate_evidence_type_across_formulas_deduplicated(self):
        """ventas_del_periodo aparece en ambas fórmulas → solo un req."""
        catalog = _make_catalog([_FORMULA_LIQ, _FORMULA_REN])
        hyp = _make_hypothesis(
            candidate_formula_ids=["LIQ_001_vendido_cobrado", "REN_001_margen_neto_real"]
        )
        result = derive_evidence_requirements_from_formulas(
            hyp, tenant_id="t1", intake_id="i1", formula_catalog=catalog,
        )
        types = [r.evidence_type for r in result]
        assert len(types) == len(set(types)), "No debe haber evidence_types duplicados"

    def test_dedup_first_formula_wins_formula_id(self):
        """ventas_del_periodo es reclamado por LIQ primero."""
        catalog = _make_catalog([_FORMULA_LIQ, _FORMULA_REN])
        hyp = _make_hypothesis(
            candidate_formula_ids=["LIQ_001_vendido_cobrado", "REN_001_margen_neto_real"]
        )
        result = derive_evidence_requirements_from_formulas(
            hyp, tenant_id="t1", intake_id="i1", formula_catalog=catalog,
        )
        ventas_req = next(r for r in result if r.evidence_type == "ventas_del_periodo")
        assert ventas_req.formula_id == "LIQ_001_vendido_cobrado"


class TestBlocksAnalysis:
    def test_calculable_formula_blocks_analysis_true(self):
        catalog = _make_catalog([_FORMULA_LIQ])
        hyp = _make_hypothesis(candidate_formula_ids=["LIQ_001_vendido_cobrado"])
        result = derive_evidence_requirements_from_formulas(
            hyp, tenant_id="t1", intake_id="i1", formula_catalog=catalog,
        )
        assert all(r.blocks_analysis is True for r in result)

    def test_calculable_con_supuestos_blocks_analysis_false(self):
        catalog = _make_catalog([_FORMULA_REN])
        hyp = _make_hypothesis(candidate_formula_ids=["REN_001_margen_neto_real"])
        result = derive_evidence_requirements_from_formulas(
            hyp, tenant_id="t1", intake_id="i1", formula_catalog=catalog,
        )
        assert all(r.blocks_analysis is False for r in result)


class TestPriority:
    def test_priority_alta_maps_to_1(self):
        catalog = _make_catalog([_FORMULA_LIQ])
        hyp = _make_hypothesis(candidate_formula_ids=["LIQ_001_vendido_cobrado"])
        result = derive_evidence_requirements_from_formulas(
            hyp, tenant_id="t1", intake_id="i1", formula_catalog=catalog,
        )
        assert all(r.priority == 1 for r in result)

    def test_priority_media_maps_to_2(self):
        catalog = _make_catalog([_FORMULA_REN])
        hyp = _make_hypothesis(candidate_formula_ids=["REN_001_margen_neto_real"])
        result = derive_evidence_requirements_from_formulas(
            hyp, tenant_id="t1", intake_id="i1", formula_catalog=catalog,
        )
        # costos_directos es exclusivo de REN (media)
        costos_req = next(r for r in result if r.evidence_type == "costos_directos")
        assert costos_req.priority == 2


class TestTrazabilidad:
    def test_formula_id_trazable_in_requirement(self):
        catalog = _make_catalog([_FORMULA_LIQ])
        hyp = _make_hypothesis(candidate_formula_ids=["LIQ_001_vendido_cobrado"])
        result = derive_evidence_requirements_from_formulas(
            hyp, tenant_id="t1", intake_id="i1", formula_catalog=catalog,
        )
        for r in result:
            assert r.formula_id == "LIQ_001_vendido_cobrado"

    def test_hypothesis_id_propagated(self):
        catalog = _make_catalog([_FORMULA_LIQ])
        hyp = _make_hypothesis(
            hypothesis_id="hyp_custom_id",
            candidate_formula_ids=["LIQ_001_vendido_cobrado"],
        )
        result = derive_evidence_requirements_from_formulas(
            hyp, tenant_id="t1", intake_id="i1", formula_catalog=catalog,
        )
        for r in result:
            assert r.hypothesis_id == "hyp_custom_id"

    def test_tenant_id_propagated(self):
        catalog = _make_catalog([_FORMULA_LIQ])
        hyp = _make_hypothesis(candidate_formula_ids=["LIQ_001_vendido_cobrado"])
        result = derive_evidence_requirements_from_formulas(
            hyp, tenant_id="tenant_xyz", intake_id="i1", formula_catalog=catalog,
        )
        for r in result:
            assert r.tenant_id == "tenant_xyz"

    def test_intake_id_propagated(self):
        catalog = _make_catalog([_FORMULA_LIQ])
        hyp = _make_hypothesis(candidate_formula_ids=["LIQ_001_vendido_cobrado"])
        result = derive_evidence_requirements_from_formulas(
            hyp, tenant_id="t1", intake_id="intake_abc", formula_catalog=catalog,
        )
        for r in result:
            assert r.intake_id == "intake_abc"

    def test_requirement_id_contains_intake_and_formula(self):
        catalog = _make_catalog([_FORMULA_LIQ])
        hyp = _make_hypothesis(candidate_formula_ids=["LIQ_001_vendido_cobrado"])
        result = derive_evidence_requirements_from_formulas(
            hyp, tenant_id="t1", intake_id="intake_abc", formula_catalog=catalog,
        )
        for r in result:
            assert "intake_abc" in r.requirement_id
            assert "LIQ_001" in r.requirement_id


class TestEdgeCases:
    def test_unknown_formula_id_is_ignored(self):
        catalog = _make_catalog([_FORMULA_LIQ])
        hyp = _make_hypothesis(candidate_formula_ids=["NONEXISTENT_formula_999"])
        result = derive_evidence_requirements_from_formulas(
            hyp, tenant_id="t1", intake_id="i1", formula_catalog=catalog,
        )
        assert result == []

    def test_mixed_known_unknown_formula_ids(self):
        catalog = _make_catalog([_FORMULA_LIQ])
        hyp = _make_hypothesis(
            candidate_formula_ids=["NONEXISTENT", "LIQ_001_vendido_cobrado"]
        )
        result = derive_evidence_requirements_from_formulas(
            hyp, tenant_id="t1", intake_id="i1", formula_catalog=catalog,
        )
        assert len(result) == 2  # Solo los de LIQ

    def test_formula_with_empty_required_evidence(self):
        formula_no_evidence = {**_FORMULA_LIQ, "required_evidence": []}
        catalog = _make_catalog([formula_no_evidence])
        hyp = _make_hypothesis(candidate_formula_ids=["LIQ_001_vendido_cobrado"])
        result = derive_evidence_requirements_from_formulas(
            hyp, tenant_id="t1", intake_id="i1", formula_catalog=catalog,
        )
        assert result == []

    def test_output_is_json_serializable(self):
        import json
        catalog = _make_catalog([_FORMULA_LIQ])
        hyp = _make_hypothesis(candidate_formula_ids=["LIQ_001_vendido_cobrado"])
        result = derive_evidence_requirements_from_formulas(
            hyp, tenant_id="t1", intake_id="i1", formula_catalog=catalog,
        )
        for r in result:
            serialized = json.dumps(r.to_dict())
            assert isinstance(serialized, str)


class TestInputValidation:
    def test_invalid_hypothesis_type_raises(self):
        with pytest.raises(ValueError, match="hypothesis"):
            derive_evidence_requirements_from_formulas(
                "not_a_hypothesis",  # type: ignore
                tenant_id="t1",
                intake_id="i1",
            )

    def test_empty_tenant_id_raises(self):
        hyp = _make_hypothesis()
        with pytest.raises(ValueError, match="tenant_id"):
            derive_evidence_requirements_from_formulas(hyp, tenant_id="", intake_id="i1")

    def test_whitespace_tenant_id_raises(self):
        hyp = _make_hypothesis()
        with pytest.raises(ValueError, match="tenant_id"):
            derive_evidence_requirements_from_formulas(hyp, tenant_id="  ", intake_id="i1")

    def test_empty_intake_id_raises(self):
        hyp = _make_hypothesis()
        with pytest.raises(ValueError, match="intake_id"):
            derive_evidence_requirements_from_formulas(hyp, tenant_id="t1", intake_id="")

    def test_whitespace_intake_id_raises(self):
        hyp = _make_hypothesis()
        with pytest.raises(ValueError, match="intake_id"):
            derive_evidence_requirements_from_formulas(hyp, tenant_id="t1", intake_id="  ")
