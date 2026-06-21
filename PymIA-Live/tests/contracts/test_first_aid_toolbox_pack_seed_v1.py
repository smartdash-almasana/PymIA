"""
Test de contrato para First Aid Toolbox Pack Seed V1.

Este test valida que el artefacto candidato reconciliado
(first_aid_toolbox_pack_seed_v1.json) cumple con todos los campos
obligatorios declarados en el contrato documental.

AUDIT ONLY:
- No toca runtime
- No ejecuta herramientas
- No modifica código
- Solo valida estructura documental

v2: Actualizado para validar la resolución de los 2 MISSING_COMPONENT
    (gastos_triage y proveedores_precio_variacion_triage) mediante
    creación de componentes nuevos específicos de triage FIRST_AID.
    Decisión documentada en FIRST_AID_TRIAGE_COMPONENTS_DECISION_V1.md.
"""
import json
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def seed_path() -> Path:
    """Retorna el path al archivo seed."""
    return Path(__file__).parent.parent.parent / "pymia" / "contracts" / "first_aid_toolbox_pack_seed_v1.json"


@pytest.fixture(scope="module")
def seed_data(seed_path: Path) -> dict:
    """Carga y retorna el contenido del seed JSON."""
    assert seed_path.exists(), f"Seed file not found: {seed_path}"
    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


class TestSeedStructure:
    """Valida estructura básica del seed."""

    def test_seed_is_valid_json(self, seed_data: dict):
        """El seed debe ser JSON válido y cargable."""
        assert isinstance(seed_data, dict)
        assert len(seed_data) > 0

    def test_seed_has_all_mandatory_top_level_fields(self, seed_data: dict):
        """El seed debe tener todos los campos obligatorios de primer nivel."""
        mandatory_fields = [
            "schema_version",
            "seed_id",
            "contract_id",
            "status",
            "implementation_authorized",
            "runtime_authorized",
            "version",
            "source",
            "scope",
            "owner_facing_name",
            "summary",
            "allowed_service_depth",
            "requires_minimal_case_file_layer",
            "components",
            "compositions",
            "formula_refs",
            "restricted_formula_refs",
            "validation_refs",
            "tool_refs",
            "tool_component_mapping",
            "evidence_requirements",
            "owner_facing_limitations",
            "forbidden_claims",
            "escalation_rules",
            "notes",
        ]
        for field in mandatory_fields:
            assert field in seed_data, f"Missing mandatory field: {field}"


class TestSeedValues:
    """Valida valores obligatorios específicos."""

    def test_seed_id_is_correct(self, seed_data: dict):
        """seed_id debe ser FIRST_AID_TOOLBOX_PACK_SEED_V1."""
        assert seed_data["seed_id"] == "FIRST_AID_TOOLBOX_PACK_SEED_V1"

    def test_contract_id_is_correct(self, seed_data: dict):
        """contract_id debe ser FIRST_AID_TOOLBOX_PACK_CONTRACT_V1."""
        assert seed_data["contract_id"] == "FIRST_AID_TOOLBOX_PACK_CONTRACT_V1"

    def test_status_is_candidate_seed(self, seed_data: dict):
        """status debe ser CANDIDATE_SEED."""
        assert seed_data["status"] == "CANDIDATE_SEED"

    def test_implementation_authorized_is_false(self, seed_data: dict):
        """implementation_authorized debe ser False."""
        assert seed_data["implementation_authorized"] is False

    def test_runtime_authorized_is_false(self, seed_data: dict):
        """runtime_authorized debe ser False."""
        assert seed_data["runtime_authorized"] is False

    def test_scope_is_first_aid(self, seed_data: dict):
        """scope debe ser FIRST_AID."""
        assert seed_data["scope"] == "FIRST_AID"

    def test_allowed_service_depth_is_first_aid(self, seed_data: dict):
        """allowed_service_depth debe ser ["FIRST_AID"]."""
        assert seed_data["allowed_service_depth"] == ["FIRST_AID"]

    def test_requires_minimal_case_file_layer_is_true(self, seed_data: dict):
        """requires_minimal_case_file_layer debe ser True."""
        assert seed_data["requires_minimal_case_file_layer"] is True


