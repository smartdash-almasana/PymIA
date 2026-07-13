from __future__ import annotations

import math
from datetime import date, datetime
from typing import Final

ReconciliationMatchCandidatesV1 = dict[str, object]

ALLOWED_STATUSES: Final[tuple[str, ...]] = (
    "READY_FOR_HUMAN_REVIEW",
    "NEEDS_MORE_EVIDENCE",
    "BLOCKED_BY_INVALID_INPUTS",
    "NO_CANDIDATES_FOUND",
    "PARTIAL_MATCHES_FOUND",
)

DEFAULT_OPTIONS: Final[dict[str, object]] = {
    "fecha_cercana_dias": 3,
    "importe_tolerancia_absoluta": 0.01,
    "importe_tolerancia_relativa": 0.0,
    "confianza_exacta": 1.0,
    "confianza_probable_minima": 0.6,
}

FORBIDDEN_CLAIMS: Final[tuple[str, ...]] = (
    "No declara conciliacion definitiva.",
    "No certifica saldo bancario real.",
    "No reemplaza revision humana ni criterio contable.",
    "No detecta fraude.",
    "No produce cierre contable o fiscal.",
)

LIMITATIONS: Final[tuple[str, ...]] = (
    "Genera candidatos de conciliacion para revision humana.",
    "No fusiona movimientos ni oculta duplicados.",
    "No corrige fechas, importes, comprobantes ni contrapartes silenciosamente.",
)


def build_reconciliation_match_candidates_v1(
    bank_movements: object,
    internal_movements: object,
    options: dict[str, object] | None = None,
) -> ReconciliationMatchCandidatesV1:
    options_used = _normalize_options(options)
    invalid_options = _validate_options(options_used)
    if invalid_options:
        return _base_result(
            status="BLOCKED_BY_INVALID_INPUTS",
            options_used=options_used,
            faltantes_evidencia=invalid_options,
        )

    bank_result = _normalize_movements(bank_movements, side="bank")
    internal_result = _normalize_movements(internal_movements, side="internal")
    if bank_result["blocking_errors"] or internal_result["blocking_errors"]:
        return _base_result(
            status="BLOCKED_BY_INVALID_INPUTS",
            options_used=options_used,
            faltantes_evidencia=[
                *bank_result["blocking_errors"],
                *internal_result["blocking_errors"],
                *bank_result["faltantes_evidencia"],
                *internal_result["faltantes_evidencia"],
            ],
        )

    bank_rows = bank_result["movements"]
    internal_rows = internal_result["movements"]
    faltantes_evidencia = [
        *bank_result["faltantes_evidencia"],
        *internal_result["faltantes_evidencia"],
    ]

    matches_exactos: list[dict[str, object]] = []
    matches_probables: list[dict[str, object]] = []
    diferencias_importe: list[dict[str, object]] = []
    diferencias_fecha: list[dict[str, object]] = []

    candidate_bank_indexes: set[int] = set()
    candidate_internal_indexes: set[int] = set()

    for bank in bank_rows:
        for internal in internal_rows:
            comparison = _compare_movements(bank, internal, options_used)
            if comparison["exact"]:
                matches_exactos.append(
                    _match_pair(
                        bank,
                        internal,
                        criterio="same_date_same_amount",
                        confianza=float(options_used["confianza_exacta"]),
                    )
                )
                candidate_bank_indexes.add(int(bank["index"]))
                candidate_internal_indexes.add(int(internal["index"]))
                continue

            if comparison["near_date_same_amount"]:
                matches_probables.append(
                    _match_pair(
                        bank,
                        internal,
                        criterio="near_date_same_amount",
                        confianza=float(options_used["confianza_probable_minima"]),
                        diferencias={"dias": comparison["date_delta_days"]},
                    )
                )
                diferencias_fecha.append(
                    _difference_pair(
                        bank,
                        internal,
                        criterio="same_amount_different_date",
                        diferencias={"dias": comparison["date_delta_days"]},
                    )
                )
                candidate_bank_indexes.add(int(bank["index"]))
                candidate_internal_indexes.add(int(internal["index"]))
                continue

            if comparison["same_date_different_amount"]:
                diferencias_importe.append(
                    _difference_pair(
                        bank,
                        internal,
                        criterio="same_date_different_amount",
                        diferencias={
                            "importe_banco": bank["importe"],
                            "importe_interno": internal["importe"],
                            "diferencia_absoluta": comparison["amount_delta"],
                        },
                    )
                )
                candidate_bank_indexes.add(int(bank["index"]))
                candidate_internal_indexes.add(int(internal["index"]))

    banco_sin_imputar = [
        _public_movement(row)
        for row in bank_rows
        if int(row["index"]) not in candidate_bank_indexes
    ]
    interno_sin_banco = [
        _public_movement(row)
        for row in internal_rows
        if int(row["index"]) not in candidate_internal_indexes
    ]

    status = _derive_status(
        matches_exactos=matches_exactos,
        matches_probables=matches_probables,
        banco_sin_imputar=banco_sin_imputar,
        interno_sin_banco=interno_sin_banco,
        diferencias_importe=diferencias_importe,
        diferencias_fecha=diferencias_fecha,
        faltantes_evidencia=faltantes_evidencia,
    )

    return {
        **_base_result(
            status=status,
            options_used=options_used,
            faltantes_evidencia=faltantes_evidencia,
        ),
        "matches_exactos": matches_exactos,
        "matches_probables": matches_probables,
        "banco_sin_imputar": banco_sin_imputar,
        "interno_sin_banco": interno_sin_banco,
        "diferencias_importe": diferencias_importe,
        "diferencias_fecha": diferencias_fecha,
    }


