from __future__ import annotations

from types import SimpleNamespace

import pytest

from pymia.smartpyme.service_1_assisted_web_v1 import AssistedWebApplicationV1
from pymia.smartpyme.service_1_pydantic_ai_column_semantic_provider_v1 import (
    ColumnSemanticBatchV1,
    ColumnSemanticDecisionV1,
    Service1PydanticAIColumnSemanticProviderV1,
    semantic_provider_from_environment_v1,
)


class _FakeAgent:
    def __init__(self, output: ColumnSemanticBatchV1) -> None:
        self.output = output

    def run_sync(self, prompt: str):
        return SimpleNamespace(output=self.output)


def _productive_payload() -> dict:
    ref = "Ventas.Hora"
    return {
        "case_id": "case-f10",
        "requested_capability": None,
        "allowed_semantic_roles": ["operation_time"],
        "capability_relevant_roles": [],
        "compatible_tenant_memory_hints": [],
        "deterministic_hypotheses": [],
        "workbook_profile": {
            "status": "WORKBOOK_PROFILE_READY",
            "columns": [
                {
                    "column_ref": ref,
                    "sheet_name": "Ventas",
                    "column_name": "Hora",
                    "normalized_header": "hora",
                    "sample_values": ["10:00:00"],
                }
            ],
        },
        "workbook_semantic_context": {
            "schema_version": "SERVICE_1_WORKBOOK_SEMANTIC_CONTEXT_V1",
            "status": "WORKBOOK_SEMANTIC_CONTEXT_READY",
            "case_id": "case-f10",
            "tables": [{"sheet_name": "Ventas", "columns": []}],
            "relationships": [],
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
        },
        "evidence_registry": {
            f"ev:column:{ref}:type": {
                "kind": "COLUMN_TYPE",
                "column_ref": ref,
                "value": "text",
            }
        },
    }


def test_f10_productive_context_never_promotes_legacy_role_variable_output() -> None:
    agent = _FakeAgent(
        ColumnSemanticBatchV1(
            decisions=[
                ColumnSemanticDecisionV1(
                    column_ref="Ventas.Hora",
                    semantic_role="operation_time",
                    variable_name="operation_time",
                    confidence=0.99,
                    needs_owner_confirmation=False,
                    rationale="Legacy role-only answer.",
                )
            ]
        )
    )
    result = Service1PydanticAIColumnSemanticProviderV1(agent=agent)(_productive_payload())

    assert result["concept_proposals"] == []
    assert len(result["material_ambiguities"]) == 1
    assert "No governed V2 compositional projection" in result["material_ambiguities"][0]["reason"]


def test_f10_missing_llm_configuration_fails_closed_instead_of_falling_back(monkeypatch) -> None:
    monkeypatch.setenv("PYMIA_SEMANTIC_PROVIDER", "VERTEX")
    monkeypatch.delenv("PYMIA_SEMANTIC_LLM_MODEL", raising=False)
    provider = semantic_provider_from_environment_v1()
    with pytest.raises(RuntimeError, match="PYMIA_SEMANTIC_LLM_MODEL"):
        provider({})


def test_f10_assisted_web_default_uses_fail_closed_productive_provider(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("PYMIA_SEMANTIC_PROVIDER", "VERTEX")
    monkeypatch.delenv("PYMIA_SEMANTIC_LLM_MODEL", raising=False)
    app = AssistedWebApplicationV1(output_dir=tmp_path)
    with pytest.raises(RuntimeError, match="PYMIA_SEMANTIC_LLM_MODEL"):
        app._semantic_provider({})


def test_f10_structural_relationship_is_projected_from_profile_and_matching_v2_identity() -> None:
    left = "Ventas.ProductoID"
    right = "Productos.ProductoID"
    payload = _productive_payload()
    payload["workbook_profile"] = {
        "status": "WORKBOOK_PROFILE_READY",
        "columns": [
            {"column_ref": left, "sheet_name": "Ventas", "column_name": "ProductoID", "normalized_header": "productoid"},
            {"column_ref": right, "sheet_name": "Productos", "column_name": "ProductoID", "normalized_header": "productoid"},
        ],
        "relationships": [
            {
                "left_column_ref": left,
                "right_column_ref": right,
                "relationship_kind": "MANY_TO_ONE",
            }
        ],
    }
    payload["evidence_registry"] = {
        f"ev:column:{left}:type": {"kind": "COLUMN_TYPE", "column_ref": left, "value": "text"},
        f"ev:column:{right}:type": {"kind": "COLUMN_TYPE", "column_ref": right, "value": "text"},
        f"ev:relationship:{left}->{right}:overlap": {"kind": "RELATIONSHIP_OVERLAP"},
    }
    payload["workbook_semantic_context"]["tables"] = [
        {"sheet_name": "Ventas", "columns": []},
        {"sheet_name": "Productos", "columns": []},
    ]
    agent = _FakeAgent(
        ColumnSemanticBatchV1(
            decisions=[
                ColumnSemanticDecisionV1(
                    column_ref=left,
                    confidence=0.99,
                    needs_owner_confirmation=False,
                    rationale="Product identity in sales.",
                    compositional_semantic={
                        "entity": "product", "identity": "identifier", "grain": "sale", "confidence": 0.99
                    },
                ),
                ColumnSemanticDecisionV1(
                    column_ref=right,
                    confidence=0.99,
                    needs_owner_confirmation=False,
                    rationale="Product identity in catalog.",
                    compositional_semantic={
                        "entity": "product", "identity": "identifier", "grain": "product", "confidence": 0.99
                    },
                ),
            ]
        )
    )

    result = Service1PydanticAIColumnSemanticProviderV1(agent=agent)(payload)

    assert len(result["relationship_proposals"]) == 1
    relation = result["relationship_proposals"][0]
    assert relation["left_column_ref"] == left
    assert relation["right_column_ref"] == right
    assert relation["relationship_type"] == "MANY_TO_ONE"
    assert relation["evidence_refs"] == [f"ev:relationship:{left}->{right}:overlap"]
    assert relation["relationship_id"].startswith("structural-v2:relationship:")
