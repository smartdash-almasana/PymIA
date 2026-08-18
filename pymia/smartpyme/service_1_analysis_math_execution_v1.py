"""F8 mathematical execution for governed Service 1 AnalysisPlan evidence.

F8 is the only analytical aggregation runtime. It consumes F7 prepared evidence
and delegates every arithmetic primitive and business formula to
FormulaEngineService. It does not render UI, create findings, persist results,
or introduce capability/rubro-specific engines.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Final, Mapping

from pymia.contracts.formula_contract import (
    FormulaInput,
    FormulaStatus,
    MathPrimitiveInput,
    MathPrimitiveOperation,
)
from pymia.services.formula_engine_service import FormulaEngineService
from pymia.smartpyme.service_1_analysis_evidence_preparation_v1 import (
    Service1PreparedAnalysisEvidenceV1,
    Service1PreparedGroupV1,
    Service1PreparedRowV1,
)
from pymia.smartpyme.service_1_analysis_plan_v1 import AnalysisKind
from pymia.smartpyme.service_1_computability_v1 import Service1GovernedAnalysisInputV1

SCHEMA_VERSION: Final[str] = "SERVICE_1_ANALYSIS_MATH_EXECUTION_V1"
RESULT_SCHEMA_VERSION: Final[str] = "SERVICE_1_ANALYSIS_MATH_RESULT_V1"

STATUS_EVALUATED: Final[str] = "EVALUATED"
STATUS_NEEDS_EVIDENCE: Final[str] = "NEEDS_EVIDENCE"
STATUS_UNSUPPORTED: Final[str] = "UNSUPPORTED"
STATUS_BLOCKED: Final[str] = "BLOCKED"
ALLOWED_STATUSES: Final[frozenset[str]] = frozenset(
    {STATUS_EVALUATED, STATUS_NEEDS_EVIDENCE, STATUS_UNSUPPORTED, STATUS_BLOCKED}
)

_AUTHORITY_FLAGS: Final[tuple[str, ...]] = (
    "runtime_authorized",
    "tool_execution_authorized",
    "product_ready",
    "delivery_authorized",
    "diagnosis_generated",
    "analysis_execution_authorized",
)


@dataclass(frozen=True)
class _MeasureInputOption:
    operation: MathPrimitiveOperation
    role_alternatives: tuple[str, ...]
    paired_role_alternatives: tuple[str, ...] = ()


@dataclass(frozen=True)
class _MeasureInputSpec:
    input_name: str
    operation: MathPrimitiveOperation
    role_alternatives: tuple[str, ...]
    paired_role_alternatives: tuple[str, ...] = ()
    fallback_options: tuple[_MeasureInputOption, ...] = ()


@dataclass(frozen=True)
class _MeasureExecutionSpec:
    measure_ref: str
    inputs: tuple[_MeasureInputSpec, ...]
    formula_ref: str | None
    direct_input_name: str | None
    output_unit: str


@dataclass(frozen=True)
class _CrossGroupMeasureExecutionSpec:
    measure_ref: str
    basis_input: _MeasureInputSpec
    formula_ref: str
    numerator_input_name: str
    denominator_input_name: str
    output_unit: str


_MEASURE_SPECS: Final[dict[str, _MeasureExecutionSpec]] = {
    "sales": _MeasureExecutionSpec(
        measure_ref="sales",
        inputs=(
            _MeasureInputSpec(
                input_name="sales",
                operation=MathPrimitiveOperation.SUM,
                role_alternatives=("sales_amount",),
                fallback_options=(
                    _MeasureInputOption(
                        operation=MathPrimitiveOperation.SUM_PRODUCT,
                        role_alternatives=("quantity",),
                        paired_role_alternatives=("unit_sale_price",),
                    ),
                ),
            ),
        ),
        formula_ref=None,
        direct_input_name="sales",
        output_unit="currency",
    ),
    "gross_margin": _MeasureExecutionSpec(
        measure_ref="gross_margin",
        inputs=(
            _MeasureInputSpec(
                input_name="ventas",
                operation=MathPrimitiveOperation.SUM,
                role_alternatives=("sales_amount",),
                fallback_options=(
                    _MeasureInputOption(
                        operation=MathPrimitiveOperation.SUM_PRODUCT,
                        role_alternatives=("quantity",),
                        paired_role_alternatives=("unit_sale_price",),
                    ),
                ),
            ),
            _MeasureInputSpec(
                input_name="costos",
                operation=MathPrimitiveOperation.SUM_PRODUCT,
                role_alternatives=("quantity",),
                paired_role_alternatives=("unit_cost_candidate",),
            ),
        ),
        formula_ref="margen_bruto",
        direct_input_name=None,
        output_unit="ratio",
    ),
    "units": _MeasureExecutionSpec(
        measure_ref="units",
        inputs=(
            _MeasureInputSpec(
                input_name="units",
                operation=MathPrimitiveOperation.SUM,
                role_alternatives=("quantity",),
            ),
        ),
        formula_ref=None,
        direct_input_name="units",
        output_unit="units",
    ),
    "row_count": _MeasureExecutionSpec(
        measure_ref="row_count",
        inputs=(
            _MeasureInputSpec(
                input_name="row_count",
                operation=MathPrimitiveOperation.COUNT,
                role_alternatives=("transaction_identifier",),
            ),
        ),
        formula_ref=None,
        direct_input_name="row_count",
        output_unit="count",
    ),
    "catalog_price_variance_pct": _MeasureExecutionSpec(
        measure_ref="catalog_price_variance_pct",
        inputs=(
            _MeasureInputSpec(
                input_name="observed_sales",
                operation=MathPrimitiveOperation.SUM_PRODUCT,
                role_alternatives=("quantity",),
                paired_role_alternatives=("unit_sale_price",),
            ),
            _MeasureInputSpec(
                input_name="observed_units",
                operation=MathPrimitiveOperation.SUM,
                role_alternatives=("quantity",),
            ),
            _MeasureInputSpec(
                input_name="catalog_price",
                operation=MathPrimitiveOperation.SINGLE_VALUE,
                role_alternatives=("list_price",),
            ),
        ),
        formula_ref="precio_catalogo_variacion_pct",
        direct_input_name=None,
        output_unit="percentage",
    ),
    "dso": _MeasureExecutionSpec(
        measure_ref="dso",
        inputs=(
            _MeasureInputSpec(
                input_name="accounts_receivable",
                operation=MathPrimitiveOperation.SUM,
                role_alternatives=("accounts_receivable_amount",),
            ),
            _MeasureInputSpec(
                input_name="sales",
                operation=MathPrimitiveOperation.SUM,
                role_alternatives=("sales_amount",),
                fallback_options=(
                    _MeasureInputOption(
                        operation=MathPrimitiveOperation.SUM_PRODUCT,
                        role_alternatives=("quantity",),
                        paired_role_alternatives=("unit_sale_price",),
                    ),
                ),
            ),
            _MeasureInputSpec(
                input_name="days",
                operation=MathPrimitiveOperation.SINGLE_VALUE,
                role_alternatives=("period_days", "days"),
            ),
        ),
        formula_ref="PYME_011_dso",
        direct_input_name=None,
        output_unit="days",
    ),
    "projected_cash_balance": _MeasureExecutionSpec(
        measure_ref="projected_cash_balance",
        inputs=(
            _MeasureInputSpec(
                input_name="initial_balance",
                operation=MathPrimitiveOperation.SINGLE_VALUE,
                role_alternatives=("initial_balance",),
            ),
            _MeasureInputSpec(
                input_name="expected_collections",
                operation=MathPrimitiveOperation.SUM,
                role_alternatives=("expected_collections",),
            ),
            _MeasureInputSpec(
                input_name="expected_payments",
                operation=MathPrimitiveOperation.SUM,
                role_alternatives=("expected_payments",),
            ),
        ),
        formula_ref="LIQ_002_saldo_final_proyectado",
        direct_input_name=None,
        output_unit="currency",
    ),
}


_CROSS_GROUP_MEASURE_SPECS: Final[dict[str, _CrossGroupMeasureExecutionSpec]] = {
    "sales_concentration": _CrossGroupMeasureExecutionSpec(
        measure_ref="sales_concentration",
        basis_input=_MeasureInputSpec(
            input_name="group_sales",
            operation=MathPrimitiveOperation.SUM,
            role_alternatives=("sales_amount",),
            fallback_options=(
                _MeasureInputOption(
                    operation=MathPrimitiveOperation.SUM_PRODUCT,
                    role_alternatives=("quantity",),
                    paired_role_alternatives=("unit_sale_price",),
                ),
            ),
        ),
        formula_ref="PYME_033_concentracion_sku",
        numerator_input_name="main_sku_sales",
        denominator_input_name="total_sales",
        output_unit="percentage",
    ),
}


@dataclass(frozen=True)
class Service1ExecutedMeasureV1:
    measure_ref: str
    value: float
    unit: str
    formula_ref: str | None
    formula_inputs: Mapping[str, float]
    source_refs: tuple[str, ...]
    math_trace: tuple[Mapping[str, Any], ...]

    def __post_init__(self) -> None:
        if not str(self.measure_ref or "").strip() or not str(self.unit or "").strip():
            raise ValueError("measure_ref and unit are required")
        if isinstance(self.value, bool):
            raise ValueError("measure value must be numeric")
        if not isinstance(self.formula_inputs, Mapping):
            raise ValueError("formula_inputs must be a mapping")
        if not self.source_refs or any(not str(ref).strip() for ref in self.source_refs):
            raise ValueError("source_refs must be non-empty")
        object.__setattr__(self, "formula_inputs", dict(self.formula_inputs))
        object.__setattr__(self, "source_refs", tuple(self.source_refs))
        object.__setattr__(self, "math_trace", tuple(dict(item) for item in self.math_trace))

    def to_dict(self) -> dict[str, Any]:
        return {
            "measure_ref": self.measure_ref,
            "value": float(self.value),
            "unit": self.unit,
            "formula_ref": self.formula_ref,
            "formula_inputs": dict(self.formula_inputs),
            "source_refs": list(self.source_refs),
            "math_trace": [dict(item) for item in self.math_trace],
        }


@dataclass(frozen=True)
class Service1ExecutedGroupV1:
    group_ref: str
    key: Mapping[str, str]
    measures: Mapping[str, Service1ExecutedMeasureV1]
    member_row_refs: tuple[str, ...]
    rank: int | None = None

    def __post_init__(self) -> None:
        if not str(self.group_ref or "").strip():
            raise ValueError("group_ref is required")
        if not isinstance(self.key, Mapping) or not isinstance(self.measures, Mapping) or not self.measures:
            raise ValueError("key and non-empty measures mappings are required")
        if any(not isinstance(value, Service1ExecutedMeasureV1) for value in self.measures.values()):
            raise TypeError("measures must contain Service1ExecutedMeasureV1")
        if not self.member_row_refs:
            raise ValueError("member_row_refs must be non-empty")
        if self.rank is not None and self.rank <= 0:
            raise ValueError("rank must be positive")
        object.__setattr__(self, "key", dict(self.key))
        object.__setattr__(self, "measures", dict(self.measures))
        object.__setattr__(self, "member_row_refs", tuple(self.member_row_refs))

    def to_dict(self) -> dict[str, Any]:
        return {
            "group_ref": self.group_ref,
            "key": dict(self.key),
            "measures": {key: value.to_dict() for key, value in self.measures.items()},
            "member_row_refs": list(self.member_row_refs),
            "rank": self.rank,
        }


@dataclass(frozen=True)
class Service1AnalysisMathResultV1:
    case_id: str
    analysis_id: str
    groups: tuple[Service1ExecutedGroupV1, ...]
    provenance: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = RESULT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not str(self.case_id or "").strip() or not str(self.analysis_id or "").strip():
            raise ValueError("case_id and analysis_id are required")
        if not self.groups:
            raise ValueError("groups must be non-empty")
        if not isinstance(self.provenance, Mapping):
            raise ValueError("provenance must be a mapping")
        if set(_AUTHORITY_FLAGS).intersection(self.provenance):
            raise ValueError("provenance cannot carry downstream authority")
        object.__setattr__(self, "groups", tuple(self.groups))
        object.__setattr__(self, "provenance", dict(self.provenance))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "analysis_id": self.analysis_id,
            "groups": [group.to_dict() for group in self.groups],
            "provenance": dict(self.provenance),
            "mathematical_execution_performed": True,
            "aggregation_execution_performed": True,
            "formula_execution_performed": any(
                measure.formula_ref is not None
                for group in self.groups
                for measure in group.measures.values()
            ),
            "ranking_execution_performed": any(group.rank is not None for group in self.groups),
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
            "analysis_execution_authorized": False,
        }


@dataclass(frozen=True)
class Service1AnalysisMathExecutionDecisionV1:
    case_id: str
    analysis_id: str
    status: str
    reason: str | None
    result: Service1AnalysisMathResultV1 | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not str(self.case_id or "").strip() or not str(self.analysis_id or "").strip():
            raise ValueError("case_id and analysis_id are required")
        if self.status not in ALLOWED_STATUSES:
            raise ValueError("invalid math execution status")
        if self.status == STATUS_EVALUATED and self.result is None:
            raise ValueError("EVALUATED requires result")
        if self.status != STATUS_EVALUATED and self.result is not None:
            raise ValueError("non-evaluated decision cannot carry result")
        if self.status == STATUS_EVALUATED and self.reason is not None:
            raise ValueError("EVALUATED cannot carry reason")
        if self.status != STATUS_EVALUATED and not str(self.reason or "").strip():
            raise ValueError("non-evaluated decision requires reason")
        if not isinstance(self.provenance, Mapping):
            raise ValueError("provenance must be a mapping")
        object.__setattr__(self, "provenance", dict(self.provenance))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "analysis_id": self.analysis_id,
            "status": self.status,
            "reason": self.reason,
            "result": self.result.to_dict() if self.result else None,
            "provenance": dict(self.provenance),
            "runtime_authorized": False,
            "tool_execution_authorized": False,
            "product_ready": False,
            "delivery_authorized": False,
            "diagnosis_generated": False,
            "analysis_execution_authorized": False,
        }


def execute_service_1_analysis_math_v1(
    *,
    case_id: str,
    governed_analysis_input: Service1GovernedAnalysisInputV1,
    prepared_evidence: Service1PreparedAnalysisEvidenceV1,
    formula_engine: FormulaEngineService | None = None,
) -> Service1AnalysisMathExecutionDecisionV1:
    """Execute governed aggregation/formulas over F7 evidence through the Math Brain."""
    case = str(case_id or "").strip()
    if not case:
        raise ValueError("case_id is required")
    if not isinstance(governed_analysis_input, Service1GovernedAnalysisInputV1):
        raise TypeError("governed_analysis_input must be Service1GovernedAnalysisInputV1")
    if not isinstance(prepared_evidence, Service1PreparedAnalysisEvidenceV1):
        raise TypeError("prepared_evidence must be Service1PreparedAnalysisEvidenceV1")
    plan = governed_analysis_input.analysis_plan
    if governed_analysis_input.case_id != case or prepared_evidence.case_id != case:
        return _decision(case, plan.analysis_id, STATUS_BLOCKED, "CASE_ID_DRIFT")
    if prepared_evidence.analysis_id != plan.analysis_id:
        return _decision(case, plan.analysis_id, STATUS_BLOCKED, "ANALYSIS_ID_DRIFT")
    if prepared_evidence.analysis_plan.to_dict() != plan.to_dict():
        return _decision(case, plan.analysis_id, STATUS_BLOCKED, "ANALYSIS_PLAN_DRIFT")
    if prepared_evidence.grain.to_dict() != governed_analysis_input.grain.to_dict():
        return _decision(case, plan.analysis_id, STATUS_BLOCKED, "RESOLVED_GRAIN_DRIFT")

    specs: list[_MeasureExecutionSpec] = []
    cross_group_specs: list[_CrossGroupMeasureExecutionSpec] = []
    expected_formula_refs: list[str] = []
    for measure in plan.measures:
        spec = _MEASURE_SPECS.get(measure)
        cross_spec = _CROSS_GROUP_MEASURE_SPECS.get(measure)
        if spec is None and cross_spec is None:
            return _decision(case, plan.analysis_id, STATUS_UNSUPPORTED, f"UNSUPPORTED_ANALYSIS_MEASURE:{measure}")
        if spec is not None:
            specs.append(spec)
            if spec.formula_ref and spec.formula_ref not in expected_formula_refs:
                expected_formula_refs.append(spec.formula_ref)
        if cross_spec is not None:
            cross_group_specs.append(cross_spec)
            if cross_spec.formula_ref not in expected_formula_refs:
                expected_formula_refs.append(cross_spec.formula_ref)
    if tuple(expected_formula_refs) != tuple(governed_analysis_input.formula_refs):
        return _decision(case, plan.analysis_id, STATUS_BLOCKED, "P8_FORMULA_REF_DRIFT")

    rows_by_ref = {row.row_ref: row for row in prepared_evidence.prepared_rows}
    if len(rows_by_ref) != len(prepared_evidence.prepared_rows):
        return _decision(case, plan.analysis_id, STATUS_BLOCKED, "DUPLICATE_PREPARED_ROW_REF")
    engine = formula_engine or FormulaEngineService()
    group_contexts: list[
        tuple[Service1PreparedGroupV1, list[Service1PreparedRowV1], dict[str, Service1ExecutedMeasureV1]]
    ] = []
    for group in prepared_evidence.groups:
        group_rows: list[Service1PreparedRowV1] = []
        for row_ref in group.member_row_refs:
            row = rows_by_ref.get(row_ref)
            if row is None:
                return _decision(case, plan.analysis_id, STATUS_BLOCKED, f"GROUP_MEMBER_ROW_NOT_FOUND:{row_ref}")
            group_rows.append(row)
        measures: dict[str, Service1ExecutedMeasureV1] = {}
        for spec in specs:
            measure, measure_error = _execute_measure(
                spec=spec,
                rows=group_rows,
                engine=engine,
            )
            if measure_error is not None:
                status, reason = measure_error
                return _decision(case, plan.analysis_id, status, f"{group.group_ref}:{spec.measure_ref}:{reason}")
            assert measure is not None
            measures[spec.measure_ref] = measure
        group_contexts.append((group, group_rows, measures))

    for cross_spec in cross_group_specs:
        cross_error = _execute_cross_group_measure(
            spec=cross_spec,
            group_contexts=group_contexts,
            engine=engine,
        )
        if cross_error is not None:
            status, reason = cross_error
            return _decision(case, plan.analysis_id, status, reason)

    executed_groups = [
        Service1ExecutedGroupV1(
            group_ref=group.group_ref,
            key=group.key,
            measures=measures,
            member_row_refs=group.member_row_refs,
        )
        for group, _rows, measures in group_contexts
    ]
    ordered, order_error = _apply_order_and_limit(plan=plan, groups=executed_groups)
    if order_error is not None:
        return _decision(case, plan.analysis_id, STATUS_UNSUPPORTED, order_error)
    result = Service1AnalysisMathResultV1(
        case_id=case,
        analysis_id=plan.analysis_id,
        groups=tuple(ordered),
        provenance={
            "source": "F7_PREPARED_EVIDENCE_PLUS_P8_GOVERNED_INPUT",
            "math_authority": "FormulaEngineService",
            "aggregation_runtime": "F8",
            "finding_generation_performed": False,
            "delivery_performed": False,
        },
    )
    return Service1AnalysisMathExecutionDecisionV1(
        case_id=case,
        analysis_id=plan.analysis_id,
        status=STATUS_EVALUATED,
        reason=None,
        result=result,
        provenance={"source": "F8_ANALYSIS_MATH_EXECUTION"},
    )


def _execute_measure(
    *,
    spec: _MeasureExecutionSpec,
    rows: list[Service1PreparedRowV1],
    engine: FormulaEngineService,
) -> tuple[Service1ExecutedMeasureV1 | None, tuple[str, str] | None]:
    formula_inputs: dict[str, float] = {}
    all_refs: list[str] = []
    trace: list[dict[str, Any]] = []
    for input_spec in spec.inputs:
        options = (
            _MeasureInputOption(
                operation=input_spec.operation,
                role_alternatives=input_spec.role_alternatives,
                paired_role_alternatives=input_spec.paired_role_alternatives,
            ),
            *input_spec.fallback_options,
        )
        selected: tuple[float, tuple[str, ...], dict[str, Any]] | None = None
        role_errors: list[str] = []
        for option in options:
            primary_role, role_error = _resolve_role(rows, option.role_alternatives)
            if role_error is not None:
                role_errors.append(role_error)
                continue
            assert primary_role is not None
            if option.operation is MathPrimitiveOperation.COUNT:
                refs, evidence_error = _role_source_refs(rows, primary_role)
                if evidence_error is not None:
                    return None, (STATUS_NEEDS_EVIDENCE, evidence_error)
                values = [1.0] * len(rows)
            else:
                values, refs, numeric_error = _numeric_values(rows, primary_role)
                if numeric_error is not None:
                    return None, (STATUS_NEEDS_EVIDENCE, numeric_error)
            paired_values: list[float] = []
            paired_refs: list[str] = []
            paired_role: str | None = None
            if option.paired_role_alternatives:
                paired_role, paired_error = _resolve_role(rows, option.paired_role_alternatives)
                if paired_error is not None:
                    role_errors.append(paired_error)
                    continue
                assert paired_role is not None
                paired_values, paired_refs, numeric_error = _numeric_values(rows, paired_role)
                if numeric_error is not None:
                    return None, (STATUS_NEEDS_EVIDENCE, numeric_error)
            primitive_refs = tuple(dict.fromkeys((*refs, *paired_refs)))
            primitive = engine.calculate_math_primitive(
                MathPrimitiveInput(
                    operation=option.operation,
                    values=values,
                    paired_values=paired_values,
                    source_refs=list(primitive_refs),
                )
            )
            if primitive.status != FormulaStatus.OK or primitive.value is None:
                return None, (STATUS_BLOCKED, primitive.blocking_reason or "MATH_PRIMITIVE_BLOCKED")
            selected = (
                float(primitive.value),
                tuple(primitive.source_refs),
                {
                    "input_name": input_spec.input_name,
                    "operation": option.operation.value,
                    "primary_role": primary_role,
                    "paired_role": paired_role,
                    "value": float(primitive.value),
                    "source_refs": list(primitive.source_refs),
                },
            )
            break
        if selected is None:
            return None, (
                STATUS_NEEDS_EVIDENCE,
                role_errors[0] if role_errors else f"REQUIRED_INPUT_MISSING:{input_spec.input_name}",
            )
        value, source_refs, trace_item = selected
        formula_inputs[input_spec.input_name] = value
        all_refs.extend(source_refs)
        trace.append(trace_item)

    unique_refs = tuple(dict.fromkeys(all_refs))
    if spec.formula_ref is None:
        if not spec.direct_input_name or spec.direct_input_name not in formula_inputs:
            return None, (STATUS_BLOCKED, "DIRECT_MEASURE_INPUT_MISSING")
        value = formula_inputs[spec.direct_input_name]
        return Service1ExecutedMeasureV1(
            measure_ref=spec.measure_ref,
            value=value,
            unit=spec.output_unit,
            formula_ref=None,
            formula_inputs=formula_inputs,
            source_refs=unique_refs,
            math_trace=tuple(trace),
        ), None

    formula_result = engine.calculate(
        spec.formula_ref,
        [
            FormulaInput(name=name, value=value, source_refs=list(unique_refs))
            for name, value in formula_inputs.items()
        ],
    )
    if formula_result.status != FormulaStatus.OK or formula_result.value is None:
        return None, (STATUS_BLOCKED, formula_result.blocking_reason or "FORMULA_EXECUTION_BLOCKED")
    trace.append(
        {
            "operation": "FORMULA",
            "formula_ref": spec.formula_ref,
            "value": float(formula_result.value),
            "source_refs": list(formula_result.source_refs),
        }
    )
    return Service1ExecutedMeasureV1(
        measure_ref=spec.measure_ref,
        value=float(formula_result.value),
        unit=spec.output_unit,
        formula_ref=spec.formula_ref,
        formula_inputs=formula_inputs,
        source_refs=tuple(dict.fromkeys(formula_result.source_refs or unique_refs)),
        math_trace=tuple(trace),
    ), None


def _execute_cross_group_measure(
    *,
    spec: _CrossGroupMeasureExecutionSpec,
    group_contexts: list[
        tuple[Service1PreparedGroupV1, list[Service1PreparedRowV1], dict[str, Service1ExecutedMeasureV1]]
    ],
    engine: FormulaEngineService,
) -> tuple[str, str] | None:
    if not group_contexts:
        return STATUS_NEEDS_EVIDENCE, f"{spec.measure_ref}:GROUP_EVIDENCE_MISSING"

    basis_spec = _MeasureExecutionSpec(
        measure_ref=f"{spec.measure_ref}__basis",
        inputs=(spec.basis_input,),
        formula_ref=None,
        direct_input_name=spec.basis_input.input_name,
        output_unit="currency",
    )
    basis_by_group: list[tuple[float, Service1ExecutedMeasureV1]] = []
    all_basis_refs: list[str] = []
    for group, rows, _measures in group_contexts:
        basis, error = _execute_measure(spec=basis_spec, rows=rows, engine=engine)
        if error is not None:
            status, reason = error
            return status, f"{group.group_ref}:{spec.measure_ref}:{reason}"
        assert basis is not None
        basis_by_group.append((basis.value, basis))
        all_basis_refs.extend(basis.source_refs)

    denominator = engine.calculate_math_primitive(
        MathPrimitiveInput(
            operation=MathPrimitiveOperation.SUM,
            values=[value for value, _basis in basis_by_group],
            source_refs=list(dict.fromkeys(all_basis_refs)),
        )
    )
    if denominator.status != FormulaStatus.OK or denominator.value is None:
        return STATUS_BLOCKED, denominator.blocking_reason or "CROSS_GROUP_DENOMINATOR_BLOCKED"
    total_value = float(denominator.value)
    denominator_refs = tuple(dict.fromkeys(denominator.source_refs))

    for (group, _rows, measures), (basis_value, basis) in zip(group_contexts, basis_by_group, strict=True):
        formula_inputs = {
            spec.numerator_input_name: float(basis_value),
            spec.denominator_input_name: total_value,
        }
        formula_result = engine.calculate(
            spec.formula_ref,
            [
                FormulaInput(
                    name=spec.numerator_input_name,
                    value=float(basis_value),
                    source_refs=list(basis.source_refs),
                ),
                FormulaInput(
                    name=spec.denominator_input_name,
                    value=total_value,
                    source_refs=list(denominator_refs),
                ),
            ],
        )
        if formula_result.status != FormulaStatus.OK or formula_result.value is None:
            return STATUS_BLOCKED, formula_result.blocking_reason or "CROSS_GROUP_FORMULA_BLOCKED"
        source_refs = tuple(dict.fromkeys(formula_result.source_refs or (*basis.source_refs, *denominator_refs)))
        trace = [dict(item) for item in basis.math_trace]
        trace.append(
            {
                "operation": "SUM",
                "scope": "ALL_GROUPS",
                "input_name": spec.denominator_input_name,
                "value": total_value,
                "source_refs": list(denominator_refs),
            }
        )
        trace.append(
            {
                "operation": "FORMULA",
                "formula_ref": spec.formula_ref,
                "numerator_group_ref": group.group_ref,
                "value": float(formula_result.value),
                "source_refs": list(source_refs),
            }
        )
        measures[spec.measure_ref] = Service1ExecutedMeasureV1(
            measure_ref=spec.measure_ref,
            value=float(formula_result.value),
            unit=spec.output_unit,
            formula_ref=spec.formula_ref,
            formula_inputs=formula_inputs,
            source_refs=source_refs,
            math_trace=tuple(trace),
        )
    return None


def _resolve_role(
    rows: list[Service1PreparedRowV1], alternatives: tuple[str, ...]
) -> tuple[str | None, str | None]:
    available = [
        role
        for role in alternatives
        if rows and all(role in row.role_values for row in rows)
    ]
    if len(available) != 1:
        token = "|".join(alternatives)
        if not available:
            return None, f"REQUIRED_NUMERIC_ROLE_MISSING:{token}"
        return None, f"AMBIGUOUS_NUMERIC_ROLE:{token}"
    return available[0], None


def _role_source_refs(
    rows: list[Service1PreparedRowV1], role: str
) -> tuple[list[str], str | None]:
    refs: list[str] = []
    for row in rows:
        if role not in row.role_values:
            return [], f"REQUIRED_ROLE_MISSING:{role}:{row.row_ref}"
        source_ref = str(row.role_source_refs.get(role) or "").strip()
        if not source_ref:
            return [], f"SOURCE_REF_MISSING:{role}:{row.row_ref}"
        refs.append(f"{source_ref}@{row.row_ref}")
    return refs, None


def _numeric_values(
    rows: list[Service1PreparedRowV1], role: str
) -> tuple[list[float], list[str], str | None]:
    values: list[float] = []
    refs: list[str] = []
    for row in rows:
        raw = row.role_values.get(role)
        value, error = _number(raw)
        if error is not None:
            return [], [], f"INVALID_NUMERIC_EVIDENCE:{role}:{row.row_ref}:{error}"
        values.append(value)
        source_ref = str(row.role_source_refs.get(role) or "").strip()
        if not source_ref:
            return [], [], f"NUMERIC_SOURCE_REF_MISSING:{role}:{row.row_ref}"
        refs.append(f"{source_ref}@{row.row_ref}")
    return values, refs, None


def _number(value: Any) -> tuple[float, str | None]:
    if value is None or isinstance(value, bool):
        return 0.0, "value must be numeric"
    text = str(value).strip().replace(" ", "").replace(",", ".")
    if not text:
        return 0.0, "value must be numeric"
    try:
        number = Decimal(text)
    except InvalidOperation:
        return 0.0, "value must be numeric"
    if not number.is_finite():
        return 0.0, "value must be finite"
    return float(number), None


def _apply_order_and_limit(
    *,
    plan: Any,
    groups: list[Service1ExecutedGroupV1],
) -> tuple[list[Service1ExecutedGroupV1], str | None]:
    ordered = list(groups)
    for item in reversed(plan.order_by):
        field = str(item.field_ref or "").strip()
        reverse = item.direction == "DESC"
        if not ordered:
            break
        if all(field in group.measures for group in ordered):
            ordered.sort(key=lambda group: group.measures[field].value, reverse=reverse)
            continue
        if all(field in group.key for group in ordered):
            ordered.sort(key=lambda group: group.key[field], reverse=reverse)
            continue
        return [], f"ORDER_BY_FIELD_UNSUPPORTED:{field}"

    if plan.kind is AnalysisKind.RANKED:
        ranked: list[Service1ExecutedGroupV1] = []
        for index, group in enumerate(ordered, start=1):
            ranked.append(
                Service1ExecutedGroupV1(
                    group_ref=group.group_ref,
                    key=group.key,
                    measures=group.measures,
                    member_row_refs=group.member_row_refs,
                    rank=index,
                )
            )
        ordered = ranked
    if plan.limit is not None:
        ordered = ordered[: plan.limit]
    return ordered, None


def _decision(
    case_id: str,
    analysis_id: str,
    status: str,
    reason: str,
) -> Service1AnalysisMathExecutionDecisionV1:
    return Service1AnalysisMathExecutionDecisionV1(
        case_id=case_id,
        analysis_id=analysis_id,
        status=status,
        reason=reason,
        provenance={"source": "F8_ANALYSIS_MATH_EXECUTION"},
    )


__all__ = [
    "SCHEMA_VERSION",
    "RESULT_SCHEMA_VERSION",
    "STATUS_EVALUATED",
    "STATUS_NEEDS_EVIDENCE",
    "STATUS_UNSUPPORTED",
    "STATUS_BLOCKED",
    "Service1ExecutedMeasureV1",
    "Service1ExecutedGroupV1",
    "Service1AnalysisMathResultV1",
    "Service1AnalysisMathExecutionDecisionV1",
    "execute_service_1_analysis_math_v1",
]
