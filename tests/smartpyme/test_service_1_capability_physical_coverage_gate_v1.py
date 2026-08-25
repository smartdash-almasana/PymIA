from __future__ import annotations

from copy import deepcopy
import subprocess

import tools.service_1_capability_physical_coverage_gate_v1 as gate


def _rows(result: dict) -> dict[str, dict]:
    return {row["capability"]: row for row in result["productive_capabilities"]}


def test_capability_gate_derives_exactly_twelve_from_external_authorities() -> None:
    result = gate.evaluate_service_1_capability_physical_coverage_gate_v1()

    assert result["verdict"] == gate.VERDICT_PASS
    assert result["productive_capability_count"] == 12
    assert result["inventory_authority_match"] is True
    repo = gate.Path(gate.__file__).resolve().parents[1]
    closure_path = repo / "tests" / "smartpyme" / "test_service_1_cycle_053_global_12_pathology_closure_v1.py"
    external_root_refs = set(gate._literal_assignment(closure_path, "EXPECTED_ROOT_REFS"))

    assert len(result["inventory_authority"]["closure_root_refs"]) == 12
    assert set(result["inventory_authority"]["closure_root_refs"]) == external_root_refs
    assert len(result["inventory_authority"]["closure_pathologies"]) == 12
    assert set(result["inventory_authority"]["specialized_refs"]) == {
        "sold_vs_collected_gap",
        "net_margin_real",
    }
    assert "dpo" in result["inventory_authority"]["registry_refs"]
    assert "dpo" not in result["inventory_authority"]["closure_root_refs"]


def test_dpo_is_only_a_prerequisite_and_never_a_thirteenth_capability() -> None:
    result = gate.evaluate_service_1_capability_physical_coverage_gate_v1()

    assert result["dpo_counted_as_productive_capability"] is False
    assert result["dpo_prerequisite"]["capability"] == "dpo"
    assert result["dpo_prerequisite"]["pathology"] == "PYME_013_PREREQUISITE_DPO"
    assert all(row["capability"] != "dpo" for row in result["productive_capabilities"])


def test_structural_guards_certify_canonical_ingestion_and_product_root() -> None:
    result = gate.evaluate_service_1_capability_physical_coverage_gate_v1()

    assert result["canonical_ingestion_guard"] == gate.PASS, result["structural_guard_evidence"]
    assert result["canonical_product_root_guard"] == gate.PASS, result["structural_guard_evidence"]
    assert "canonical_ingestion_reused" not in result
    assert "canonical_product_root_reused" not in result


def test_specialized_required_variables_are_complete() -> None:
    rows = _rows(gate.evaluate_service_1_capability_physical_coverage_gate_v1())

    assert rows["sold_vs_collected_gap"]["required_variables"] == ["sold_amount", "collected_amount"]
    assert rows["net_margin_real"]["required_variables"] == ["sale_price", "costs", "taxes"]


def test_each_physical_pass_has_governed_input_p9_and_safe_flags() -> None:
    result = gate.evaluate_service_1_capability_physical_coverage_gate_v1()

    assert result["unsafe_executions"] == 0
    assert result["failed_unsafe_count"] == 0
    for row in result["productive_capabilities"]:
        if row["coverage_status"] != gate.PHYSICAL_E2E_PASS:
            continue
        assert row["governed_input"] is True
        assert row["p9"] == "EVALUATED"
        assert row["safety"]["unsafe"] is False
        assert row["safety"]["complete"] is True
        assert row["safety"]["missing_flags"] == []
        assert row["safety"]["executed_without_governed_input"] is False
        assert all(value is False for value in row["safety"]["flags"].values())


