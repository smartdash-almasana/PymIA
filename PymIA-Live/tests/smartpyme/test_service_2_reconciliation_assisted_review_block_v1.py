from __future__ import annotations

import inspect

from pymia.smartpyme import service_2_reconciliation_assisted_review_block_v1 as module
from pymia.smartpyme.service_2_reconciliation_assisted_review_block_v1 import (
    build_reconciliation_assisted_review_block_v1,
)


def test_uses_match_candidates_and_preserves_source_result(monkeypatch) -> None:
    source_result = {
        "status": "READY_FOR_HUMAN_REVIEW",
        "matches_exactos": [{"banco_id": "b1", "interno_id": "i1"}],
        "matches_probables": [],
        "banco_sin_imputar": [],
        "interno_sin_banco": [],
        "diferencias_importe": [],
        "diferencias_fecha": [],
        "faltantes_evidencia": [],
        "requires_human_review": True,
    }
    calls: list[dict[str, object]] = []

    def fake_match_candidates(bank_movements, internal_movements, options=None):
        calls.append(
            {
                "bank_movements": bank_movements,
                "internal_movements": internal_movements,
                "options": options,
            }
        )
        return source_result

    monkeypatch.setattr(module, "build_reconciliation_match_candidates_v1", fake_match_candidates)

    result = build_reconciliation_assisted_review_block_v1(
        [{"id": "b1"}],
        [{"id": "i1"}],
        options={"fecha_cercana_dias": 1},
    )

    assert calls == [
        {
            "bank_movements": [{"id": "b1"}],
            "internal_movements": [{"id": "i1"}],
            "options": {"fecha_cercana_dias": 1},
        }
    ]
    assert result["source_result"] is source_result
    assert result["source_status"] == "READY_FOR_HUMAN_REVIEW"


def test_exact_matches_generate_ready_for_assisted_review() -> None:
    result = build_reconciliation_assisted_review_block_v1(
        [{"id": "b1", "fecha": "2026-06-01", "importe": 1000}],
        [{"id": "i1", "fecha": "2026-06-01", "importe": 1000}],
    )

    assert result["status"] == "READY_FOR_ASSISTED_REVIEW"
    assert result["exact_matches_summary"]["count"] == 1
    assert result["requires_human_review"] is True


def test_partial_matches_generate_partial_review_ready() -> None:
    result = build_reconciliation_assisted_review_block_v1(
        [{"id": "b1", "fecha": "2026-06-03", "importe": 1000}],
        [{"id": "i1", "fecha": "2026-06-01", "importe": 1000}],
    )

    assert result["status"] == "PARTIAL_REVIEW_READY"
    assert result["probable_matches_summary"]["count"] == 1
    assert result["date_differences_summary"]["count"] == 1


def test_no_candidates_generate_no_reviewable_candidates() -> None:
    result = build_reconciliation_assisted_review_block_v1(
        [{"id": "b1", "fecha": "2026-06-01", "importe": 1000}],
        [],
    )

    assert result["status"] == "NO_REVIEWABLE_CANDIDATES"
    assert result["bank_pending_summary"]["count"] == 1


def test_missing_evidence_generates_needs_more_evidence() -> None:
    result = build_reconciliation_assisted_review_block_v1(
        [{"id": "b1", "fecha": "", "importe": 1000}],
        [],
    )

    assert result["status"] == "NEEDS_MORE_EVIDENCE"
    assert result["missing_evidence_summary"]["count"] == 1


def test_invalid_input_generates_blocked_by_invalid_inputs() -> None:
    result = build_reconciliation_assisted_review_block_v1(
        {"id": "b1", "fecha": "2026-06-01", "importe": 1000},
        [],
    )

    assert result["status"] == "BLOCKED_BY_INVALID_INPUTS"
    assert result["missing_evidence_summary"]["items"][0]["reason"] == "movements_must_be_a_list"


def test_requires_human_review_is_always_true() -> None:
    ready = build_reconciliation_assisted_review_block_v1(
        [{"id": "b1", "fecha": "2026-06-01", "importe": 1000}],
        [{"id": "i1", "fecha": "2026-06-01", "importe": 1000}],
    )
    blocked = build_reconciliation_assisted_review_block_v1(None, [])

    assert ready["requires_human_review"] is True
    assert blocked["requires_human_review"] is True


