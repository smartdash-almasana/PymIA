from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


@lru_cache(maxsize=1)
def load_presentation_labels() -> dict[str, Any]:
    """Carga y cachea el contrato de labels de presentación."""
    catalog_path = Path(__file__).resolve().parent / "presentation_labels_v1.json"
    if not catalog_path.exists():
        return {}
    return json.loads(catalog_path.read_text(encoding="utf-8"))


def label_for_pathology(code: str) -> str:
    """Devuelve el label owner-friendly para un código de patología."""
    data = load_presentation_labels()
    labels = data.get("pathology_labels") or {}
    return labels.get(code, code.replace("_", " ").lower())


def label_for_field(name: str) -> str:
    """Devuelve el label owner-friendly para un nombre de campo."""
    data = load_presentation_labels()
    labels = data.get("field_labels") or {}
    return labels.get(name, name.replace("_", " ").lower())


def load_operational_terms() -> list[str]:
    """Devuelve la lista de términos operativos para detección de columnas."""
    data = load_presentation_labels()
    return list(data.get("operational_terms") or [])
