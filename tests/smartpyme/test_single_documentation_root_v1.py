from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT_DOCS = REPO_ROOT / "docs"
ROOT_PACKAGE = REPO_ROOT / "pymia"
FORBIDDEN_TRANSITIONAL_ROOT = REPO_ROOT / ("PymIA" + "-Live")

REQUIRED_TECHNICAL_ARTIFACTS = (
    "formula_catalog.schema.v1.json",
    "formula_catalog.v1.json",
    "pathology_catalog.v1.json",
    "pathology_catalog.enriched.v1.json",
    "service_1_formula_pathology_evidence_matrix.v1.json",
    "service_1_module_disposition.v1.json",
    "service_1_semantic_variable_catalog.v1.json",
)


def test_repository_has_single_physical_documentation_root() -> None:
    assert ROOT_DOCS.is_dir()
    assert not FORBIDDEN_TRANSITIONAL_ROOT.exists()


def test_repository_has_single_pymia_package_root() -> None:
    assert ROOT_PACKAGE.is_dir()
    spec = importlib.util.find_spec("pymia")
    assert spec is not None and spec.origin is not None
    assert Path(spec.origin).resolve() == (ROOT_PACKAGE / "__init__.py").resolve()


def test_required_runtime_catalogs_live_in_root_docs() -> None:
    missing = [name for name in REQUIRED_TECHNICAL_ARTIFACTS if not (ROOT_DOCS / name).is_file()]
    assert missing == []
