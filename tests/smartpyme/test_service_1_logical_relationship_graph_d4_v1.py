from __future__ import annotations

from copy import deepcopy

from pymia.smartpyme.service_1_logical_relationship_graph_v1 import (
    CARDINALITY_MANY_TO_MANY,
    CARDINALITY_MANY_TO_ONE,
    CARDINALITY_ONE_TO_ONE,
    FANOUT_RISK,
    FANOUT_SAFE_LOOKUP,
    FANOUT_UNRESOLVED,
    PATH_NO_PATH,
    STATE_RESOLVED,
    STATE_UNRESOLVED,
    STATUS_READY,
    STATUS_UNRESOLVED,
    TABLE_MATCH_REF_RE,
    build_service_1_logical_relationship_graph_v1,
)
from pymia.smartpyme.service_1_owner_relationship_confirmation_event_v1 import (
    build_service_1_owner_relationship_confirmation_event_v1,
)


def _candidate(
    table_ref: str,
    *,
    sheet: str = "Data",
    region: str = "region:1",
    columns: tuple[str, ...] = ("id", "value"),
    structural_signature: str | None = None,
) -> dict:
    signature = structural_signature or f"ltf_{table_ref.replace(':', '_')}"
    return {
        "candidate_id": table_ref,
        "logical_table_id": table_ref,
        "table_key": table_ref,
        "workbook_ref": "january.xlsx",
        "source_region_refs": [f"{sheet}:{region}"],
        "source_sheet_refs": [sheet],
        "structural_signature": signature,
        "grain_state": "RESOLVED",
        "grain_candidate": {"kind": "ROW_KEYED_BY_CANDIDATE", "key_refs": [f"{table_ref}.id"]},
        "primary_key_candidates": [
            {
                "column_refs": [f"{table_ref}.id"],
                "key_kind": "SINGLE_COLUMN",
                "candidate_primary_key": True,
                "authoritative": False,
            }
        ],
        "unique_key_candidates": [],
        "provenance": {
            "sheet_ref": sheet,
            "region_ref": f"{sheet}:{region}",
            "structural_payload": {
                "columns": [
                    {
                        "normalized_header": column,
                        "inferred_type": "number" if column in {"id", "amount", "qty"} else "text",
                    }
                    for column in columns
                ]
            },
        },
        "runtime_authorized": False,
        "tool_execution_authorized": False,
        "product_ready": False,
        "delivery_authorized": False,
        "diagnosis_generated": False,
    }


def _evidence(
    left: str,
    right: str,
    cardinality: str,
    *,
    ref: str | None = None,
    candidate_foreign_key: bool | None = True,
) -> dict:
    result = {
        "relationship_ref": ref or f"{left}->{right}",
        "left_column_ref": left,
        "right_column_ref": right,
        "relationship_kind": cardinality,
        "evidence_refs": [f"ev:{left}->{right}"],
        "left_value_coverage": 1.0,
        "right_value_coverage": 1.0,
        "intersection_cardinality": 2,
    }
    if candidate_foreign_key is not None:
        result["candidate_foreign_key"] = candidate_foreign_key
        result["candidate_primary_key_ref"] = right
    return result


def _graph(candidates: list[dict], evidence: list[dict], *, filename: str = "january.xlsx", events=()) -> dict:
    payload = deepcopy(candidates)
    for item in payload:
        item["workbook_ref"] = filename
    return build_service_1_logical_relationship_graph_v1(
        logical_table_candidates=payload,
        relationship_evidence=evidence,
        owner_confirmation_events=events,
    )


def test_many_to_one_relationship_is_resolved_from_profiler_evidence() -> None:
    candidates = [
        _candidate("table:events", columns=("account_id", "amount")),
        _candidate("table:accounts", columns=("id", "name"), region="region:2"),
    ]
    result = _graph(candidates, [_evidence("Data.account_id", "Data.id", CARDINALITY_MANY_TO_ONE)])

    assert result["status"] == STATUS_READY
    assert result["relationships"][0]["cardinality"] == CARDINALITY_MANY_TO_ONE
    assert result["relationships"][0]["state"] == STATE_RESOLVED


