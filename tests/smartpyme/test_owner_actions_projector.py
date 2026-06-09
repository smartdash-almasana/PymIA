from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from pymia.contracts.owner_resolved_actions import (
    OwnerResolvedNextAction,
    OwnerResolvedNextActionBundle,
)


def test_project_resolved_owner_actions_to_render_contract_asks_clarification() -> None:
    from pymia.smartpyme.owner_actions_projector import (
        project_resolved_owner_actions_to_render_contract,
    )

    render_contract = {
        "tenant_id": "tenant-1",
        "references": ["ref-1"],
        "next_questions": [],
        "blocked_message": "",
    }
    bundle = OwnerResolvedNextActionBundle(
        bundle_id="resolved-1",
        source_action_bundle_id="actions-1",
        source_questions_bundle_id="questions-1",
        resolved_actions=[
            OwnerResolvedNextAction(
                action_id="action-1",
                action_type="ask_clarification",
                resolved_questions=[
                    "¿Qué período cubre esta planilla?",
                    "¿Cuál es el monto de impuestos?",
                ],
            )
        ],
    )

    projected = project_resolved_owner_actions_to_render_contract(render_contract, bundle)

    assert projected["next_questions"] == [
        "¿Qué período cubre esta planilla?",
        "¿Cuál es el monto de impuestos?",
    ]
    assert projected["blocked_message"] == "¿Qué período cubre esta planilla?"


def test_project_resolved_owner_actions_to_render_contract_rejects_answer_with_fixed_message() -> None:
    from pymia.smartpyme.owner_actions_projector import (
        REJECT_ANSWER_MESSAGE,
        REJECT_WARNING,
        project_resolved_owner_actions_to_render_contract,
    )

    render_contract = {
        "tenant_id": "tenant-1",
        "references": ["ref-1"],
        "forbidden_inferences": ["warning-0"],
    }
    bundle = OwnerResolvedNextActionBundle(
        bundle_id="resolved-2",
        source_action_bundle_id="actions-2",
        source_questions_bundle_id="questions-2",
        resolved_actions=[
            OwnerResolvedNextAction(
                action_id="action-2",
                action_type="reject_answer",
                resolved_questions=["¿Podés aclarar esa respuesta?"],
            )
        ],
    )

    projected = project_resolved_owner_actions_to_render_contract(render_contract, bundle)

    assert projected["blocked_message"] == REJECT_ANSWER_MESSAGE
    assert projected["next_questions"] == ["¿Podés aclarar esa respuesta?"]
    assert REJECT_WARNING in projected["forbidden_inferences"]


def test_project_resolved_owner_actions_to_render_contract_keeps_declared_with_next_step() -> None:
    from pymia.smartpyme.owner_actions_projector import (
        DECLARED_WARNING,
        KEEP_AS_DECLARED_STEP,
        project_resolved_owner_actions_to_render_contract,
    )

    render_contract = {
        "tenant_id": "tenant-1",
        "references": ["ref-1"],
        "next_steps": ["Paso previo."],
        "limit_warnings": [],
    }
    bundle = OwnerResolvedNextActionBundle(
        bundle_id="resolved-3",
        source_action_bundle_id="actions-3",
        source_questions_bundle_id="questions-3",
        resolved_actions=[
            OwnerResolvedNextAction(
                action_id="action-3",
                action_type="keep_as_declared",
                resolved_questions=["¿Qué significa esta columna?"],
            )
        ],
    )

    projected = project_resolved_owner_actions_to_render_contract(render_contract, bundle)

    assert KEEP_AS_DECLARED_STEP in projected["next_steps"]
    assert DECLARED_WARNING in projected["limit_warnings"]


def test_project_resolved_owner_actions_to_render_contract_empty_bundle_keeps_contract() -> None:
    from pymia.smartpyme.owner_actions_projector import (
        project_resolved_owner_actions_to_render_contract,
    )

    render_contract = {
        "tenant_id": "tenant-1",
        "references": ["ref-1"],
        "next_questions": ["Pregunta previa"],
    }
    original = deepcopy(render_contract)
    bundle = OwnerResolvedNextActionBundle(
        bundle_id="resolved-4",
        source_action_bundle_id="actions-4",
        source_questions_bundle_id="questions-4",
        resolved_actions=[],
    )

    projected = project_resolved_owner_actions_to_render_contract(render_contract, bundle)

    assert projected == original
    assert projected is not render_contract


def test_project_resolved_owner_actions_to_render_contract_does_not_mutate_input_and_preserves_fields() -> None:
    from pymia.smartpyme.owner_actions_projector import (
        project_resolved_owner_actions_to_render_contract,
    )

    render_contract = {
        "tenant_id": "tenant-1",
        "references": ["ref-1", "ref-2"],
        "summary": "Resumen existente.",
        "diagnosis": {"should_preserve": True},
        "findings": [{"id": "f-1"}],
        "next_questions": [],
    }
    original = deepcopy(render_contract)
    bundle = OwnerResolvedNextActionBundle(
        bundle_id="resolved-5",
        source_action_bundle_id="actions-5",
        source_questions_bundle_id="questions-5",
        resolved_actions=[
            OwnerResolvedNextAction(
                action_id="action-5",
                action_type="ask_clarification",
                resolved_questions=["¿Cuál es el período correcto?"],
            )
        ],
    )

    projected = project_resolved_owner_actions_to_render_contract(render_contract, bundle)

    assert render_contract == original
    assert projected["tenant_id"] == "tenant-1"
    assert projected["references"] == ["ref-1", "ref-2"]
    assert projected["diagnosis"] == {"should_preserve": True}
    assert projected["findings"] == [{"id": "f-1"}]


def test_project_resolved_owner_actions_to_render_contract_never_shows_ids_or_creates_evidence_candidate() -> None:
    from pymia.smartpyme.owner_actions_projector import (
        project_resolved_owner_actions_to_render_contract,
    )

    render_contract = {"tenant_id": "tenant-1"}
    bundle = OwnerResolvedNextActionBundle(
        bundle_id="resolved-6",
        source_action_bundle_id="actions-6",
        source_questions_bundle_id="questions-6",
        resolved_actions=[
            OwnerResolvedNextAction(
                action_id="action-6",
                action_type="reject_answer",
                resolved_questions=["¿Podés aclarar esa respuesta?"],
                metadata={"target_id": "q-6"},
            )
        ],
    )

    payload = project_resolved_owner_actions_to_render_contract(render_contract, bundle)

    assert "q-6" not in str(payload.get("next_questions", []))
    assert "evidence_candidate" not in str(payload)


def test_owner_actions_projector_has_no_prohibited_imports() -> None:
    source = Path("pymia/smartpyme/owner_actions_projector.py").read_text(encoding="utf-8")
    lowered = source.lower()

    forbidden_tokens = [
        "core_delivery_bridge",
        "graph",
        "state",
        "owner_facing_report",
        "delivery_markdown",
        "diagnosticcore",
        "diagnostic_core",
        "telegram",
        "hermes",
        "fastapi",
        "runtime",
        "llm",
        "learningmemory",
    ]

    for token in forbidden_tokens:
        assert f"import {token}" not in lowered
        assert f"from {token} import" not in lowered
