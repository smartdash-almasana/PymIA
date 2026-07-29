from __future__ import annotations

import math
from collections import defaultdict
from datetime import date, datetime
from typing import Final

from pymia.smartpyme.service_2_reconciliation_match_candidates_v1 import (
    build_reconciliation_match_candidates_v1,
)

MercadoPagoBankReconciliationV1 = dict[str, object]

COINCIDENCIA_REFERENCIA_EXACTA: Final[str] = "COINCIDENCIA_REFERENCIA_EXACTA"
COINCIDENCIA_IMPORTE_NETO: Final[str] = "COINCIDENCIA_IMPORTE_NETO"
COINCIDENCIA_LOTE: Final[str] = "COINCIDENCIA_LOTE"
COINCIDENCIA_FECHA_CERCANA: Final[str] = "COINCIDENCIA_FECHA_CERCANA"
DIFERENCIA_IMPORTE: Final[str] = "DIFERENCIA_IMPORTE"
AMBIGUO: Final[str] = "AMBIGUO"
SIN_CONTRAPARTE: Final[str] = "SIN_CONTRAPARTE"

DEFAULT_OPTIONS: Final[dict[str, object]] = {
    "fecha_cercana_dias": 3,
    "importe_tolerancia_absoluta": 0.01,
    "importe_tolerancia_relativa": 0.0,
    "tolerancia_formula_neto": 0.01,
}

LIMITATIONS: Final[tuple[str, ...]] = (
    "Agrupa operaciones de Mercado Pago por lote cuando existe lote_id.",
    "Calcula importe_neto como importe_bruto menos comision menos retencion.",
    "Reutiliza el matcher deterministico general de conciliacion.",
    "No confirma liquidacion definitiva ni genera asientos contables.",
    "Las ambiguedades y diferencias requieren revision humana.",
)


