from __future__ import annotations

import math

from tests.golden_replay_utils import canonical_normalize


def test_canonical_normalize_removes_nondeterministic_fields() -> None:
    payload = {
        "generated_at": "2026-01-01T00:00:00Z",
        "audit_id": "audit-123",
        "tenant_id": "tenant-a",
        "source_file": "archivo.xlsx",
        "audit_trail": {
            "validation_issues_count": 3,
            "source_evidence_count": 12,
        },
    }
    out = canonical_normalize(payload)

    assert "generated_at" not in out
    assert "audit_id" not in out
    assert out["tenant_id"] == "tenant-a"
    assert out["source_file"] == "archivo.xlsx"
    assert out["audit_trail"]["validation_issues_count"] == 3
    assert out["audit_trail"]["source_evidence_count"] == 12


def test_canonical_normalize_float_rules() -> None:
    payload = {
        "a": math.nan,
        "b": math.inf,
        "c": -math.inf,
        "d": 14.285714,
    }
    out = canonical_normalize(payload)

    assert out["a"] is None
    assert out["b"] is None
    assert out["c"] is None
    assert out["d"] == "14.2857"


def test_canonical_normalize_stable_nested_dict_order_and_list_order() -> None:
    payload = {
        "z": {"b": 2.0, "a": 1.0},
        "list_semantica": [
            {"finding_id": "f2", "severity": "high"},
            {"finding_id": "f1", "severity": "critical"},
        ],
    }
    out = canonical_normalize(payload)

    assert list(out.keys()) == ["list_semantica", "z"]
    assert list(out["z"].keys()) == ["a", "b"]
    assert out["z"]["a"] == "1.0000"
    assert out["z"]["b"] == "2.0000"

    # List order must be preserved for semantic replay.
    assert [x["finding_id"] for x in out["list_semantica"]] == ["f2", "f1"]

