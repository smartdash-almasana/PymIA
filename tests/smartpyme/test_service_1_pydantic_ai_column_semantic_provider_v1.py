from __future__ import annotations

from types import SimpleNamespace

from pymia.smartpyme.service_1_pydantic_ai_column_semantic_provider_v1 import (
    ColumnSemanticAssistanceReplyV1,
    ColumnSemanticBatchV1,
    ColumnSemanticDecisionV1,
    Service1PydanticAIColumnSemanticProviderV1,
    _vertex_open_model_name_v1,
    _vertex_openai_base_url_v1,
    build_service_1_pydantic_ai_column_semantic_provider_v1,
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


def test_vertex_open_model_transport_uses_global_openai_compatible_endpoint() -> None:
    assert _vertex_open_model_name_v1("gemma-4-26b-a4b-it-maas") == "google/gemma-4-26b-a4b-it-maas"
    assert _vertex_openai_base_url_v1(project="pymia-503920", location="global") == (
        "https://aiplatform.googleapis.com/v1/projects/pymia-503920/locations/global/endpoints/openapi"
    )


def test_builder_resolves_gemma_maas_through_vertex_openai_transport(monkeypatch) -> None:
    import google.auth
    import pydantic_ai

    captured_models: list[object] = []

    class _Credentials:
        valid = True
        token = "test-token"

        def refresh(self, _request) -> None:
            raise AssertionError("valid fake credentials must not refresh during construction")

    class _CaptureAgent:
        def __init__(self, model, *, output_type, instructions) -> None:
            captured_models.append(model)
            self.output_type = output_type
            self.instructions = instructions

    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "pymia-503920")
    monkeypatch.setenv("GOOGLE_CLOUD_LOCATION", "global")
    monkeypatch.setattr(google.auth, "default", lambda **_kwargs: (_Credentials(), "pymia-503920"))
    monkeypatch.setattr(pydantic_ai, "Agent", _CaptureAgent)

    provider = build_service_1_pydantic_ai_column_semantic_provider_v1(
        model="gemma-4-26b-a4b-it-maas"
    )

    assert isinstance(provider, Service1PydanticAIColumnSemanticProviderV1)
    assert len(captured_models) == 2
    assert type(captured_models[0]).__name__ == "OpenAIChatModel"
    assert captured_models[0].model_name == "google/gemma-4-26b-a4b-it-maas"
    assert captured_models[0].profile.supports_json_object_output is True
    assert captured_models[0].profile.default_structured_output_mode == "prompted"
    assert captured_models[1] is captured_models[0]