def test_review_summary_counts_all_sections() -> None:
    result = build_reconciliation_assisted_review_block_v1(
        [
            {"id": "b-exact", "fecha": "2026-06-01", "importe": 1000},
            {"id": "b-probable", "fecha": "2026-06-04", "importe": 2000},
            {"id": "b-amount", "fecha": "2026-06-05", "importe": 3000},
            {"id": "b-pending", "fecha": "2026-06-20", "importe": 4000},
            {"id": "b-missing", "fecha": None, "importe": 5000},
        ],
        [
            {"id": "i-exact", "fecha": "2026-06-01", "importe": 1000},
            {"id": "i-probable", "fecha": "2026-06-02", "importe": 2000},
            {"id": "i-amount", "fecha": "2026-06-05", "importe": 2990},
            {"id": "i-pending", "fecha": "2026-06-21", "importe": 6000},
            {"id": "i-missing", "fecha": "2026-06-22", "importe": "bad"},
        ],
    )

    assert result["review_summary"] == {
        "matches_exactos": 1,
        "matches_probables": 1,
        "banco_sin_imputar": 1,
        "interno_sin_banco": 1,
        "diferencias_importe": 1,
        "diferencias_fecha": 1,
        "faltantes_evidencia": 2,
    }
    assert "1 matches exactos" in result["executive_summary"]
    assert "2 faltantes de evidencia" in result["executive_summary"]


def test_next_steps_change_by_status() -> None:
    blocked = build_reconciliation_assisted_review_block_v1(None, [])
    missing = build_reconciliation_assisted_review_block_v1([{"id": "b1", "fecha": "", "importe": 1}], [])
    empty = build_reconciliation_assisted_review_block_v1([], [])
    partial = build_reconciliation_assisted_review_block_v1(
        [{"id": "b1", "fecha": "2026-06-03", "importe": 1000}],
        [{"id": "i1", "fecha": "2026-06-01", "importe": 1000}],
    )
    ready = build_reconciliation_assisted_review_block_v1(
        [{"id": "b1", "fecha": "2026-06-01", "importe": 1000}],
        [{"id": "i1", "fecha": "2026-06-01", "importe": 1000}],
    )

    assert "Corregir la estructura" in blocked["next_steps"][0]
    assert "Completar fecha" in missing["next_steps"][0]
    assert "Revisar criterio" in empty["next_steps"][0]
    assert "matches probables" in partial["next_steps"][0]
    assert "matches exactos" in ready["next_steps"][0]


def test_caveats_contain_no_final_reconciliation_no_audit_and_human_review() -> None:
    result = build_reconciliation_assisted_review_block_v1([], [])
    caveats_blob = " ".join(result["caveats"]).lower()

    assert "no es conciliación definitiva" in caveats_blob
    assert "no reemplaza revisión contable" in caveats_blob
    assert "requiere revisión humana" in caveats_blob
    assert "no detecta fraude" in caveats_blob


def test_forbidden_claims_do_not_appear_as_status_or_positive_conclusion() -> None:
    result = build_reconciliation_assisted_review_block_v1(
        [{"id": "b1", "fecha": "2026-06-01", "importe": 1000}],
        [{"id": "i1", "fecha": "2026-06-01", "importe": 1000}],
    )
    positive_blob = " ".join(
        [
            str(result["status"]),
            str(result["executive_summary"]),
            " ".join(result["next_steps"]),
        ]
    ).lower()

    assert "banco conciliado" not in positive_blob
    assert "conciliación cerrada" not in positive_blob
    assert "saldo real confirmado" not in positive_blob
    assert "auditoría" not in positive_blob
    assert "certificación" not in positive_blob


def test_output_is_deterministic() -> None:
    bank = [
        {"id": "b1", "fecha": "2026-06-01", "importe": 1000},
        {"id": "b2", "fecha": "2026-06-03", "importe": 2000},
    ]
    internal = [
        {"id": "i1", "fecha": "2026-06-01", "importe": 1000},
        {"id": "i2", "fecha": "2026-06-01", "importe": 2000},
    ]

    assert build_reconciliation_assisted_review_block_v1(bank, internal) == build_reconciliation_assisted_review_block_v1(bank, internal)


def test_module_does_not_touch_or_import_service_1() -> None:
    source = inspect.getsource(module)

    assert "service_1" not in source.lower()


def test_module_has_no_io_or_heavy_file_dependencies() -> None:
    source = inspect.getsource(module).lower()

    assert "open(" not in source
    assert "pathlib" not in source
    assert ".write" not in source
    assert "pandas" not in source
    assert "openpyxl" not in source


def test_no_forbidden_statuses_are_used() -> None:
    source = inspect.getsource(module)

    assert "CONCILIATED" not in source
    assert "CERTIFIED" not in source
    assert "AUDITED" not in source
    assert "TAX_READY" not in source
