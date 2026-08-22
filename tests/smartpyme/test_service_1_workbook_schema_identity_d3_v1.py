from __future__ import annotations

from copy import deepcopy

from pymia.smartpyme.service_1_workbook_schema_identity_v1 import (
    COLUMN_ORDER_POLICY,
    DRIFT_COMPATIBLE_DELTA,
    DRIFT_IDENTICAL,
    DRIFT_MATERIAL,
    DRIFT_UNRESOLVED,
    GRAIN_UNRESOLVED,
    STATUS_READY,
    TABLE_MATCH_UNRESOLVED,
    UNKNOWN_FAMILY,
    build_service_1_workbook_schema_delta_v1,
    build_service_1_workbook_schema_identity_v1,
)
from pymia.smartpyme.service_1_structural_compatibility_v1 import (
    build_service_1_structural_digest_v1,
)


def _candidate(
    table_key: str = "table:orders",
    *,
    columns: list[tuple[str, str]] | None = None,
    key_refs: list[str] | None = None,
    grain_state: str = "RESOLVED",
    grain_refs: list[str] | None = None,
    filename: str = "january.xlsx",
    business_values: object | None = None,
) -> dict:
    columns = columns or [("id", "number"), ("amount", "number")]
    key_refs = key_refs or ["id"]
    grain_refs = grain_refs or key_refs
    structural_columns = [
        {
            "position": position,
            "normalized_header": header,
            "inferred_type": inferred_type,
            "nullability_class": "NONE",
            "uniqueness_class": "UNIQUE" if header in key_refs else "DUPLICATED",
            "candidate_primary_key": header in key_refs,
        }
        for position, (header, inferred_type) in enumerate(columns)
    ]
    primary = {
        "column_refs": [f"region.{ref}" for ref in key_refs],
        "key_kind": "COMPOSITE_UNIQUE" if len(key_refs) > 1 else "SINGLE_COLUMN",
        "candidate_primary_key": True,
        "evidence_refs": ["evidence:key"],
    }
    candidate = {
        "candidate_id": table_key,
        "logical_table_id": table_key,
        "table_key": table_key,
        "workbook_ref": filename,
        "source_region_refs": ["Sheet:region:1"],
        "source_sheet_refs": ["Sheet"],
        "structural_signature": "d2-signature-is-not-used-directly",
        "grain_state": grain_state,
        "grain_candidate": (
            {
                "kind": "ROW_KEYED_BY_CANDIDATE",
                "key_refs": [f"region.{ref}" for ref in grain_refs],
            }
            if grain_state == "RESOLVED"
            else None
        ),
        "primary_key_candidates": [primary] if key_refs else [],
        "unique_key_candidates": [primary] if key_refs else [],
        "provenance": {
            "workbook_ref": filename,
            "sample_values": business_values,
            "structural_payload": {
                "contract": "D2",
                "region_shape": "RECTANGULAR",
                "columns": structural_columns,
            },
        },
    }
    return candidate


def _identity(candidates: list[dict], *, filename: str = "january.xlsx", family: str | None = "family:orders") -> dict:
    return build_service_1_workbook_schema_identity_v1(
        logical_table_candidates=candidates,
        workbook_ref=filename,
        schema_family_ref=family,
        schema_version="1",
    )


def _real_d2_candidate(
    columns: list[tuple[str, str]],
    *,
    region_index: int,
    filename: str = "january.xlsx",
) -> dict:
    """Reproduce D2's generated ``lt_<hash>_r<region_index>`` ref."""
    structural_payload = {
        "contract": "SERVICE_1_LOGICAL_TABLE_CANDIDATE_V1",
        "region_shape": "RECTANGULAR",
        "columns": [
            {
                "position": position,
                "normalized_header": header,
                "inferred_type": inferred_type,
                "nullability_class": "NONE",
                "uniqueness_class": "UNIQUE" if position == 0 else "DUPLICATED",
                "candidate_primary_key": position == 0,
            }
            for position, (header, inferred_type) in enumerate(columns)
        ],
    }
    structural_signature = build_service_1_structural_digest_v1(
        payload=structural_payload,
        prefix="ltf_",
    )
    logical_table_id = f"lt_{structural_signature[4:28]}_r{region_index}"
    candidate = _candidate(
        table_key=logical_table_id,
        columns=columns,
        key_refs=[columns[0][0]],
        filename=filename,
    )
    candidate.pop("table_key", None)
    candidate["candidate_id"] = logical_table_id
    candidate["logical_table_id"] = logical_table_id
    candidate["structural_signature"] = structural_signature
    candidate["provenance"]["structural_payload"] = structural_payload
    return candidate


