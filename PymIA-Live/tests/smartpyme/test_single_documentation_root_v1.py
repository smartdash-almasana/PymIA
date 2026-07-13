from __future__ import annotations

from pathlib import Path

from pymia.audit_result.evidence_requirement_matcher import _docs_root
from tools.bem_schema_builder.cli import _repo_root as _bem_repo_root


REPO_ROOT = Path(__file__).resolve().parents[3]
LIVE_ROOT = REPO_ROOT / "PymIA-Live"
ROOT_DOCS = REPO_ROOT / "docs"
FORBIDDEN_SECONDARY_DOCS_REF = "PymIA-Live" + "/docs"

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
    assert not (LIVE_ROOT / "docs").exists()


def test_required_runtime_catalogs_live_in_root_docs() -> None:
    missing = [
        name for name in REQUIRED_TECHNICAL_ARTIFACTS if not (ROOT_DOCS / name).is_file()
    ]
    assert missing == []


def test_active_service_1_sources_do_not_reference_secondary_docs_root() -> None:
    roots = (
        LIVE_ROOT / "pymia",
        LIVE_ROOT / "tests",
        LIVE_ROOT / "tools",
        REPO_ROOT / "docs" / "current",
    )
    violations: list[str] = []
    for root in roots:
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {
                ".py",
                ".md",
                ".json",
                ".yaml",
                ".yml",
                ".toml",
            }:
                continue
            text = path.read_text(encoding="utf-8-sig")
            if FORBIDDEN_SECONDARY_DOCS_REF in text:
                violations.append(path.relative_to(REPO_ROOT).as_posix())
    assert violations == []


def test_runtime_catalog_resolvers_target_repository_root() -> None:
    assert _docs_root() == ROOT_DOCS
    assert _bem_repo_root() == REPO_ROOT
