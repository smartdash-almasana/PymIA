"""Contracts for the minimal generic productive capability kernel."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Literal

SCHEMA_VERSION: Final[str] = "SERVICE_1_GENERIC_CAPABILITY_CONTRACTS_V1"

CapabilityKind = Literal["ATOMIC", "COMPOSITE"]
AggregationMode = Literal["SUM", "SINGLE_VALUE"]
Comparison = Literal["LT", "LE", "EQ", "GE", "GT"]
ClassificationMatch = Literal["ALL", "ANY"]


@dataclass(frozen=True)
class VariableRequirementV1:
    name: str
    aggregation: AggregationMode
    minimum: Decimal | None = None
    minimum_inclusive: bool = True
    maximum: Decimal | None = None
    maximum_inclusive: bool = True
    unit: str | None = None
    source_capability_ref: str | None = None
    source_result_key: str | None = None


@dataclass(frozen=True)
class ClassificationPredicate:
    """One declarative comparison; it never derives a value."""

    left_ref: str
    comparison: Comparison
    right_ref: str | None = None
    literal: Decimal | None = None


@dataclass(frozen=True, init=False)
class ClassificationRule:
    """Declarative policy composed from one or more comparisons.

    ``comparison``/``reference_*`` are accepted only as a migration boundary
    for the former single-predicate contract. New definitions should provide
    ``match`` and ``predicates`` explicitly.
    """

    code: str
    match: ClassificationMatch
    predicates: tuple[ClassificationPredicate, ...]

    def __init__(
        self,
        code: str,
        comparison: Comparison | None = None,
        reference_variable: str | None = None,
        reference_value: Decimal | None = None,
        *,
        match: ClassificationMatch = "ALL",
        predicates: tuple[ClassificationPredicate, ...] | list[ClassificationPredicate] = (),
    ) -> None:
        if match not in ("ALL", "ANY"):
            raise ValueError("classification match must be ALL or ANY")
        explicit_predicates = tuple(predicates)
        legacy_arguments = comparison is not None or reference_variable is not None or reference_value is not None
        if explicit_predicates and legacy_arguments:
            raise ValueError("use predicates or legacy comparison arguments, not both")
        if not explicit_predicates:
            if comparison is None:
                raise ValueError("classification rule requires predicates")
            explicit_predicates = (
                ClassificationPredicate(
                    left_ref="result",
                    comparison=comparison,
                    right_ref=reference_variable,
                    literal=reference_value,
                ),
            )
        if not all(isinstance(predicate, ClassificationPredicate) for predicate in explicit_predicates):
            raise TypeError("classification predicates must be ClassificationPredicate instances")
        if not str(code).strip():
            raise ValueError("classification rule code is required")
        object.__setattr__(self, "code", str(code).strip())
        object.__setattr__(self, "match", match)
        object.__setattr__(self, "predicates", explicit_predicates)

    @property
    def comparison(self) -> Comparison:
        """Expose the former atomic field during the bounded migration."""

        return self.predicates[0].comparison

    @property
    def reference_variable(self) -> str | None:
        predicate = self.predicates[0]
        return predicate.right_ref

    @property
    def reference_value(self) -> Decimal | None:
        predicate = self.predicates[0]
        return predicate.literal


@dataclass(frozen=True, init=False)
class ClassificationRuleV1(ClassificationRule):
    """Compatibility constructor for pre-R7 single-predicate definitions."""

    def __init__(
        self,
        code: str,
        comparison: Comparison | None = None,
        reference_variable: str | None = None,
        reference_value: Decimal | None = None,
        *,
        match: ClassificationMatch = "ALL",
        predicates: tuple[ClassificationPredicate, ...] | list[ClassificationPredicate] = (),
    ) -> None:
        super().__init__(
            code,
            comparison,
            reference_variable,
            reference_value,
            match=match,
            predicates=predicates,
        )


def classify_classification_rules(
    rules: tuple[ClassificationRule, ...],
    *,
    result: Decimal | float | int,
    inputs: dict[str, Decimal | float | int] | None = None,
    derived_values: dict[str, Decimal | float | int] | None = None,
) -> str | None:
    """Return the first matching policy code using comparisons only."""

    context: dict[str, Decimal | float | int] = {"result": result}
    context.update(inputs or {})
    context.update(derived_values or {})
    for rule in rules:
        matches = tuple(_evaluate_classification_predicate(predicate, context) for predicate in rule.predicates)
        if matches and (all(matches) if rule.match == "ALL" else any(matches)):
            return rule.code
    return None


def _evaluate_classification_predicate(
    predicate: ClassificationPredicate,
    context: dict[str, Decimal | float | int],
) -> bool:
    left = context.get(predicate.left_ref)
    right = context.get(predicate.right_ref) if predicate.right_ref is not None else predicate.literal
    if left is None or right is None:
        return False
    return {
        "LT": left < right,
        "LE": left <= right,
        "EQ": left == right,
        "GE": left >= right,
        "GT": left > right,
    }[predicate.comparison]


@dataclass(frozen=True)
class OutcomePolicyV1:
    findings: tuple[tuple[str, str], ...]
    treatments: tuple[tuple[str, tuple[str, ...]], ...]
    limitations: tuple[str, ...]
    forbidden_claims: tuple[str, ...]


@dataclass(frozen=True)
class CapabilityDefinitionV1:
    capability_ref: str
    pathology_code: str
    formula_ref: str
    kind: CapabilityKind
    variables: tuple[VariableRequirementV1, ...]
    result_key: str
    result_unit: str
    classifications: tuple[ClassificationRule, ...]
    outcome_policy: OutcomePolicyV1
    delivery_authorized: bool = False


__all__ = [
    "SCHEMA_VERSION",
    "VariableRequirementV1",
    "ClassificationMatch",
    "ClassificationPredicate",
    "ClassificationRule",
    "ClassificationRuleV1",
    "classify_classification_rules",
    "OutcomePolicyV1",
    "CapabilityDefinitionV1",
]
