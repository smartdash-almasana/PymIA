from __future__ import annotations

from pymia.smartpyme.service_2_reconciliation_match_candidates_v1 import (
    DEFAULT_OPTIONS,
    build_reconciliation_match_candidates_v1,
)


def test_exact_match_by_date_and_amount() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[{"id": "b1", "fecha": "2026-06-01", "importe": 1000, "descripcion": "Cobro"}],
        internal_movements=[{"id": "i1", "fecha": "2026-06-01", "importe": 1000, "descripcion": "Cobro"}],
    )

    assert result["status"] == "READY_FOR_HUMAN_REVIEW"
    assert result["matches_exactos"] == [
        {
            "banco_id": "b1",
            "interno_id": "i1",
            "criterio": "same_date_same_amount",
            "confianza": 1.0,
        }
    ]


def test_probable_match_by_near_date_and_same_amount() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[{"id": "b1", "fecha": "2026-06-03", "importe": 1000}],
        internal_movements=[{"id": "i1", "fecha": "2026-06-01", "importe": 1000}],
    )

    assert result["status"] == "PARTIAL_MATCHES_FOUND"
    assert result["matches_probables"][0]["criterio"] == "near_date_same_amount"
    assert result["matches_probables"][0]["diferencias"] == {"dias": 2}


def test_amount_difference_with_compatible_date() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[{"id": "b1", "fecha": "2026-06-01", "importe": 1000}],
        internal_movements=[{"id": "i1", "fecha": "2026-06-01", "importe": 990}],
    )

    assert result["status"] == "PARTIAL_MATCHES_FOUND"
    assert result["diferencias_importe"] == [
        {
            "banco_id": "b1",
            "interno_id": "i1",
            "criterio": "same_date_different_amount",
            "diferencias": {
                "importe_banco": 1000.0,
                "importe_interno": 990.0,
                "diferencia_absoluta": 10.0,
            },
            "requires_human_review": True,
        }
    ]


def test_date_difference_with_compatible_amount() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[{"id": "b1", "fecha": "2026-06-04", "importe": 1000}],
        internal_movements=[{"id": "i1", "fecha": "2026-06-01", "importe": 1000}],
    )

    assert result["diferencias_fecha"] == [
        {
            "banco_id": "b1",
            "interno_id": "i1",
            "criterio": "same_amount_different_date",
            "diferencias": {"dias": 3},
            "requires_human_review": True,
        }
    ]


def test_bank_without_internal_candidate() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[{"id": "b1", "fecha": "2026-06-01", "importe": 1000}],
        internal_movements=[],
    )

    assert result["status"] == "NO_CANDIDATES_FOUND"
    assert result["banco_sin_imputar"][0]["id"] == "b1"


def test_internal_without_bank_candidate() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[],
        internal_movements=[{"id": "i1", "fecha": "2026-06-01", "importe": 1000}],
    )

    assert result["status"] == "NO_CANDIDATES_FOUND"
    assert result["interno_sin_banco"][0]["id"] == "i1"


def test_invalid_input_blocks() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements={"fecha": "2026-06-01", "importe": 1000},
        internal_movements=[],
    )

    assert result["status"] == "BLOCKED_BY_INVALID_INPUTS"
    assert result["faltantes_evidencia"][0]["reason"] == "movements_must_be_a_list"


def test_duplicates_are_not_hidden() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[
            {"id": "b1", "fecha": "2026-06-01", "importe": 1000},
            {"id": "b2", "fecha": "2026-06-01", "importe": 1000},
        ],
        internal_movements=[{"id": "i1", "fecha": "2026-06-01", "importe": 1000}],
    )

    assert result["matches_exactos"] == [
        {
            "banco_id": "b1",
            "interno_id": "i1",
            "criterio": "same_date_same_amount",
            "confianza": 1.0,
        },
        {
            "banco_id": "b2",
            "interno_id": "i1",
            "criterio": "same_date_same_amount",
            "confianza": 1.0,
        },
    ]


def test_requires_human_review_is_always_true() -> None:
    ok_result = build_reconciliation_match_candidates_v1(
        bank_movements=[{"id": "b1", "fecha": "2026-06-01", "importe": 1000}],
        internal_movements=[{"id": "i1", "fecha": "2026-06-01", "importe": 1000}],
    )
    blocked_result = build_reconciliation_match_candidates_v1(
        bank_movements=None,
        internal_movements=[],
    )

    assert ok_result["requires_human_review"] is True
    assert blocked_result["requires_human_review"] is True


def test_output_is_deterministic() -> None:
    bank = [
        {"id": "b1", "fecha": "2026-06-01", "importe": 1000},
        {"id": "b2", "fecha": "2026-06-02", "importe": 2000},
    ]
    internal = [
        {"id": "i1", "fecha": "2026-06-01", "importe": 1000},
        {"id": "i2", "fecha": "2026-06-03", "importe": 2000},
    ]

    first = build_reconciliation_match_candidates_v1(bank, internal)
    second = build_reconciliation_match_candidates_v1(bank, internal)

    assert first == second


def test_no_definitive_reconciliation_claims() -> None:
    result = build_reconciliation_match_candidates_v1([], [])
    forbidden_blob = " ".join(result["forbidden_claims"]).lower()
    status_blob = str(result["status"]).lower()

    assert "conciliacion definitiva" in forbidden_blob
    assert "certifica" in forbidden_blob
    assert "conciliated" not in status_blob
    assert "certified" not in status_blob
    assert "audited" not in status_blob


def test_thresholds_are_explicit_and_overridable() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[{"id": "b1", "fecha": "2026-06-05", "importe": 1000}],
        internal_movements=[{"id": "i1", "fecha": "2026-06-01", "importe": 1000}],
        options={"fecha_cercana_dias": 5, "confianza_probable_minima": 0.7},
    )

    assert result["options_used"]["fecha_cercana_dias"] == 5
    assert result["options_used"]["confianza_probable_minima"] == 0.7
    assert result["options_used"]["importe_tolerancia_absoluta"] == DEFAULT_OPTIONS["importe_tolerancia_absoluta"]
    assert result["matches_probables"][0]["confianza"] == 0.7