def test_ren_001_positive_reaches_p9_and_negative_never_executes() -> None:
    row = _rows(gate.evaluate_service_1_capability_physical_coverage_gate_v1())["net_margin_real"]

    assert row["coverage_status"] == gate.PHYSICAL_E2E_PASS
    assert row["p6"] == "APPROVED"
    assert row["p7"] == "REQUIREMENT_MATCHED"
    assert row["p8"] == "COMPUTABLE"
    assert row["governed_input"] is True
    assert row["p9"] == "EVALUATED"
    assert row["negative"] == {
        "p8": "NEEDS_EVIDENCE",
        "governed_input": False,
        "p9": None,
        "execution_attempted": False,
        "product_root_calls": 0,
        "p9_calls": 0,
        "unsafe": False,
    }


def test_pyme_026_remains_partial_until_capability_is_governed() -> None:
    row = _rows(gate.evaluate_service_1_capability_physical_coverage_gate_v1())["adjusted_operating_cash_flow"]

    assert row["coverage_status"] == gate.PHYSICAL_PARTIAL
    assert row["blocker"] == "P6:BLOCKED"
    assert row["p6"] == "BLOCKED"
    assert row["governed_input"] is False
    assert row["p9"] is None


def test_pyme_013_stays_deferred_without_implicit_prerequisite_execution() -> None:
    result = gate.evaluate_service_1_capability_physical_coverage_gate_v1()
    row = _rows(result)["payment_collection_gap"]

    assert result["dpo_prerequisite"]["coverage_status"] == gate.PHYSICAL_PARTIAL
    assert row["coverage_status"] == gate.DEFERRED_BY_CONTRACT
    assert row["blocker"] == "PHYSICAL_DSO_AND_DPO_RESULTS_REQUIRED"
    assert row["p7"] == "PREREQUISITES_NOT_READY"
    assert row["governed_input"] is False
    assert row["p9"] is None
    assert row["safety"]["executed_without_governed_input"] is False


def test_open_safety_flag_produces_failed_unsafe(monkeypatch) -> None:
    real = gate.product_root.run_service_1_product_pipeline_v1

    def unsafe_product(*args, **kwargs):
        product = dict(real(*args, **kwargs))
        request = args[0] if args else kwargs.get("request")
        if getattr(request, "requested_capability", None) == "sold_vs_collected_gap":
            product["runtime_authorized"] = True
        return product

    monkeypatch.setattr(gate.product_root, "run_service_1_product_pipeline_v1", unsafe_product)
    result = gate.evaluate_service_1_capability_physical_coverage_gate_v1()
    rows = _rows(result)

    assert result["verdict"] == gate.VERDICT_FAIL
    assert result["unsafe_executions"] == 1
    assert result["failed_unsafe_count"] == 1
    assert rows["sold_vs_collected_gap"]["coverage_status"] == gate.FAILED_UNSAFE
    assert rows["sold_vs_collected_gap"]["safety"]["flags"]["runtime_authorized"] is True
    assert "UNSAFE_EXECUTIONS_MUST_BE_ZERO" in result["failures"]


def test_missing_safety_flag_cannot_be_physical_e2e_pass(monkeypatch) -> None:
    real = gate.product_root.run_service_1_product_pipeline_v1

    def incomplete_product(*args, **kwargs):
        product = dict(real(*args, **kwargs))
        request = args[0] if args else kwargs.get("request")
        if getattr(request, "requested_capability", None) == "sold_vs_collected_gap":
            product.pop("diagnosis_generated", None)
        return product

    monkeypatch.setattr(gate.product_root, "run_service_1_product_pipeline_v1", incomplete_product)
    result = gate.evaluate_service_1_capability_physical_coverage_gate_v1()
    row = _rows(result)["sold_vs_collected_gap"]

    assert row["coverage_status"] == gate.PHYSICAL_PARTIAL
    assert row["blocker"] == "MISSING_EXPLICIT_SAFETY_FLAGS"
    assert row["safety"]["complete"] is False
    assert row["safety"]["missing_flags"] == ["diagnosis_generated"]


