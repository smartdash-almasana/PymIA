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

MATCH_REFERENCE_EXACT: Final[str] = "MATCH_REFERENCE_EXACT"
MATCH_ATTRIBUTES_EXACT: Final[str] = "MATCH_ATTRIBUTES_EXACT"
MATCH_PROBABLE_DATE: Final[str] = "MATCH_PROBABLE_DATE"
AMBIGUOUS: Final[str] = "AMBIGUOUS"

DEFAULT_OPTIONS: Final[dict[str, object]] = {
    "fecha_cercana_dias": 3,
    "importe_tolerancia_absoluta": 0.01,
    "importe_tolerancia_relativa": 0.0,
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
    "La coincidencia de atributos no demuestra por si sola identidad economica.",
    "Las colisiones de cardinalidad permanecen ambiguas hasta revision humana.",
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

    candidate_edges: list[dict[str, object]] = []
    amount_difference_edges: list[dict[str, object]] = []

    for bank in bank_rows:
        for internal in internal_rows:
            comparison = _compare_movements(bank, internal, options_used)
            match_type = _candidate_match_type(comparison)
            if match_type is not None:
                candidate_edges.append(
                    {
                        "bank": bank,
                        "internal": internal,
                        "comparison": comparison,
                        "match_type": match_type,
                    }
                )
                continue

            if comparison["same_date_different_amount"]:
                amount_difference_edges.append(
                    {
                        "bank": bank,
                        "internal": internal,
                        "comparison": comparison,
                    }
                )

    prioritized_edges = _apply_reference_priority(candidate_edges)
    resolved = _resolve_candidate_edges(prioritized_edges)
    matches_exactos = resolved["matches_exactos"]
    matches_probables = resolved["matches_probables"]
    matches_ambiguos = resolved["matches_ambiguos"]
    diferencias_fecha = resolved["diferencias_fecha"]
    diferencias_importe = _select_amount_differences(
        amount_difference_edges,
        candidate_edges=prioritized_edges,
    )

    candidate_bank_indexes = resolved["resolved_bank_indexes"]
    candidate_internal_indexes = resolved["resolved_internal_indexes"]

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
        matches_ambiguos=matches_ambiguos,
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
        "matches_ambiguos": matches_ambiguos,
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
        "matches_ambiguos": [],
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
        for key in DEFAULT_OPTIONS:
            if key in options:
                normalized[key] = options[key]
    return normalized


def _validate_options(options: dict[str, object]) -> list[dict[str, object]]:
    errors: list[dict[str, object]] = []
    if not isinstance(options.get("fecha_cercana_dias"), int) or int(options["fecha_cercana_dias"]) < 0:
        errors.append({"field": "fecha_cercana_dias", "reason": "must_be_non_negative_integer"})
    for field in ("importe_tolerancia_absoluta", "importe_tolerancia_relativa"):
        value = options.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            errors.append({"field": field, "reason": "must_be_finite_number"})
        elif float(value) < 0:
            errors.append({"field": field, "reason": "must_be_non_negative_number"})
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
    amount_match = amount_delta <= amount_tolerance
    date_delta_days = abs((bank["fecha"] - internal["fecha"]).days)  # type: ignore[operator]
    date_match = date_delta_days == 0
    near_date = 0 < date_delta_days <= int(options["fecha_cercana_dias"])

    bank_reference = _reference_key(bank.get("referencia"))
    internal_reference = _reference_key(internal.get("referencia"))
    references_present = bank_reference is not None and internal_reference is not None
    reference_match = references_present and bank_reference == internal_reference
    reference_related = references_present and bool(
        _reference_tokens(bank_reference) & _reference_tokens(internal_reference)
    )
    reference_conflict = references_present and not reference_match and not reference_related

    return {
        "amount_match": amount_match,
        "date_match": date_match,
        "near_date": near_date,
        "reference_match": reference_match,
        "reference_related": reference_related,
        "reference_conflict": reference_conflict,
        "same_date_different_amount": date_match and not amount_match,
        "amount_delta": round(amount_delta, 2),
        "amount_tolerance": round(amount_tolerance, 6),
        "date_delta_days": date_delta_days,
    }


def _reference_key(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = " ".join(value.strip().casefold().split())
    return normalized or None


def _reference_tokens(value: str | None) -> set[str]:
    if value is None:
        return set()
    normalized = value
    for separator in (";", ",", "/", "|"):
        normalized = normalized.replace(separator, " ")
    return {token for token in normalized.split() if token}


def _candidate_match_type(comparison: dict[str, object]) -> str | None:
    if comparison["amount_match"] and comparison["reference_match"]:
        return MATCH_REFERENCE_EXACT
    if comparison["amount_match"] and comparison["date_match"]:
        return MATCH_ATTRIBUTES_EXACT
    if comparison["amount_match"] and comparison["near_date"]:
        return MATCH_PROBABLE_DATE
    return None


def _amount_tolerance(
    bank: dict[str, object],
    internal: dict[str, object],
    options: dict[str, object],
) -> float:
    absolute = float(options["importe_tolerancia_absoluta"])
    relative = float(options["importe_tolerancia_relativa"])
    base = max(abs(float(bank["importe"])), abs(float(internal["importe"])))
    return max(absolute, base * relative)


def _select_amount_differences(
    edges: list[dict[str, object]],
    *,
    candidate_edges: list[dict[str, object]],
) -> list[dict[str, object]]:
    candidate_bank_indexes = {
        int(edge["bank"]["index"])  # type: ignore[index]
        for edge in candidate_edges
    }
    candidate_internal_indexes = {
        int(edge["internal"]["index"])  # type: ignore[index]
        for edge in candidate_edges
    }
    reference_bank_indexes = {
        int(edge["bank"]["index"])  # type: ignore[index]
        for edge in edges
        if bool(edge["comparison"]["reference_match"])  # type: ignore[index]
        or bool(edge["comparison"]["reference_related"])  # type: ignore[index]
    }
    reference_internal_indexes = {
        int(edge["internal"]["index"])  # type: ignore[index]
        for edge in edges
        if bool(edge["comparison"]["reference_match"])  # type: ignore[index]
        or bool(edge["comparison"]["reference_related"])  # type: ignore[index]
    }

    residual_edges: list[dict[str, object]] = []
    for edge in edges:
        comparison = edge["comparison"]  # type: ignore[assignment]
        if bool(comparison["reference_match"]) or bool(comparison["reference_related"]):  # type: ignore[index]
            continue
        bank_index = int(edge["bank"]["index"])  # type: ignore[index]
        internal_index = int(edge["internal"]["index"])  # type: ignore[index]
        if bank_index in candidate_bank_indexes or internal_index in candidate_internal_indexes:
            continue
        if bank_index in reference_bank_indexes or internal_index in reference_internal_indexes:
            continue
        residual_edges.append(edge)

    residual_bank_counts: dict[int, int] = {}
    residual_internal_counts: dict[int, int] = {}
    for edge in residual_edges:
        bank_index = int(edge["bank"]["index"])  # type: ignore[index]
        internal_index = int(edge["internal"]["index"])  # type: ignore[index]
        residual_bank_counts[bank_index] = residual_bank_counts.get(bank_index, 0) + 1
        residual_internal_counts[internal_index] = residual_internal_counts.get(internal_index, 0) + 1

    selected: list[dict[str, object]] = []
    for edge in edges:
        comparison = edge["comparison"]  # type: ignore[assignment]
        bank_index = int(edge["bank"]["index"])  # type: ignore[index]
        internal_index = int(edge["internal"]["index"])  # type: ignore[index]
        reference_anchor = bool(comparison["reference_match"]) or bool(comparison["reference_related"])  # type: ignore[index]
        unique_residual = (
            edge in residual_edges
            and not bool(comparison["reference_conflict"])  # type: ignore[index]
            and residual_bank_counts.get(bank_index) == 1
            and residual_internal_counts.get(internal_index) == 1
        )
        if not reference_anchor and not unique_residual:
            continue
        bank = edge["bank"]  # type: ignore[assignment]
        internal = edge["internal"]  # type: ignore[assignment]
        selected.append(
            _difference_pair(
                bank,  # type: ignore[arg-type]
                internal,  # type: ignore[arg-type]
                criterio="same_date_different_amount",
                diferencias={
                    "importe_banco": bank["importe"],  # type: ignore[index]
                    "importe_interno": internal["importe"],  # type: ignore[index]
                    "diferencia_absoluta": comparison["amount_delta"],  # type: ignore[index]
                },
                evidencia=_evidence_payload(comparison),  # type: ignore[arg-type]
            )
        )
    return selected


def _apply_reference_priority(edges: list[dict[str, object]]) -> list[dict[str, object]]:
    bank_with_reference_match = {
        int(edge["bank"]["index"])  # type: ignore[index]
        for edge in edges
        if edge["match_type"] == MATCH_REFERENCE_EXACT
    }
    internal_with_reference_match = {
        int(edge["internal"]["index"])  # type: ignore[index]
        for edge in edges
        if edge["match_type"] == MATCH_REFERENCE_EXACT
    }

    prioritized: list[dict[str, object]] = []
    for edge in edges:
        bank_index = int(edge["bank"]["index"])  # type: ignore[index]
        internal_index = int(edge["internal"]["index"])  # type: ignore[index]
        if bank_index in bank_with_reference_match and edge["match_type"] != MATCH_REFERENCE_EXACT:
            continue
        if internal_index in internal_with_reference_match and edge["match_type"] != MATCH_REFERENCE_EXACT:
            continue
        prioritized.append(edge)
    return prioritized


def _resolve_candidate_edges(edges: list[dict[str, object]]) -> dict[str, object]:
    bank_edges: dict[int, list[dict[str, object]]] = {}
    internal_edges: dict[int, list[dict[str, object]]] = {}
    for edge in edges:
        bank_index = int(edge["bank"]["index"])  # type: ignore[index]
        internal_index = int(edge["internal"]["index"])  # type: ignore[index]
        bank_edges.setdefault(bank_index, []).append(edge)
        internal_edges.setdefault(internal_index, []).append(edge)

    matches_exactos: list[dict[str, object]] = []
    matches_probables: list[dict[str, object]] = []
    diferencias_fecha: list[dict[str, object]] = []
    resolved_bank_indexes: set[int] = set()
    resolved_internal_indexes: set[int] = set()

    ambiguous_edges: list[dict[str, object]] = []
    for edge in edges:
        bank = edge["bank"]
        internal = edge["internal"]
        bank_index = int(bank["index"])  # type: ignore[index]
        internal_index = int(internal["index"])  # type: ignore[index]
        if len(bank_edges[bank_index]) > 1 or len(internal_edges[internal_index]) > 1:
            ambiguous_edges.append(edge)
            continue

        payload = _match_pair(
            bank,  # type: ignore[arg-type]
            internal,  # type: ignore[arg-type]
            match_type=str(edge["match_type"]),
            comparison=edge["comparison"],  # type: ignore[arg-type]
        )
        if edge["match_type"] == MATCH_PROBABLE_DATE:
            matches_probables.append(payload)
        else:
            matches_exactos.append(payload)

        comparison = edge["comparison"]  # type: ignore[assignment]
        if int(comparison["date_delta_days"]) > 0:  # type: ignore[index]
            diferencias_fecha.append(
                _difference_pair(
                    bank,  # type: ignore[arg-type]
                    internal,  # type: ignore[arg-type]
                    criterio="same_amount_different_date",
                    diferencias={"dias": comparison["date_delta_days"]},  # type: ignore[index]
                    evidencia=_evidence_payload(comparison),  # type: ignore[arg-type]
                )
            )
        resolved_bank_indexes.add(bank_index)
        resolved_internal_indexes.add(internal_index)

    matches_ambiguos = _build_ambiguous_components(ambiguous_edges)
    return {
        "matches_exactos": matches_exactos,
        "matches_probables": matches_probables,
        "matches_ambiguos": matches_ambiguos,
        "diferencias_fecha": diferencias_fecha,
        "resolved_bank_indexes": resolved_bank_indexes,
        "resolved_internal_indexes": resolved_internal_indexes,
    }


def _build_ambiguous_components(edges: list[dict[str, object]]) -> list[dict[str, object]]:
    if not edges:
        return []

    by_bank: dict[int, list[int]] = {}
    by_internal: dict[int, list[int]] = {}
    for edge_index, edge in enumerate(edges):
        bank_index = int(edge["bank"]["index"])  # type: ignore[index]
        internal_index = int(edge["internal"]["index"])  # type: ignore[index]
        by_bank.setdefault(bank_index, []).append(edge_index)
        by_internal.setdefault(internal_index, []).append(edge_index)

    visited: set[int] = set()
    components: list[dict[str, object]] = []
    for start in range(len(edges)):
        if start in visited:
            continue
        pending = [start]
        component_edge_indexes: set[int] = set()
        while pending:
            current = pending.pop()
            if current in component_edge_indexes:
                continue
            component_edge_indexes.add(current)
            edge = edges[current]
            bank_index = int(edge["bank"]["index"])  # type: ignore[index]
            internal_index = int(edge["internal"]["index"])  # type: ignore[index]
            pending.extend(by_bank.get(bank_index, []))
            pending.extend(by_internal.get(internal_index, []))

        visited.update(component_edge_indexes)
        component_edges = [edges[index] for index in sorted(component_edge_indexes)]
        components.append(_ambiguous_component_payload(component_edges))

    return components


def _ambiguous_component_payload(edges: list[dict[str, object]]) -> dict[str, object]:
    bank_ids = _ordered_unique(str(edge["bank"]["id"]) for edge in edges)  # type: ignore[index]
    internal_ids = _ordered_unique(str(edge["internal"]["id"]) for edge in edges)  # type: ignore[index]
    bank_count = len(bank_ids)
    internal_count = len(internal_ids)
    if bank_count == 1 and internal_count > 1:
        cardinality = "1:N"
    elif bank_count > 1 and internal_count == 1:
        cardinality = "N:1"
    else:
        cardinality = "N:M"

    candidates = [
        _match_pair(
            edge["bank"],  # type: ignore[arg-type]
            edge["internal"],  # type: ignore[arg-type]
            match_type=str(edge["match_type"]),
            comparison=edge["comparison"],  # type: ignore[arg-type]
        )
        for edge in edges
    ]
    return {
        "tipo": AMBIGUOUS,
        "cardinalidad": cardinality,
        "banco_ids": bank_ids,
        "interno_ids": internal_ids,
        "candidate_count": len(candidates),
        "candidatos": candidates,
        "requires_human_review": True,
    }


def _ordered_unique(values: object) -> list[str]:
    result: list[str] = []
    for value in values:  # type: ignore[union-attr]
        if value not in result:
            result.append(value)
    return result


def _match_pair(
    bank: dict[str, object],
    internal: dict[str, object],
    *,
    match_type: str,
    comparison: dict[str, object],
) -> dict[str, object]:
    criterio = {
        MATCH_REFERENCE_EXACT: "same_reference_same_amount",
        MATCH_ATTRIBUTES_EXACT: "same_date_same_amount",
        MATCH_PROBABLE_DATE: "near_date_same_amount",
    }[match_type]
    payload: dict[str, object] = {
        "banco_id": bank["id"],
        "interno_id": internal["id"],
        "tipo_match": match_type,
        "criterio": criterio,
        "evidencia": _evidence_payload(comparison),
    }
    if int(comparison["date_delta_days"]) > 0:
        payload["diferencias"] = {"dias": comparison["date_delta_days"]}
    return payload


def _evidence_payload(comparison: dict[str, object]) -> dict[str, object]:
    return {
        "reference_match": bool(comparison["reference_match"]),
        "reference_conflict": bool(comparison["reference_conflict"]),
        "amount_match": bool(comparison["amount_match"]),
        "amount_delta": comparison["amount_delta"],
        "date_match": bool(comparison["date_match"]),
        "date_delta_days": comparison["date_delta_days"],
    }


def _difference_pair(
    bank: dict[str, object],
    internal: dict[str, object],
    *,
    criterio: str,
    diferencias: dict[str, object],
    evidencia: dict[str, object],
) -> dict[str, object]:
    return {
        "banco_id": bank["id"],
        "interno_id": internal["id"],
        "criterio": criterio,
        "diferencias": diferencias,
        "evidencia": evidencia,
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
    matches_ambiguos: list[dict[str, object]],
    banco_sin_imputar: list[dict[str, object]],
    interno_sin_banco: list[dict[str, object]],
    diferencias_importe: list[dict[str, object]],
    diferencias_fecha: list[dict[str, object]],
    faltantes_evidencia: list[dict[str, object]],
) -> str:
    has_candidates = bool(matches_exactos or matches_probables or matches_ambiguos or diferencias_importe or diferencias_fecha)
    has_pending = bool(banco_sin_imputar or interno_sin_banco or faltantes_evidencia)
    has_partial = bool(matches_probables or matches_ambiguos or diferencias_importe or diferencias_fecha)

    if has_partial or (has_candidates and has_pending):
        return "PARTIAL_MATCHES_FOUND"
    if matches_exactos:
        return "READY_FOR_HUMAN_REVIEW"
    if faltantes_evidencia:
        return "NEEDS_MORE_EVIDENCE"
    return "NO_CANDIDATES_FOUND"
