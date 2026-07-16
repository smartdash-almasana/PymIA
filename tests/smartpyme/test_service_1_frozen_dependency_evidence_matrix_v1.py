from __future__ import annotations

import json
from pathlib import Path

OFFICIAL_CLI = "pymia/cli/service_1_product.py"
LEGACY_OPERATOR = "pymia/cli/service_1_operator.py"
RUNTIME_BRIDGE = "pymia/smartpyme/service_1_xlsx_runtime_bridge_v1.py"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_json(relative_path: str) -> dict:
    return json.loads((_repo_root() / relative_path).read_text(encoding="utf-8"))


def _iter_text_files() -> list[Path]:
    root = _repo_root()
    matrix_path = root / "docs" / "service_1_frozen_dependency_evidence_matrix.v1.json"
    paths: list[Path] = []
    for base in ("pymia", "tests", "docs"):
        for path in (root / base).rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".py", ".md", ".json"}:
                continue
            if path == matrix_path:
                continue
            paths.append(path)
    return sorted(paths)


def _rel(path: Path) -> str:
    return path.relative_to(_repo_root()).as_posix()


def _files_containing(token: str) -> list[str]:
    hits: list[str] = []
    for path in _iter_text_files():
        text = path.read_text(encoding="utf-8")
        if token in text:
            hits.append(_rel(path))
    return hits


def _bucket_hits(module: str, hits: list[str], module_path: str) -> dict[str, list[str]]:
    external = [path for path in hits if path != module_path]
    return {
        "official_cli_refs": sorted(path for path in external if path == OFFICIAL_CLI),
        "legacy_operator_refs": sorted(path for path in external if path == LEGACY_OPERATOR),
        "runtime_bridge_refs": sorted(path for path in external if path == RUNTIME_BRIDGE),
        "other_source_refs": sorted(
            path
            for path in external
            if path.startswith("pymia/")
            and path not in {OFFICIAL_CLI, LEGACY_OPERATOR, RUNTIME_BRIDGE}
        ),
        "test_refs": sorted(path for path in external if path.startswith("tests/")),
        "current_doc_refs": sorted(path for path in external if path.startswith("docs/current/")),
        "registry_refs": sorted(
            path
            for path in external
            if path
            in {
                "docs/service_1_module_disposition.v1.json",
                "docs/service_1_architecture_lock.v1.json",
            }
        ),
        "other_doc_refs": sorted(
            path
            for path in external
            if path.startswith("docs/")
            and not path.startswith("docs/current/")
            and path
            not in {
                "docs/service_1_module_disposition.v1.json",
                "docs/service_1_architecture_lock.v1.json",
            }
        ),
    }


def test_matrix_covers_current_frozen_modules_exactly() -> None:
    registry = _read_json("docs/service_1_module_disposition.v1.json")
    matrix = _read_json("docs/service_1_frozen_dependency_evidence_matrix.v1.json")

    frozen = {
        item["module"]
        for item in registry["modules"]
        if item["disposition"] == "EXPERIMENTAL_FROZEN"
    }
    matrix_modules = {entry["module"] for entry in matrix["entries"]}

    assert matrix["frozen_module_count"] == len(frozen)
    assert matrix_modules == frozen
    assert len(matrix["entries"]) == len(matrix_modules)


def test_matrix_references_are_recomputed_from_repo_text() -> None:
    matrix = _read_json("docs/service_1_frozen_dependency_evidence_matrix.v1.json")

    for entry in matrix["entries"]:
        hits = _files_containing(entry["module"])
        buckets = _bucket_hits(entry["module"], hits, entry["path"])
        assert entry["references"] == buckets
        assert entry["reference_counts"] == {key: len(value) for key, value in buckets.items()}


def test_matrix_matches_architecture_lock_cluster_membership() -> None:
    lock = _read_json("docs/service_1_architecture_lock.v1.json")
    matrix = _read_json("docs/service_1_frozen_dependency_evidence_matrix.v1.json")

    legacy = set(lock["legacy_operator_cluster"]["modules"])
    runtime = set(lock["runtime_legacy_cluster"]["modules"])
    laboratory = set(lock["frozen_laboratory_modules"])
    by_module = {entry["module"]: entry for entry in matrix["entries"]}

    assert legacy <= set(by_module)
    assert runtime <= set(by_module)
    assert laboratory <= set(by_module)

    for module in legacy:
        entry = by_module[module]
        if entry["references"]["legacy_operator_refs"]:
            assert entry["architecture_lock_decision"] == "LEGACY_OPERATOR_CLUSTER_CANDIDATE"

    for module in runtime:
        assert by_module[module]["architecture_lock_decision"] == "RUNTIME_LEGACY_CLUSTER_CANDIDATE"

    for module in laboratory:
        assert by_module[module]["architecture_lock_decision"] == "FROZEN_LABORATORY"


def test_no_frozen_module_is_referenced_by_official_cli() -> None:
    matrix = _read_json("docs/service_1_frozen_dependency_evidence_matrix.v1.json")

    assert all(not entry["references"]["official_cli_refs"] for entry in matrix["entries"])
    assert matrix["decision_counts"].get("BLOCKED_PRODUCT_CLI_REF", 0) == 0


def test_manual_review_resolution_is_preserved_after_runtime_legacy_removal() -> None:
    matrix = _read_json("docs/service_1_frozen_dependency_evidence_matrix.v1.json")

    assert "NEEDS_MANUAL_REVIEW" not in matrix["decision_counts"]
    assert matrix["resolved_manual_review"]["resolved_count"] == 5
    retired = {entry["cycle"]: entry for entry in matrix.get("removed_clusters", [])}
    assert "CYCLE_025_REMOVE_LEGACY_OPERATOR_CLI_AND_OPERATOR_ONLY_REENTRY_SHELL" in retired
    assert "CYCLE_028_REMOVE_TRANSITIONAL_RUNTIME_BRIDGE_AND_RUNTIME_LEGACY_CLUSTER" in retired


def test_decision_counts_sum_to_frozen_module_count_without_manual_review() -> None:
    matrix = _read_json("docs/service_1_frozen_dependency_evidence_matrix.v1.json")

    assert sum(matrix["decision_counts"].values()) == matrix["frozen_module_count"]
    assert matrix["decision_counts"] == {}
