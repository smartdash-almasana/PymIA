from __future__ import annotations

import asyncio
import json
import time
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

import pymia.smartpyme.service_1_pydantic_ai_column_semantic_provider_v1 as provider_module

from pymia.smartpyme.service_1_pydantic_ai_column_semantic_provider_v1 import (
    ColumnSemanticAssistanceReplyV1,
    ColumnSemanticBatchV1,
    ColumnSemanticDecisionV1,
    CompositionalSemanticProposalV1,
    Service1PydanticAIColumnSemanticProviderV1,
    Service1SemanticProviderTimeoutError,
    Service1SemanticTimeoutError,
    service_1_semantic_execution_scope_v1,
)
from pymia.smartpyme.service_1_llm_semantic_contract_v1 import (
    parse_service_1_llm_semantic_proposal_v1,
)
from pymia.smartpyme.service_1_workbook_profiler_v1 import SCHEMA_VERSION as PROFILE_SCHEMA_VERSION


class _FakeAgent:
    def __init__(self, output: ColumnSemanticBatchV1) -> None:
        self.output = output
        self.prompts: list[str] = []

    def run_sync(self, prompt: str):
        self.prompts.append(prompt)
        return SimpleNamespace(output=self.output)


class _SlowAsyncAgent:
    async def run(self, prompt: str):
        await asyncio.sleep(1)


def _payload() -> dict:
    column_ref = "Ventas.Hora"
    return {
        "case_id": "case-1",
        "requested_capability": "net_margin_real",
        "allowed_semantic_roles": ["operation_date", "product_name"],
        "capability_relevant_roles": ["operation_date", "product_name"],
        "compatible_tenant_memory_hints": [],
        "deterministic_hypotheses": [
            {
                "sheet_name": "Ventas",
                "column_name": "Hora",
                "primary_hypothesis": {
                    "semantic_role": "product_name",
                    "variable_name": "product_name",
                    "score": 0.71,
                },
                "candidate_meanings": [],
                "confidence": 0.71,
            }
        ],
        "workbook_profile": {
            "schema_version": PROFILE_SCHEMA_VERSION,
            "status": "WORKBOOK_PROFILE_READY",
            "case_id": "case-1",
            "columns": [
                {
                    "column_ref": column_ref,
                    "sheet_name": "Ventas",
                    "column_name": "Hora",
                    "normalized_header": "hora",
                    "inferred_type": "text",
                    "sample_values": ["17:15:44", "07:37:24"],
                    "null_ratio": 0.0,
                    "cardinality": 2,
                }
            ],
            "relationships": [],
            "evidence_registry": {
                f"ev:column:{column_ref}:type": {
                    "kind": "COLUMN_TYPE",
                    "column_ref": column_ref,
                    "value": "text",
                }
            },
        },
        "evidence_registry": {
            f"ev:column:{column_ref}:type": {
                "kind": "COLUMN_TYPE",
                "column_ref": column_ref,
                "value": "text",
            }
        },
    }


def test_provider_can_refuse_wrong_deterministic_mapping_without_granting_authority() -> None:
    agent = _FakeAgent(
        ColumnSemanticBatchV1(
            decisions=[
                ColumnSemanticDecisionV1(
                    column_ref="Ventas.Hora",
                    semantic_role=None,
                    variable_name=None,
                    confidence=0.98,
                    needs_owner_confirmation=True,
                    rationale="The values are times; product_name is not supported by the evidence.",
                )
            ]
        )
    )
    provider = Service1PydanticAIColumnSemanticProviderV1(agent=agent)

    result = provider(_payload())

    assert result["concept_proposals"] == []
    assert result["material_ambiguities"][0]["target_refs"] == ["Ventas.Hora"]
    assert "runtime_authorized" not in result
    assert "tool_execution_authorized" not in result
    assert "delivery_authorized" not in result
    assert "calculation_result" not in result
    assert agent.prompts
    assert "17:15:44" in agent.prompts[0]


def test_provider_accepts_only_allowed_relevant_semantic_role() -> None:
    payload = _payload()
    payload["allowed_semantic_roles"].append("operation_time")
    payload["capability_relevant_roles"].append("operation_time")
    agent = _FakeAgent(
        ColumnSemanticBatchV1(
            decisions=[
                ColumnSemanticDecisionV1(
                    column_ref="Ventas.Hora",
                    semantic_role="operation_time",
                    variable_name="operation_time",
                    confidence=0.99,
                    needs_owner_confirmation=False,
                    rationale="Header and HH:MM:SS samples identify operation time.",
                )
            ]
        )
    )

    result = Service1PydanticAIColumnSemanticProviderV1(agent=agent)(payload)

    proposal = result["concept_proposals"][0]
    assert proposal["target_column_refs"] == ["Ventas.Hora"]
    assert proposal["semantic_role"] == "operation_time"
    assert proposal["variable_name"] == "operation_time"
    assert result["material_ambiguities"] == []


