from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

AXIS_CAJA_LIQUIDEZ = "caja_liquidez"
AXIS_VENTAS_MARGEN = "ventas_margen"
AXIS_STOCK_REPOSICION = "stock_reposicion"
AXIS_COSTOS_PROVEEDORES = "costos_proveedores"
AXIS_PRODUCCION = "produccion"
AXIS_RRHH = "rrhh"
AXIS_AUTOMATIZACION_MANUAL = "automatizacion_manual"
AXIS_DESCONOCIDO = "desconocido"

@lru_cache(maxsize=1)
def load_question_alignment_rules() -> dict[str, Any]:
    contract_path = Path(__file__).resolve().parent.parent / "contracts" / "question_alignment_v1.json"
    if not contract_path.exists():
        return {}
    return json.loads(contract_path.read_text(encoding="utf-8"))


def _owner_keywords() -> dict[str, list[str]]:
    return load_question_alignment_rules().get("owner_keywords", {})


def _formula_prefix_axis() -> dict[str, str]:
    return load_question_alignment_rules().get("formula_prefix_axis", {})


def _pathology_axis() -> dict[str, str]:
    return load_question_alignment_rules().get("pathology_axis", {})


def _misalignment_rules() -> list[dict[str, str]]:
    return load_question_alignment_rules().get("misalignment_rules", [])


def detect_owner_axis(message: str) -> str:
    if not message or not message.strip():
        return AXIS_DESCONOCIDO
    msg_lower = message.lower()
    for axis, keywords in _owner_keywords().items():
        for keyword in keywords:
            if keyword in msg_lower:
                return axis
    return AXIS_DESCONOCIDO


def detect_question_axis(entry: dict[str, Any]) -> str:
    formula_id = entry.get("formula_id", "") or ""
    pathology_code = entry.get("pathology_code", "") or ""
    pathology_axis = _pathology_axis()
    if pathology_code in pathology_axis:
        return pathology_axis[pathology_code]
    if "_" in formula_id:
        prefix = formula_id.split("_")[0]
        formula_prefix_axis = _formula_prefix_axis()
        if prefix in formula_prefix_axis:
            return formula_prefix_axis[prefix]
    return AXIS_DESCONOCIDO


def _alignment_status(owner_axis: str, question_axis: str) -> str:
    for rule in _misalignment_rules():
        if (
            owner_axis == rule.get("owner_axis")
            and question_axis == rule.get("question_axis")
        ):
            return str(rule.get("status", "MISALIGNED"))
    return "ALIGNED"


def _get_question_text(entry: dict[str, Any]) -> str:
    questions = entry.get("next_audit_questions") or []
    return str(questions[0]) if questions else ""


def align_next_question(
    owner_message: str,
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    if not candidates:
        return {
            "status": "UNKNOWN",
            "declared_axis": detect_owner_axis(owner_message),
            "question_axis": AXIS_DESCONOCIDO,
            "final_question_text": "",
            "technical_reference": "sin candidatos para evaluar",
        }
    owner_axis = detect_owner_axis(owner_message)
    target_entry = candidates[0]
    question_axis = detect_question_axis(target_entry)
    question_text = _get_question_text(target_entry)
    formula_id = target_entry.get("formula_id", "") or ""
    if not owner_message or not owner_message.strip():
        status = "UNKNOWN"
    elif owner_axis == AXIS_DESCONOCIDO:
        status = "UNKNOWN"
    else:
        status = _alignment_status(owner_axis, question_axis)
    return {
        "status": status,
        "declared_axis": owner_axis,
        "question_axis": question_axis,
        "final_question_text": question_text,
        "technical_reference": formula_id if formula_id else "",
    }


__all__ = [
    "AXIS_CAJA_LIQUIDEZ",
    "AXIS_VENTAS_MARGEN",
    "AXIS_STOCK_REPOSICION",
    "AXIS_COSTOS_PROVEEDORES",
    "AXIS_PRODUCCION",
    "AXIS_RRHH",
    "AXIS_AUTOMATIZACION_MANUAL",
    "AXIS_DESCONOCIDO",
    "load_question_alignment_rules",
    "detect_owner_axis",
    "detect_question_axis",
    "align_next_question",
]
