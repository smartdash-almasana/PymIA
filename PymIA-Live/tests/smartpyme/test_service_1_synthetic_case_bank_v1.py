from __future__ import annotations

from pathlib import Path

from pymia.smartpyme.service_1_synthetic_case_bank_v1 import (
    STATUS_FIXTURE_MISSING,
    STATUS_REGRESSION_READY,
    REQUIRED_COVERAGE,
    service_1_synthetic_case_bank_v1,
    validate_service_1_synthetic_case_bank_v1,
)


def _touch(base: Path, relative_path: str) -> None:
    path = base / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("fixture", encoding="utf-8")


def _materialize_bank(base: Path) -> None:
    for spec in service_1_synthetic_case_bank_v1():
        _touch(base, spec.input_xlsx_path)
        if spec.tool_requests_path is not None:
            _touch(base, spec.tool_requests_path)
        for artifact in spec.expected_artifacts:
            _touch(base, artifact)


def test_case_bank_has_regression_cases_without_runtime_authorization() -> None:
    cases = service_1_synthetic_case_bank_v1()

    assert len(cases) >= 4
    assert all(case.runtime_authorized is False for case in cases)
    assert all(case.autonomous_use_authorized is False for case in cases)
    assert all("demo" not in " ".join(case.notes).lower() for case in cases)


def test_case_bank_covers_required_first_aid_families() -> None:
    covered = {tool for case in service_1_synthetic_case_bank_v1() for tool in case.covered_tool_refs}

    assert set(REQUIRED_COVERAGE).issubset(covered)


def test_validation_reports_ready_when_all_fixture_paths_exist(tmp_path: Path) -> None:
    _materialize_bank(tmp_path)

    validation = validate_service_1_synthetic_case_bank_v1(base_dir=tmp_path)

    assert validation.status == STATUS_REGRESSION_READY
    assert validation.total_cases == len(service_1_synthetic_case_bank_v1())
    assert len(validation.ready_case_ids) == validation.total_cases
    assert validation.blocked_case_ids == ()
    assert validation.missing_coverage == ()
    assert validation.runtime_authorized is False
    assert validation.autonomous_use_authorized is False
    assert validation.metadata["not_a_demo"] is True
    assert validation.metadata["does_not_reopen_full_assisted_v1_closure"] is True


def test_validation_reports_missing_fixture_paths(tmp_path: Path) -> None:
    first_case = service_1_synthetic_case_bank_v1()[0]
    _touch(tmp_path, first_case.input_xlsx_path)

    validation = validate_service_1_synthetic_case_bank_v1(base_dir=tmp_path, cases=(first_case,))

    assert validation.status == STATUS_FIXTURE_MISSING
    assert validation.ready_case_ids == ()
    assert validation.blocked_case_ids == (first_case.case_id,)
    assert validation.case_results[0]["missing_paths"]
    assert validation.runtime_authorized is False