def test_provider_assist_is_explanatory_only() -> None:
    semantic_agent = _FakeAgent(
        ColumnSemanticBatchV1(
            decisions=[
                ColumnSemanticDecisionV1(
                    column_ref="Ventas.Hora",
                    semantic_role=None,
                    variable_name=None,
                    confidence=0.5,
                    needs_owner_confirmation=True,
                    rationale="Ambiguous.",
                )
            ]
        )
    )
    assistant_agent = _FakeAgent(
        ColumnSemanticAssistanceReplyV1(
            response_text="Parece una hora de operación por los ejemplos; confirmalo según tu proceso."
        )
    )
    provider = Service1PydanticAIColumnSemanticProviderV1(
        agent=semantic_agent,
        assistant_agent=assistant_agent,
    )

    result = provider.assist(
        {
            "decision_id": "d1",
            "column_refs": ["Ventas.Hora"],
            "sample_values": ["17:15:44", "07:37:24"],
            "owner_message": "¿Por qué pensás que es una hora?",
        }
    )

    assert result == {
        "response_text": "Parece una hora de operación por los ejemplos; confirmalo según tu proceso.",
        "suggested_compositional_semantic": None,
        "suggestion_reason": None,
    }
    assert assistant_agent.prompts
    assert "07:37:24" in assistant_agent.prompts[0]
    assert "runtime_authorized" not in result
    assert "confirmed_by_owner" not in result


def test_provider_does_not_turn_understood_but_capability_irrelevant_role_into_owner_ambiguity() -> None:
    payload = _payload()
    payload["allowed_semantic_roles"] = ["employee_name", "product_name"]
    payload["capability_relevant_roles"] = ["product_name"]
    payload["workbook_profile"]["columns"][0].update(
        {
            "column_ref": "Ventas.Empleado",
            "column_name": "Empleado",
            "normalized_header": "empleado",
            "sample_values": ["Carlos Pérez", "Fernanda Ruiz"],
        }
    )
    payload["deterministic_hypotheses"] = [
        {
            "sheet_name": "Ventas",
            "column_name": "Empleado",
            "primary_hypothesis": {
                "semantic_role": "employee_name",
                "variable_name": "employee_name",
                "score": 1.0,
            },
            "candidate_meanings": [],
            "confidence": 1.0,
        }
    ]
    payload["workbook_profile"]["evidence_registry"] = {}
    payload["evidence_registry"] = {}

    agent = _FakeAgent(
        ColumnSemanticBatchV1(
            decisions=[
                ColumnSemanticDecisionV1(
                    column_ref="Ventas.Empleado",
                    semantic_role="employee_name",
                    variable_name="employee_name",
                    confidence=0.99,
                    needs_owner_confirmation=False,
                    rationale="Names identify the employee who handled the sale.",
                )
            ]
        )
    )

    result = Service1PydanticAIColumnSemanticProviderV1(agent=agent)(payload)

    assert result["concept_proposals"] == []
    assert result["material_ambiguities"] == []
    assert result["irrelevant_refs"] == ["Ventas.Empleado"]


def test_f4_column_prompt_carries_explicit_f3_business_context() -> None:
    payload = _payload()
    payload["workbook_business_understanding"] = {
        "schema_version": "SERVICE_1_WORKBOOK_BUSINESS_UNDERSTANDING_V1",
        "status": "WORKBOOK_BUSINESS_UNDERSTANDING_READY",
        "authority": "CONTEXT_ONLY",
        "workbook_summary": "Ventas registradas por operación.",
        "tables": [
            {
                "sheet_name": "Ventas",
                "table_meaning": "registro de ventas",
                "grain": "una fila por operación de venta",
                "business_objects": ["venta", "cliente", "producto"],
                "processes": ["venta", "cobro"],
                "semantic_groups": ["identidad", "economía de la venta", "tiempo"],
                "confidence": 0.93,
            }
        ],
        "material_ambiguities": [],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }
    agent = _FakeAgent(
        ColumnSemanticBatchV1(
            decisions=[
                ColumnSemanticDecisionV1(
                    column_ref="Ventas.Hora",
                    semantic_role=None,
                    variable_name=None,
                    confidence=0.9,
                    needs_owner_confirmation=True,
                    rationale="Hora necesita contexto del evento de venta.",
                )
            ]
        )
    )

    Service1PydanticAIColumnSemanticProviderV1(agent=agent)(payload)

    prompt = agent.prompts[0]
    assert '"business_context"' in prompt
    assert '"table_meaning": "registro de ventas"' in prompt
    assert '"grain": "una fila por operación de venta"' in prompt
    assert '"business_objects": ["venta", "cliente", "producto"]' in prompt
    assert '"processes": ["venta", "cobro"]' in prompt
    assert '"semantic_groups": ["identidad", "economía de la venta", "tiempo"]' in prompt