def build_mercado_pago_bank_reconciliation_v1(
    mercado_pago_operations: object,
    bank_movements: object,
    options: dict[str, object] | None = None,
) -> MercadoPagoBankReconciliationV1:
    options_used = _normalize_options(options)
    option_errors = _validate_options(options_used)
    if option_errors:
        return _base_result(
            status="BLOCKED_BY_INVALID_INPUTS",
            options_used=options_used,
            faltantes_evidencia=option_errors,
        )

    mp_result = _normalize_mp_operations(
        mercado_pago_operations,
        formula_tolerance=float(options_used["tolerancia_formula_neto"]),
    )
    bank_result = _normalize_bank_movements(bank_movements)
    blocking_errors = [*mp_result["blocking_errors"], *bank_result["blocking_errors"]]
    faltantes_evidencia = [*mp_result["faltantes_evidencia"], *bank_result["faltantes_evidencia"]]
    inconsistencias_calculo = list(mp_result["inconsistencias_calculo"])

    if blocking_errors:
        return {
            **_base_result(
                status="BLOCKED_BY_INVALID_INPUTS",
                options_used=options_used,
                faltantes_evidencia=[*blocking_errors, *faltantes_evidencia],
            ),
            "inconsistencias_calculo": inconsistencias_calculo,
        }

    mp_groups = _build_mp_groups(mp_result["operations"])
    bank_groups = _build_bank_groups(
        bank_result["movements"],
        mp_groups=mp_groups,
        options=options_used,
    )

    generic_result = build_reconciliation_match_candidates_v1(
        bank_movements=[group["movement"] for group in bank_groups],
        internal_movements=[group["movement"] for group in mp_groups],
        options={
            "fecha_cercana_dias": options_used["fecha_cercana_dias"],
            "importe_tolerancia_absoluta": options_used["importe_tolerancia_absoluta"],
            "importe_tolerancia_relativa": options_used["importe_tolerancia_relativa"],
        },
    )

    mp_by_id = {str(group["movement"]["id"]): group for group in mp_groups}
    bank_by_id = {str(group["movement"]["id"]): group for group in bank_groups}

    conciliaciones: list[dict[str, object]] = []
    used_mp_ids: set[str] = set()
    used_bank_ids: set[str] = set()
    for item in [*generic_result["matches_exactos"], *generic_result["matches_probables"]]:  # type: ignore[index]
        mp_group = mp_by_id[str(item["interno_id"])]
        bank_group = bank_by_id[str(item["banco_id"])]
        conciliaciones.append(_build_match_payload(mp_group, bank_group, item))
        used_mp_ids.add(str(item["interno_id"]))
        used_bank_ids.add(str(item["banco_id"]))

    ambiguos: list[dict[str, object]] = []
    for item in generic_result["matches_ambiguos"]:  # type: ignore[index]
        mp_group_ids = [str(value) for value in item["interno_ids"]]
        bank_group_ids = [str(value) for value in item["banco_ids"]]
        mp_selected = [mp_by_id[value] for value in mp_group_ids]
        bank_selected = [bank_by_id[value] for value in bank_group_ids]
        ambiguos.append(_build_ambiguous_payload(mp_selected, bank_selected, item))
        used_mp_ids.update(mp_group_ids)
        used_bank_ids.update(bank_group_ids)

    diferencias_importe: list[dict[str, object]] = []
    for item in generic_result["diferencias_importe"]:  # type: ignore[index]
        mp_group = mp_by_id[str(item["interno_id"])]
        bank_group = bank_by_id[str(item["banco_id"])]
        diferencias_importe.append(_build_difference_payload(mp_group, bank_group, item))
        used_mp_ids.add(str(item["interno_id"]))
        used_bank_ids.add(str(item["banco_id"]))

    operaciones_mp_sin_acreditacion = [
        operation
        for group_id, group in mp_by_id.items()
        if group_id not in used_mp_ids
        for operation in group["operations"]
    ]
    movimientos_banco_sin_operacion_mp = [
        movement
        for group_id, group in bank_by_id.items()
        if group_id not in used_bank_ids
        for movement in group["bank_movements"]
    ]

    status = _derive_status(
        conciliaciones=conciliaciones,
        ambiguos=ambiguos,
        diferencias_importe=diferencias_importe,
        operaciones_mp_sin_acreditacion=operaciones_mp_sin_acreditacion,
        movimientos_banco_sin_operacion_mp=movimientos_banco_sin_operacion_mp,
        faltantes_evidencia=faltantes_evidencia,
        inconsistencias_calculo=inconsistencias_calculo,
    )

    return {
        **_base_result(
            status=status,
            options_used=options_used,
            faltantes_evidencia=faltantes_evidencia,
        ),
        "conciliaciones": conciliaciones,
        "ambiguos": ambiguos,
        "diferencias_importe": diferencias_importe,
        "operaciones_mp_sin_acreditacion": operaciones_mp_sin_acreditacion,
        "movimientos_banco_sin_operacion_mp": movimientos_banco_sin_operacion_mp,
        "inconsistencias_calculo": inconsistencias_calculo,
    }


def _base_result(
    *,
    status: str,
    options_used: dict[str, object],
    faltantes_evidencia: list[dict[str, object]],
) -> MercadoPagoBankReconciliationV1:
    return {
        "schema_version": "1.0",
        "service": "S2_MERCADO_PAGO_BANK_RECONCILIATION_V1",
        "status": status,
        "conciliaciones": [],
        "ambiguos": [],
        "diferencias_importe": [],
        "operaciones_mp_sin_acreditacion": [],
        "movimientos_banco_sin_operacion_mp": [],
        "inconsistencias_calculo": [],
        "faltantes_evidencia": faltantes_evidencia,
        "requires_human_review": True,
        "options_used": options_used,
        "limitations": list(LIMITATIONS),
    }


def _normalize_options(options: dict[str, object] | None) -> dict[str, object]:
    normalized = dict(DEFAULT_OPTIONS)
    if options:
        for key in DEFAULT_OPTIONS:
            if key in options:
                normalized[key] = options[key]
    return normalized


