import json
from types import SimpleNamespace

from pymia.smartpyme.service_1_llm_semantic_interpreter_v1 import STATUS_READY, interpret_service_1_semantics_v1
from pymia.smartpyme.service_1_llm_semantic_contract_v1 import build_service_1_llm_semantic_context_v1
from pymia.smartpyme.service_1_pydantic_ai_column_semantic_provider_v1 import (
    ColumnSemanticBatchV1,
    ColumnSemanticDecisionV1,
    Service1PydanticAIColumnSemanticProviderV1,
    WorkbookBusinessUnderstandingV1,
    WorkbookTableUnderstandingV1,
)
from pymia.smartpyme.service_1_workbook_profiler_v1 import SCHEMA_VERSION as PROFILE_SCHEMA_VERSION


class _FakeAgent:
    def __init__(self, output):
        self.output = output
        self.prompts = []

    def run_sync(self, prompt: str):
        self.prompts.append(prompt)
        return SimpleNamespace(output=self.output)


def _context():
    ref = "ORDENES_TRABAJO.orden_id"
    profile = {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "status": "WORKBOOK_PROFILE_READY",
        "case_id": "case-f3",
        "columns": [{
            "column_ref": ref,
            "sheet_name": "ORDENES_TRABAJO",
            "column_name": "orden_id",
            "normalized_header": "orden_id",
            "inferred_type": "text",
            "sample_values": ["OT-001", "OT-002"],
            "null_ratio": 0.0,
            "cardinality": 2,
        }],
        "relationships": [],
        "evidence_registry": {
            f"ev:column:{ref}:type": {"kind": "COLUMN_TYPE", "column_ref": ref, "value": "text"}
        },
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }
    workbook_semantic_context = {
        "schema_version": "SERVICE_1_WORKBOOK_SEMANTIC_CONTEXT_V1",
        "status": "WORKBOOK_SEMANTIC_CONTEXT_READY",
        "case_id": "case-f3",
        "tables": [{
            "sheet_name": "ORDENES_TRABAJO",
            "row_count": 2,
            "column_count": 1,
            "columns": [{"column_ref": ref, "column_name": "orden_id", "sample_values": ["OT-001", "OT-002"]}],
        }],
        "relationships": [],
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }
    return build_service_1_llm_semantic_context_v1(
        case_id="case-f3",
        requested_capability=None,
        workbook_profile=profile,
        deterministic_hypotheses=[{
            "sheet_name": "ORDENES_TRABAJO",
            "column_name": "orden_id",
            "primary_hypothesis": {"semantic_role": "operation_id", "variable_name": "operation_id", "score": 0.8},
            "candidate_meanings": [],
            "confidence": 0.8,
        }],
        allowed_semantic_roles=["operation_id"],
        workbook_semantic_context=workbook_semantic_context,
    )


def test_business_understanding_runs_before_column_pass_and_is_injected_into_prompt():
    business_agent = _FakeAgent(
        WorkbookBusinessUnderstandingV1(
            workbook_summary="Libro de gestión de trabajos de servicio.",
            tables=[WorkbookTableUnderstandingV1(
                sheet_name="ORDENES_TRABAJO",
                table_meaning="Órdenes de trabajo",
                grain="una fila por orden de trabajo",
                business_objects=["orden de trabajo"],
                processes=["prestación de servicio"],
                semantic_groups=["identidad", "mano de obra"],
                confidence=0.99,
            )],
        )
    )
    semantic_agent = _FakeAgent(
        ColumnSemanticBatchV1(decisions=[ColumnSemanticDecisionV1(
            column_ref="ORDENES_TRABAJO.orden_id",
            semantic_role="operation_id",
            variable_name="operation_id",
            confidence=0.9,
            needs_owner_confirmation=False,
            rationale="Identificador de la orden.",
        )])
    )
    provider = Service1PydanticAIColumnSemanticProviderV1(
        agent=semantic_agent,
        business_understanding_agent=business_agent,
    )

    result = interpret_service_1_semantics_v1(context=_context(), provider=provider)

    assert result["status"] == STATUS_READY, result
    understanding = result["workbook_business_understanding"]
    assert understanding["authority"] == "CONTEXT_ONLY"
    assert understanding["tables"][0]["sheet_name"] == "ORDENES_TRABAJO"
    assert "Órdenes de trabajo" in semantic_agent.prompts[0]
    assert business_agent.prompts
    assert business_agent.prompts[0] in business_agent.prompts
    assert business_agent.prompts[0] != semantic_agent.prompts[0]


def test_business_understanding_validator_blocks_invented_sheet_before_column_pass():
    business_agent = _FakeAgent(
        WorkbookBusinessUnderstandingV1(
            workbook_summary="Inventado",
            tables=[WorkbookTableUnderstandingV1(
                sheet_name="NO_EXISTE",
                table_meaning="Tabla inventada",
                confidence=0.5,
            )],
        )
    )
    semantic_agent = _FakeAgent(ColumnSemanticBatchV1(decisions=[]))
    provider = Service1PydanticAIColumnSemanticProviderV1(
        agent=semantic_agent,
        business_understanding_agent=business_agent,
    )

    result = interpret_service_1_semantics_v1(context=_context(), provider=provider)

    assert result["status"] == "BLOCKED"
    assert result["detail"]["failing_stage"] == "WORKBOOK_BUSINESS_UNDERSTANDING"
    assert semantic_agent.prompts == []


class _PerTableBusinessAgent:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def run_sync(self, prompt: str):
        self.prompts.append(prompt)
        payload = json.loads(prompt)
        tables = payload["workbook_semantic_context"]["tables"]
        return SimpleNamespace(
            output=WorkbookBusinessUnderstandingV1(
                workbook_summary="Libro de ventas y clientes",
                tables=[WorkbookTableUnderstandingV1(
                    sheet_name=t["sheet_name"],
                    table_meaning=f"Tabla {t['sheet_name']}",
                    grain="una fila por registro",
                    confidence=0.8,
                ) for t in tables],
            )
        )


def test_business_understanding_runs_one_call_per_workbook() -> None:
    business_agent = _PerTableBusinessAgent()
    provider = Service1PydanticAIColumnSemanticProviderV1(
        agent=_FakeAgent(ColumnSemanticBatchV1(decisions=[])),
        business_understanding_agent=business_agent,
    )
    payload = {
        "case_id": "case-batched",
        "workbook_semantic_context": {
            "schema_version": "SERVICE_1_WORKBOOK_SEMANTIC_CONTEXT_V1",
            "status": "WORKBOOK_SEMANTIC_CONTEXT_READY",
            "case_id": "case-batched",
            "tables": [
                {"sheet_name": "Ventas", "row_count": 3, "columns": [{"column_ref": "Ventas.id"}]},
                {"sheet_name": "Clientes", "row_count": 2, "columns": [{"column_ref": "Clientes.id"}]},
            ],
            "relationships": [],
        },
        "semantic_knowledge_context": {},
    }

    result = provider.understand_workbook(payload)

    assert [item["sheet_name"] for item in result["tables"]] == ["Ventas", "Clientes"]
    assert len(business_agent.prompts) == 1
    assert len(json.loads(business_agent.prompts[0])["workbook_semantic_context"]["tables"]) == 2
    metrics = [item for item in provider.last_call_metrics if item["stage"] == "WORKBOOK_BUSINESS_UNDERSTANDING"]
    assert len(metrics) == 1