class TestSeedCounts:
    """Valida conteos exactos de elementos."""

    def test_formula_refs_count_is_10(self, seed_data: dict):
        """Debe haber exactamente 10 formula_refs."""
        assert len(seed_data["formula_refs"]) == 10, (
            f"Expected 10 formula_refs, got {len(seed_data['formula_refs'])}"
        )

    def test_restricted_formula_refs_count_is_5(self, seed_data: dict):
        """Debe haber exactamente 5 restricted_formula_refs."""
        assert len(seed_data["restricted_formula_refs"]) == 5, (
            f"Expected 5 restricted_formula_refs, got {len(seed_data['restricted_formula_refs'])}"
        )

    def test_validation_refs_count_is_6(self, seed_data: dict):
        """Debe haber exactamente 6 validation_refs."""
        assert len(seed_data["validation_refs"]) == 6, (
            f"Expected 6 validation_refs, got {len(seed_data['validation_refs'])}"
        )

    def test_tool_refs_count_is_5(self, seed_data: dict):
        """Debe haber exactamente 5 tool_refs."""
        assert len(seed_data["tool_refs"]) == 5, (
            f"Expected 5 tool_refs, got {len(seed_data['tool_refs'])}"
        )

    def test_components_count_is_29(self, seed_data: dict):
        """Debe haber exactamente 29 components (27 originales + 2 nuevos triage)."""
        assert len(seed_data["components"]) == 29, (
            f"Expected 29 components, got {len(seed_data['components'])}"
        )

    def test_compositions_count_is_5(self, seed_data: dict):
        """Debe haber exactamente 5 compositions."""
        assert len(seed_data["compositions"]) == 5, (
            f"Expected 5 compositions, got {len(seed_data['compositions'])}"
        )


class TestFormulaRefs:
    """Valida presencia de formula_refs obligatorias."""

    EXPECTED_FORMULA_REFS = [
        "margen_bruto",
        "margen_bruto_pesos",
        "precio_venta_con_margen",
        "markup",
        "ingresos_totales",
        "egresos_totales",
        "flujo_caja_neto",
        "saldo_acumulado",
        "alerta_stock_minimo",
        "dias_stock_restante",
    ]

    def test_all_formula_refs_are_present(self, seed_data: dict):
        """Todas las formula_refs obligatorias deben estar presentes."""
        formula_ids = [f["id"] for f in seed_data["formula_refs"]]
        for expected_id in self.EXPECTED_FORMULA_REFS:
            assert expected_id in formula_ids, (
                f"Missing formula_ref: {expected_id}"
            )


class TestRestrictedFormulaRefs:
    """Valida presencia de restricted_formula_refs obligatorias."""

    EXPECTED_RESTRICTED_FORMULA_REFS = [
        "resultado_neto",
        "punto_equilibrio_unidades",
        "punto_equilibrio_pesos",
        "rotacion_inventario",
        "costo_reposicion_promedio",
    ]

    def test_all_restricted_formula_refs_are_present(self, seed_data: dict):
        """Todas las restricted_formula_refs obligatorias deben estar presentes."""
        restricted_ids = [f["id"] for f in seed_data["restricted_formula_refs"]]
        for expected_id in self.EXPECTED_RESTRICTED_FORMULA_REFS:
            assert expected_id in restricted_ids, (
                f"Missing restricted_formula_ref: {expected_id}"
            )


class TestValidationRefs:
    """Valida presencia de validation_refs obligatorias."""

    EXPECTED_VALIDATION_REFS = [
        "positive_number",
        "non_negative_number",
        "percentage_0_1",
        "percentage_0_100",
        "integer_positive",
        "integer_non_negative",
    ]

    def test_all_validation_refs_are_present(self, seed_data: dict):
        """Todas las validation_refs obligatorias deben estar presentes."""
        validation_refs = seed_data["validation_refs"]
        for expected_ref in self.EXPECTED_VALIDATION_REFS:
            assert expected_ref in validation_refs, (
                f"Missing validation_ref: {expected_ref}"
            )


class TestToolRefs:
    """Valida presencia de tool_refs obligatorias."""

    EXPECTED_TOOL_REFS = [
        "caja_diaria_triage",
        "precio_margen_basico",
        "stock_alertas_basicas",
        "gastos_triage",
        "proveedores_precio_variacion_triage",
    ]

    def test_all_tool_refs_are_present(self, seed_data: dict):
        """Todas las tool_refs obligatorias deben estar presentes."""
        tool_ids = [t["id"] for t in seed_data["tool_refs"]]
        for expected_id in self.EXPECTED_TOOL_REFS:
            assert expected_id in tool_ids, (
                f"Missing tool_ref: {expected_id}"
            )