def _base_result(
    *,
    status: str,
    options_used: dict[str, object],
    faltantes_evidencia: list[dict[str, object]],
) -> ReconciliationMatchCandidatesV1:
    return {
        "schema_version": "1.0",
        "service": "S2_ADMIN_OPERATIONS_V1",
        "status": status,
        "matches_exactos": [],
        "matches_probables": [],
        "banco_sin_imputar": [],
        "interno_sin_banco": [],
        "diferencias_importe": [],
        "diferencias_fecha": [],
        "faltantes_evidencia": faltantes_evidencia,
        "requires_human_review": True,
        "options_used": options_used,
        "allowed_statuses": list(ALLOWED_STATUSES),
        "limitations": list(LIMITATIONS),
        "forbidden_claims": list(FORBIDDEN_CLAIMS),
    }


def _normalize_options(options: dict[str, object] | None) -> dict[str, object]:
    normalized = dict(DEFAULT_OPTIONS)
    if options:
        normalized.update(options)
    return normalized


def _validate_options(options: dict[str, object]) -> list[dict[str, object]]:
    errors: list[dict[str, object]] = []
    if not isinstance(options.get("fecha_cercana_dias"), int) or int(options["fecha_cercana_dias"]) < 0:
        errors.append({"field": "fecha_cercana_dias", "reason": "must_be_non_negative_integer"})
    for field in ("importe_tolerancia_absoluta", "importe_tolerancia_relativa", "confianza_exacta", "confianza_probable_minima"):
        value = options.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            errors.append({"field": field, "reason": "must_be_finite_number"})
    return errors


def _normalize_movements(value: object, *, side: str) -> dict[str, list[dict[str, object]]]:
    if not isinstance(value, (list, tuple)):
        return {
            "movements": [],
            "blocking_errors": [{"side": side, "reason": "movements_must_be_a_list"}],
            "faltantes_evidencia": [],
        }

    movements: list[dict[str, object]] = []
    faltantes_evidencia: list[dict[str, object]] = []
    for index, raw in enumerate(value):
        if not isinstance(raw, dict):
            return {
                "movements": [],
                "blocking_errors": [{"side": side, "index": index, "reason": "movement_must_be_a_dict"}],
                "faltantes_evidencia": faltantes_evidencia,
            }

        movement_id = _movement_id(raw, side=side, index=index)
        fecha = _parse_date(raw.get("fecha"))
        importe = _parse_amount(raw.get("importe"))
        descripcion = _normalize_optional_text(raw.get("descripcion"))
        referencia = _normalize_optional_text(raw.get("referencia"))

        if fecha is None:
            faltantes_evidencia.append({"side": side, "id": movement_id, "field": "fecha", "reason": "fecha_invalid_or_missing"})
            continue
        if importe is None:
            faltantes_evidencia.append({"side": side, "id": movement_id, "field": "importe", "reason": "importe_invalid_or_missing"})
            continue

        movements.append(
            {
                "index": index,
                "id": movement_id,
                "fecha": fecha,
                "importe": importe,
                "descripcion": descripcion,
                "referencia": referencia,
                "raw": dict(raw),
            }
        )

    return {
        "movements": movements,
        "blocking_errors": [],
        "faltantes_evidencia": faltantes_evidencia,
    }