def _validate_options(options: dict[str, object]) -> list[dict[str, object]]:
    errors: list[dict[str, object]] = []
    days = options.get("fecha_cercana_dias")
    if isinstance(days, bool) or not isinstance(days, int) or days < 0:
        errors.append({"field": "fecha_cercana_dias", "reason": "must_be_non_negative_integer"})
    for field in (
        "importe_tolerancia_absoluta",
        "importe_tolerancia_relativa",
        "tolerancia_formula_neto",
    ):
        value = options.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            errors.append({"field": field, "reason": "must_be_finite_number"})
        elif float(value) < 0:
            errors.append({"field": field, "reason": "must_be_non_negative_number"})
    return errors


def _normalize_mp_operations(value: object, *, formula_tolerance: float) -> dict[str, list[dict[str, object]]]:
    if not isinstance(value, (list, tuple)):
        return {
            "operations": [],
            "blocking_errors": [{"side": "mercado_pago", "reason": "operations_must_be_a_list"}],
            "faltantes_evidencia": [],
            "inconsistencias_calculo": [],
        }

    operations: list[dict[str, object]] = []
    missing: list[dict[str, object]] = []
    inconsistencies: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(value):
        if not isinstance(raw, dict):
            return {
                "operations": [],
                "blocking_errors": [{"side": "mercado_pago", "index": index, "reason": "operation_must_be_a_dict"}],
                "faltantes_evidencia": missing,
                "inconsistencias_calculo": inconsistencies,
            }
        operation_id = _required_text(raw.get("id") or raw.get("operacion_mp_id"))
        operation_date = _parse_date(raw.get("fecha") or raw.get("fecha_operacion"))
        gross = _parse_amount(raw.get("importe_bruto"))
        commission = _parse_amount(raw.get("comision"))
        withholding = _parse_amount(raw.get("retencion"))
        declared_net = _parse_amount(raw.get("importe_neto"))
        if operation_id is None:
            missing.append({"side": "mercado_pago", "index": index, "field": "operacion_mp_id", "reason": "missing"})
            continue
        if operation_id in seen_ids:
            return {
                "operations": [],
                "blocking_errors": [{"side": "mercado_pago", "id": operation_id, "reason": "duplicate_operation_id"}],
                "faltantes_evidencia": missing,
                "inconsistencias_calculo": inconsistencies,
            }
        seen_ids.add(operation_id)
        required_values = {
            "fecha_operacion": operation_date,
            "importe_bruto": gross,
            "comision": commission,
            "retencion": withholding,
            "importe_neto": declared_net,
        }
        invalid_fields = [field for field, field_value in required_values.items() if field_value is None]
        if invalid_fields:
            for field in invalid_fields:
                missing.append({"side": "mercado_pago", "id": operation_id, "field": field, "reason": "invalid_or_missing"})
            continue
        calculated_net = round(float(gross) - float(commission) - float(withholding), 2)
        formula_delta = round(abs(calculated_net - float(declared_net)), 2)
        if formula_delta > formula_tolerance:
            inconsistencies.append(
                {
                    "operacion_mp_id": operation_id,
                    "importe_neto_declarado": float(declared_net),
                    "importe_neto_calculado": calculated_net,
                    "diferencia": formula_delta,
                }
            )
            continue
        operations.append(
            {
                "operacion_mp_id": operation_id,
                "fecha_operacion": operation_date,
                "venta_id": _optional_text(raw.get("venta_id")),
                "importe_bruto": float(gross),
                "comision": float(commission),
                "retencion": float(withholding),
                "importe_neto": calculated_net,
                "lote_id": _optional_text(raw.get("lote_id")),
                "referencia": _optional_text(raw.get("referencia")),
            }
        )
    return {
        "operations": operations,
        "blocking_errors": [],
        "faltantes_evidencia": missing,
        "inconsistencias_calculo": inconsistencies,
    }


