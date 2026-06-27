"""
Tests for service_1_xlsx_structure_v1

Validates:
1. Reads existing XLSX fixture and detects at least one sheet
2. Returns headers as a list
3. runtime_authorized is always False
4. Non-existent file raises FileNotFoundError or controlled error
5. Does not import forbidden modules
6. Does not expose forbidden keys: diagnosis, recommendation, accounting_result, runtime_authorized true
"""

import ast
import os
import sys
from pathlib import Path

import pytest


# Add PymIA-Live to sys.path for imports
TESTS_DIR = Path(__file__).resolve().parent.parent
PYMIA_LIVE = TESTS_DIR.parent
REPO_ROOT = PYMIA_LIVE.parent
sys.path.insert(0, str(PYMIA_LIVE))


@pytest.fixture
def xlsx_fixture_path():
    """Return path to a real XLSX fixture."""
    fixture = REPO_ROOT / "prueba_excels" / "cafeteria_abc.xlsx"
    if not fixture.exists():
        pytest.skip(f"Fixture not found: {fixture}")
    return str(fixture)


@pytest.fixture
def nonexistent_path():
    """Return a path that does not exist."""
    return str(REPO_ROOT / "prueba_excels" / "nonexistent_file_12345.xlsx")


def test_reads_xlsx_fixture_and_detects_sheets(xlsx_fixture_path):
    """Test 1: Read existing XLSX fixture and detect at least one sheet."""
    from pymia.smartpyme.service_1_xlsx_structure_v1 import read_service_1_xlsx_structure_v1

    result = read_service_1_xlsx_structure_v1(xlsx_fixture_path)

    assert result is not None
    assert "workbook" in result
    assert "sheet_count" in result["workbook"]
    assert result["workbook"]["sheet_count"] >= 1
    assert "sheets" in result["workbook"]
    assert len(result["workbook"]["sheets"]) >= 1


def test_returns_headers_as_list(xlsx_fixture_path):
    """Test 2: Returns headers as a list."""
    from pymia.smartpyme.service_1_xlsx_structure_v1 import read_service_1_xlsx_structure_v1

    result = read_service_1_xlsx_structure_v1(xlsx_fixture_path)

    assert "workbook" in result
    assert "sheets" in result["workbook"]
    assert len(result["workbook"]["sheets"]) > 0

    first_sheet = result["workbook"]["sheets"][0]
    assert "headers" in first_sheet
    assert isinstance(first_sheet["headers"], list)
    assert all(isinstance(h, str) for h in first_sheet["headers"])


def test_runtime_authorized_always_false(xlsx_fixture_path):
    """Test 3: runtime_authorized is always False."""
    from pymia.smartpyme.service_1_xlsx_structure_v1 import read_service_1_xlsx_structure_v1

    result = read_service_1_xlsx_structure_v1(xlsx_fixture_path)

    assert "runtime_authorized" in result
    assert result["runtime_authorized"] is False


def test_nonexistent_file_raises_error(nonexistent_path):
    """Test 4: Non-existent file raises FileNotFoundError or controlled error."""
    from pymia.smartpyme.service_1_xlsx_structure_v1 import read_service_1_xlsx_structure_v1

    with pytest.raises((FileNotFoundError, OSError, ValueError)):
        read_service_1_xlsx_structure_v1(nonexistent_path)


def test_does_not_import_forbidden_modules():
    """Test 5: Does not import forbidden modules."""
    module_path = PYMIA_LIVE / "pymia" / "smartpyme" / "service_1_xlsx_structure_v1.py"

    with open(module_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    forbidden_modules = {
        "vertical_pipeline",
        "document_ingestion",
        "openai",
        "chatbot",
        "service_1_pipeline_v1",
        "service_1_fsm_decision_patch_v1",
        "service_1_owner_answer_reentry_v1",
        "service_1_owner_answer_reentry_persistence_v1",
        "service_1_case_reentry_read_model_v1",
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split(".")[0]
                assert module_name not in forbidden_modules, (
                    f"Forbidden import: {alias.name}"
                )
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module_name = node.module.split(".")[0]
                assert module_name not in forbidden_modules, (
                    f"Forbidden import from: {node.module}"
                )


def test_does_not_expose_forbidden_keys(xlsx_fixture_path):
    """Test 6: Does not expose forbidden keys."""
    from pymia.smartpyme.service_1_xlsx_structure_v1 import read_service_1_xlsx_structure_v1

    result = read_service_1_xlsx_structure_v1(xlsx_fixture_path)

    forbidden_keys = {
        "diagnosis",
        "recommendation",
        "accounting_result",
        "pipeline_run",
        "evidence_id",
        "document_ingestion",
        "reentry",
        "fsm",
        "llm",
    }

    def check_forbidden_keys(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                assert key not in forbidden_keys, (
                    f"Forbidden key found at {path}.{key}"
                )
                check_forbidden_keys(value, f"{path}.{key}")
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                check_forbidden_keys(item, f"{path}[{idx}]")

    check_forbidden_keys(result)

    # Verify runtime_authorized is False (not True)
    assert result["runtime_authorized"] is False


def test_returns_required_schema_fields(xlsx_fixture_path):
    """Additional validation: Returns all required schema fields."""
    from pymia.smartpyme.service_1_xlsx_structure_v1 import read_service_1_xlsx_structure_v1

    result = read_service_1_xlsx_structure_v1(xlsx_fixture_path)

    required_top_level_keys = {
        "schema_version",
        "service_name",
        "source_path_basename",
        "workbook",
        "warnings",
        "runtime_authorized",
    }

    for key in required_top_level_keys:
        assert key in result, f"Missing required key: {key}"

    assert result["schema_version"] == "1.0"
    assert result["service_name"] == "SERVICE_1"
    assert isinstance(result["source_path_basename"], str)
    assert isinstance(result["warnings"], list)


def test_workbook_structure_fields(xlsx_fixture_path):
    """Additional validation: Workbook has correct structure."""
    from pymia.smartpyme.service_1_xlsx_structure_v1 import read_service_1_xlsx_structure_v1

    result = read_service_1_xlsx_structure_v1(xlsx_fixture_path)

    assert "sheet_count" in result["workbook"]
    assert isinstance(result["workbook"]["sheet_count"], int)
    assert result["workbook"]["sheet_count"] >= 0

    assert "sheets" in result["workbook"]
    assert isinstance(result["workbook"]["sheets"], list)

    for sheet in result["workbook"]["sheets"]:
        required_sheet_keys = {
            "name",
            "max_row",
            "max_column",
            "headers",
            "empty_header_count",
            "sample_rows_count",
        }
        for key in required_sheet_keys:
            assert key in sheet, f"Missing sheet key: {key}"

        assert isinstance(sheet["name"], str)
        assert isinstance(sheet["max_row"], int)
        assert isinstance(sheet["max_column"], int)
        assert isinstance(sheet["headers"], list)
        assert isinstance(sheet["empty_header_count"], int)
        assert isinstance(sheet["sample_rows_count"], int)


def test_source_path_basename_is_correct(xlsx_fixture_path):
    """Additional validation: source_path_basename matches input file."""
    from pymia.smartpyme.service_1_xlsx_structure_v1 import read_service_1_xlsx_structure_v1

    result = read_service_1_xlsx_structure_v1(xlsx_fixture_path)

    expected_basename = os.path.basename(xlsx_fixture_path)
    assert result["source_path_basename"] == expected_basename