def test_same_structure_different_filename_has_same_fingerprint() -> None:
    first = _identity([_candidate(filename="january.xlsx")], filename="january.xlsx")
    second = _identity([_candidate(filename="renamed.xlsx")], filename="renamed.xlsx")

    assert first["status"] == STATUS_READY
    assert first["schema_fingerprint"] == second["schema_fingerprint"]
    assert "january.xlsx" not in first["schema_fingerprint"]
    assert "renamed.xlsx" not in second["schema_fingerprint"]


def test_added_column_is_limited_compatible_delta() -> None:
    prior = _identity([_candidate()])
    current = _identity([_candidate(columns=[("id", "number"), ("amount", "number"), ("note", "text")])])

    delta = build_service_1_workbook_schema_delta_v1(prior_identity=prior, current_identity=current)

    assert delta["added_columns"][0]["column"] == "note"
    assert delta["removed_columns"] == []
    assert delta["affected_scope"] == ["table:table:orders", "column:table:orders.note"]
    assert delta["drift_state"] == DRIFT_COMPATIBLE_DELTA


def test_removed_column_is_reported_without_whole_workbook_scope() -> None:
    prior = _identity([_candidate(columns=[("id", "number"), ("amount", "number"), ("note", "text")])])
    current = _identity([_candidate()])

    delta = build_service_1_workbook_schema_delta_v1(prior_identity=prior, current_identity=current)

    assert delta["removed_columns"][0]["column"] == "note"
    assert delta["affected_scope"] == ["table:table:orders", "column:table:orders.note"]


def test_changed_column_type_is_material_drift() -> None:
    prior = _identity([_candidate()])
    current = _identity([_candidate(columns=[("id", "number"), ("amount", "text")])])

    delta = build_service_1_workbook_schema_delta_v1(prior_identity=prior, current_identity=current)

    assert delta["changed_columns"][0]["column"] == "amount"
    assert delta["drift_state"] == DRIFT_MATERIAL


def test_table_added_and_removed_are_explicit() -> None:
    second = _candidate(table_key="table:customers", columns=[("id", "number"), ("name", "text")])
    prior = _identity([_candidate()])
    current = _identity([_candidate(), second])
    added = build_service_1_workbook_schema_delta_v1(prior_identity=prior, current_identity=current)
    assert [item["table_key"] for item in added["added_tables"]] == ["table:customers"]
    assert "table:table:customers" in added["affected_scope"]

    removed = build_service_1_workbook_schema_delta_v1(prior_identity=current, current_identity=prior)
    assert [item["table_key"] for item in removed["removed_tables"]] == ["table:customers"]


def test_grain_change_is_material_and_preserves_evidence() -> None:
    prior = _identity([_candidate(grain_refs=["id"])])
    current = _identity([_candidate(grain_refs=["id", "amount"])])

    delta = build_service_1_workbook_schema_delta_v1(prior_identity=prior, current_identity=current)

    assert delta["changed_grains"]
    assert delta["drift_state"] == DRIFT_MATERIAL


def test_key_shape_change_is_reported() -> None:
    prior = _identity([_candidate(key_refs=["id"])])
    current = _identity([_candidate(key_refs=["amount"])])

    delta = build_service_1_workbook_schema_delta_v1(prior_identity=prior, current_identity=current)

    assert delta["changed_keys"]


def test_table_and_column_order_are_canonicalized() -> None:
    first = _identity([
        _candidate(table_key="table:a", columns=[("id", "number"), ("value", "text")]),
        _candidate(table_key="table:b", columns=[("code", "text"), ("qty", "number")]),
    ])
    second = _identity([
        _candidate(table_key="table:b", columns=[("qty", "number"), ("code", "text")]),
        _candidate(table_key="table:a", columns=[("value", "text"), ("id", "number")]),
    ])

    assert first["schema_fingerprint"] == second["schema_fingerprint"]
    assert first["provenance"]["column_order_policy"] == COLUMN_ORDER_POLICY