def _normalize_bank_movements(value: object) -> dict[str, list[dict[str, object]]]:
    if not isinstance(value, (list, tuple)):
        return {
            "movements": [],
            "blocking_errors": [{"side": "bank", "reason": "movements_must_be_a_list"}],
            "faltantes_evidencia": [],
        }
    movements: list[dict[str, object]] = []
    missing: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(value):
        if not isinstance(raw, dict):
            return {
                "movements": [],
                "blocking_errors": [{"side": "bank", "index": index, "reason": "movement_must_be_a_dict"}],
                "faltantes_evidencia": missing,
            }
        movement_id = _required_text(raw.get("id") or raw.get("movimiento_banco_id"))
        movement_date = _parse_date(raw.get("fecha"))
        amount = _parse_amount(raw.get("importe"))
        if movement_id is None:
            missing.append({"side": "bank", "index": index, "field": "movimiento_banco_id", "reason": "missing"})
            continue
        if movement_id in seen_ids:
            return {
                "movements": [],
                "blocking_errors": [{"side": "bank", "id": movement_id, "reason": "duplicate_movement_id"}],
                "faltantes_evidencia": missing,
            }
        seen_ids.add(movement_id)
        if movement_date is None:
            missing.append({"side": "bank", "id": movement_id, "field": "fecha", "reason": "invalid_or_missing"})
            continue
        if amount is None:
            missing.append({"side": "bank", "id": movement_id, "field": "importe", "reason": "invalid_or_missing"})
            continue
        movements.append(
            {
                "movimiento_banco_id": movement_id,
                "fecha": movement_date,
                "descripcion": _optional_text(raw.get("descripcion")),
                "importe": float(amount),
                "lote_id": _optional_text(raw.get("lote_id")),
                "referencia": _optional_text(raw.get("referencia")),
            }
        )
    return {"movements": movements, "blocking_errors": [], "faltantes_evidencia": missing}


