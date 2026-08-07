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
            "tipo_match": "MATCH_ATTRIBUTES_EXACT",
            "criterio": "same_date_same_amount",
            "evidencia": {
                "reference_match": False,
                "reference_conflict": False,
                "amount_match": True,
                "amount_delta": 0.0,
                "date_match": True,
                "date_delta_days": 0,
            },
        }
    ]


def test_probable_match_by_near_date_and_same_amount() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[{"id": "b1", "fecha": "2026-06-03", "importe": 1000}],
        internal_movements=[{"id": "i1", "fecha": "2026-06-01", "importe": 1000}],
    )

    assert result["status"] == "PARTIAL_MATCHES_FOUND"
    assert result["matches_probables"][0]["tipo_match"] == "MATCH_PROBABLE_DATE"
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
            "evidencia": {
                "reference_match": False,
                "reference_conflict": False,
                "amount_match": False,
                "amount_delta": 10.0,
                "date_match": True,
                "date_delta_days": 0,
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
            "evidencia": {
                "reference_match": False,
                "reference_conflict": False,
                "amount_match": True,
                "amount_delta": 0.0,
                "date_match": False,
                "date_delta_days": 3,
            },
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

    assert result["matches_exactos"] == []
    assert result["matches_ambiguos"][0]["tipo"] == "AMBIGUOUS"
    assert result["matches_ambiguos"][0]["cardinalidad"] == "N:1"
    assert result["matches_ambiguos"][0]["candidate_count"] == 2
    assert [item["id"] for item in result["banco_sin_imputar"]] == ["b1", "b2"]
    assert [item["id"] for item in result["interno_sin_banco"]] == ["i1"]


def test_composite_reference_and_total_build_one_to_many_candidate() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[
            {
                "id": "G0",
                "fecha": "2026-09-03",
                "importe": 33563,
                "referencia": "REF050+REF051",
            }
        ],
        internal_movements=[
            {
                "id": "F00050",
                "fecha": "2026-09-03",
                "importe": 16713,
                "referencia": "REF050",
            },
            {
                "id": "F00051",
                "fecha": "2026-07-16",
                "importe": 16850,
                "referencia": "REF051",
            },
        ],
    )

    assert result["matches_exactos"] == [
        {
            "banco_ids": ["G0"],
            "interno_ids": ["F00050", "F00051"],
            "tipo_match": "MATCH_REFERENCE_AGGREGATE",
            "cardinalidad": "1:N",
            "criterio": "composite_reference_sum",
            "evidencia": {
                "reference_members_match": True,
                "amount_match": True,
                "amount_delta": 0.0,
                "importe_banco_total": 33563.0,
                "importe_interno_total": 33563.0,
            },
            "requires_human_review": True,
        }
    ]
    assert result["banco_sin_imputar"] == []
    assert result["interno_sin_banco"] == []


def test_repeated_reference_and_total_build_many_to_one_candidate() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[
            {
                "id": "PA",
                "fecha": "2026-07-21",
                "importe": 8767.5,
                "referencia": "REF056",
            },
            {
                "id": "PB",
                "fecha": "2026-07-22",
                "importe": 8767.5,
                "referencia": "REF056",
            },
        ],
        internal_movements=[
            {
                "id": "F00056",
                "fecha": "2026-07-21",
                "importe": 17535,
                "referencia": "REF056",
            }
        ],
    )

    match = result["matches_exactos"][0]
    assert match["tipo_match"] == "MATCH_REFERENCE_AGGREGATE"
    assert match["cardinalidad"] == "N:1"
    assert match["banco_ids"] == ["PA", "PB"]
    assert match["interno_ids"] == ["F00056"]
    assert match["evidencia"]["amount_delta"] == 0.0
    assert match["requires_human_review"] is True
    assert result["diferencias_importe"] == []
    assert result["banco_sin_imputar"] == []
    assert result["interno_sin_banco"] == []


def test_overlapping_aggregate_candidates_abstain_instead_of_using_row_order() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[
            {
                "id": "b1",
                "fecha": "2026-07-21",
                "importe": 300,
                "referencia": "REF-A+REF-B",
            },
            {
                "id": "b2",
                "fecha": "2026-07-21",
                "importe": 300,
                "referencia": "REF-A+REF-B",
            },
        ],
        internal_movements=[
            {
                "id": "i1",
                "fecha": "2026-07-21",
                "importe": 100,
                "referencia": "REF-A",
            },
            {
                "id": "i2",
                "fecha": "2026-07-21",
                "importe": 200,
                "referencia": "REF-B",
            },
        ],
    )

    assert result["matches_exactos"] == []
    assert [item["id"] for item in result["banco_sin_imputar"]] == ["b1", "b2"]
    assert [item["id"] for item in result["interno_sin_banco"]] == ["i1", "i2"]


