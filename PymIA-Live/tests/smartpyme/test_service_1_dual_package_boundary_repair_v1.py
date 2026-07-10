"""Focal tests for SERVICE_1_DUAL_PACKAGE_BOUNDARY_REPAIR_V1."""
from __future__ import annotations

import inspect
from pathlib import Path

import pymia
from pymia.smartpyme import service_1_runtime_release_gate_v1
from pymia.smartpyme.service_1_dual_package_boundary_repair_v1 import (
    EXPECTED_ACTIVE_PACKAGE_FLAVOR,
    ROOT_LEGACY_PACKAGE_FLAVOR,
    STATUS_BOUNDARY_READY,
    build_service_1_dual_package_boundary_repair_v1,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _live_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_active_pymia_package_is_pymia_live_when_running_service_1_tests() -> None:
    result = build_service_1_dual_package_boundary_repair_v1()

    assert result.boundary_status == STATUS_BOUNDARY_READY
    assert result.active_package_flavor == EXPECTED_ACTIVE_PACKAGE_FLAVOR
    assert result.active_package_is_live is True
    assert result.service_1_runtime_imports_allowed is True
    assert "PymIA-Live" in Path(result.active_package_file).parts
    assert result.runtime_authorized is False
    assert result.delivery_authorized is False
    assert result.product_ready is False


def test_package_markers_make_root_and_live_boundary_explicit() -> None:
    root_init = _repo_root() / "pymia" / "__init__.py"
    live_init = _live_root() / "pymia" / "__init__.py"

    assert 'PACKAGE_FLAVOR = "PYMIA_ROOT_LEGACY"' in root_init.read_text(encoding="utf-8")
    assert 'PACKAGE_FLAVOR = "PYMIA_LIVE"' in live_init.read_text(encoding="utf-8")
    assert getattr(pymia, "PACKAGE_FLAVOR") == EXPECTED_ACTIVE_PACKAGE_FLAVOR
    assert ROOT_LEGACY_PACKAGE_FLAVOR == "PYMIA_ROOT_LEGACY"


def test_service_1_active_modules_resolve_under_pymia_live() -> None:
    module_file = Path(inspect.getfile(service_1_runtime_release_gate_v1)).resolve()

    assert "PymIA-Live" in module_file.parts
    assert module_file.name == "service_1_runtime_release_gate_v1.py"


def test_root_smartpyme_does_not_host_service_1_runtime_modules() -> None:
    root_smartpyme = _repo_root() / "pymia" / "smartpyme"
    service_1_files = sorted(path.name for path in root_smartpyme.glob("service_1_*.py"))

    assert service_1_files == []


def test_boundary_module_has_no_cli_parser_or_runtime_authorization_paths() -> None:
    module_path = (
        _live_root()
        / "pymia"
        / "smartpyme"
        / "service_1_dual_package_boundary_repair_v1.py"
    )
    content = module_path.read_text(encoding="utf-8")
    forbidden = [
        "pymia.cli",
        "document_ingestion",
        "xlsx_to_normalized",
        "excel_lab_ingestion",
        "runtime_authorized=True",
        '"runtime_authorized": True',
        "delivery_authorized=True",
        "product_ready=True",
        "CASE_001",
    ]
    for pattern in forbidden:
        assert pattern not in content