def test_one_to_one_relationship_is_resolved() -> None:
    candidates = [
        _candidate("table:left", columns=("id", "value")),
        _candidate("table:right", sheet="Lookup", columns=("id", "value"), region="region:2"),
    ]
    result = _graph(candidates, [_evidence("Data.id", "Lookup.id", CARDINALITY_ONE_TO_ONE)])

    assert result["status"] == STATUS_READY
    assert result["relationships"][0]["state"] == STATE_RESOLVED


def test_many_to_many_is_not_lookup_safe() -> None:
    candidates = [
        _candidate("table:left", columns=("left_id", "value")),
        _candidate("table:right", columns=("right_id", "value"), region="region:2"),
    ]
    result = _graph(
        candidates,
        [_evidence("Data.left_id", "Data.right_id", CARDINALITY_MANY_TO_MANY, candidate_foreign_key=None)],
    )

    assert result["relationships"][0]["cardinality"] == CARDINALITY_MANY_TO_MANY
    assert result["relationships"][0]["fanout_risk"] == FANOUT_RISK
    assert result["fanout_certificate"]["fanout_risk"] == FANOUT_RISK


def test_same_column_name_without_profiler_evidence_does_not_create_join() -> None:
    candidates = [
        _candidate("table:left", columns=("id", "value")),
        _candidate("table:right", columns=("id", "value"), region="region:2"),
    ]
    result = _graph(candidates, [])

    assert result["relationships"] == []


def test_two_logical_tables_in_one_sheet_map_by_region_and_column() -> None:
    candidates = [
        _candidate("table:one", region="region:1", columns=("event_id", "account_id")),
        _candidate("table:two", region="region:2", columns=("id", "name")),
    ]
    result = _graph(candidates, [_evidence("Data.account_id", "Data.id", CARDINALITY_MANY_TO_ONE)])

    relation = result["relationships"][0]
    assert relation["left_logical_table_ref"] == "table:one"
    assert relation["right_logical_table_ref"] == "table:two"


def test_ambiguous_endpoint_fails_closed() -> None:
    candidates = [
        _candidate("table:one", region="region:1", columns=("id", "value")),
        _candidate("table:two", region="region:2", columns=("id", "name")),
    ]
    result = _graph(candidates, [_evidence("Data.id", "Data.id", CARDINALITY_ONE_TO_ONE)])

    assert result["status"] == STATUS_UNRESOLVED
    assert result["relationships"][0]["state"] == STATE_UNRESOLVED
    assert "AMBIGUOUS" in result["relationships"][0]["provenance"]["blocked_reason"]


def test_owner_confirmation_is_evidence_only() -> None:
    candidates = [
        _candidate("table:events", columns=("account_id", "amount")),
        _candidate("table:accounts", columns=("id", "name"), region="region:2"),
    ]
    evidence = [_evidence("Data.account_id", "Data.id", CARDINALITY_MANY_TO_ONE)]
    event = build_service_1_owner_relationship_confirmation_event_v1(
        case_id="case-1",
        file_ref="january.xlsx",
        left_sheet_ref="Data",
        left_column_ref="account_id",
        right_sheet_ref="Data",
        right_column_ref="id",
        relationship_kind=CARDINALITY_MANY_TO_ONE,
        owner_answer="The account id points to the account table.",
        question_ref="question:relationship:1",
        timestamp="2026-08-21T00:00:00Z",
    )
    result = _graph(candidates, evidence, events=[event])

    relation = result["relationships"][0]
    assert relation["owner_confirmation_ref"]
    assert relation["join_execution_authorized"] is False
    assert result["join_execution_authorized"] is False


def test_owner_contradiction_fails_closed() -> None:
    candidates = [
        _candidate("table:events", columns=("account_id", "amount")),
        _candidate("table:accounts", columns=("id", "name"), region="region:2"),
    ]
    event = build_service_1_owner_relationship_confirmation_event_v1(
        case_id="case-1",
        file_ref="january.xlsx",
        left_sheet_ref="Data",
        left_column_ref="account_id",
        right_sheet_ref="Data",
        right_column_ref="id",
        relationship_kind=CARDINALITY_ONE_TO_ONE,
        owner_answer="The relationship is one-to-one.",
        question_ref="question:relationship:1",
        timestamp="2026-08-21T00:00:00Z",
    )
    result = _graph(candidates, [_evidence("Data.account_id", "Data.id", CARDINALITY_MANY_TO_ONE)], events=[event])

    assert result["status"] == STATUS_UNRESOLVED
    assert result["relationships"][0]["provenance"]["blocked_reason"] == "OWNER_CONTRADICTS_PHYSICAL_EVIDENCE"


