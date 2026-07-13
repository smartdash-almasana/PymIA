from __future__ import annotations

from typing import Any

from pymia.contracts.vertical_slice_copy_v1 import (
    owner_simple_readable_areas,
    owner_simple_understanding_by_axis,
    vertical_slice_copy_for,
)
from pymia.smartpyme.question_alignment_gate import detect_owner_axis


def _owner_understanding_text(message: str) -> str:
    owner_axis = detect_owner_axis(message)
    axis_messages = owner_simple_understanding_by_axis()
    return axis_messages[owner_axis]


def _owner_readable_summary(profile: dict) -> str:
    headers = [str(item).lower() for item in profile.get("headers", [])]
    joined = " ".join(headers)
    readable_areas: list[str] = []

    for label, payload in owner_simple_readable_areas().items():
        keywords = payload.get("keywords") or []
        if any(keyword in joined for keyword in keywords):
            readable_areas.append(label)

    if readable_areas:
        if len(readable_areas) == 1:
            area_text = readable_areas[0]
        elif len(readable_areas) == 2:
            area_text = f"{readable_areas[0]} y {readable_areas[1]}"
        else:
            area_text = ", ".join(readable_areas[:-1]) + f" y {readable_areas[-1]}"
        return vertical_slice_copy_for("owner_simple_readable_summary_template").format(area_text=area_text)

    if profile.get("rows", 0) > 1 and profile.get("columns", 0) > 0:
        return vertical_slice_copy_for("owner_simple_minimal_signals")

    return vertical_slice_copy_for("owner_simple_unreadable")


def build_owner_simple_view(
    *,
    report: dict,
    message: str,
    profile: dict,
    owner_question: str | None,
) -> dict[str, Any]:
    return {
        "que_entendimos": _owner_understanding_text(message),
        "que_pudimos_leer": _owner_readable_summary(profile),
        "que_todavia_no_podemos_afirmar": vertical_slice_copy_for("owner_simple_unknown_assertion"),
        "proxima_pregunta": owner_question or vertical_slice_copy_for("next_question_fallback"),
        "limites": list(report.get("limit_warnings") or []) + [vertical_slice_copy_for("final_limit_warning")],
    }


__all__ = ["build_owner_simple_view"]