def test_f5_productive_f3_path_rejects_legacy_role_only_semantics_into_ambiguity() -> None:
    payload = _payload()
    payload["workbook_business_understanding"] = {
        "schema_version": "SERVICE_1_WORKBOOK_BUSINESS_UNDERSTANDING_V1",
        "status": "WORKBOOK_BUSINESS_UNDERSTANDING_READY",
        "authority": "CONTEXT_ONLY",
        "workbook_summary": "Ventas registradas por operación.",
        "tables": [
            {
                "sheet_name": "Ventas",
                "table_meaning": "Ventas por operación",
                "grain": "sale",
                "business_objects": ["sale"],
                "processes": ["sale"],
                "semantic_groups": ["timing"],
                "confidence": 0.9,
            }
        ],
        "material_ambiguities": [],
    }
    agent = _FakeAgent(
        ColumnSemanticBatchV1(
            decisions=[
                ColumnSemanticDecisionV1(
                    column_ref="Ventas.Hora",
                    semantic_role="operation_time",
                    variable_name="operation_time",
                    confidence=0.99,
                    needs_owner_confirmation=False,
                    rationale="Legacy role-only output.",
                )
            ]
        )
    )

    result = Service1PydanticAIColumnSemanticProviderV1(agent=agent)(payload)

    assert result["concept_proposals"] == []
    assert len(result["material_ambiguities"]) == 1
    assert "No governed V2 compositional projection" in result["material_ambiguities"][0]["reason"]


def test_f5_productive_f3_path_emits_only_governed_v2_concept_shape() -> None:
    payload = _payload()
    payload["workbook_business_understanding"] = {
        "schema_version": "SERVICE_1_WORKBOOK_BUSINESS_UNDERSTANDING_V1",
        "status": "WORKBOOK_BUSINESS_UNDERSTANDING_READY",
        "authority": "CONTEXT_ONLY",
        "workbook_summary": "Ventas registradas por operación.",
        "tables": [
            {
                "sheet_name": "Ventas",
                "table_meaning": "Ventas por operación",
                "grain": "sale",
                "business_objects": ["sale"],
                "processes": ["sale"],
                "semantic_groups": ["timing"],
                "confidence": 0.9,
            }
        ],
        "material_ambiguities": [],
    }
    agent = _FakeAgent(
        ColumnSemanticBatchV1(
            decisions=[
                ColumnSemanticDecisionV1(
                    column_ref="Ventas.Hora",
                    semantic_role=None,
                    variable_name=None,
                    confidence=0.96,
                    needs_owner_confirmation=False,
                    rationale="Duration measure in the sale context.",
                    compositional_semantic=CompositionalSemanticProposalV1(
                        process="sale",
                        measure="duration",
                        grain="sale",
                        scope="event",
                        unit="hours",
                        confidence=0.96,
                    ),
                )
            ]
        )
    )

    result = Service1PydanticAIColumnSemanticProviderV1(agent=agent)(payload)

    assert result["material_ambiguities"] == []
    assert len(result["concept_proposals"]) == 1
    proposal = result["concept_proposals"][0]
    assert proposal["semantic_role"] is None
    assert proposal["variable_name"] is None
    semantic = proposal["compositional_semantic"]
    axes = {
        "entity", "object", "process", "measure", "state", "grain", "scope",
        "time", "identity", "relation", "unit", "aggregation",
    }
    assert set(semantic) == axes | {
        "field_ref", "confidence", "evidence", "source",
        "runtime_semantic_role", "runtime_variable_name",
    }
    assert semantic["measure"] == "duration"
    assert semantic["process"] == "sale"
    assert semantic["runtime_semantic_role"] is None
    assert semantic["runtime_variable_name"] is None
    assert not {
        "automatic_reuse_authorized",
        "delivery_authorized",
        "product_ready",
        "runtime_authorized",
        "tool_execution_authorized",
    }.intersection(semantic)
    assert parse_service_1_llm_semantic_proposal_v1(result).concept_proposals


