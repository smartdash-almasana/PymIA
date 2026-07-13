from __future__ import annotations

import json
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path
from typing import Any, Protocol

from pymia.contracts.pathology_contract import (
    PathologyDefinition,
    PathologyEvaluationInput,
    PathologyFinding,
    PathologySeverity,
    PathologyStatus,
)


PathologyEvaluator = Callable[[PathologyEvaluationInput], PathologyFinding]

_OPERATORS: dict[str, Callable[[float, float], bool]] = {
    "lt": lambda v, t: v < t,
    "lte": lambda v, t: v <= t,
    "gt": lambda v, t: v > t,
    "gte": lambda v, t: v >= t,
    "eq": lambda v, t: v == t,
    "neq": lambda v, t: v != t,
}


class PathologyKnowledgeTank(Protocol):
    def get_definition(self, pathology_id: str) -> PathologyDefinition | None: ...
    def get_metadata(self, pathology_id: str) -> dict: ...
    def get_evaluator(self, pathology_id: str) -> PathologyEvaluator | None: ...


def _load_rules() -> dict[str, Any]:
    catalog_path = Path(__file__).resolve().parents[1] / "contracts" / "pathology_rules_v1.json"
    raw = json.loads(catalog_path.read_text(encoding="utf-8"))
    rules = raw.get("rules_by_pathology")
    if not isinstance(rules, dict):
        raise ValueError("pathology_rules_v1.json: rules_by_pathology must be a dict")
    return rules


def _build_definition(pathology_id: str, rule: dict[str, Any]) -> PathologyDefinition | None:
    if not isinstance(rule, dict):
        return None
    formula_id = rule.get("formula_id")
    description = rule.get("description")
    severity = rule.get("severity")
    if not isinstance(formula_id, str) or not isinstance(description, str) or not isinstance(severity, str):
        return None
    try:
        sev = PathologySeverity(severity)
    except ValueError:
        return None
    suggested_action = rule.get("suggested_action")
    if not isinstance(suggested_action, str):
        suggested_action = None
    return PathologyDefinition(
        pathology_id=pathology_id,
        formula_id=formula_id,
        description=description,
        severity=sev,
        suggested_action=suggested_action,
    )


def _build_metadata(pathology_id: str, rule: dict[str, Any]) -> dict[str, Any]:
    meta = rule.get("metadata")
    if isinstance(meta, dict):
        return dict(meta)
    return {}


def _build_activation_rule(pathology_id: str, rule: dict[str, Any]) -> dict[str, Any] | None:
    activation = rule.get("activation_rule")
    if not isinstance(activation, dict):
        return None
    field = activation.get("field")
    operator = activation.get("operator")
    threshold = activation.get("threshold")
    if not isinstance(field, str) or not isinstance(operator, str) or threshold is None:
        return None
    if operator not in _OPERATORS:
        return None
    return {"field": field, "operator": operator, "threshold": threshold}


