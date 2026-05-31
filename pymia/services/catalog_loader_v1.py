from __future__ import annotations

import json
from pathlib import Path

from pymia.contracts.catalogs_v1 import FormulaCatalogV1, PathologyCatalogV1


_REPO_ROOT = Path(__file__).resolve().parents[2]
_DOCS_DIR = _REPO_ROOT / "docs"


class CatalogLoadError(RuntimeError):
    pass


def _load_json(path: Path) -> dict:
    if not path.exists():
        raise CatalogLoadError(f"Catalog file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CatalogLoadError(f"Invalid JSON catalog: {path}") from exc


def load_pathology_catalog_v1(path: Path | None = None) -> PathologyCatalogV1:
    catalog_path = path or (_DOCS_DIR / "pathology_catalog.v1.json")
    return PathologyCatalogV1.model_validate(_load_json(catalog_path))


def load_formula_catalog_v1(path: Path | None = None) -> FormulaCatalogV1:
    catalog_path = path or (_DOCS_DIR / "formula_catalog.v1.json")
    return FormulaCatalogV1.model_validate(_load_json(catalog_path))


def validate_formula_pathology_links(
    pathology_catalog: PathologyCatalogV1 | None = None,
    formula_catalog: FormulaCatalogV1 | None = None,
) -> list[str]:
    pathologies = pathology_catalog or load_pathology_catalog_v1()
    formulas = formula_catalog or load_formula_catalog_v1()

    pathology_codes = {entry.pathology_code for entry in pathologies.pathologies}
    return [
        formula.pathology_code
        for formula in formulas.formulas
        if formula.pathology_code not in pathology_codes
    ]


def get_candidate_formula_ids_by_pathology_codes(
    pathology_codes: list[str],
    formula_catalog: FormulaCatalogV1 | None = None,
) -> list[str]:
    """Return lightweight formula IDs linked to candidate pathologies."""
    candidate_codes = {
        code.strip()
        for code in pathology_codes
        if isinstance(code, str) and code.strip()
    }
    formulas = formula_catalog or load_formula_catalog_v1()
    formula_ids: list[str] = []
    for formula in formulas.formulas:
        if formula.pathology_code in candidate_codes and formula.formula_id not in formula_ids:
            formula_ids.append(formula.formula_id)
    return formula_ids