class TestToolComponentMapping:
    """Valida tool_component_mapping."""

    def test_tool_component_mapping_has_5_entries(self, seed_data: dict):
        """Debe haber exactamente 5 entradas en tool_component_mapping."""
        assert len(seed_data["tool_component_mapping"]) == 5, (
            f"Expected 5 tool_component_mapping entries, got {len(seed_data['tool_component_mapping'])}"
        )

    def test_each_tool_ref_has_mapping_entry(self, seed_data: dict):
        """Cada tool_ref debe tener una entrada en tool_component_mapping."""
        tool_ids = {t["id"] for t in seed_data["tool_refs"]}
        mapped_tool_refs = {m["tool_ref"] for m in seed_data["tool_component_mapping"]}
        
        for tool_id in tool_ids:
            assert tool_id in mapped_tool_refs, (
                f"tool_ref {tool_id} has no entry in tool_component_mapping"
            )

    def test_mapping_has_5_aligned_and_0_missing(self, seed_data: dict):
        """Debe haber exactamente 5 ALIGNED y 0 MISSING_COMPONENT (resueltos)."""
        mapping_statuses = [m["mapping_status"] for m in seed_data["tool_component_mapping"]]
        aligned_count = mapping_statuses.count("ALIGNED")
        missing_count = mapping_statuses.count("MISSING_COMPONENT")
        
        assert aligned_count == 5, (
            f"Expected 5 ALIGNED mappings, got {aligned_count}"
        )
        assert missing_count == 0, (
            f"Expected 0 MISSING_COMPONENT mappings (both resolved), got {missing_count}"
        )

    def test_gastos_triage_mapping_is_aligned(self, seed_data: dict):
        """gastos_triage debe mapear a componente nuevo gastos_triage con status ALIGNED."""
        mapping = next(
            (m for m in seed_data["tool_component_mapping"] if m["tool_ref"] == "gastos_triage"),
            None
        )
        assert mapping is not None, "gastos_triage mapping not found"
        assert mapping["component_id"] == "gastos_triage", (
            f"gastos_triage must map to new component 'gastos_triage', got '{mapping['component_id']}'"
        )
        assert mapping["mapping_status"] == "ALIGNED"
        assert mapping["component_decision"] == "USE_IN_PHASE_1_WITH_GUARDRAILS"

    def test_proveedores_triage_mapping_is_aligned(self, seed_data: dict):
        """proveedores_precio_variacion_triage debe mapear a componente nuevo con status ALIGNED."""
        mapping = next(
            (m for m in seed_data["tool_component_mapping"] if m["tool_ref"] == "proveedores_precio_variacion_triage"),
            None
        )
        assert mapping is not None, "proveedores_precio_variacion_triage mapping not found"
        assert mapping["component_id"] == "proveedores_precio_variacion_triage", (
            f"proveedores_precio_variacion_triage must map to new component, got '{mapping['component_id']}'"
        )
        assert mapping["mapping_status"] == "ALIGNED"
        assert mapping["component_decision"] == "USE_IN_PHASE_1_WITH_GUARDRAILS"


