from __future__ import annotations

import json
from pathlib import Path

_ALLOWED = {
    "PRODUCTIVE",
    "SUPPORT_NECESSARY",
    "EXPERIMENTAL_FROZEN",
    "OBSOLETE_ELIMINABLE",
}
_SPECIAL = {
    "accounting_human_review_gate_v1",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _registry() -> dict:
    path = _repo_root() / "docs" / "service_1_module_disposition.v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _live_modules() -> set[str]:
    root = _repo_root() / "pymia" / "smartpyme"
    return {
        path.stem
        for path in root.glob("*.py")
        if path.stem.startswith("service_1_") or path.stem in _SPECIAL
    }


def test_registry_covers_every_service_1_module_exactly_once() -> None:
    payload = _registry()
    names = [item["module"] for item in payload["modules"]]
    assert len(names) == len(set(names))
    assert set(names) == _live_modules()
    assert payload["total_modules"] == len(names)


def test_registry_uses_only_governed_dispositions() -> None:
    payload = _registry()
    assert {item["disposition"] for item in payload["modules"]} <= _ALLOWED
    counts = {key: 0 for key in _ALLOWED}
    for item in payload["modules"]:
        counts[item["disposition"]] += 1
    assert payload["counts"] == {key: value for key, value in sorted(counts.items()) if value}


def test_canonical_root_is_productive_and_closed_over_internal_imports() -> None:
    payload = _registry()
    by_name = {item["module"]: item for item in payload["modules"]}
    root = payload["canonical_product_root"]
    assert by_name[root]["disposition"] == "PRODUCTIVE"

    productive = {
        name for name, item in by_name.items() if item["disposition"] == "PRODUCTIVE"
    }
    for name in productive:
        for dependency in by_name[name]["imports_service_1"]:
            assert dependency in productive, (name, dependency)


def test_frozen_or_obsolete_modules_are_not_in_canonical_root_closure() -> None:
    payload = _registry()
    for item in payload["modules"]:
        if item["disposition"] in {"EXPERIMENTAL_FROZEN", "OBSOLETE_ELIMINABLE"}:
            assert item["canonical_root_reachable"] is False


def test_registry_keeps_active_surface_bounded_during_cleanup() -> None:
    payload = _registry()
    productive = payload["counts"].get("PRODUCTIVE", 0)
    support = payload["counts"].get("SUPPORT_NECESSARY", 0)
    active = productive + support

    # Cleanup cycles delete frozen/obsolete modules by design, so ratio-based
    # denominator guards become noisier as cleanup succeeds. CYCLE_016 and CYCLE_017 correct
    # retained support modules that had been misclassified as frozen; these
    # are registry truth corrections, not runtime surface expansions.
    assert productive <= 15
    assert support <= 35
    assert active <= 50

def test_registry_has_no_known_obsolete_eliminable_modules() -> None:
    payload = _registry()
    assert payload["counts"].get("OBSOLETE_ELIMINABLE", 0) == 0
