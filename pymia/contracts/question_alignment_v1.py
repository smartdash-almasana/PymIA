from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


QUESTION_ALIGNMENT_CONTRACT_PATH = Path(__file__).resolve().with_name("question_alignment_v1.json")

_REQUIRED_TOP_LEVEL_KEYS = (
    "schema_version",
    "status",
    "owner_keywords",
    "formula_prefix_axis",
    "pathology_axis",
    "misalignment_rules",
    "copy_templates",
)

_REQUIRED_COPY_TEMPLATES = (
    "misaligned_reconduction",
    "misaligned_technical_reference",
    "no_candidates_reference",
)


class QuestionAlignmentContractError(ValueError):
    """Raised when the declarative question alignment contract is invalid."""


def validate_question_alignment_contract(data: dict[str, Any]) -> dict[str, Any]:
    """Validate the minimal declarative contract required by QuestionAlignmentGate.

    This loader validates shape only. It does not classify owner messages,
    choose questions, diagnose, read evidence, or mutate runtime state.
    """
    if not isinstance(data, dict):
        raise QuestionAlignmentContractError("question alignment contract must be an object")

    missing = [key for key in _REQUIRED_TOP_LEVEL_KEYS if key not in data]
    if missing:
        raise QuestionAlignmentContractError(f"missing required keys: {', '.join(missing)}")

    if data["status"] != "ACTIVE":
        raise QuestionAlignmentContractError("question alignment contract status must be ACTIVE")

    if not isinstance(data["owner_keywords"], dict) or not data["owner_keywords"]:
        raise QuestionAlignmentContractError("owner_keywords must be a non-empty object")

    if "caja_liquidez" not in data["owner_keywords"]:
        raise QuestionAlignmentContractError("owner_keywords must include caja_liquidez")

    if not isinstance(data["formula_prefix_axis"], dict):
        raise QuestionAlignmentContractError("formula_prefix_axis must be an object")

    if not isinstance(data["pathology_axis"], dict):
        raise QuestionAlignmentContractError("pathology_axis must be an object")

    if not isinstance(data["misalignment_rules"], list):
        raise QuestionAlignmentContractError("misalignment_rules must be a list")

    copy_templates = data["copy_templates"]
    if not isinstance(copy_templates, dict):
        raise QuestionAlignmentContractError("copy_templates must be an object")

    missing_templates = [key for key in _REQUIRED_COPY_TEMPLATES if key not in copy_templates]
    if missing_templates:
        raise QuestionAlignmentContractError(
            f"missing required copy templates: {', '.join(missing_templates)}"
        )

    return data


@lru_cache(maxsize=1)
def load_question_alignment_contract() -> dict[str, Any]:
    """Load and validate the active question alignment contract.

    The gate is intentionally a consumer of this contract. Domain keywords,
    formula-axis mappings, pathology-axis mappings, and reconduction copy must
    live in JSON rather than Python runtime code.
    """
    data = json.loads(QUESTION_ALIGNMENT_CONTRACT_PATH.read_text(encoding="utf-8"))
    return validate_question_alignment_contract(data)


__all__ = [
    "QUESTION_ALIGNMENT_CONTRACT_PATH",
    "QuestionAlignmentContractError",
    "load_question_alignment_contract",
    "validate_question_alignment_contract",
]