class TestNewTriageComponents:
    """Valida los 2 nuevos componentes de triage FIRST_AID."""

    def test_gastos_triage_component_exists(self, seed_data: dict):
        """El componente gastos_triage debe existir en components."""
        component_ids = [c["id"] for c in seed_data["components"]]
        assert "gastos_triage" in component_ids, "gastos_triage component not found in components"

    def test_proveedores_triage_component_exists(self, seed_data: dict):
        """El componente proveedores_precio_variacion_triage debe existir en components."""
        component_ids = [c["id"] for c in seed_data["components"]]
        assert "proveedores_precio_variacion_triage" in component_ids, (
            "proveedores_precio_variacion_triage component not found in components"
        )

    def test_gastos_triage_has_scope_first_aid(self, seed_data: dict):
        """gastos_triage debe tener scope FIRST_AID."""
        component = next(c for c in seed_data["components"] if c["id"] == "gastos_triage")
        assert component.get("scope") == "FIRST_AID", (
            f"gastos_triage scope must be FIRST_AID, got '{component.get('scope')}'"
        )

    def test_proveedores_triage_has_scope_first_aid(self, seed_data: dict):
        """proveedores_precio_variacion_triage debe tener scope FIRST_AID."""
        component = next(c for c in seed_data["components"] if c["id"] == "proveedores_precio_variacion_triage")
        assert component.get("scope") == "FIRST_AID", (
            f"proveedores_precio_variacion_triage scope must be FIRST_AID, got '{component.get('scope')}'"
        )

    def test_gastos_triage_has_guardrails_status(self, seed_data: dict):
        """gastos_triage debe tener decision USE_IN_PHASE_1_WITH_GUARDRAILS."""
        component = next(c for c in seed_data["components"] if c["id"] == "gastos_triage")
        assert component["decision"] == "USE_IN_PHASE_1_WITH_GUARDRAILS", (
            f"gastos_triage decision must be USE_IN_PHASE_1_WITH_GUARDRAILS, got '{component['decision']}'"
        )

    def test_proveedores_triage_has_guardrails_status(self, seed_data: dict):
        """proveedores_precio_variacion_triage debe tener decision USE_IN_PHASE_1_WITH_GUARDRAILS."""
        component = next(c for c in seed_data["components"] if c["id"] == "proveedores_precio_variacion_triage")
        assert component["decision"] == "USE_IN_PHASE_1_WITH_GUARDRAILS", (
            f"proveedores_precio_variacion_triage decision must be USE_IN_PHASE_1_WITH_GUARDRAILS, "
            f"got '{component['decision']}'"
        )

    def test_gastos_triage_has_forbidden_claims(self, seed_data: dict):
        """gastos_triage debe declarar forbidden_claims."""
        component = next(c for c in seed_data["components"] if c["id"] == "gastos_triage")
        assert "forbidden_claims" in component, "gastos_triage missing forbidden_claims"
        assert isinstance(component["forbidden_claims"], list)
        assert len(component["forbidden_claims"]) >= 5, (
            f"gastos_triage should have at least 5 forbidden_claims, got {len(component['forbidden_claims'])}"
        )

    def test_proveedores_triage_has_forbidden_claims(self, seed_data: dict):
        """proveedores_precio_variacion_triage debe declarar forbidden_claims."""
        component = next(c for c in seed_data["components"] if c["id"] == "proveedores_precio_variacion_triage")
        assert "forbidden_claims" in component, "proveedores_precio_variacion_triage missing forbidden_claims"
        assert isinstance(component["forbidden_claims"], list)
        assert len(component["forbidden_claims"]) >= 5, (
            f"proveedores_precio_variacion_triage should have at least 5 forbidden_claims, "
            f"got {len(component['forbidden_claims'])}"
        )

    def test_gastos_triage_forbidden_claims_content(self, seed_data: dict):
        """gastos_triage debe prohibir clasificación contable/fiscal definitiva y auditoría."""
        component = next(c for c in seed_data["components"] if c["id"] == "gastos_triage")
        claims = component["forbidden_claims"]
        expected_fragments = ["clasificación contable", "clasificación fiscal", "auditoría", "diagnóstico", "decisión impositiva"]
        for fragment in expected_fragments:
            found = any(fragment.lower() in claim.lower() for claim in claims)
            assert found, f"gastos_triage forbidden_claims missing fragment: '{fragment}'"

    def test_proveedores_triage_forbidden_claims_content(self, seed_data: dict):
        """proveedores_precio_variacion_triage debe prohibir estrategia de compras y auditoría de proveedores."""
        component = next(c for c in seed_data["components"] if c["id"] == "proveedores_precio_variacion_triage")
        claims = component["forbidden_claims"]
        expected_fragments = ["estrategia de compras", "rentabilidad por proveedor", "recomendación final", "auditoría de proveedores", "diagnóstico financiero"]
        for fragment in expected_fragments:
            found = any(fragment.lower() in claim.lower() for claim in claims)
            assert found, f"proveedores_precio_variacion_triage forbidden_claims missing fragment: '{fragment}'"

    def test_gastos_triage_not_reusing_control_de_gastos(self, seed_data: dict):
        """control_de_gastos debe seguir siendo NOT_FOR_PHASE_1_PHASE_2 (no reclasificado)."""
        component = next((c for c in seed_data["components"] if c["id"] == "control_de_gastos"), None)
        assert component is not None, "control_de_gastos must still exist in components"
        assert component["decision"] == "NOT_FOR_PHASE_1_PHASE_2", (
            f"control_de_gastos must remain NOT_FOR_PHASE_1_PHASE_2, got '{component['decision']}'"
        )

    def test_proveedores_triage_not_reusing_compras_y_proveedores(self, seed_data: dict):
        """compras_y_proveedores debe seguir siendo NOT_FOR_PHASE_1_PHASE_2 (no reclasificado)."""
        component = next((c for c in seed_data["components"] if c["id"] == "compras_y_proveedores"), None)
        assert component is not None, "compras_y_proveedores must still exist in components"
        assert component["decision"] == "NOT_FOR_PHASE_1_PHASE_2", (
            f"compras_y_proveedores must remain NOT_FOR_PHASE_1_PHASE_2, got '{component['decision']}'"
        )