def _build_mp_groups(operations: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for operation in operations:
        lot_id = operation["lote_id"]
        key = f"lot:{lot_id}" if lot_id else f"operation:{operation['operacion_mp_id']}"
        grouped[key].append(operation)

    result: list[dict[str, object]] = []
    for key, members in grouped.items():
        lot_ids = _ordered_unique(str(item["lote_id"]) for item in members if item["lote_id"])
        lot_id = lot_ids[0] if len(lot_ids) == 1 else None
        references = _ordered_unique(str(item["referencia"]) for item in members if item["referencia"])
        shared_reference = references[0] if len(references) == 1 else None
        movement_id = f"mp:{key}"
        result.append(
            {
                "movement": {
                    "id": movement_id,
                    "fecha": max(item["fecha_operacion"] for item in members),
                    "importe": round(sum(float(item["importe_neto"]) for item in members), 2),
                    "referencia": lot_id or shared_reference,
                    "descripcion": f"Liquidacion Mercado Pago {lot_id or key}",
                },
                "operations": members,
                "lote_id": lot_id,
                "references": references,
                "importe_bruto_total": round(sum(float(item["importe_bruto"]) for item in members), 2),
                "comision_total": round(sum(float(item["comision"]) for item in members), 2),
                "retencion_total": round(sum(float(item["retencion"]) for item in members), 2),
                "importe_neto_total": round(sum(float(item["importe_neto"]) for item in members), 2),
            }
        )
    return result


def _build_bank_groups(
    movements: list[dict[str, object]],
    *,
    mp_groups: list[dict[str, object]],
    options: dict[str, object],
) -> list[dict[str, object]]:
    mp_by_lot = {str(group["lote_id"]): group for group in mp_groups if group["lote_id"]}
    by_lot: dict[str, list[dict[str, object]]] = defaultdict(list)
    without_lot: list[dict[str, object]] = []
    for movement in movements:
        lot_id = movement["lote_id"]
        if lot_id:
            by_lot[str(lot_id)].append(movement)
        else:
            without_lot.append(movement)

    result: list[dict[str, object]] = []
    for lot_id, members in by_lot.items():
        mp_group = mp_by_lot.get(lot_id)
        bank_total = round(sum(float(item["importe"]) for item in members), 2)
        should_aggregate = (
            len(members) > 1
            and mp_group is not None
            and _amounts_match(
                bank_total,
                float(mp_group["importe_neto_total"]),
                options=options,
            )
        )
        if should_aggregate:
            result.append(_bank_group_payload(members, lot_id=lot_id, aggregate=True))
        else:
            result.extend(_bank_group_payload([member], lot_id=lot_id, aggregate=False) for member in members)
    result.extend(_bank_group_payload([member], lot_id=None, aggregate=False) for member in without_lot)
    return result


def _bank_group_payload(
    members: list[dict[str, object]],
    *,
    lot_id: str | None,
    aggregate: bool,
) -> dict[str, object]:
    references = _ordered_unique(str(item["referencia"]) for item in members if item["referencia"])
    shared_reference = references[0] if len(references) == 1 else None
    member_ids = [str(item["movimiento_banco_id"]) for item in members]
    movement_id = f"bank:lot:{lot_id}" if aggregate else f"bank:movement:{member_ids[0]}"
    return {
        "movement": {
            "id": movement_id,
            "fecha": max(item["fecha"] for item in members),
            "importe": round(sum(float(item["importe"]) for item in members), 2),
            "referencia": lot_id or shared_reference,
            "descripcion": " + ".join(str(item["descripcion"] or item["movimiento_banco_id"]) for item in members),
        },
        "bank_movements": members,
        "lote_id": lot_id,
        "references": references,
        "importe_banco_total": round(sum(float(item["importe"]) for item in members), 2),
    }


def _build_match_payload(
    mp_group: dict[str, object],
    bank_group: dict[str, object],
    generic_item: dict[str, object],
) -> dict[str, object]:
    evidence = _domain_evidence(mp_group, bank_group, generic_item)
    mp_count = len(mp_group["operations"])  # type: ignore[arg-type]
    bank_count = len(bank_group["bank_movements"])  # type: ignore[arg-type]
    date_delta = int(generic_item["evidencia"]["date_delta_days"])  # type: ignore[index]
    if date_delta > 0:
        result_type = COINCIDENCIA_FECHA_CERCANA
    elif mp_count > 1 or bank_count > 1:
        result_type = COINCIDENCIA_LOTE if evidence["lote_coincidente"] else COINCIDENCIA_IMPORTE_NETO
    elif evidence["referencia_coincidente"]:
        result_type = COINCIDENCIA_REFERENCIA_EXACTA
    else:
        result_type = COINCIDENCIA_IMPORTE_NETO
    return {
        "resultado": result_type,
        "cardinalidad": _cardinality(mp_count, bank_count),
        "operaciones_mp_ids": _mp_ids(mp_group),
        "movimientos_banco_ids": _bank_ids(bank_group),
        "importe_bruto_total": mp_group["importe_bruto_total"],
        "comision_total": mp_group["comision_total"],
        "retencion_total": mp_group["retencion_total"],
        "importe_neto_esperado": mp_group["importe_neto_total"],
        "importe_banco_total": bank_group["importe_banco_total"],
        "evidencia": evidence,
        "requires_human_review": True,
    }


def _build_ambiguous_payload(
    mp_groups: list[dict[str, object]],
    bank_groups: list[dict[str, object]],
    generic_item: dict[str, object],
) -> dict[str, object]:
    operation_ids = _ordered_unique(value for group in mp_groups for value in _mp_ids(group))
    bank_ids = _ordered_unique(value for group in bank_groups for value in _bank_ids(group))
    return {
        "resultado": AMBIGUO,
        "cardinalidad": _cardinality(len(operation_ids), len(bank_ids)),
        "operaciones_mp_ids": operation_ids,
        "movimientos_banco_ids": bank_ids,
        "candidate_count": generic_item["candidate_count"],
        "requires_human_review": True,
    }


def _build_difference_payload(
    mp_group: dict[str, object],
    bank_group: dict[str, object],
    generic_item: dict[str, object],
) -> dict[str, object]:
    expected = float(mp_group["importe_neto_total"])
    bank_total = float(bank_group["importe_banco_total"])
    return {
        "resultado": DIFERENCIA_IMPORTE,
        "cardinalidad": _cardinality(
            len(mp_group["operations"]),  # type: ignore[arg-type]
            len(bank_group["bank_movements"]),  # type: ignore[arg-type]
        ),
        "operaciones_mp_ids": _mp_ids(mp_group),
        "movimientos_banco_ids": _bank_ids(bank_group),
        "importe_bruto_total": mp_group["importe_bruto_total"],
        "comision_total": mp_group["comision_total"],
        "retencion_total": mp_group["retencion_total"],
        "importe_neto_esperado": expected,
        "importe_banco_total": bank_total,
        "diferencia": round(bank_total - expected, 2),
        "evidencia": _domain_evidence(mp_group, bank_group, generic_item),
        "requires_human_review": True,
    }


def _domain_evidence(
    mp_group: dict[str, object],
    bank_group: dict[str, object],
    generic_item: dict[str, object],
) -> dict[str, object]:
    mp_references = {_reference_key(value) for value in mp_group["references"]}  # type: ignore[union-attr]
    bank_references = {_reference_key(value) for value in bank_group["references"]}  # type: ignore[union-attr]
    mp_references.discard(None)
    bank_references.discard(None)
    mp_lot = _reference_key(mp_group["lote_id"])
    bank_lot = _reference_key(bank_group["lote_id"])
    evidence = generic_item.get("evidencia", {})
    return {
        "formula_neto_verificada": True,
        "lote_coincidente": mp_lot is not None and mp_lot == bank_lot,
        "referencia_coincidente": bool(mp_references & bank_references),
        "importe_coincidente": bool(evidence.get("amount_match")),
        "diferencia_importe": evidence.get("amount_delta"),
        "diferencia_dias": evidence.get("date_delta_days"),
    }


def _mp_ids(group: dict[str, object]) -> list[str]:
    return [str(item["operacion_mp_id"]) for item in group["operations"]]  # type: ignore[index]


def _bank_ids(group: dict[str, object]) -> list[str]:
    return [str(item["movimiento_banco_id"]) for item in group["bank_movements"]]  # type: ignore[index]


def _cardinality(mp_count: int, bank_count: int) -> str:
    if mp_count == 1 and bank_count == 1:
        return "1:1"
    if mp_count == 1:
        return "1:N"
    if bank_count == 1:
        return "N:1"
    return "N:M"


def _amounts_match(left: float, right: float, *, options: dict[str, object]) -> bool:
    absolute = float(options["importe_tolerancia_absoluta"])
    relative = float(options["importe_tolerancia_relativa"])
    tolerance = max(absolute, max(abs(left), abs(right)) * relative)
    return abs(left - right) <= tolerance


def _derive_status(
    *,
    conciliaciones: list[dict[str, object]],
    ambiguos: list[dict[str, object]],
    diferencias_importe: list[dict[str, object]],
    operaciones_mp_sin_acreditacion: list[dict[str, object]],
    movimientos_banco_sin_operacion_mp: list[dict[str, object]],
    faltantes_evidencia: list[dict[str, object]],
    inconsistencias_calculo: list[dict[str, object]],
) -> str:
    if ambiguos or diferencias_importe or operaciones_mp_sin_acreditacion or movimientos_banco_sin_operacion_mp:
        return "PARTIAL_MATCHES_FOUND"
    if conciliaciones and (faltantes_evidencia or inconsistencias_calculo):
        return "PARTIAL_MATCHES_FOUND"
    if conciliaciones:
        return "READY_FOR_HUMAN_REVIEW"
    if faltantes_evidencia or inconsistencias_calculo:
        return "NEEDS_MORE_EVIDENCE"
    return "NO_CANDIDATES_FOUND"


def _parse_date(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        text = value.strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
    return None


def _parse_amount(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    amount = float(value)
    if not math.isfinite(amount):
        return None
    return amount


def _required_text(value: object) -> str | None:
    text = _optional_text(value)
    return text


def _optional_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def _reference_key(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = " ".join(value.strip().casefold().split())
    return normalized or None


def _ordered_unique(values: object) -> list[str]:
    result: list[str] = []
    for value in values:  # type: ignore[union-attr]
        if value not in result:
            result.append(value)
    return result