def test_f5_projects_exact_deterministic_c2_meaning_for_cafeteria_price() -> None:
    payload = _payload()
    payload["allowed_semantic_roles"] = ["unit_sale_price"]
    payload["capability_relevant_roles"] = ["unit_sale_price"]
    payload["workbook_profile"]["columns"][0].update(
        column_ref="Ventas.PrecioUnitario",
        column_name="PrecioUnitario",
        normalized_header="precio_unitario",
        inferred_type="number",
        sample_values=[60, 45],
    )
    evidence = {
        "ev:column:Ventas.PrecioUnitario:type": {
            "kind": "COLUMN_TYPE",
            "column_ref": "Ventas.PrecioUnitario",
            "value": "number",
        }
    }
    payload["workbook_profile"]["evidence_registry"] = evidence
    payload["evidence_registry"] = evidence
    payload["deterministic_hypotheses"] = [{
        "sheet_name": "Ventas",
        "column_name": "PrecioUnitario",
        "primary_hypothesis": {
            "semantic_role": "unit_sale_price",
            "variable_name": "sale_price",
            "score": 1.0,
        },
        "candidate_meanings": [{
            "semantic_role": "unit_sale_price",
            "variable_name": "sale_price",
            "score": 1.0,
        }],
        "compositional_semantic": {
            "process": "sale",
            "measure": "price",
            "grain": "unit",
            "scope": "unit",
            "unit": "currency",
            "aggregation": "non_additive",
        },
    }]
    agent = _FakeAgent(ColumnSemanticBatchV1(decisions=[
        ColumnSemanticDecisionV1(
            column_ref="Ventas.PrecioUnitario",
            semantic_role=None,
            variable_name=None,
            confidence=0.99,
            needs_owner_confirmation=False,
            rationale="Precio unitario efectivo de venta.",
            compositional_semantic=CompositionalSemanticProposalV1(
                process="sale",
                measure="price",
                grain="unit",
                scope="unit",
                unit="currency",
                aggregation="non_additive",
                confidence=0.99,
            ),
        )
    ]))

    result = Service1PydanticAIColumnSemanticProviderV1(agent=agent)(payload)
    proposal = result["concept_proposals"][0]

    assert proposal["semantic_role"] is None
    assert proposal["variable_name"] is None
    semantic = proposal["compositional_semantic"]
    assert semantic["runtime_semantic_role"] == "unit_sale_price"
    assert semantic["runtime_variable_name"] == "sale_price"
    parsed = parse_service_1_llm_semantic_proposal_v1(result).concept_proposals[0]
    assert parsed.compositional_semantic["runtime_semantic_role"] == "unit_sale_price"
    assert parsed.compositional_semantic["runtime_variable_name"] == "sale_price"


def test_raw_compositional_model_rejects_authority_fields_instead_of_stripping_them() -> None:
    with pytest.raises(ValidationError, match="runtime_authorized"):
        CompositionalSemanticProposalV1(
            process="sale",
            measure="duration",
            confidence=0.96,
            runtime_authorized=False,
        )


class _GroupedAgent:
    def __init__(self, *, omit_refs: set[str] | None = None) -> None:
        self.prompts: list[str] = []
        self.omit_refs = omit_refs or set()

    def run_sync(self, prompt: str):
        self.prompts.append(prompt)
        payload = json.loads(prompt)
        decisions = [
            ColumnSemanticDecisionV1(
                column_ref=str(item["column_ref"]),
                semantic_role="operation_date",
                variable_name="operation_date",
                confidence=0.8,
                needs_owner_confirmation=False,
                rationale="bounded grouped proposal",
            )
            for item in payload.get("columns_to_interpret") or ()
            if str(item.get("column_ref") or "") not in self.omit_refs
        ]
        return SimpleNamespace(output=ColumnSemanticBatchV1(decisions=decisions))


def _grouped_payload() -> dict:
    payload = _payload()
    columns = payload["workbook_profile"]["columns"]
    columns.extend(
        [
            {
                "column_ref": "Ventas.PrecioUnitario",
                "sheet_name": "Ventas",
                "column_name": "PrecioUnitario",
                "normalized_header": "precio_unitario",
                "inferred_type": "number",
                "sample_values": [10, 20],
                "null_ratio": 0.0,
                "cardinality": 2,
            },
            {
                "column_ref": "Ventas.CostoUnitario",
                "sheet_name": "Ventas",
                "column_name": "CostoUnitario",
                "normalized_header": "costo_unitario",
                "inferred_type": "number",
                "sample_values": [5, 8],
                "null_ratio": 0.0,
                "cardinality": 2,
            },
            {
                "column_ref": "Ventas.Producto",
                "sheet_name": "Ventas",
                "column_name": "Producto",
                "normalized_header": "producto",
                "inferred_type": "text",
                "sample_values": ["A", "B"],
                "null_ratio": 0.0,
                "cardinality": 2,
            },
        ]
    )
    payload["workbook_profile"]["relationships"] = [
        {
            "left_column_ref": "Ventas.PrecioUnitario",
            "right_column_ref": "Ventas.CostoUnitario",
            "relationship_kind": "SAME_OPERATION",
        }
    ]
    payload["evidence_registry"].update(
        {
            f"ev:column:{item['column_ref']}:type": {
                "kind": "COLUMN_TYPE",
                "column_ref": item["column_ref"],
                "value": item.get("inferred_type"),
            }
            for item in columns[1:]
        }
    )
    return payload


def test_provider_batches_contextual_groups_with_complete_coverage_and_metrics() -> None:
    payload = _grouped_payload()
    agent = _GroupedAgent()
    provider = Service1PydanticAIColumnSemanticProviderV1(agent=agent)

    result = provider(payload)

    refs = [item["column_ref"] for item in payload["workbook_profile"]["columns"]]
    prompt_groups = [
        [item["column_ref"] for item in json.loads(prompt)["columns_to_interpret"]]
        for prompt in agent.prompts
    ]
    assert sorted(ref for group in prompt_groups for ref in group) == sorted(refs)
    assert len(prompt_groups) >= 2
    assert all(set(group) != set(refs) for group in prompt_groups)
    metrics = [item for item in provider.last_call_metrics if item["stage"] == "COLUMN_SEMANTICS"]
    assert len(metrics) == len(prompt_groups)
    assert max(item["estimated_input_tokens"] for item in metrics) < sum(item["estimated_input_tokens"] for item in metrics)
    assert len(result["concept_proposals"]) == len(refs)