class TestEvidenceRequirements:
    """Valida evidence_requirements."""

    EXPECTED_TOOL_REFS = [
        "caja_diaria_triage",
        "precio_margen_basico",
        "stock_alertas_basicas",
        "gastos_triage",
        "proveedores_precio_variacion_triage",
    ]

    def test_evidence_requirements_covers_all_tool_refs(self, seed_data: dict):
        """evidence_requirements debe cubrir las 5 tool_refs."""
        evidence_tools = set(seed_data["evidence_requirements"].keys())
        
        for tool_ref in self.EXPECTED_TOOL_REFS:
            assert tool_ref in evidence_tools, (
                f"evidence_requirements missing for tool_ref: {tool_ref}"
            )

    def test_each_evidence_requirement_has_minimum_optional_missing_response(self, seed_data: dict):
        """Cada evidence_requirement debe tener minimum, optional y missing_response."""
        for tool_ref, requirements in seed_data["evidence_requirements"].items():
            assert "minimum" in requirements, (
                f"evidence_requirements for {tool_ref} missing 'minimum'"
            )
            assert "optional" in requirements, (
                f"evidence_requirements for {tool_ref} missing 'optional'"
            )
            assert "missing_response" in requirements, (
                f"evidence_requirements for {tool_ref} missing 'missing_response'"
            )
            
            assert isinstance(requirements["minimum"], list), (
                f"evidence_requirements[{tool_ref}].minimum must be a list"
            )
            assert isinstance(requirements["optional"], list), (
                f"evidence_requirements[{tool_ref}].optional must be a list"
            )
            assert isinstance(requirements["missing_response"], str), (
                f"evidence_requirements[{tool_ref}].missing_response must be a string"
            )


class TestEscalationRules:
    """Valida escalation_rules."""

    def test_escalation_rules_has_deterministic_diagnosis_branch(self, seed_data: dict):
        """escalation_rules debe tener rama hacia DETERMINISTIC_DIAGNOSIS."""
        assert "to_deterministic_diagnosis" in seed_data["escalation_rules"], (
            "escalation_rules missing 'to_deterministic_diagnosis' branch"
        )
        
        branch = seed_data["escalation_rules"]["to_deterministic_diagnosis"]
        assert "conditions" in branch, (
            "to_deterministic_diagnosis branch missing 'conditions'"
        )
        assert "message" in branch, (
            "to_deterministic_diagnosis branch missing 'message'"
        )
        assert isinstance(branch["conditions"], list), (
            "to_deterministic_diagnosis.conditions must be a list"
        )
        assert len(branch["conditions"]) > 0, (
            "to_deterministic_diagnosis.conditions must not be empty"
        )

    def test_escalation_rules_has_organizational_lab_branch(self, seed_data: dict):
        """escalation_rules debe tener rama hacia ORGANIZATIONAL_LAB."""
        assert "to_organizational_lab" in seed_data["escalation_rules"], (
            "escalation_rules missing 'to_organizational_lab' branch"
        )
        
        branch = seed_data["escalation_rules"]["to_organizational_lab"]
        assert "conditions" in branch, (
            "to_organizational_lab branch missing 'conditions'"
        )
        assert "message" in branch, (
            "to_organizational_lab branch missing 'message'"
        )
        assert isinstance(branch["conditions"], list), (
            "to_organizational_lab.conditions must be a list"
        )
        assert len(branch["conditions"]) > 0, (
            "to_organizational_lab.conditions must not be empty"
        )