class LocalPathologyKnowledgeTank:
    def __init__(self) -> None:
        raw_rules = _load_rules()
        self._definitions: dict[str, PathologyDefinition] = {}
        self._metadata: dict[str, dict[str, Any]] = {}
        self._rules: dict[str, dict[str, Any]] = {}
        for pathology_id, rule in raw_rules.items():
            if not isinstance(pathology_id, str) or not isinstance(rule, dict):
                continue
            definition = _build_definition(pathology_id, rule)
            if definition is None:
                continue
            self._definitions[pathology_id] = definition
            self._metadata[pathology_id] = _build_metadata(pathology_id, rule)
            activation = _build_activation_rule(pathology_id, rule)
            if activation is not None:
                self._rules[pathology_id] = {
                    "activation": activation,
                    "active_explanation_template": rule.get("active_explanation_template", ""),
                    "not_detected_explanation": rule.get("not_detected_explanation", ""),
                }

    def get_definition(self, pathology_id: str) -> PathologyDefinition | None:
        return self._definitions.get(pathology_id)

    def get_metadata(self, pathology_id: str) -> dict:
        return dict(self._metadata.get(pathology_id, {}))

    def get_evaluator(self, pathology_id: str) -> PathologyEvaluator | None:
        if pathology_id not in self._rules:
            return None
        return lambda payload: self._evaluate_rule(pathology_id, payload)

    def _evaluate_rule(self, pathology_id: str, payload: PathologyEvaluationInput) -> PathologyFinding:
        definition = self.get_definition(pathology_id)
        if definition is None:
            return PathologyFinding(
                cliente_id=payload.cliente_id,
                pathology_id=pathology_id,
                formula_result_id=payload.formula_result_id,
                formula_id=payload.formula_result.formula_id,
                status=PathologyStatus.PENDING_DATA,
                source_refs=payload.formula_result.source_refs,
                explanation="Patolog\u00eda no encontrada en tanque local.",
                metadata={"blocking_reason": "PATHOLOGY_NOT_SUPPORTED"},
            )

        result = payload.formula_result
        rule = self._rules.get(pathology_id)
        if rule is None:
            return PathologyFinding(
                cliente_id=payload.cliente_id,
                pathology_id=pathology_id,
                formula_result_id=payload.formula_result_id,
                formula_id=result.formula_id,
                status=PathologyStatus.PENDING_DATA,
                source_refs=result.source_refs,
                explanation="Patolog\u00eda sin regla de activaci\u00f3n implementada.",
                metadata={"blocking_reason": "PATHOLOGY_NOT_IMPLEMENTED"},
            )

        activation = rule["activation"]
        field = activation["field"]
        operator = activation["operator"]
        threshold = activation["threshold"]

        raw_field = getattr(result, field, None)
        if raw_field is None:
            return PathologyFinding(
                cliente_id=payload.cliente_id,
                pathology_id=pathology_id,
                formula_result_id=payload.formula_result_id,
                formula_id=result.formula_id,
                status=PathologyStatus.PENDING_DATA,
                source_refs=result.source_refs,
                explanation="Valor de activaci\u00f3n no disponible para evaluar la patolog\u00eda.",
                metadata={"blocking_reason": "PATHOLOGY_RULE_VALUE_MISSING"},
            )

        op_fn = _OPERATORS.get(operator)
        if op_fn is None:
            return PathologyFinding(
                cliente_id=payload.cliente_id,
                pathology_id=pathology_id,
                formula_result_id=payload.formula_result_id,
                formula_id=result.formula_id,
                status=PathologyStatus.PENDING_DATA,
                source_refs=result.source_refs,
                explanation=f"Operador de regla no soportado: {operator}.",
                metadata={"blocking_reason": "PATHOLOGY_RULE_UNSUPPORTED"},
            )

        metadata = {"catalog": self.get_metadata(pathology_id)}
        if op_fn(raw_field, threshold):
            template = rule.get("active_explanation_template", "")
            try:
                explanation = template.format(value=raw_field)
            except (KeyError, ValueError):
                explanation = template
            return PathologyFinding(
                cliente_id=payload.cliente_id,
                pathology_id=definition.pathology_id,
                formula_result_id=payload.formula_result_id,
                formula_id=result.formula_id,
                status=PathologyStatus.ACTIVE,
                severity=definition.severity,
                suggested_action=definition.suggested_action,
                source_refs=result.source_refs,
                explanation=explanation,
                metadata=metadata,
            )

        not_detected = rule.get("not_detected_explanation", "")
        return PathologyFinding(
            cliente_id=payload.cliente_id,
            pathology_id=definition.pathology_id,
            formula_result_id=payload.formula_result_id,
            formula_id=result.formula_id,
            status=PathologyStatus.NOT_DETECTED,
            source_refs=result.source_refs,
            explanation=not_detected,
            metadata=metadata,
        )