def test_missing_capability_in_external_inventory_fails(monkeypatch) -> None:
    real = gate._derive_inventory_authority_v1

    def missing(repo):
        authority = deepcopy(real(repo))
        authority["rows"] = tuple(authority["rows"][:-1])
        authority["authority_match"] = False
        return authority

    monkeypatch.setattr(gate, "_derive_inventory_authority_v1", missing)
    result = gate.evaluate_service_1_capability_physical_coverage_gate_v1()

    assert result["verdict"] == gate.VERDICT_FAIL
    assert result["productive_capability_count"] == 11
    assert "INVENTORY_AUTHORITY_DIVERGENCE" in result["failures"]
    assert "PRODUCTIVE_CAPABILITY_COUNT_MUST_BE_EXACTLY_12" in result["failures"]


def test_additional_capability_and_dpo_as_thirteenth_fail(monkeypatch) -> None:
    real = gate._derive_inventory_authority_v1

    def with_dpo(repo):
        authority = deepcopy(real(repo))
        authority["rows"] = tuple(authority["rows"]) + (("dpo", "PYME_013_PREREQUISITE_DPO"),)
        authority["authority_match"] = False
        return authority

    monkeypatch.setattr(gate, "_derive_inventory_authority_v1", with_dpo)
    result = gate.evaluate_service_1_capability_physical_coverage_gate_v1()

    assert result["verdict"] == gate.VERDICT_FAIL
    assert result["productive_capability_count"] == 13
    assert result["dpo_counted_as_productive_capability"] is True
    assert "DPO_MUST_NOT_BE_A_THIRTEENTH_CAPABILITY" in result["failures"]


def test_authority_divergence_produces_stop(monkeypatch) -> None:
    real = gate._derive_inventory_authority_v1

    def divergent(repo):
        authority = deepcopy(real(repo))
        authority["closure_root_refs"] = tuple(ref for ref in authority["closure_root_refs"] if ref != "dso")
        authority["authority_match"] = False
        return authority

    monkeypatch.setattr(gate, "_derive_inventory_authority_v1", divergent)
    result = gate.evaluate_service_1_capability_physical_coverage_gate_v1()

    assert result["verdict"] == gate.VERDICT_FAIL
    assert result["inventory_authority_match"] is False
    assert "INVENTORY_AUTHORITY_DIVERGENCE" in result["failures"]


def test_structural_guard_failure_cannot_be_certified_by_fixed_boolean(monkeypatch) -> None:
    monkeypatch.setattr(
        gate,
        "_structural_guards_v1",
        lambda: {"canonical_ingestion_guard": gate.FAIL, "canonical_product_root_guard": gate.FAIL},
    )
    result = gate.evaluate_service_1_capability_physical_coverage_gate_v1()

    assert result["verdict"] == gate.VERDICT_FAIL
    assert result["canonical_ingestion_guard"] == gate.FAIL
    assert result["canonical_product_root_guard"] == gate.FAIL
    assert "CANONICAL_INGESTION_GUARD_FAILED" in result["failures"]
    assert "CANONICAL_PRODUCT_ROOT_GUARD_FAILED" in result["failures"]


def test_git_diff_check_covers_untracked_gate_files_without_touching_index() -> None:
    repo = gate.Path(gate.__file__).resolve().parents[1]
    tracked = subprocess.run(
        [
            "git",
            "diff",
            "--check",
            "--",
            "tools/service_1_capability_physical_coverage_gate_v1.py",
            "tests/smartpyme/test_service_1_capability_physical_coverage_gate_v1.py",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert tracked.returncode == 0, tracked.stdout + tracked.stderr

    for relative in (
        "tools/service_1_capability_physical_coverage_gate_v1.py",
        "tests/smartpyme/test_service_1_capability_physical_coverage_gate_v1.py",
    ):
        result = subprocess.run(
            ["git", "diff", "--no-index", "--check", "--", "NUL", str(repo / relative)],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode in {0, 1}, result.stdout + result.stderr
        assert result.stdout == ""
        assert "trailing whitespace" not in result.stderr.lower()
        assert "space before tab" not in result.stderr.lower()