def test_identical_repeated_bank_row_is_explicit_duplicate_not_competing_match() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[
            {
                "id": "OP0001",
                "fecha": "2026-07-16",
                "importe": 10000,
                "referencia": "REF001",
            },
            {
                "id": "OP0001",
                "fecha": "2026-07-16",
                "importe": 10000,
                "referencia": "REF001",
            },
        ],
        internal_movements=[
            {
                "id": "F00001",
                "fecha": "2026-07-16",
                "importe": 10000,
                "referencia": "REF001",
            }
        ],
    )

    assert len(result["matches_exactos"]) == 1
    assert result["matches_exactos"][0]["banco_id"] == "OP0001"
    duplicate = result["matches_ambiguos"][0]
    assert duplicate["ambiguedad"] == "EXACT_DUPLICATE"
    assert duplicate["duplicado_id"] == "OP0001"
    assert duplicate["requires_human_review"] is True
    assert len(result["banco_sin_imputar"]) == 1
    assert result["banco_sin_imputar"][0]["duplicate_of"] == "OP0001"


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
        options={"fecha_cercana_dias": 5, "importe_tolerancia_absoluta": 0.5},
    )

    assert result["options_used"]["fecha_cercana_dias"] == 5
    assert result["options_used"]["importe_tolerancia_absoluta"] == 0.5
    assert result["options_used"]["importe_tolerancia_relativa"] == DEFAULT_OPTIONS["importe_tolerancia_relativa"]
    assert result["matches_probables"][0]["tipo_match"] == "MATCH_PROBABLE_DATE"


def test_reference_is_prioritized_over_same_date_same_amount_competitor() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[{"id": "b1", "fecha": "2026-06-01", "importe": 1000, "referencia": "OP-77"}],
        internal_movements=[
            {"id": "i-ref", "fecha": "2026-06-01", "importe": 1000, "referencia": " op-77 "},
            {"id": "i-other", "fecha": "2026-06-01", "importe": 1000, "referencia": "OP-99"},
        ],
    )

    assert result["matches_ambiguos"] == []
    assert result["matches_exactos"][0]["interno_id"] == "i-ref"
    assert result["matches_exactos"][0]["tipo_match"] == "MATCH_REFERENCE_EXACT"
    assert result["matches_exactos"][0]["evidencia"]["reference_match"] is True
    assert [item["id"] for item in result["interno_sin_banco"]] == ["i-other"]


def test_one_bank_to_two_internal_candidates_is_ambiguous() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[{"id": "b1", "fecha": "2026-06-01", "importe": 1000}],
        internal_movements=[
            {"id": "i1", "fecha": "2026-06-01", "importe": 1000},
            {"id": "i2", "fecha": "2026-06-01", "importe": 1000},
        ],
    )

    assert result["status"] == "PARTIAL_MATCHES_FOUND"
    assert result["matches_exactos"] == []
    assert result["matches_ambiguos"][0]["cardinalidad"] == "1:N"
    assert result["matches_ambiguos"][0]["candidate_count"] == 2
    assert [item["id"] for item in result["banco_sin_imputar"]] == ["b1"]
    assert [item["id"] for item in result["interno_sin_banco"]] == ["i1", "i2"]


def test_amount_difference_does_not_hide_unmatched_movements() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[{"id": "b1", "fecha": "2026-06-01", "importe": 1000}],
        internal_movements=[{"id": "i1", "fecha": "2026-06-01", "importe": 990}],
    )

    assert len(result["diferencias_importe"]) == 1
    assert [item["id"] for item in result["banco_sin_imputar"]] == ["b1"]
    assert [item["id"] for item in result["interno_sin_banco"]] == ["i1"]


def test_output_has_no_float_confidence_authority() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[{"id": "b1", "fecha": "2026-06-01", "importe": 1000}],
        internal_movements=[{"id": "i1", "fecha": "2026-06-01", "importe": 1000}],
        options={"confianza_exacta": 0.1, "confianza_probable_minima": 0.99},
    )

    def collect_keys(value: object) -> list[str]:
        if isinstance(value, dict):
            keys = [str(key) for key in value]
            for nested in value.values():
                keys.extend(collect_keys(nested))
            return keys
        if isinstance(value, list):
            keys: list[str] = []
            for nested in value:
                keys.extend(collect_keys(nested))
            return keys
        return []

    assert not [key for key in collect_keys(result) if "confianza" in key.lower() or "confidence" in key.lower()]
    assert result["matches_exactos"][0]["tipo_match"] == "MATCH_ATTRIBUTES_EXACT"


def test_many_to_many_collision_exposes_all_ambiguous_candidates() -> None:
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[
            {"id": "b1", "fecha": "2026-06-01", "importe": 1000},
            {"id": "b2", "fecha": "2026-06-01", "importe": 1000},
        ],
        internal_movements=[
            {"id": "i1", "fecha": "2026-06-01", "importe": 1000},
            {"id": "i2", "fecha": "2026-06-01", "importe": 1000},
        ],
    )

    ambiguous = result["matches_ambiguos"][0]
    assert ambiguous["tipo"] == "AMBIGUOUS"
    assert ambiguous["cardinalidad"] == "N:M"
    assert ambiguous["banco_ids"] == ["b1", "b2"]
    assert ambiguous["interno_ids"] == ["i1", "i2"]
    assert ambiguous["candidate_count"] == 4
    assert len(ambiguous["candidatos"]) == 4
    assert result["matches_exactos"] == []
