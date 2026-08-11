"""Consorcios plug for the independent Servicio 1 RADAR engine.

The plug exposes deterministic values already produced by Consorcios capabilities
as neutral RADAR observables. It does not recalculate source capabilities, assign
risk/severity, choose thresholds, or create owner policies.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Mapping

from pymia.smartpyme.service_1_radar_observable_v1 import (
    KIND_METRIC,
    KIND_OPERATION,
    OP_EQ,
    OP_GT,
    OP_GTE,
    OP_LT,
    OP_LTE,
    OP_NEQ,
    RadarObservableV1,
    build_radar_observable_v1,
)

VERTICAL_REF: Final[str] = "consorcios"

OBS_DEBT_EQUIVALENT_PERIODS: Final[str] = "consorcios.debt_equivalent_periods"
OBS_EXPENSE_BUDGET_DEVIATION_PCT: Final[str] = "consorcios.expense_budget_deviation_pct"
OBS_EXPENSE_HISTORICAL_DEVIATION_PCT: Final[str] = "consorcios.expense_historical_deviation_pct"
OBS_BANK_UNMATCHED_COUNT: Final[str] = "consorcios.bank_unmatched_count"
OBS_BANK_UNMATCHED_AMOUNT: Final[str] = "consorcios.bank_unmatched_amount"
OBS_UNMATCHED_BANK_OPERATION: Final[str] = "consorcios.unmatched_bank_operation"

_METRIC_OPS: Final[tuple[str, ...]] = (OP_GT, OP_GTE, OP_LT, OP_LTE, OP_EQ, OP_NEQ)
_OPERATION_OPS: Final[tuple[str, ...]] = (OP_EQ, OP_NEQ)


@dataclass(frozen=True)
class ConsorciosRadarObservationV1:
    observable: RadarObservableV1
    observed_value: str | bool
    entity_ref: str
    source_capability_ref: str


def consorcios_radar_catalog_v1() -> tuple[RadarObservableV1, ...]:
    return (
        build_radar_observable_v1(
            observable_ref=OBS_DEBT_EQUIVALENT_PERIODS,
            vertical_ref=VERTICAL_REF,
            display_name="Períodos equivalentes de deuda",
            observable_kind=KIND_METRIC,
            source_capability_ref="collection_aging",
            value_field_ref="periodos_equivalentes",
            unit="periods",
            entity_scope="unidad_funcional",
            supported_operators=_METRIC_OPS,
            description="Estimación matemática de saldo anterior dividido por expensa del mes.",
        ),
        build_radar_observable_v1(
            observable_ref=OBS_EXPENSE_BUDGET_DEVIATION_PCT,
            vertical_ref=VERTICAL_REF,
            display_name="Desvío de gasto contra presupuesto",
            observable_kind=KIND_METRIC,
            source_capability_ref="consorcios_expense_variance",
            value_field_ref="desvio_presupuesto_pct",
            unit="percent",
            entity_scope="rubro",
            supported_operators=_METRIC_OPS,
        ),
        build_radar_observable_v1(
            observable_ref=OBS_EXPENSE_HISTORICAL_DEVIATION_PCT,
            vertical_ref=VERTICAL_REF,
            display_name="Desvío de gasto contra promedio histórico",
            observable_kind=KIND_METRIC,
            source_capability_ref="consorcios_expense_variance",
            value_field_ref="desvio_promedio_pct",
            unit="percent",
            entity_scope="rubro",
            supported_operators=_METRIC_OPS,
        ),
        build_radar_observable_v1(
            observable_ref=OBS_BANK_UNMATCHED_COUNT,
            vertical_ref=VERTICAL_REF,
            display_name="Cantidad de movimientos bancarios sin imputar",
            observable_kind=KIND_METRIC,
            source_capability_ref="bank_reconciliation",
            value_field_ref="banco_sin_imputar_count",
            unit="count",
            entity_scope="reconciliation_case",
            supported_operators=_METRIC_OPS,
        ),
        build_radar_observable_v1(
            observable_ref=OBS_BANK_UNMATCHED_AMOUNT,
            vertical_ref=VERTICAL_REF,
            display_name="Importe absoluto de movimientos bancarios sin imputar",
            observable_kind=KIND_METRIC,
            source_capability_ref="bank_reconciliation",
            value_field_ref="banco_sin_imputar_amount_abs",
            unit="currency",
            entity_scope="reconciliation_case",
            supported_operators=_METRIC_OPS,
        ),
        build_radar_observable_v1(
            observable_ref=OBS_UNMATCHED_BANK_OPERATION,
            vertical_ref=VERTICAL_REF,
            display_name="Existe movimiento bancario sin imputar",
            observable_kind=KIND_OPERATION,
            source_capability_ref="bank_reconciliation",
            value_field_ref="has_banco_sin_imputar",
            unit="boolean",
            entity_scope="reconciliation_case",
            supported_operators=_OPERATION_OPS,
        ),
    )


def _catalog_by_ref() -> dict[str, RadarObservableV1]:
    return {item.observable_ref: item for item in consorcios_radar_catalog_v1()}


def project_collection_aging_to_radar_v1(
    *, computation_result: Mapping[str, object]
) -> tuple[ConsorciosRadarObservationV1, ...]:
    if computation_result.get("status") != "EVALUATED" or computation_result.get("capability_ref") != "collection_aging":
        raise ValueError("collection aging result must be EVALUATED and canonical")
    rows = computation_result.get("rows")
    if not isinstance(rows, list):
        raise ValueError("collection aging rows are required")
    observable = _catalog_by_ref()[OBS_DEBT_EQUIVALENT_PERIODS]
    projected: list[ConsorciosRadarObservationV1] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            raise ValueError(f"collection aging row {index} is invalid")
        unit = str(row.get("unidad_funcional") or "").strip()
        value = row.get("periodos_equivalentes")
        if not unit or isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"collection aging row {index} lacks canonical RADAR evidence")
        projected.append(
            ConsorciosRadarObservationV1(
                observable=observable,
                observed_value=str(value),
                entity_ref=unit,
                source_capability_ref="collection_aging",
            )
        )
    return tuple(projected)


def project_expense_variance_to_radar_v1(
    *, computation_result: Mapping[str, object]
) -> tuple[ConsorciosRadarObservationV1, ...]:
    if computation_result.get("status") != "EVALUATED" or computation_result.get("capability_ref") != "consorcios_expense_variance":
        raise ValueError("expense variance result must be EVALUATED and canonical")
    rows = computation_result.get("rows")
    if not isinstance(rows, list):
        raise ValueError("expense variance rows are required")
    catalog = _catalog_by_ref()
    projected: list[ConsorciosRadarObservationV1] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            raise ValueError(f"expense variance row {index} is invalid")
        rubro = str(row.get("rubro") or "").strip()
        budget_dev = row.get("desvio_presupuesto_pct")
        historical_dev = row.get("desvio_promedio_pct")
        if not rubro or any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in (budget_dev, historical_dev)):
            raise ValueError(f"expense variance row {index} lacks canonical RADAR evidence")
        projected.extend(
            (
                ConsorciosRadarObservationV1(
                    observable=catalog[OBS_EXPENSE_BUDGET_DEVIATION_PCT],
                    observed_value=str(budget_dev),
                    entity_ref=rubro,
                    source_capability_ref="consorcios_expense_variance",
                ),
                ConsorciosRadarObservationV1(
                    observable=catalog[OBS_EXPENSE_HISTORICAL_DEVIATION_PCT],
                    observed_value=str(historical_dev),
                    entity_ref=rubro,
                    source_capability_ref="consorcios_expense_variance",
                ),
            )
        )
    return tuple(projected)


def project_bank_reconciliation_to_radar_v1(
    *, reconciliation_result: Mapping[str, object]
) -> tuple[ConsorciosRadarObservationV1, ...]:
    allowed = {
        "READY_FOR_HUMAN_REVIEW",
        "NO_CANDIDATES_FOUND",
        "PARTIAL_MATCHES_FOUND",
    }
    if reconciliation_result.get("status") not in allowed:
        raise ValueError("bank reconciliation result is not radarizable")
    rows = reconciliation_result.get("banco_sin_imputar")
    if not isinstance(rows, list):
        raise ValueError("banco_sin_imputar must be a list")
    total_abs = 0.0
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            raise ValueError(f"bank unmatched row {index} is invalid")
        amount = row.get("importe")
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise ValueError(f"bank unmatched row {index} has invalid importe")
        total_abs += abs(float(amount))
    catalog = _catalog_by_ref()
    return (
        ConsorciosRadarObservationV1(
            observable=catalog[OBS_BANK_UNMATCHED_COUNT],
            observed_value=str(len(rows)),
            entity_ref="bank_reconciliation",
            source_capability_ref="bank_reconciliation",
        ),
        ConsorciosRadarObservationV1(
            observable=catalog[OBS_BANK_UNMATCHED_AMOUNT],
            observed_value=str(total_abs),
            entity_ref="bank_reconciliation",
            source_capability_ref="bank_reconciliation",
        ),
        ConsorciosRadarObservationV1(
            observable=catalog[OBS_UNMATCHED_BANK_OPERATION],
            observed_value=bool(rows),
            entity_ref="bank_reconciliation",
            source_capability_ref="bank_reconciliation",
        ),
    )


__all__ = [
    "VERTICAL_REF",
    "OBS_DEBT_EQUIVALENT_PERIODS",
    "OBS_EXPENSE_BUDGET_DEVIATION_PCT",
    "OBS_EXPENSE_HISTORICAL_DEVIATION_PCT",
    "OBS_BANK_UNMATCHED_COUNT",
    "OBS_BANK_UNMATCHED_AMOUNT",
    "OBS_UNMATCHED_BANK_OPERATION",
    "ConsorciosRadarObservationV1",
    "consorcios_radar_catalog_v1",
    "project_collection_aging_to_radar_v1",
    "project_expense_variance_to_radar_v1",
    "project_bank_reconciliation_to_radar_v1",
]