class TestOwnerFacingLimitations:
    """Valida owner_facing_limitations."""

    def test_owner_facing_limitations_has_global_section(self, seed_data: dict):
        """owner_facing_limitations debe tener sección global o equivalente."""
        limitations = seed_data["owner_facing_limitations"]
        assert "global" in limitations, (
            "owner_facing_limitations missing 'global' section"
        )
        assert isinstance(limitations["global"], list), (
            "owner_facing_limitations.global must be a list"
        )
        assert len(limitations["global"]) > 0, (
            "owner_facing_limitations.global must not be empty"
        )

    def test_owner_facing_limitations_has_per_tool_section(self, seed_data: dict):
        """owner_facing_limitations debe tener limitación por tool o equivalente."""
        limitations = seed_data["owner_facing_limitations"]
        assert "per_tool" in limitations, (
            "owner_facing_limitations missing 'per_tool' section"
        )
        assert isinstance(limitations["per_tool"], dict), (
            "owner_facing_limitations.per_tool must be a dict"
        )
        assert len(limitations["per_tool"]) > 0, (
            "owner_facing_limitations.per_tool must not be empty"
        )

    def test_owner_facing_limitations_covers_new_triage_tools(self, seed_data: dict):
        """owner_facing_limitations.per_tool debe cubrir gastos_triage y proveedores_precio_variacion_triage."""
        per_tool = seed_data["owner_facing_limitations"]["per_tool"]
        assert "gastos_triage" in per_tool, "per_tool missing gastos_triage"
        assert "proveedores_precio_variacion_triage" in per_tool, "per_tool missing proveedores_precio_variacion_triage"


class TestNotes:
    """Valida notes."""

    def test_notes_declares_no_runtime_authorization(self, seed_data: dict):
        """notes debe declarar que no autoriza runtime."""
        notes_text = " ".join(seed_data["notes"]).lower()
        assert "no autoriza runtime" in notes_text or "does not authorize runtime" in notes_text, (
            "notes must declare that it does not authorize runtime"
        )

    def test_notes_declares_does_not_replace_original_json(self, seed_data: dict):
        """notes debe declarar que no reemplaza first_aid_toolbox_v1.json."""
        notes_text = " ".join(seed_data["notes"]).lower()
        assert "no reemplaza" in notes_text or "does not replace" in notes_text, (
            "notes must declare that it does not replace first_aid_toolbox_v1.json"
        )

    def test_notes_declares_next_step_is_loader_or_audit(self, seed_data: dict):
        """notes debe declarar que el próximo paso es crear loader o auditoría, no runtime directo."""
        notes_text = " ".join(seed_data["notes"]).lower()
        assert "loader" in notes_text or "auditor" in notes_text or "test" in notes_text, (
            "notes must declare that next step is loader or audit, not direct runtime"
        )

    def test_notes_declares_triage_components_decision(self, seed_data: dict):
        """notes debe declarar la decisión de crear componentes nuevos de triage."""
        notes_text = " ".join(seed_data["notes"]).lower()
        assert "gastos_triage" in notes_text, "notes must reference gastos_triage decision"
        assert "proveedores_precio_variacion_triage" in notes_text, (
            "notes must reference proveedores_precio_variacion_triage decision"
        )
        assert "FIRST_AID_TRIAGE_COMPONENTS_DECISION_V1" in " ".join(seed_data["notes"]), (
            "notes must reference FIRST_AID_TRIAGE_COMPONENTS_DECISION_V1.md"
        )


class TestExpectedCounts:
    """Valida que expected_counts coincide con la realidad del JSON."""

    def test_expected_counts_components_total(self, seed_data: dict):
        """expected_counts.components_total debe ser 29."""
        assert seed_data["expected_counts"]["components_total"] == 29

    def test_expected_counts_aligned_is_5(self, seed_data: dict):
        """expected_counts.tool_component_mapping_aligned debe ser 5."""
        assert seed_data["expected_counts"]["tool_component_mapping_aligned"] == 5

    def test_expected_counts_missing_is_0(self, seed_data: dict):
        """expected_counts.tool_component_mapping_missing debe ser 0."""
        assert seed_data["expected_counts"]["tool_component_mapping_missing"] == 0

    def test_expected_counts_guardrails_is_11(self, seed_data: dict):
        """expected_counts.USE_IN_PHASE_1_WITH_GUARDRAILS debe ser 11 (9 originales + 2 nuevos)."""
        assert seed_data["expected_counts"]["USE_IN_PHASE_1_WITH_GUARDRAILS"] == 11

    def test_expected_counts_matches_actual_components(self, seed_data: dict):
        """expected_counts.components_total debe coincidir con len(components)."""
        assert seed_data["expected_counts"]["components_total"] == len(seed_data["components"])

    def test_expected_counts_aligned_matches_actual_mappings(self, seed_data: dict):
        """expected_counts.tool_component_mapping_aligned debe coincidir con ALIGNED count real."""
        actual_aligned = sum(
            1 for m in seed_data["tool_component_mapping"]
            if m["mapping_status"] == "ALIGNED"
        )
        assert seed_data["expected_counts"]["tool_component_mapping_aligned"] == actual_aligned
