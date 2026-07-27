from __future__ import annotations

import hashlib
import json
from typing import Any

from pymia.contracts.owner_semantic_confirmation import (
    OwnerSemanticConfirmationGate,
)


def build_pending_owner_semantic_confirmation_gate_from_translation(
    translation_payload: dict[str, Any],
) -> OwnerSemanticConfirmationGate:
    """Builds a pending OwnerSemanticConfirmationGate from a structured translation payload.

    As per ModuleContract:
    - Pure and deterministic.
    - Status is unconditionally PENDING_OWNER_CONFIRMATION.
    - proposed_interpretation, target_type, and source_ref are required and validated.
    - terminal states in payload are rejected/ignored.
    - lists are normalized.
    - input payload is not mutated.
    - fails closed on validation errors.
    """
    if translation_payload is None:
        raise ValueError("translation_payload must not be None")

    # Ensure proposed_interpretation is present and non-empty
    proposed_interpretation = translation_payload.get("proposed_interpretation")
    if proposed_interpretation is None:
        raise ValueError("proposed_interpretation is required")
    proposed_interpretation_str = str(proposed_interpretation).strip()
    if not proposed_interpretation_str:
        raise ValueError("proposed_interpretation must be non-empty")

    # Ensure source_ref is present and non-empty
    source_ref = translation_payload.get("source_ref")
    if source_ref is None:
        raise ValueError("source_ref is required")
    source_ref_str = str(source_ref).strip()
    if not source_ref_str:
        raise ValueError("source_ref must be non-empty")

    # Ensure target_type is valid
    target_type = translation_payload.get("target_type", "SEMANTIC_INTERPRETATION")
    valid_target_types = {
        "SEMANTIC_INTERPRETATION",
        "EVIDENCE_REQUEST_AXIS",
        "PATHOLOGY_AXIS",
        "FORMULA_AXIS",
    }
    if target_type not in valid_target_types:
        raise ValueError(f"invalid target_type: {target_type}")

    # Reject/ignore terminal status if present
    status = translation_payload.get("status", "PENDING_OWNER_CONFIRMATION")
    if status != "PENDING_OWNER_CONFIRMATION":
        raise ValueError("Cannot create a gate in a terminal status")

    # Also check other terminal fields (owner_response_text, corrected_interpretation)
    if translation_payload.get("owner_response_text") is not None:
        raise ValueError("Cannot build a pending gate with owner response text")
    if translation_payload.get("corrected_interpretation") is not None:
        raise ValueError("Cannot build a pending gate with corrected interpretation")

    # Extract lists and normalize
    def normalize_list(key: str) -> list[str]:
        items = translation_payload.get(key)
        if items is None:
            return []
        if not isinstance(items, (list, tuple)):
            raise ValueError(f"{key} must be a list or tuple")
        return [str(item).strip() for item in items if str(item).strip()]

    related_missing_keys = normalize_list("related_missing_keys")
    related_pathology_candidates = normalize_list("related_pathology_candidates")
    related_formula_candidates = normalize_list("related_formula_candidates")

    # Generate a stable gate_id based on proposed_interpretation, target_type and source_ref
    payload_to_hash = {
        "proposed_interpretation": proposed_interpretation_str,
        "target_type": target_type,
        "source_ref": source_ref_str,
    }
    digest = hashlib.sha1(
        json.dumps(payload_to_hash, ensure_ascii=True, sort_keys=True).encode("utf-8")
    ).hexdigest()
    gate_id = f"gate_pending_{digest[:12]}"

    # A confirmation question is required by the contract model.
    confirmation_question = translation_payload.get("confirmation_question")
    if confirmation_question is None:
        confirmation_question = f"¿Confirmás que la interpretación '{proposed_interpretation_str}' es correcta para avanzar?"
    confirmation_question_str = str(confirmation_question).strip()
    if not confirmation_question_str:
        raise ValueError("confirmation_question must be non-empty")

    metadata = dict(translation_payload.get("metadata") or {})

    # Prohibit evidence_candidate and computed_variables from metadata
    if "evidence_candidate" in metadata or "computed_variables" in metadata:
        raise ValueError("Payload must not contain evidence_candidate or computed_variables")

    # Build the gate
    return OwnerSemanticConfirmationGate(
        gate_id=gate_id,
        target_type=target_type,
        proposed_interpretation=proposed_interpretation_str,
        confirmation_question=confirmation_question_str,
        status="PENDING_OWNER_CONFIRMATION",
        owner_response_text=None,
        corrected_interpretation=None,
        related_missing_keys=related_missing_keys,
        related_pathology_candidates=related_pathology_candidates,
        related_formula_candidates=related_formula_candidates,
        source_ref=source_ref_str,
        metadata=metadata,
    )
