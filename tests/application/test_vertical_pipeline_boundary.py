from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from pymia.application import vertical_pipeline


EXPECTED_PIPELINE_KEYS = {
    "status",
    "profile",
    "report",
    "markdown",
    "diagnostic_operator_summary",
    "evidence_id",
    "evidence_hash",
    "run_id",
    "output_hash",
    "missing_evidence",
    "next_questions",
    "structured_summary",
    "catalog_reconciliation",
}

EXPECTED_REPORT_TRACEABILITY_KEYS = {
    "anamnesis_record",
    "investigation_record",
    "evidence_record",
    "pipeline_run_record",
    "structured_evidence_summary",
    "owner_question",
    "owner_simple",
    "evidence_request_alignment",
}

FORBIDDEN_RUNTIME_IMPORT_FRAGMENTS = (
    "service_depth",
    "fasthtml",
    "fastapi",
    "starlette",
    "django",
    "flask",
    "postgres",
    "psycopg",
    "sqlalchemy",
    "auth",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _vertical_pipeline_source() -> str:
    return (_repo_root() / "pymia" / "application" / "vertical_pipeline.py").read_text(encoding="utf-8")


def _vertical_slice_source() -> str:
    return (_repo_root() / "pymia" / "cli" / "vertical_slice.py").read_text(encoding="utf-8")


def _sample_excel() -> Path:
    return _repo_root() / "prueba_excels" / "cafeteria_abc.xlsx"


def _assert_expected_public_keys(actual: dict, expected: set[str]) -> None:
    missing = expected - set(actual)
    assert not missing, f"Missing public keys: {sorted(missing)}"


def test_vertical_pipeline_boundary() -> None:
    vertical_pipeline_source = _vertical_pipeline_source()
    vertical_slice_source = _vertical_slice_source()

    # vertical_pipeline.py decoupling assertions
    assert "pymia.cli.vertical_slice" not in vertical_pipeline_source
    assert "import argparse" not in vertical_pipeline_source

    # vertical_slice.py adapter assertions
    assert "import argparse" in vertical_slice_source
    assert "from pymia.application.vertical_pipeline import" in vertical_slice_source

    # Ensure vertical_slice.py no longer defines the moved functions
    assert "def inspect_excel(" not in vertical_slice_source
    assert "def has_operational_columns(" not in vertical_slice_source
    assert "def build_structured_summary(" not in vertical_slice_source
    assert "def build_report(" not in vertical_slice_source
    assert "def build_markdown(" not in vertical_slice_source
    assert "def build_pipeline(" not in vertical_slice_source

    # Ensure vertical_slice.py still has main
    assert "def main(" in vertical_slice_source


def test_build_pipeline_returns_public_boundary_keys(tmp_path: Path) -> None:
    pipeline = vertical_pipeline.build_pipeline(
        _sample_excel(),
        "Vendo más pero no me queda plata.",
        tenant_id="boundary_tenant",
        intake_id="boundary_intake",
        storage_dir=tmp_path / "storage",
    )

    _assert_expected_public_keys(pipeline, EXPECTED_PIPELINE_KEYS)


def test_build_report_keeps_minimal_traceability_keys(tmp_path: Path) -> None:
    path = _sample_excel()
    profile = vertical_pipeline.inspect_excel(path)

    report = vertical_pipeline.build_report(
        path,
        "Vendo más pero no me queda plata.",
        profile,
        tenant_id="boundary_tenant",
        intake_id="boundary_intake",
        storage_dir=tmp_path / "storage",
    )

    _assert_expected_public_keys(report, EXPECTED_REPORT_TRACEABILITY_KEYS)


def test_vertical_pipeline_does_not_import_service_depth() -> None:
    source = _vertical_pipeline_source()
    tree = ast.parse(source)

    imported_modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.append(node.module or "")

    assert all("service_depth" not in module for module in imported_modules)


@pytest.mark.parametrize("forbidden", FORBIDDEN_RUNTIME_IMPORT_FRAGMENTS)
def test_vertical_pipeline_does_not_import_web_auth_postgres_or_fasthtml(forbidden: str) -> None:
    source = _vertical_pipeline_source()
    tree = ast.parse(source)

    imported_modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.append(node.module or "")

    assert all(forbidden not in module.lower() for module in imported_modules)


def test_build_markdown_delegates_to_owner_markdown_renderer() -> None:
    source = inspect.getsource(vertical_pipeline.build_markdown)

    assert "render_markdown_from_report(" in source
    assert "return render_markdown_from_report(" in source

    tree = ast.parse(source)
    call_names = [
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    ]
    assert "render_markdown_from_report" in call_names
    assert "build_owner_facing_report" not in call_names
    assert "build_owner_simple_view" not in call_names
