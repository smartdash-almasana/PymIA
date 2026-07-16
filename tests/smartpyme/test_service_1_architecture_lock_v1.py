from __future__ import annotations

import json
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _lock() -> dict:
    return json.loads((_repo_root() / "docs" / "service_1_architecture_lock.v1.json").read_text(encoding="utf-8"))


def _registry() -> dict:
    return json.loads((_repo_root() / "docs" / "service_1_module_disposition.v1.json").read_text(encoding="utf-8"))


def _registry_by_module() -> dict[str, dict]:
    return {item["module"]: item for item in _registry()["modules"]}


def test_architecture_lock_schema_and_authority_files_exist() -> None:
    root = _repo_root()
    lock = _lock()

    assert lock["schema_version"] == "SERVICE_1_ARCHITECTURE_LOCK_V1"
    assert lock["status"] == "ACTIVE"
    assert lock["cycle"] == "CYCLE_018_ARCHITECTURE_LOCK"
    assert (root / "docs" / "current" / "SERVICE_1_ARCHITECTURE_LOCK.md").exists()


def test_current_readme_indexes_architecture_lock() -> None:
    readme = (_repo_root() / "docs" / "current" / "README.md").read_text(encoding="utf-8")

    assert "SERVICE_1_ARCHITECTURE_LOCK.md" in readme
    assert "docs/current/SERVICE_1_ARCHITECTURE_LOCK.md" in readme


def test_official_entrypoint_and_product_root_are_exact() -> None:
    root = _repo_root()
    lock = _lock()
    official = lock["official_entrypoints"]

    assert official == [
        {
            "id": "service_1_product_cli",
            "path": "pymia/cli/service_1_product.py",
            "authority": "ONLY_OFFICIAL_USER_FACING_CLI",
        }
    ]
    assert (root / official[0]["path"]).exists()
    assert lock["canonical_product_root"] == {
        "module": "service_1_product_pipeline_v1",
        "path": "pymia/smartpyme/service_1_product_pipeline_v1.py",
        "authority": "ONLY_CANONICAL_PRODUCT_ROOT",
    }
    assert _registry()["canonical_product_root"] == "service_1_product_pipeline_v1"


def test_productive_nucleus_matches_registry_productive_closure() -> None:
    lock = _lock()
    by_module = _registry_by_module()
    registry_productive = {
        name for name, item in by_module.items() if item["disposition"] == "PRODUCTIVE"
    }

    assert set(lock["productive_nucleus_modules"]) == registry_productive
    for module in lock["productive_nucleus_modules"]:
        item = by_module[module]
        assert item["disposition"] == "PRODUCTIVE"
        assert item["canonical_root_reachable"] is True


def test_retained_support_decisions_are_support_not_product_roots() -> None:
    by_module = _registry_by_module()

    for decision in _lock()["retained_support_decisions"]:
        item = by_module[decision["module"]]
        assert decision["decision"] == "RETAIN_SUPPORT"
        assert item["disposition"] == "SUPPORT_NECESSARY"
        assert item["canonical_root_reachable"] is False


def test_transitional_runtime_bridge_is_support_but_not_authority() -> None:
    by_module = _registry_by_module()
    entries = _lock()["transitional_support_not_product_root"]

    assert [entry["module"] for entry in entries] == ["service_1_xlsx_runtime_bridge_v1"]
    item = by_module["service_1_xlsx_runtime_bridge_v1"]
    assert item["disposition"] == "SUPPORT_NECESSARY"
    assert item["canonical_root_reachable"] is False
    assert entries[0]["decision"] == "TRANSITIONAL_SUPPORT_NOT_PRODUCT_ROOT"


def test_all_remaining_frozen_modules_are_accounted_for_by_locked_clusters() -> None:
    lock = _lock()
    by_module = _registry_by_module()
    registry_frozen = {
        name for name, item in by_module.items() if item["disposition"] == "EXPERIMENTAL_FROZEN"
    }
    locked_frozen = set(lock["legacy_operator_cluster"]["modules"])
    locked_frozen |= set(lock["runtime_legacy_cluster"]["modules"])
    locked_frozen |= set(lock["frozen_laboratory_modules"])

    assert locked_frozen == registry_frozen
    for module in locked_frozen:
        assert by_module[module]["canonical_root_reachable"] is False


def test_non_authoritative_surfaces_are_not_official_entrypoints() -> None:
    root = _repo_root()
    lock = _lock()
    official_paths = {entry["path"] for entry in lock["official_entrypoints"]}

    for path in lock["non_authoritative_surfaces"]:
        assert path not in official_paths
        assert (root / path).exists()


def test_legacy_operator_shell_is_removed_and_shared_reentry_is_retained() -> None:
    root = _repo_root()
    lock = _lock()
    cluster = lock["legacy_operator_cluster"]

    assert cluster["entrypoint_path"] == "pymia/cli/service_1_operator.py"
    assert not (root / cluster["entrypoint_path"]).exists()
    assert cluster["decision"] == "REMOVED_OPERATOR_ONLY_SHELL_RETAIN_SHARED_RUNTIME_DEPENDENCIES"
    assert set(cluster["modules"]) == {
        "service_1_owner_answer_reentry_v1",
        "service_1_question_bundle_v1",
    }
    removed = set(cluster["removed_operator_only_modules"])
    assert "service_1_owner_reentry_bridge_v1" in removed
    assert "service_1_question_bundle_v1" not in removed
