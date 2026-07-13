from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


@lru_cache(maxsize=1)
def load_formula_rules() -> dict[str, Any]:
    """Carga y cachea las reglas de fórmulas declarativas desde formula_rules_v1.json."""
    catalog_path = Path(__file__).resolve().parent / "formula_rules_v1.json"
    if not catalog_path.exists():
        return {}
    return json.loads(catalog_path.read_text(encoding="utf-8"))