def test_unresolved_grain_is_fail_closed_but_deterministic() -> None:
    candidate = _candidate(grain_state="UNRESOLVED", key_refs=[])
    first = _identity([candidate])
    second = _identity([deepcopy(candidate)], filename="other.xlsx")

    assert first["schema_fingerprint"] == second["schema_fingerprint"]
    assert first["logical_table_signatures"][0]["grain_state"] == GRAIN_UNRESOLVED
    assert first["logical_table_signatures"][0]["grain_signature"]["candidate"] is None


def test_business_values_do_not_enter_fingerprint() -> None:
    first = _identity([_candidate(business_values=[["A", 10]])])
    second = _identity([_candidate(business_values=[["B", 999999]])])

    assert first["schema_fingerprint"] == second["schema_fingerprint"]


def test_real_d2_region_index_reorder_has_no_false_table_delta() -> None:
    prior = _identity([
        _real_d2_candidate([("id", "number"), ("amount", "number")], region_index=1),
        _real_d2_candidate([("code", "text"), ("qty", "number")], region_index=2),
    ])
    current = _identity([
        _real_d2_candidate([("code", "text"), ("qty", "number")], region_index=1, filename="february.xlsx"),
        _real_d2_candidate([("id", "number"), ("amount", "number")], region_index=2, filename="february.xlsx"),
    ], filename="february.xlsx")

    delta = build_service_1_workbook_schema_delta_v1(prior_identity=prior, current_identity=current)

    assert current["schema_fingerprint"] == prior["schema_fingerprint"]
    assert delta["drift_state"] == DRIFT_IDENTICAL
    assert delta["added_tables"] == []
    assert delta["removed_tables"] == []
    assert delta["changed_tables"] == []


def test_real_d2_reorder_plus_column_add_matches_one_table_structurally() -> None:
    prior = _identity([
        _real_d2_candidate([("id", "number"), ("amount", "number")], region_index=1),
        _real_d2_candidate([("code", "text"), ("qty", "number")], region_index=2),
    ])
    current = _identity([
        _real_d2_candidate([("code", "text"), ("qty", "number")], region_index=1, filename="february.xlsx"),
        _real_d2_candidate([("id", "number"), ("amount", "number"), ("note", "text")], region_index=2, filename="february.xlsx"),
    ], filename="february.xlsx")

    delta = build_service_1_workbook_schema_delta_v1(prior_identity=prior, current_identity=current)

    assert len(delta["changed_tables"]) == 1
    assert [item["column"] for item in delta["added_columns"]] == ["note"]
    assert delta["removed_columns"] == []
    assert delta["added_tables"] == []
    assert delta["removed_tables"] == []
    assert len(delta["affected_scope"]) == 2


def test_structural_overlap_tie_fails_closed() -> None:
    prior = _identity([
        _real_d2_candidate([("id", "number"), ("left", "text")], region_index=1),
        _real_d2_candidate([("id", "number"), ("right", "text")], region_index=2),
    ])
    current = _identity([
        _real_d2_candidate([("id", "number"), ("left", "text"), ("right", "text")], region_index=1, filename="february.xlsx"),
    ], filename="february.xlsx")

    delta = build_service_1_workbook_schema_delta_v1(prior_identity=prior, current_identity=current)

    assert delta["matching_status"] == TABLE_MATCH_UNRESOLVED
    assert delta["drift_state"] == DRIFT_UNRESOLVED
    assert delta["blocked_reason"]


def test_relationship_shape_delta_is_scoped_without_graph_execution() -> None:
    prior = _identity([_candidate()])
    current = build_service_1_workbook_schema_identity_v1(
        logical_table_candidates=[_candidate()],
        schema_family_ref="family:orders",
        relationship_evidence=[
            {
                "left_column_ref": "orders.id",
                "right_column_ref": "customers.order_id",
                "relationship_kind": "MANY_TO_ONE",
            }
        ],
    )

    delta = build_service_1_workbook_schema_delta_v1(prior_identity=prior, current_identity=current)

    assert delta["changed_relationships"]
    assert any(item.startswith("relationship:") for item in delta["affected_scope"])


def test_family_unknown_and_authority_flags_remain_closed() -> None:
    identity = _identity([_candidate()], family=None)

    assert identity["schema_family_ref"] == UNKNOWN_FAMILY
    assert identity["family_auto_reuse_authorized"] is False
    assert identity["semantic_rebind_authorized"] is False
    assert identity["computability_authorized"] is False
