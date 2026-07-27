from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


CONFIDENCE_HIGH = "high"
CONFIDENCE_MEDIUM = "medium"
CONFIDENCE_LOW = "low"


@dataclass(frozen=True)
class FieldResolution:
    required_field: str
    source_field: str
    confidence: str
    owner_confirmation_required: bool
    owner_question: str | None = None
    method: str = ""
    covered: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SemanticResolutionResult:
    covered_fields: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    ambiguous_fields: list[str] = field(default_factory=list)
    field_resolution: dict[str, FieldResolution] = field(default_factory=dict)
    owner_questions_required: bool = False
    owner_questions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "covered_fields": list(self.covered_fields),
            "missing_fields": list(self.missing_fields),
            "ambiguous_fields": list(self.ambiguous_fields),
            "field_resolution": {
                key: value.to_dict() for key, value in self.field_resolution.items()
            },
            "owner_questions_required": self.owner_questions_required,
            "owner_questions": list(self.owner_questions),
        }


def _normalize(value: str) -> str:
    return str(value or "").strip().lower()


def _question_for(required_field: str, source_field: str) -> str | None:
    if required_field == "venta_neta" and source_field == "venta_total":
        return (
            "¿La columna "
            f"{source_field} representa venta neta sin IVA, devoluciones ni descuentos?"
        )
    if required_field == "costo_directo" and source_field == "costo_unitario":
        return (
            "¿La columna "
            f"{source_field} representa el costo directo del producto vendido?"
        )
    if required_field == "costo_directo" and source_field == "costo_total":
        return (
            "¿La columna "
            f"{source_field} representa costo directo del producto vendido y no una suma parcial o agregada?"
        )
    return None


def _resolve_candidate(
    *,
    parser_field: str,
    required_field: str,
    field_map: dict[str, str],
) -> FieldResolution | None:
    parser_norm = _normalize(parser_field)
    required_norm = _normalize(required_field)

    mapped_required = _normalize(field_map.get(parser_norm, ""))
    if mapped_required == required_norm:
        return FieldResolution(
            required_field=required_field,
            source_field=parser_field,
            confidence=CONFIDENCE_HIGH,
            owner_confirmation_required=False,
            owner_question=None,
            method="field_map",
            covered=True,
        )

    if parser_norm == required_norm:
        return FieldResolution(
            required_field=required_field,
            source_field=parser_field,
            confidence=CONFIDENCE_HIGH,
            owner_confirmation_required=False,
            owner_question=None,
            method="exact_match",
            covered=True,
        )

    if required_norm == "periodo" and parser_norm in {"fecha", "mes"}:
        return FieldResolution(
            required_field=required_field,
            source_field=parser_field,
            confidence=CONFIDENCE_HIGH,
            owner_confirmation_required=False,
            owner_question=None,
            method="canonical_time_alias",
            covered=True,
        )

    if required_norm == "venta_neta" and parser_norm == "venta_total":
        return FieldResolution(
            required_field=required_field,
            source_field=parser_field,
            confidence=CONFIDENCE_MEDIUM,
            owner_confirmation_required=True,
            owner_question=_question_for(required_field, parser_field),
            method="semantic_alias_ambiguous",
            covered=False,
        )

    if required_norm == "costo_directo" and parser_norm == "costo_unitario":
        return FieldResolution(
            required_field=required_field,
            source_field=parser_field,
            confidence=CONFIDENCE_MEDIUM,
            owner_confirmation_required=True,
            owner_question=_question_for(required_field, parser_field),
            method="semantic_alias_ambiguous",
            covered=False,
        )

    if required_norm == "costo_directo" and parser_norm == "costo_total":
        return FieldResolution(
            required_field=required_field,
            source_field=parser_field,
            confidence=CONFIDENCE_LOW,
            owner_confirmation_required=True,
            owner_question=_question_for(required_field, parser_field),
            method="aggregate_cost_ambiguous",
            covered=False,
        )

    return None


def resolve_semantic_fields(
    *,
    parser_fields: list[str],
    required_fields: list[str],
    field_map: dict[str, str] | None = None,
) -> SemanticResolutionResult:
    normalized_parser_fields = []
    seen_parser: set[str] = set()
    for field in parser_fields:
        value = str(field).strip()
        if not value:
            continue
        key = _normalize(value)
        if key in seen_parser:
            continue
        seen_parser.add(key)
        normalized_parser_fields.append(value)

    normalized_required_fields = []
    seen_required: set[str] = set()
    for field in required_fields:
        value = str(field).strip()
        if not value:
            continue
        key = _normalize(value)
        if key in seen_required:
            continue
        seen_required.add(key)
        normalized_required_fields.append(value)

    effective_field_map = {
        _normalize(key): str(value).strip()
        for key, value in (field_map or {}).items()
        if str(key).strip() and str(value).strip()
    }

    covered_fields: list[str] = []
    missing_fields: list[str] = []
    ambiguous_fields: list[str] = []
    field_resolution: dict[str, FieldResolution] = {}
    owner_questions: list[str] = []

    for required_field in normalized_required_fields:
        best_resolution: FieldResolution | None = None
        for parser_field in normalized_parser_fields:
            candidate = _resolve_candidate(
                parser_field=parser_field,
                required_field=required_field,
                field_map=effective_field_map,
            )
            if candidate is None:
                continue
            if best_resolution is None:
                best_resolution = candidate
                continue
            priority = {
                CONFIDENCE_HIGH: 3,
                CONFIDENCE_MEDIUM: 2,
                CONFIDENCE_LOW: 1,
            }
            if priority[candidate.confidence] > priority[best_resolution.confidence]:
                best_resolution = candidate

        if best_resolution is None:
            missing_fields.append(required_field)
            continue

        field_resolution[required_field] = best_resolution
        if best_resolution.covered and best_resolution.confidence == CONFIDENCE_HIGH:
            covered_fields.append(required_field)
            continue

        ambiguous_fields.append(required_field)
        missing_fields.append(required_field)
        if best_resolution.owner_question and best_resolution.owner_question not in owner_questions:
            owner_questions.append(best_resolution.owner_question)

    return SemanticResolutionResult(
        covered_fields=covered_fields,
        missing_fields=missing_fields,
        ambiguous_fields=ambiguous_fields,
        field_resolution=field_resolution,
        owner_questions_required=bool(owner_questions),
        owner_questions=owner_questions,
    )


__all__ = [
    "CONFIDENCE_HIGH",
    "CONFIDENCE_MEDIUM",
    "CONFIDENCE_LOW",
    "FieldResolution",
    "SemanticResolutionResult",
    "resolve_semantic_fields",
]
