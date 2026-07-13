"""
Test contractual/documental puro para first_aid_tool_activation_v1.json

Valida:
- JSON válido y cargable
- Campos obligatorios de primer nivel
- Valores obligatorios
- 8 estados de activación
- 5 herramientas en tool_activation_matrix
- Consistencia con el seed (first_aid_toolbox_pack_seed_v1.json)
- Forbidden runtime actions
- Notes contractuales
"""
import json
from pathlib import Path

import pytest


# --- Paths ---

CONTRACTS_DIR = Path(__file__).resolve().parents[2] / "pymia" / "contracts"
ACTIVATION_JSON = CONTRACTS_DIR / "first_aid_tool_activation_v1.json"
SEED_JSON = CONTRACTS_DIR / "first_aid_toolbox_pack_seed_v1.json"


# --- Fixtures ---

@pytest.fixture(scope="module")
def activation():
    assert ACTIVATION_JSON.exists(), f"No existe {ACTIVATION_JSON}"
    with open(ACTIVATION_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def seed():
    assert SEED_JSON.exists(), f"No existe {SEED_JSON}"
    with open(SEED_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# 1. JSON válido y cargable
# ============================================================

class TestJSONValidity:
    def test_json_file_exists(self):
        assert ACTIVATION_JSON.exists()

    def test_json_loads(self):
        with open(ACTIVATION_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)


# ============================================================
# 2. Campos obligatorios de primer nivel
# ============================================================

class TestRequiredFields:
    REQUIRED_FIELDS = [
        "schema_version",
        "contract_id",
        "status",
        "runtime_authorized",
        "implementation_authorized",
        "source_seed",
        "allowed_service_depth",
        "activation_states",
        "required_inputs",
        "activation_rules",
        "blocking_rules",
        "tool_activation_matrix",
        "forbidden_runtime_actions",
        "notes",
    ]

    @pytest.mark.parametrize("field", REQUIRED_FIELDS)
    def test_field_present(self, activation, field):
        assert field in activation, f"Falta campo obligatorio: {field}"


# ============================================================
# 3. Valores obligatorios
# ============================================================

class TestRequiredValues:
    def test_contract_id(self, activation):
        assert activation["contract_id"] == "FIRST_AID_TOOL_ACTIVATION_V1"

    def test_status(self, activation):
        assert activation["status"] == "CONTRACT_ONLY"

    def test_runtime_authorized_false(self, activation):
        assert activation["runtime_authorized"] is False

    def test_implementation_authorized_false(self, activation):
        assert activation["implementation_authorized"] is False

    def test_source_seed(self, activation):
        assert activation["source_seed"] == "first_aid_toolbox_pack_seed_v1.json"

    def test_allowed_service_depth(self, activation):
        assert activation["allowed_service_depth"] == ["FIRST_AID"]

    def test_runtime_authorized_false_means_no_execution(self, activation):
        assert activation["runtime_authorized"] is False
        notes = " ".join(activation["notes"]).lower()
        assert "runtime_authorized" in notes
        assert "false" in notes


# ============================================================
# 4. Activation states
# ============================================================

class TestActivationStates:
    EXPECTED_STATES = [
        "ELIGIBLE",
        "BLOCKED_MISSING_EVIDENCE",
        "BLOCKED_COLUMN_CONFIRMATION",
        "BLOCKED_RESTRICTED_FORMULA",
        "BLOCKED_FORBIDDEN_CLAIM",
        "BLOCKED_SCOPE_MISMATCH",
        "BLOCKED_COMPONENT_NOT_ALIGNED",
        "BLOCKED_RUNTIME_NOT_AUTHORIZED",
    ]

    def test_exact_count(self, activation):
        assert len(activation["activation_states"]) == 8

    @pytest.mark.parametrize("state", EXPECTED_STATES)
    def test_state_present(self, activation, state):
        assert state in activation["activation_states"], f"Falta estado: {state}"


# ============================================================
# 5. Tool activation matrix
# ============================================================

class TestToolActivationMatrix:
    EXPECTED_TOOLS = [
        "caja_diaria_triage",
        "precio_margen_basico",
        "stock_alertas_basicas",
        "gastos_triage",
        "proveedores_precio_variacion_triage",
    ]

    def test_exact_count(self, activation):
        matrix = activation["tool_activation_matrix"]
        assert len(matrix) == 5, f"Esperadas 5 herramientas, encontradas {len(matrix)}"

    @pytest.mark.parametrize("tool", EXPECTED_TOOLS)
    def test_tool_present(self, activation, tool):
        matrix = activation["tool_activation_matrix"]
        tool_refs = [t["tool_ref"] for t in matrix]
        assert tool in tool_refs, f"Falta herramienta en matrix: {tool}"


# ============================================================
# 6. Campos obligatorios por herramienta
# ============================================================

class TestToolFields:
    REQUIRED_TOOL_FIELDS = [
        "tool_ref",
        "component_required",
        "minimum_evidence",
        "allowed_formulas",
        "restricted_formulas",
        "forbidden_claims",
        "owner_questions_if_missing",
        "eligible_when",
        "blocked_when",
        "limitations",
    ]

    def test_all_tools_have_required_fields(self, activation):
        matrix = activation["tool_activation_matrix"]
        for tool in matrix:
            tool_ref = tool.get("tool_ref", "UNKNOWN")
            for field in self.REQUIRED_TOOL_FIELDS:
                assert field in tool, (
                    f"Herramienta {tool_ref} no tiene campo obligatorio: {field}"
                )


# ============================================================
# 7. Consistencia con seed
# ============================================================

class TestSeedConsistency:
    EXPECTED_TOOLS = [
        "caja_diaria_triage",
        "precio_margen_basico",
        "stock_alertas_basicas",
        "gastos_triage",
        "proveedores_precio_variacion_triage",
    ]

    def test_all_tools_exist_in_seed(self, activation, seed):
        seed_tool_refs = [t["id"] for t in seed["tool_refs"]]
        matrix = activation["tool_activation_matrix"]
        for tool in matrix:
            assert tool["tool_ref"] in seed_tool_refs, (
                f"tool_ref {tool['tool_ref']} del activation contract "
                f"no existe en el seed"
            )

    def test_all_tools_have_aligned_mapping(self, activation, seed):
        seed_mappings = {
            m["tool_ref"]: m for m in seed["tool_component_mapping"]
        }
        matrix = activation["tool_activation_matrix"]
        for tool in matrix:
            tr = tool["tool_ref"]
            assert tr in seed_mappings, (
                f"tool_ref {tr} no tiene mapping en el seed"
            )
            assert seed_mappings[tr]["mapping_status"] == "ALIGNED", (
                f"tool_ref {tr} no tiene mapping ALIGNED en el seed "
                f"(status: {seed_mappings[tr]['mapping_status']})"
            )

    def test_all_tools_have_evidence_requirements(self, activation, seed):
        seed_evidence = seed.get("evidence_requirements", {})
        matrix = activation["tool_activation_matrix"]
        for tool in matrix:
            tr = tool["tool_ref"]
            assert tr in seed_evidence, (
                f"tool_ref {tr} no tiene evidence_requirements en el seed"
            )

    def test_minimum_evidence_not_contradicted_by_seed(self, activation, seed):
        """
        Cada minimum_evidence del activation contract debe ser un subconjunto
        de (minimum + optional) del evidence_requirements del seed.
        """
        seed_evidence = seed.get("evidence_requirements", {})
        matrix = activation["tool_activation_matrix"]
        for tool in matrix:
            tr = tool["tool_ref"]
            activation_min = set(tool["minimum_evidence"])
            seed_all = set(
                seed_evidence[tr].get("minimum", [])
                + seed_evidence[tr].get("optional", [])
            )
            unexpected = activation_min - seed_all
            assert not unexpected, (
                f"tool_ref {tr}: minimum_evidence del activation contract "
                f"contiene campos no reconocidos por el seed: {unexpected}"
            )

    def test_component_required_matches_seed_mapping(self, activation, seed):
        """
        El component_required del activation contract debe coincidir con
        el component_id del mapping en el seed.
        """
        seed_mappings = {
            m["tool_ref"]: m for m in seed["tool_component_mapping"]
        }
        matrix = activation["tool_activation_matrix"]
        for tool in matrix:
            tr = tool["tool_ref"]
            assert tr in seed_mappings
            expected_component = seed_mappings[tr]["component_id"]
            assert tool["component_required"] == expected_component, (
                f"tool_ref {tr}: component_required = {tool['component_required']} "
                f"no coincide con seed component_id = {expected_component}"
            )


# ============================================================
# 8. Forbidden runtime actions
# ============================================================

class TestForbiddenRuntimeActions:
    EXPECTED_ACTIONS = [
        "runtime execution",
        "tool execution",
        "XLSX generation",
        "pipeline wiring",
        "diagnostic claims",
        "LLM decisions",
    ]

    def test_forbidden_actions_present(self, activation):
        forbidden = activation["forbidden_runtime_actions"]
        for action in self.EXPECTED_ACTIONS:
            assert action in forbidden, (
                f"Falta forbidden runtime action: {action}"
            )

    def test_forbidden_actions_count(self, activation):
        assert len(activation["forbidden_runtime_actions"]) == 6


# ============================================================
# 9. Notes contractuales
# ============================================================

class TestNotes:
    def test_notes_is_list(self, activation):
        assert isinstance(activation["notes"], list)

    def test_notes_not_empty(self, activation):
        assert len(activation["notes"]) >= 3

    def test_notes_declare_no_runtime(self, activation):
        all_notes = " ".join(activation["notes"]).lower()
        assert "no es runtime" in all_notes or "no runtime" in all_notes, (
            "Las notes deben declarar que este contrato no es runtime"
        )

    def test_notes_declare_no_pipeline_touch(self, activation):
        all_notes = " ".join(activation["notes"]).lower()
        assert "vertical_pipeline" in all_notes, (
            "Las notes deben declarar que vertical_pipeline.py no debe tocarse"
        )

    def test_notes_declare_seed_dependency(self, activation):
        all_notes = " ".join(activation["notes"]).lower()
        assert "seed" in all_notes, (
            "Las notes deben declarar que este contrato consume el seed"
        )


# ============================================================
# 10. Activation rules
# ============================================================

class TestActivationRules:
    def test_activation_rules_not_empty(self, activation):
        assert len(activation["activation_rules"]) >= 5

    def test_activation_rules_have_required_fields(self, activation):
        for rule in activation["activation_rules"]:
            assert "rule_id" in rule
            assert "description" in rule
            assert "condition" in rule
            assert "failure_state" in rule

    def test_failure_states_are_valid(self, activation):
        valid_states = set(activation["activation_states"])
        for rule in activation["activation_rules"]:
            assert rule["failure_state"] in valid_states, (
                f"Rule {rule['rule_id']} references invalid state: "
                f"{rule['failure_state']}"
            )

    def test_scope_rule_validates_input_service_depth(self, activation):
        scope_rules = [
            rule for rule in activation["activation_rules"]
            if rule["rule_id"] == "AR_008_SCOPE_MATCH"
        ]
        assert len(scope_rules) == 1
        condition = scope_rules[0]["condition"]
        assert "input.service_depth" in condition
        assert "allowed_service_depth" in condition


# ============================================================
# 11. Blocking rules
# ============================================================

class TestBlockingRules:
    def test_blocking_rules_not_empty(self, activation):
        assert len(activation["blocking_rules"]) >= 5

    def test_blocking_rules_have_required_fields(self, activation):
        for rule in activation["blocking_rules"]:
            assert "blocking_state" in rule
            assert "trigger" in rule
            assert "recovery" in rule
            assert "escalation" in rule

    def test_blocking_states_are_valid(self, activation):
        valid_states = set(activation["activation_states"])
        for rule in activation["blocking_rules"]:
            assert rule["blocking_state"] in valid_states, (
                f"Blocking rule references invalid state: "
                f"{rule['blocking_state']}"
            )

    def test_forbidden_claim_recovery_has_no_typo(self, activation):
        rules = [
            rule for rule in activation["blocking_rules"]
            if rule["blocking_state"] == "BLOCKED_FORBIDDEN_CLAIM"
        ]
        assert len(rules) == 1
        assert rules[0]["recovery"] == "reformular el pedido o explicar limitación"
