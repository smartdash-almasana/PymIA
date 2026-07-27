"""Minimal isolated generic capability engine for Service 1."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Final, Mapping

from pymia.smartpyme.service_1_capability_contracts_v1 import CapabilityDefinitionV1, FormulaNodeV1
from pymia.smartpyme.service_1_computability_v1 import Service1GovernedComputationInputV1
from pymia.smartpyme.service_1_capability_registry_v1 import get_capability_definition_v1

SCHEMA_VERSION: Final[str] = "SERVICE_1_GENERIC_CAPABILITY_ENGINE_V1"
STATUS_EVALUATED: Final[str] = "EVALUATED"
STATUS_BLOCKED: Final[str] = "BLOCKED"
def execute_generic_capability_v1(
    *, capability_ref: str, computation_plan: object, normalized_tables: object, column_refs: object,
    governed_results: object = None, governed_computation_input: object = None,
) -> dict[str, object]:
    definition = get_capability_definition_v1(capability_ref)
    if definition is None:
        return _blocked([f"unsupported capability: {capability_ref}."])
    execution_input = _execution_input_payload(
        governed_computation_input=governed_computation_input,
    )
    input_errors = _validate_execution_input(definition, execution_input)
    if input_errors:
        return _blocked(input_errors, definition=definition)
    inputs, sources, evidence_errors = _resolve_inputs(
        definition=definition,
        computation_plan=execution_input,
        normalized_tables=normalized_tables,
        column_refs=column_refs,
        governed_results=governed_results,
    )
    if evidence_errors:
        return _blocked(evidence_errors, definition=definition, aggregation={"sources": sources, "sample_based": False})
    domain_errors = _validate_domains(definition, inputs)
    if domain_errors:
        return _blocked(domain_errors, definition=definition, inputs=inputs, aggregation={"sources": sources, "sample_based": False})
    try:
        result = _evaluate_formula(definition.formula, inputs)
    except ZeroDivisionError:
        return _blocked(["formula denominator must be greater than zero."], definition=definition, inputs=inputs)
    classification = _classify(definition, result, inputs)
    if classification is None:
        return _blocked(["no governed classification matched the computed result."], definition=definition, inputs=inputs)
    findings = dict(definition.outcome_policy.findings)
    treatments = dict(definition.outcome_policy.treatments)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_EVALUATED,
        "capability_ref": definition.capability_ref,
        "pathology_code": definition.pathology_code,
        "formula_ref": definition.formula_ref,
        "classification": classification,
        "inputs": {key: float(value) for key, value in inputs.items()},
        "computed": {
            definition.result_key: float(result),
            "typed_result": {
                "value": float(result),
                "unit": definition.result_unit,
                "period": float(inputs["days"]) if "days" in inputs else None,
                "provenance": "owner_confirmed_normalized_evidence",
            },
        },
        "aggregation": {"status": "AGGREGATED", "sources": sources, "sample_based": False},
        "outcome": {
            "status": "OUTCOME_READY",
            "capability_ref": definition.capability_ref,
            "classification": classification,
            "finding": findings[classification],
            "treatment_actions": list(treatments[classification]),
            "limitations": list(definition.outcome_policy.limitations),
            "forbidden_claims": list(definition.outcome_policy.forbidden_claims),
            "inputs_used": {key: float(value) for key, value in inputs.items()},
            "computed_results": {"computed": {definition.result_key: float(result)}},
            "bounded_finding_generated": True,
            "causal_diagnosis_generated": False,
            "runtime_authorized": False,
            "delivery_authorized": False,
        },
        "errors": [],
        **_closed_flags(definition.delivery_authorized),
    }


def _execution_input_payload(*, governed_computation_input: object) -> object:
    if isinstance(governed_computation_input, Service1GovernedComputationInputV1):
        return governed_computation_input.to_dict()
    if isinstance(governed_computation_input, Mapping):
        return dict(governed_computation_input)
    return None


def _validate_execution_input(definition: CapabilityDefinitionV1, payload: object) -> list[str]:
    if not isinstance(payload, dict):
        return ["governed computation input is required."]
    if payload.get("schema_version") != "SERVICE_1_GOVERNED_COMPUTATION_INPUT_V1":
        return ["governed computation input schema is required."]
    expected = {
        "requested_capability": definition.capability_ref,
        "pathology_code": definition.pathology_code,
        "formula_id": definition.formula_ref,
    }
    errors = [f"governed input {field} must equal {value}." for field, value in expected.items() if payload.get(field) != value]
    required = tuple(variable.name for variable in definition.variables)
    if tuple(payload.get("required_variables") or ()) != required:
        errors.append("governed input required_variables do not match capability definition.")
    bindings = payload.get("source_bindings")
    if not isinstance(bindings, dict) or set(bindings) != set(required):
        errors.append("governed input source_bindings must cover required_variables exactly.")
    if any(payload.get(flag) is not False for flag in _closed_flags(False)):
        errors.append("governed input safety flags must be explicitly false.")
    return errors


def _resolve_inputs(
    *, definition: CapabilityDefinitionV1, computation_plan: object, normalized_tables: object, column_refs: object, governed_results: object
) -> tuple[dict[str, Decimal], dict[str, dict[str, object]], list[str]]:
    if definition.kind == "COMPOSITE":
        return _resolve_composite_inputs(
            definition=definition,
            computation_plan=computation_plan,
            governed_results=governed_results,
        )
    return _resolve_atomic_inputs(
        definition=definition,
        computation_plan=computation_plan,
        normalized_tables=normalized_tables,
        column_refs=column_refs,
    )


def _resolve_atomic_inputs(
    *, definition: CapabilityDefinitionV1, computation_plan: object, normalized_tables: object, column_refs: object
) -> tuple[dict[str, Decimal], dict[str, dict[str, object]], list[str]]:
    if not isinstance(computation_plan, dict):
        return {}, {}, ["computation_plan must be an object."]
    if not isinstance(normalized_tables, list) or not normalized_tables:
        return {}, {}, ["normalized_tables must be a non-empty list."]
    if not isinstance(column_refs, list) or not column_refs:
        return {}, {}, ["column_refs must be a non-empty list."]
    bindings = computation_plan.get("source_bindings")
    if not isinstance(bindings, dict):
        return {}, {}, ["computation_plan source_bindings must be an object."]
    tables: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for raw in normalized_tables:
        if not isinstance(raw, dict):
            errors.append("normalized table entries must be objects.")
            continue
        sheet = str(raw.get("sheet_name") or "").strip()
        if not sheet or sheet in tables:
            errors.append("normalized table sheet_name must be present and unique.")
            continue
        tables[sheet] = raw
    inputs: dict[str, Decimal] = {}
    sources: dict[str, dict[str, object]] = {}
    for requirement in definition.variables:
        source_column = str(bindings.get(requirement.name) or "").strip()
        matches = [ref for ref in column_refs if isinstance(ref, dict) and str(ref.get("column_name") or "").strip() == source_column]
        if len(matches) != 1:
            errors.append(f"source binding for {requirement.name} must resolve exactly once: {source_column}.")
            continue
        ref = matches[0]
        sheet = str(ref.get("sheet_name") or "").strip()
        normalized_column = str(ref.get("normalized_column_name") or ref.get("column_name") or "").strip()
        rows = (tables.get(sheet) or {}).get("rows")
        if not isinstance(rows, list) or not rows:
            errors.append(f"normalized rows must be a non-empty list for sheet: {sheet}.")
            continue
        values: list[Decimal] = []
        for index, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                errors.append(f"row {index} in {sheet} must be an object.")
                continue
            raw_value = row.get(normalized_column)
            if raw_value is None or (isinstance(raw_value, str) and not raw_value.strip()):
                continue
            value, error = _number(raw_value)
            if error:
                errors.append(f"{sheet}.{normalized_column} row {index}: {error}")
            else:
                values.append(value)
        if not values:
            errors.append(f"{requirement.name} requires at least one confirmed numeric value.")
            continue
        if requirement.aggregation == "SINGLE_VALUE":
            unique = set(values)
            if len(unique) != 1:
                errors.append(f"{requirement.name} must resolve to one consistent confirmed value.")
                continue
            aggregated = values[0]
        else:
            aggregated = sum(values, Decimal("0"))
        inputs[requirement.name] = aggregated
        sources[requirement.name] = {
            "sheet_name": sheet,
            "column_name": source_column,
            "normalized_column_name": normalized_column,
            "value_count": len(values),
            "aggregation_mode": requirement.aggregation,
        }
    return inputs, sources, errors


def _resolve_composite_inputs(
    *, definition: CapabilityDefinitionV1, computation_plan: object, governed_results: object
) -> tuple[dict[str, Decimal], dict[str, dict[str, object]], list[str]]:
    if not isinstance(computation_plan, dict):
        return {}, {}, ["computation_plan must be an object."]
    if not isinstance(governed_results, list) or not governed_results:
        return {}, {}, ["governed_results must be a non-empty list for a composite capability."]
    bindings = computation_plan.get("source_bindings")
    if not isinstance(bindings, dict):
        return {}, {}, ["computation_plan source_bindings must be an object."]

    inputs: dict[str, Decimal] = {}
    sources: dict[str, dict[str, object]] = {}
    errors: list[str] = []
    for requirement in definition.variables:
        expected_capability = requirement.source_capability_ref
        expected_result_key = requirement.source_result_key
        if not expected_capability or not expected_result_key:
            errors.append(f"composite requirement {requirement.name} has no governed source contract.")
            continue
        expected_binding = {"capability_ref": expected_capability, "result_key": expected_result_key}
        if bindings.get(requirement.name) != expected_binding:
            errors.append(f"source binding for {requirement.name} must equal its governed source contract.")
            continue
        matches = [
            result
            for result in governed_results
            if isinstance(result, dict) and result.get("capability_ref") == expected_capability
        ]
        if len(matches) != 1:
            errors.append(f"governed result for {requirement.name} must resolve exactly once: {expected_capability}.")
            continue
        source = matches[0]
        source_errors, value = _validate_governed_result(
            source=source,
            capability_ref=expected_capability,
            result_key=expected_result_key,
        )
        if source_errors:
            errors.extend(f"{requirement.name}: {error}" for error in source_errors)
            continue
        assert value is not None
        inputs[requirement.name] = value
        sources[requirement.name] = {
            "source_kind": "GOVERNED_RESULT",
            "capability_ref": expected_capability,
            "result_key": expected_result_key,
            "aggregation_mode": requirement.aggregation,
        }
    return inputs, sources, errors


def _validate_governed_result(
    *, source: dict[str, Any], capability_ref: str, result_key: str
) -> tuple[list[str], Decimal | None]:
    errors: list[str] = []
    if source.get("status") != STATUS_EVALUATED:
        errors.append("status must equal EVALUATED.")
    if source.get("capability_ref") != capability_ref:
        errors.append(f"capability_ref must equal {capability_ref}.")
    if any(source.get(flag) is not False for flag in _closed_flags(False)):
        errors.append("safety flags must be explicitly false.")
    outcome = source.get("outcome")
    if isinstance(outcome, dict) and outcome.get("causal_diagnosis_generated") is True:
        errors.append("causal diagnosis must remain disabled.")
    computed = source.get("computed")
    if not isinstance(computed, dict):
        return [*errors, "computed must be an object."], None
    main_value, main_error = _number(computed.get(result_key))
    if main_error:
        errors.append(f"{result_key} {main_error}")
    typed_result = computed.get("typed_result")
    if not isinstance(typed_result, dict):
        return [*errors, "typed_result must be an object."], None
    typed_value, typed_error = _number(typed_result.get("value"))
    if typed_error:
        errors.append(f"typed_result.value {typed_error}")
    if typed_result.get("unit") != "days":
        errors.append("typed_result.unit must equal days.")
    if main_error or typed_error:
        return errors, None
    if main_value != typed_value:
        errors.append(f"{result_key} must equal typed_result.value.")
    return errors, main_value if not errors else None


def _validate_domains(definition: CapabilityDefinitionV1, inputs: dict[str, Decimal]) -> list[str]:
    errors: list[str] = []
    for requirement in definition.variables:
        value = inputs.get(requirement.name)
        if value is None:
            continue
        if requirement.minimum is not None:
            invalid = value < requirement.minimum if requirement.minimum_inclusive else value <= requirement.minimum
            if invalid:
                comparator = "greater than or equal to" if requirement.minimum_inclusive else "greater than"
                errors.append(f"{requirement.name} must be {comparator} {requirement.minimum}.")
        if requirement.maximum is not None:
            invalid = value > requirement.maximum if requirement.maximum_inclusive else value >= requirement.maximum
            if invalid:
                comparator = "less than or equal to" if requirement.maximum_inclusive else "less than"
                errors.append(f"{requirement.name} must be {comparator} {requirement.maximum}.")
    return errors


def _evaluate_formula(node: FormulaNodeV1, inputs: dict[str, Decimal]) -> Decimal:
    if node.operation == "VARIABLE":
        if not node.variable_name or node.variable_name not in inputs:
            raise ValueError("formula variable is not available")
        return inputs[node.variable_name]
    if node.operation == "VALUE":
        if node.value is None:
            raise ValueError("formula literal is missing")
        return node.value
    if node.left is None or node.right is None:
        raise ValueError("binary formula node requires both operands")
    left = _evaluate_formula(node.left, inputs)
    right = _evaluate_formula(node.right, inputs)
    if node.operation == "ADD":
        return left + right
    if node.operation == "SUBTRACT":
        return left - right
    if node.operation == "MULTIPLY":
        return left * right
    if node.operation == "DIVIDE":
        if right <= 0:
            raise ZeroDivisionError
        return left / right
    raise ValueError(f"unsupported formula operation: {node.operation}")


def _classify(definition: CapabilityDefinitionV1, result: Decimal, inputs: dict[str, Decimal]) -> str | None:
    for rule in definition.classifications:
        reference = inputs.get(rule.reference_variable) if rule.reference_variable else rule.reference_value
        if reference is None:
            continue
        matched = {
            "LT": result < reference,
            "LE": result <= reference,
            "EQ": result == reference,
            "GE": result >= reference,
            "GT": result > reference,
        }[rule.comparison]
        if matched:
            return rule.code
    return None


def _number(value: object) -> tuple[Decimal, str | None]:
    if isinstance(value, bool):
        return Decimal("0"), "value must be numeric."
    try:
        number = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return Decimal("0"), "value must be numeric."
    if not number.is_finite():
        return Decimal("0"), "value must be finite."
    return number, None


def _closed_flags(delivery_authorized: bool) -> dict[str, bool]:
    return {
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": delivery_authorized,
        "diagnosis_generated": False,
    }


def _blocked(
    errors: list[str], *, definition: CapabilityDefinitionV1 | None = None, inputs: dict[str, Decimal] | None = None, aggregation: dict[str, object] | None = None
) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_BLOCKED,
        "capability_ref": definition.capability_ref if definition else None,
        "pathology_code": definition.pathology_code if definition else None,
        "formula_ref": definition.formula_ref if definition else None,
        "inputs": {key: float(value) for key, value in (inputs or {}).items()},
        "computed": {},
        "aggregation": dict(aggregation or {}),
        "outcome": {"status": "OUTCOME_BLOCKED", "bounded_finding_generated": False, "causal_diagnosis_generated": False},
        "errors": list(errors),
        **_closed_flags(False),
    }


__all__ = ["SCHEMA_VERSION", "STATUS_EVALUATED", "STATUS_BLOCKED", "execute_generic_capability_v1"]