def test_fanout_star_is_risk() -> None:
    candidates = [
        _candidate("table:a", columns=("b_id_a", "value")),
        _candidate("table:b", columns=("id", "value"), region="region:2"),
        _candidate("table:c", columns=("b_id_c", "value"), region="region:3"),
    ]
    evidence = [
        _evidence("Data.b_id_a", "Data.id", CARDINALITY_MANY_TO_ONE, ref="a->b"),
        _evidence("Data.b_id_c", "Data.id", CARDINALITY_MANY_TO_ONE, ref="c->b"),
    ]
    result = _graph(candidates, evidence)

    assert result["fanout_certificate"]["fanout_risk"] == FANOUT_RISK
    assert result["fanout_certificate"]["risk_paths"]


def test_lookup_chain_is_safe() -> None:
    candidates = [
        _candidate("table:a", columns=("b_id", "value")),
        _candidate("table:b", columns=("id", "c_id"), region="region:2"),
        _candidate("table:c", columns=("customer_id", "value"), region="region:3"),
    ]
    evidence = [
        _evidence("Data.b_id", "Data.id", CARDINALITY_MANY_TO_ONE, ref="a->b"),
        _evidence("Data.c_id", "Data.customer_id", CARDINALITY_MANY_TO_ONE, ref="b->c"),
    ]
    result = _graph(candidates, evidence)

    assert result["fanout_certificate"]["fanout_risk"] == FANOUT_SAFE_LOOKUP
    assert result["fanout_certificate"]["safe_paths"]


def test_disconnected_graph_has_no_path_and_is_unresolved() -> None:
    candidates = [
        _candidate("table:a", columns=("id", "b_id")),
        _candidate("table:b", columns=("id", "value"), region="region:2"),
        _candidate("table:c", columns=("id", "value"), region="region:3"),
    ]
    result = _graph(candidates, [_evidence("Data.b_id", "Data.id", CARDINALITY_MANY_TO_ONE)])

    assert result["fanout_certificate"]["path_state"] == PATH_NO_PATH
    assert result["status"] == STATUS_UNRESOLVED


def test_graph_identity_is_stable_for_reorder_and_filename_change() -> None:
    candidates = [
        _candidate("table:a", columns=("id", "b_id")),
        _candidate("table:b", columns=("id", "value"), region="region:2"),
    ]
    evidence = [_evidence("Data.b_id", "Data.id", CARDINALITY_MANY_TO_ONE)]
    first = _graph(candidates, evidence, filename="january.xlsx")
    second = _graph(list(reversed(candidates)), list(reversed(evidence)), filename="renamed.xlsx")

    assert first["graph_fingerprint"] == second["graph_fingerprint"]
    assert first["graph_ref"] == second["graph_ref"]
    assert not TABLE_MATCH_REF_RE.fullmatch("table:a")


def test_profiler_relationship_evidence_is_consumed_without_join_execution() -> None:
    candidates = [
        _candidate("table:events", columns=("account_id", "amount")),
        _candidate("table:accounts", columns=("id", "name"), region="region:2"),
    ]
    evidence = _evidence("Data.account_id", "Data.id", CARDINALITY_MANY_TO_ONE)
    result = build_service_1_logical_relationship_graph_v1(
        logical_table_candidates=candidates,
        workbook_profile={"relationships": [evidence]},
    )

    assert result["relationships"][0]["state"] == STATE_RESOLVED
    assert result["relationships"][0]["join_execution_authorized"] is False


def test_filename_change_only_preserves_graph_identity() -> None:
    candidates = [
        _candidate("table:events", columns=("account_id", "amount")),
        _candidate("table:accounts", columns=("id", "name"), region="region:2"),
    ]
    evidence = [_evidence("Data.account_id", "Data.id", CARDINALITY_MANY_TO_ONE)]

    first = _graph(candidates, evidence, filename="january.xlsx")
    second = _graph(candidates, evidence, filename="renamed.xlsx")

    assert first["graph_fingerprint"] == second["graph_fingerprint"]