def _movement_id(raw: dict[str, object], *, side: str, index: int) -> str:
    for key in ("id", f"{side}_id", "id_movimiento", "referencia", "referencia_externa"):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return f"{side}-{index + 1}"


def _parse_date(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
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


def _normalize_optional_text(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def _compare_movements(
    bank: dict[str, object],
    internal: dict[str, object],
    options: dict[str, object],
) -> dict[str, object]:
    amount_delta = abs(float(bank["importe"]) - float(internal["importe"]))
    amount_tolerance = _amount_tolerance(bank, internal, options)
    same_amount = amount_delta <= amount_tolerance
    date_delta_days = abs((bank["fecha"] - internal["fecha"]).days)  # type: ignore[operator]
    same_date = date_delta_days == 0
    near_date = 0 < date_delta_days <= int(options["fecha_cercana_dias"])
    return {
        "exact": same_date and same_amount,
        "near_date_same_amount": near_date and same_amount,
        "same_date_different_amount": same_date and not same_amount,
        "amount_delta": round(amount_delta, 2),
        "date_delta_days": date_delta_days,
    }


def _amount_tolerance(
    bank: dict[str, object],
    internal: dict[str, object],
    options: dict[str, object],
) -> float:
    absolute = float(options["importe_tolerancia_absoluta"])
    relative = float(options["importe_tolerancia_relativa"])
    base = max(abs(float(bank["importe"])), abs(float(internal["importe"])))
    return max(absolute, base * relative)


def _match_pair(
    bank: dict[str, object],
    internal: dict[str, object],
    *,
    criterio: str,
    confianza: float,
    diferencias: dict[str, object] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "banco_id": bank["id"],
        "interno_id": internal["id"],
        "criterio": criterio,
        "confianza": confianza,
    }
    if diferencias:
        payload["diferencias"] = diferencias
    return payload


def _difference_pair(
    bank: dict[str, object],
    internal: dict[str, object],
    *,
    criterio: str,
    diferencias: dict[str, object],
) -> dict[str, object]:
    return {
        "banco_id": bank["id"],
        "interno_id": internal["id"],
        "criterio": criterio,
        "diferencias": diferencias,
        "requires_human_review": True,
    }


def _public_movement(row: dict[str, object]) -> dict[str, object]:
    return {
        "id": row["id"],
        "fecha": row["fecha"].isoformat(),  # type: ignore[union-attr]
        "importe": row["importe"],
        "descripcion": row["descripcion"],
        "referencia": row["referencia"],
    }


def _derive_status(
    *,
    matches_exactos: list[dict[str, object]],
    matches_probables: list[dict[str, object]],
    banco_sin_imputar: list[dict[str, object]],
    interno_sin_banco: list[dict[str, object]],
    diferencias_importe: list[dict[str, object]],
    diferencias_fecha: list[dict[str, object]],
    faltantes_evidencia: list[dict[str, object]],
) -> str:
    has_candidates = bool(matches_exactos or matches_probables or diferencias_importe or diferencias_fecha)
    has_pending = bool(banco_sin_imputar or interno_sin_banco or faltantes_evidencia)
    has_partial = bool(matches_probables or diferencias_importe or diferencias_fecha)

    if has_partial or (has_candidates and has_pending):
        return "PARTIAL_MATCHES_FOUND"
    if matches_exactos:
        return "READY_FOR_HUMAN_REVIEW"
    if faltantes_evidencia:
        return "NEEDS_MORE_EVIDENCE"
    return "NO_CANDIDATES_FOUND"