def test_provider_fails_closed_when_a_group_drops_a_column() -> None:
    payload = _grouped_payload()
    agent = _GroupedAgent(omit_refs={"Ventas.Producto"})

    with pytest.raises(ValueError, match="COLUMN_GROUP_COVERAGE_INCOMPLETE"):
        Service1PydanticAIColumnSemanticProviderV1(agent=agent)(payload)


def test_provider_fails_closed_on_contradictory_group_decisions(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = _grouped_payload()

    class _ConflictingAgent(_GroupedAgent):
        def __init__(self) -> None:
            super().__init__()
            self.calls = 0

        def run_sync(self, prompt: str):
            self.calls += 1
            self.prompts.append(prompt)
            ref = json.loads(prompt)["columns_to_interpret"][0]["column_ref"]
            return SimpleNamespace(output=ColumnSemanticBatchV1(decisions=[ColumnSemanticDecisionV1(
                column_ref=ref,
                semantic_role="operation_date",
                variable_name="operation_date",
                confidence=0.9 if self.calls == 1 else 0.1,
                needs_owner_confirmation=False,
                rationale="conflicting proposal",
            )]))

    monkeypatch.setattr(provider_module, "_column_groups", lambda payload: [("Ventas.Hora",), ("Ventas.Hora",)])
    with pytest.raises(ValueError, match="CONTRADICTORY_COLUMN_DECISIONS"):
        Service1PydanticAIColumnSemanticProviderV1(agent=_ConflictingAgent())(payload)


def test_semantic_deadline_cancels_pending_async_agent() -> None:
    provider = Service1PydanticAIColumnSemanticProviderV1(agent=_SlowAsyncAgent())

    with service_1_semantic_execution_scope_v1(total_timeout_seconds=0.01):
        with pytest.raises(Service1SemanticTimeoutError, match="SERVICE_1_SEMANTIC_OPERATION_TIMEOUT"):
            provider(_payload())


def test_provider_timeout_is_distinct_from_total_deadline() -> None:
    provider = Service1PydanticAIColumnSemanticProviderV1(
        agent=_SlowAsyncAgent(),
        provider_timeout_seconds=0.01,
    )

    started = time.monotonic()
    with pytest.raises(
        Service1SemanticProviderTimeoutError,
        match="SERVICE_1_SEMANTIC_PROVIDER_TIMEOUT",
    ):
        provider._run_sync(provider._agent, "prompt")
    assert time.monotonic() - started < 0.5


def test_column_semantics_provider_deadline_covers_all_contextual_groups(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _SecondGroupHangs:
        def __init__(self) -> None:
            self.calls = 0

        async def run(self, prompt: str):
            self.calls += 1
            if self.calls == 1:
                return SimpleNamespace(output=ColumnSemanticBatchV1(decisions=[]))
            await asyncio.sleep(1)
            return SimpleNamespace(output=ColumnSemanticBatchV1(decisions=[]))

    monkeypatch.setattr(
        provider_module,
        "_column_groups",
        lambda payload: [("Ventas.A",), ("Ventas.B",)],
    )
    agent = _SecondGroupHangs()
    provider = Service1PydanticAIColumnSemanticProviderV1(
        agent=agent,
        provider_timeout_seconds=0.05,
    )

    started = time.monotonic()
    with pytest.raises(
        Service1SemanticProviderTimeoutError,
        match="SERVICE_1_SEMANTIC_PROVIDER_TIMEOUT",
    ):
        provider(_payload())
    assert agent.calls == 2
    assert time.monotonic() - started < 0.5


# ---------------------------------------------------------------------------
# Focal tests: C2 coordinate fallback projection table
# SERVICE1_COMPOSITIONAL_ROLE_PROJECTION_FIX_V1
# ---------------------------------------------------------------------------

_WORKBOOK_BUSINESS_UNDERSTANDING = {
    "schema_version": "SERVICE_1_WORKBOOK_BUSINESS_UNDERSTANDING_V1",
    "status": "WORKBOOK_BUSINESS_UNDERSTANDING_READY",
    "authority": "CONTEXT_ONLY",
    "workbook_summary": "Registro de ventas por operación.",
    "tables": [
        {
            "sheet_name": "Ventas",
            "table_meaning": "Ventas por operación",
            "grain": "sale",
            "business_objects": ["sale"],
            "processes": ["sale"],
            "semantic_groups": ["timing"],
            "confidence": 0.9,
        }
    ],
    "material_ambiguities": [],
}


def _c2_payload(
    *,
    column_ref: str,
    column_name: str,
    normalized_header: str,
    inferred_type: str = "number",
    sample_values: list | None = None,
) -> dict:
    """Minimal payload with NO deterministic hypothesis — forces fallback table."""
    return {
        "case_id": "case-c2fallback",
        "requested_capability": "reconstruct_transactions",
        "allowed_semantic_roles": [
            "quantity", "unit_sale_price", "sales_amount", "operation_date",
            "operation_time", "transaction_identifier", "product_name",
            "product_identifier", "branch_name", "branch_identifier",
            "sales_channel", "payment_method", "discount_candidate",
            "unit_cost_candidate",
        ],
        "capability_relevant_roles": [
            "quantity", "unit_sale_price", "sales_amount", "operation_date",
            "operation_time", "transaction_identifier", "product_name",
            "product_identifier", "branch_name", "branch_identifier",
            "sales_channel", "payment_method", "discount_candidate",
            "unit_cost_candidate",
        ],
        "compatible_tenant_memory_hints": [],
        "deterministic_hypotheses": [],  # empty -> fallback table fires
        "workbook_business_understanding": _WORKBOOK_BUSINESS_UNDERSTANDING,
        "workbook_profile": {
            "schema_version": PROFILE_SCHEMA_VERSION,
            "status": "WORKBOOK_PROFILE_READY",
            "case_id": "case-c2fallback",
            "columns": [
                {
                    "column_ref": column_ref,
                    "sheet_name": "Ventas",
                    "column_name": column_name,
                    "normalized_header": normalized_header,
                    "inferred_type": inferred_type,
                    "sample_values": sample_values or [1, 2],
                    "null_ratio": 0.0,
                    "cardinality": 2,
                }
            ],
            "relationships": [],
            "evidence_registry": {
                f"ev:column:{column_ref}:type": {
                    "kind": "COLUMN_TYPE",
                    "column_ref": column_ref,
                    "value": inferred_type,
                }
            },
        },
        "evidence_registry": {
            f"ev:column:{column_ref}:type": {
                "kind": "COLUMN_TYPE",
                "column_ref": column_ref,
                "value": inferred_type,
            }
        },
    }


def _run_c2_fallback(
    *,
    column_ref: str,
    column_name: str,
    normalized_header: str,
    compositional: CompositionalSemanticProposalV1,
    inferred_type: str = "number",
    sample_values: list | None = None,
) -> dict:
    payload = _c2_payload(
        column_ref=column_ref,
        column_name=column_name,
        normalized_header=normalized_header,
        inferred_type=inferred_type,
        sample_values=sample_values,
    )
    agent = _FakeAgent(
        ColumnSemanticBatchV1(
            decisions=[
                ColumnSemanticDecisionV1(
                    column_ref=column_ref,
                    semantic_role=None,
                    variable_name=None,
                    confidence=0.9,
                    needs_owner_confirmation=False,
                    rationale="C2 fallback test.",
                    compositional_semantic=compositional,
                )
            ]
        )
    )
    result = Service1PydanticAIColumnSemanticProviderV1(agent=agent)(payload)
    proposals = result.get("concept_proposals", [])
    assert len(proposals) == 1, f"Expected 1 concept proposal, got {len(proposals)}"
    return proposals[0]["compositional_semantic"]


def test_c2_fallback_projects_quantity() -> None:
    """measure=quantity + unit=units → runtime_semantic_role = 'quantity'."""
    sem = _run_c2_fallback(
        column_ref="Ventas.Cantidad",
        column_name="Cantidad",
        normalized_header="cantidad",
        compositional=CompositionalSemanticProposalV1(
            process="sale",
            measure="quantity",
            grain="line_item",
            scope="unit",
            unit="units",
            aggregation="sum",
            confidence=0.95,
        ),
    )
    assert sem["runtime_semantic_role"] == "quantity"
    assert sem["runtime_variable_name"] == "volume_sold"


def test_c2_fallback_projects_unit_sale_price() -> None:
    """measure=price + scope=unit + process=sale → runtime_semantic_role = 'unit_sale_price'."""
    sem = _run_c2_fallback(
        column_ref="Ventas.PrecioVenta",
        column_name="PrecioVenta",
        normalized_header="precio_venta",
        compositional=CompositionalSemanticProposalV1(
            process="sale",
            measure="price",
            grain="line_item",
            scope="unit",
            unit="currency",
            aggregation="non_additive",
            confidence=0.95,
        ),
    )
    assert sem["runtime_semantic_role"] == "unit_sale_price"
    assert sem["runtime_variable_name"] == "sale_price"


def test_c2_fallback_projects_operation_date() -> None:
    """time=event_date (no unit) → runtime_semantic_role = 'operation_date'."""
    sem = _run_c2_fallback(
        column_ref="Ventas.Fecha",
        column_name="Fecha",
        normalized_header="fecha",
        inferred_type="date",
        sample_values=["2025-01-15", "2025-01-16"],
        compositional=CompositionalSemanticProposalV1(
            process="sale",
            time="event_date",
            confidence=0.97,
        ),
    )
    assert sem["runtime_semantic_role"] == "operation_date"
    assert sem["runtime_variable_name"] == "business_period"


def test_c2_fallback_projects_operation_time_via_hours() -> None:
    """time=event_date + unit=hours → runtime_semantic_role = 'operation_time'."""
    sem = _run_c2_fallback(
        column_ref="Ventas.Hora",
        column_name="Hora",
        normalized_header="hora",
        inferred_type="text",
        sample_values=["17:15:00", "09:30:00"],
        compositional=CompositionalSemanticProposalV1(
            process="sale",
            time="event_date",
            unit="hours",
            confidence=0.9,
        ),
    )
    assert sem["runtime_semantic_role"] == "operation_time"
    assert sem["runtime_variable_name"] == "operation_time"


def test_c2_fallback_projects_operation_time_via_minutes() -> None:
    """time=event_date + unit=minutes → runtime_semantic_role = 'operation_time'."""
    sem = _run_c2_fallback(
        column_ref="Ventas.HoraMin",
        column_name="HoraMin",
        normalized_header="hora_min",
        inferred_type="text",
        sample_values=["1035", "570"],
        compositional=CompositionalSemanticProposalV1(
            time="event_date",
            unit="minutes",
            confidence=0.88,
        ),
    )
    assert sem["runtime_semantic_role"] == "operation_time"
    assert sem["runtime_variable_name"] == "operation_time"


def test_c2_fallback_projects_product_name() -> None:
    """entity=product (no identity) → runtime_semantic_role = 'product_name'."""
    sem = _run_c2_fallback(
        column_ref="Ventas.Producto",
        column_name="Producto",
        normalized_header="producto",
        inferred_type="text",
        sample_values=["Café chico", "Medialunas"],
        compositional=CompositionalSemanticProposalV1(
            entity="product",
            process="sale",
            confidence=0.95,
        ),
    )
    assert sem["runtime_semantic_role"] == "product_name"
    assert sem["runtime_variable_name"] == "product"


def test_c2_fallback_projects_product_identifier() -> None:
    """entity=product + identity=sequence → runtime_semantic_role = 'product_identifier'."""
    sem = _run_c2_fallback(
        column_ref="Ventas.CodigoProducto",
        column_name="CodigoProducto",
        normalized_header="codigo_producto",
        inferred_type="text",
        sample_values=["SKU-001", "SKU-002"],
        compositional=CompositionalSemanticProposalV1(
            entity="product",
            identity="sequence",
            process="sale",
            confidence=0.92,
        ),
    )
    assert sem["runtime_semantic_role"] == "product_identifier"
    assert sem["runtime_variable_name"] == "product_id"


def test_c2_fallback_projects_branch_name() -> None:
    """entity=branch (no identity) → runtime_semantic_role = 'branch_name'."""
    sem = _run_c2_fallback(
        column_ref="Ventas.Sucursal",
        column_name="Sucursal",
        normalized_header="sucursal",
        inferred_type="text",
        sample_values=["Centro", "Palermo"],
        compositional=CompositionalSemanticProposalV1(
            entity="branch",
            process="sale",
            confidence=0.93,
        ),
    )
    assert sem["runtime_semantic_role"] == "branch_name"
    assert sem["runtime_variable_name"] == "branch_name"


def test_c2_fallback_projects_sales_channel() -> None:
    """grain=sale + no entity + no measure → runtime_semantic_role = 'sales_channel'."""
    sem = _run_c2_fallback(
        column_ref="Ventas.CanalVenta",
        column_name="CanalVenta",
        normalized_header="canal_venta",
        inferred_type="text",
        sample_values=["Mostrador", "Delivery"],
        compositional=CompositionalSemanticProposalV1(
            process="sale",
            grain="sale",
            confidence=0.91,
        ),
    )
    assert sem["runtime_semantic_role"] == "sales_channel"
    assert sem["runtime_variable_name"] == "segment"


def test_c2_fallback_projects_payment_method() -> None:
    """grain=payment + no entity + no measure → runtime_semantic_role = 'payment_method'."""
    sem = _run_c2_fallback(
        column_ref="Ventas.MedioPago",
        column_name="MedioPago",
        normalized_header="medio_pago",
        inferred_type="text",
        sample_values=["Efectivo", "Tarjeta"],
        compositional=CompositionalSemanticProposalV1(
            process="sale",
            grain="payment",
            confidence=0.94,
        ),
    )
    assert sem["runtime_semantic_role"] == "payment_method"
    assert sem["runtime_variable_name"] == "payment_method"


def test_c2_fallback_projects_discount_candidate() -> None:
    """measure=discount → runtime_semantic_role = 'discount_candidate'."""
    sem = _run_c2_fallback(
        column_ref="Ventas.Descuento",
        column_name="Descuento",
        normalized_header="descuento",
        compositional=CompositionalSemanticProposalV1(
            process="sale",
            measure="discount",
            unit="currency",
            confidence=0.88,
        ),
    )
    assert sem["runtime_semantic_role"] == "discount_candidate"
    assert sem["runtime_variable_name"] == "discount"


def test_c2_fallback_projects_unit_cost_candidate() -> None:
    """measure=cost → runtime_semantic_role = 'unit_cost_candidate'."""
    sem = _run_c2_fallback(
        column_ref="Ventas.Costo",
        column_name="Costo",
        normalized_header="costo",
        compositional=CompositionalSemanticProposalV1(
            process="sale",
            measure="cost",
            scope="unit",
            unit="currency",
            confidence=0.9,
        ),
    )
    assert sem["runtime_semantic_role"] == "unit_cost_candidate"
    assert sem["runtime_variable_name"] == "cost"


def test_c2_fallback_projects_transaction_identifier() -> None:
    """process=sale + identity=sequence → runtime_semantic_role = 'transaction_identifier'."""
    sem = _run_c2_fallback(
        column_ref="Ventas.NroOperacion",
        column_name="NroOperacion",
        normalized_header="nro_operacion",
        inferred_type="text",
        sample_values=["V-001", "V-002"],
        compositional=CompositionalSemanticProposalV1(
            entity="sale",
            process="sale",
            identity="sequence",
            confidence=0.9,
        ),
    )
    assert sem["runtime_semantic_role"] == "transaction_identifier"
    assert sem["runtime_variable_name"] == "transaction_id"


def test_c2_fallback_returns_none_for_duration() -> None:
    """measure=duration has no P7 role — runtime_semantic_role must be None (existing contract)."""
    sem = _run_c2_fallback(
        column_ref="Ventas.Hora",
        column_name="Hora",
        normalized_header="hora",
        inferred_type="text",
        sample_values=["00:30:00", "01:00:00"],
        compositional=CompositionalSemanticProposalV1(
            process="sale",
            measure="duration",
            unit="hours",
            confidence=0.9,
        ),
    )
    assert sem["runtime_semantic_role"] is None
    assert sem["runtime_variable_name"] is None


def test_c2_fallback_returns_none_for_balance() -> None:
    """measure=balance has no P7 role — runtime_semantic_role must be None."""
    sem = _run_c2_fallback(
        column_ref="Caja.Saldo",
        column_name="Saldo",
        normalized_header="saldo",
        compositional=CompositionalSemanticProposalV1(
            measure="balance",
            state="actual",
            unit="currency",
            confidence=0.85,
        ),
    )
    assert sem["runtime_semantic_role"] is None
    assert sem["runtime_variable_name"] is None


def test_c2_fallback_deterministic_path_still_takes_priority(monkeypatch) -> None:
    """When a matching deterministic hypothesis exists, the deterministic role wins
    over the C2 fallback table. Regression guard for the existing deterministic path."""
    payload = _c2_payload(
        column_ref="Ventas.PrecioUnitario",
        column_name="PrecioUnitario",
        normalized_header="precio_unitario",
        inferred_type="number",
        sample_values=[60, 45],
    )
    # Inject a deterministic hypothesis that matches the proposed C2 coordinates.
    payload["deterministic_hypotheses"] = [
        {
            "sheet_name": "Ventas",
            "column_name": "PrecioUnitario",
            "primary_hypothesis": {
                "semantic_role": "unit_sale_price",
                "variable_name": "sale_price",
                "score": 1.0,
            },
            "candidate_meanings": [{"semantic_role": "unit_sale_price", "variable_name": "sale_price", "score": 1.0}],
            "compositional_semantic": {
                "process": "sale",
                "measure": "price",
                "grain": "unit",
                "scope": "unit",
                "unit": "currency",
                "aggregation": "non_additive",
            },
            "confidence": 1.0,
        }
    ]
    payload["evidence_registry"]["ev:column:Ventas.PrecioUnitario:range"] = {
        "kind": "COLUMN_RANGE",
        "column_ref": "Ventas.PrecioUnitario",
    }
    payload["workbook_profile"]["evidence_registry"]["ev:column:Ventas.PrecioUnitario:range"] = (
        payload["evidence_registry"]["ev:column:Ventas.PrecioUnitario:range"]
    )
    agent = _FakeAgent(
        ColumnSemanticBatchV1(
            decisions=[
                ColumnSemanticDecisionV1(
                    column_ref="Ventas.PrecioUnitario",
                    semantic_role=None,
                    variable_name=None,
                    confidence=0.99,
                    needs_owner_confirmation=False,
                    rationale="Precio unitario de venta.",
                    compositional_semantic=CompositionalSemanticProposalV1(
                        process="sale",
                        measure="price",
                        grain="unit",
                        scope="unit",
                        unit="currency",
                        aggregation="non_additive",
                        confidence=0.99,
                    ),
                )
            ]
        )
    )

    def _fallback_must_not_run(_descriptor):
        pytest.fail("C2 fallback projection ran despite an exact deterministic hypothesis")

    monkeypatch.setattr(provider_module, "_c2_coordinate_fallback_projection", _fallback_must_not_run)
    result = Service1PydanticAIColumnSemanticProviderV1(agent=agent)(payload)
    proposals = result.get("concept_proposals", [])
    assert len(proposals) == 1
    sem = proposals[0]["compositional_semantic"]
    # Deterministic path should fire (not fallback), result is the same role.
    assert sem["runtime_semantic_role"] == "unit_sale_price"
    assert sem["runtime_variable_name"] == "sale_price"
