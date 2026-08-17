from __future__ import annotations

from types import SimpleNamespace

from pymia.smartpyme.service_1_pydantic_ai_column_semantic_provider_v1 import (
    ColumnSemanticAssistanceReplyV1,
    ColumnSemanticBatchV1,
    ColumnSemanticDecisionV1,
    Service1PydanticAIColumnSemanticProviderV1,
)
from pymia.smartpyme.service_1_workbook_profiler_v1 import SCHEMA_VERSION as PROFILE_SCHEMA_VERSION


class _FakeAgent:
    def __init__(self, output: ColumnSemanticBatchV1) -> None:
        self.output = output
        self.prompts: list[str] = []

    def run_sync(self, prompt: str):
        self.prompts.append(prompt)
        return SimpleNamespace(output=self.output)


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
        "suggested_semantic_role": None,
        "suggested_variable_name": None,
        "suggestion_reason": None,
    }
    assert assistant_agent.prompts
    assert "07:37:24" in assistant_agent.prompts[0]
    assert "runtime_authorized" not in result
    assert "confirmed_by_owner" not in result
