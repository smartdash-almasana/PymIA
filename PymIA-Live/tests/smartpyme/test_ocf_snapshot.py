from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from pymia.smartpyme.ocf_snapshot import (
    SnapshotBuildError,
    build_snapshot_from_replay,
    compose_ocf_snapshot,
)
from pymia.smartpyme.pipeline_registration import (
    register_anamnesis_record,
    register_evidence_record,
    register_evidence_request_record,
    register_investigation_record,
    register_owner_answer_record,
    register_pipeline_run_record,
)


def _append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _seed_basic_case(
    *,
    storage_dir: Path,
    tmp_path: Path,
    tenant_id: str = "tenant_test",
    intake_id: str = "intake_test",
    with_owner_answer: bool = False,
    with_evidence_request: bool = False,
    with_evidence: bool = False,
    with_pipeline_run: bool = False,
    structured_summary: dict | None = None,
    evidence_type: str = "xlsx_upload",
    requested_evidence: list[str] | None = None,
    question_ref: str | None = None,
    raw_owner_answer: str | None = None,
) -> dict:
    evidence_path = tmp_path / f"{tenant_id}_{intake_id}.xlsx"
    if not evidence_path.exists():
        evidence_path.write_bytes(b"fake-xlsx-content")

    anamnesis_record = register_anamnesis_record(
        "Necesito entender mi flujo de caja.",
        tenant_id,
        intake_id,
        storage_dir,
    )
    investigation_record = register_investigation_record(
        "Necesito entender mi flujo de caja.",
        tenant_id,
        intake_id,
        anamnesis_record["anamnesis_id"],
        storage_dir,
    )

    owner_answer_record = None
    if with_owner_answer:
        owner_answer_record = register_owner_answer_record(
            tenant_id=tenant_id,
            intake_id=intake_id,
            anamnesis_id=anamnesis_record["anamnesis_id"],
            investigation_id=investigation_record["investigation_id"],
            question_ref=question_ref or "owner_question:cash_flow",
            raw_owner_answer=raw_owner_answer or "No sé bien los números.",
            storage_dir=storage_dir,
        )

    evidence_request_record = None
    if with_evidence_request:
        evidence_request_record = register_evidence_request_record(
            tenant_id=tenant_id,
            intake_id=intake_id,
            anamnesis_id=anamnesis_record["anamnesis_id"],
            investigation_id=investigation_record["investigation_id"],
            owner_answer_id=owner_answer_record["answer_id"] if owner_answer_record else None,
            requested_evidence=requested_evidence or ["ventas_del_periodo"],
            request_reason="Falta archivo de ventas.",
            storage_dir=storage_dir,
        )

    evidence_record = None
    if with_evidence:
        # We manually register or tweak evidence_record to test evidence type
        evidence_record = register_evidence_record(
            evidence_path,
            tenant_id,
            intake_id,
            storage_dir,
            request_id=evidence_request_record["request_id"] if evidence_request_record else None,
        )
        if evidence_type != "xlsx_upload":
            # Update evidence_type inside the file directly since register_evidence_record hardcodes xlsx_upload
            ev_file = storage_dir / tenant_id / "evidences.jsonl"
            lines = ev_file.read_text(encoding="utf-8").splitlines()
            if lines:
                last_line = json.loads(lines[-1])
                last_line["evidence_type"] = evidence_type
                lines[-1] = json.dumps(last_line, ensure_ascii=False)
                ev_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
                evidence_record["evidence_type"] = evidence_type

    pipeline_run_record = None
    if with_pipeline_run:
        pipeline_run_record = register_pipeline_run_record(
            tenant_id=tenant_id,
            intake_id=intake_id,
            message="Necesito entender mi flujo de caja.",
            anamnesis_record=anamnesis_record,
            investigation_record=investigation_record,
            owner_answer_record=owner_answer_record,
            evidence_request_record=evidence_request_record,
            evidence_record=evidence_record or {"evidence_id": "dummy_evidence"},
            structured_summary=structured_summary or {"status": "available"},
            blocked=False,
            storage_dir=storage_dir,
        )
        if structured_summary:
            runs_file = storage_dir / tenant_id / "pipeline_runs.jsonl"
            lines = runs_file.read_text(encoding="utf-8").splitlines()
            if lines:
                last_line = json.loads(lines[-1])
                last_line["metadata"]["structured_summary"] = structured_summary
                lines[-1] = json.dumps(last_line, ensure_ascii=False)
                runs_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
                pipeline_run_record["metadata"]["structured_summary"] = structured_summary

    return {
        "anamnesis_record": anamnesis_record,
        "investigation_record": investigation_record,
        "owner_answer_record": owner_answer_record,
        "evidence_request_record": evidence_request_record,
        "evidence_record": evidence_record,
        "pipeline_run_record": pipeline_run_record,
    }


def test_returns_not_found_for_missing_case(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    snapshot = build_snapshot_from_replay(
        storage_dir=storage_dir,
        tenant_id="non_existent_tenant",
        intake_id="non_existent_intake",
    )
    assert snapshot.case_status == "NOT_FOUND"
    assert snapshot.case_id == "non_existent_intake"
    assert snapshot.tenant_id == "non_existent_tenant"
    assert snapshot.intake_id == "non_existent_intake"


def test_returns_partial_snapshot_when_replay_has_evidence_without_pipeline_run(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    _seed_basic_case(
        storage_dir=storage_dir,
        tmp_path=tmp_path,
        with_evidence=True,
        with_pipeline_run=False,
    )
    snapshot = build_snapshot_from_replay(
        storage_dir=storage_dir,
        tenant_id="tenant_test",
        intake_id="intake_test",
    )
    assert snapshot.case_status == "PARTIAL_SNAPSHOT"


def test_returns_snapshot_ready_for_completed_replay(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    _seed_basic_case(
        storage_dir=storage_dir,
        tmp_path=tmp_path,
        with_evidence=True,
        with_pipeline_run=True,
    )
    snapshot = build_snapshot_from_replay(
        storage_dir=storage_dir,
        tenant_id="tenant_test",
        intake_id="intake_test",
    )
    assert snapshot.case_status == "SNAPSHOT_READY"


def test_includes_evidence_refs_with_trace_fields(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    seeded = _seed_basic_case(
        storage_dir=storage_dir,
        tmp_path=tmp_path,
        with_evidence=True,
    )
    snapshot = build_snapshot_from_replay(
        storage_dir=storage_dir,
        tenant_id="tenant_test",
        intake_id="intake_test",
    )
    assert len(snapshot.evidence_refs) == 1
    ref = snapshot.evidence_refs[0]
    expected_ev_id = seeded["evidence_record"]["evidence_id"]
    assert ref["evidence_id"] == expected_ev_id
    assert ref["evidence_type"] == "xlsx_upload"
    assert ref["source_kind"] == "uploaded_file"
    assert ref["status"] == "REGISTERED"
    assert ref["trace_ref"] == f"evidences.jsonl:{expected_ev_id}"


def test_includes_run_refs_with_run_id_and_output_hash_when_available(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    seeded = _seed_basic_case(
        storage_dir=storage_dir,
        tmp_path=tmp_path,
        with_evidence=True,
        with_pipeline_run=True,
    )
    snapshot = build_snapshot_from_replay(
        storage_dir=storage_dir,
        tenant_id="tenant_test",
        intake_id="intake_test",
    )
    assert len(snapshot.run_refs) == 1
    ref = snapshot.run_refs[0]
    expected_run_id = seeded["pipeline_run_record"]["run_id"]
    assert ref["run_id"] == expected_run_id
    assert "output_hash" in ref
    assert ref["trace_ref"] == f"pipeline_runs.jsonl:{expected_run_id}"


def test_extracts_available_variables_only_when_present_in_replay_outputs(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    tenant_id = "tenant_test"
    intake_id = "intake_test"

    # Seed case with pipeline run having computed variables under metadata.structured_summary
    structured_summary = {
        "status": "available",
        "computed_variables": {"ventas_total": 1000.0},
    }
    _seed_basic_case(
        storage_dir=storage_dir,
        tmp_path=tmp_path,
        tenant_id=tenant_id,
        intake_id=intake_id,
        with_owner_answer=True,
        question_ref="owner_question:costos_total",
        raw_owner_answer="500.0",
        with_evidence=True,
        with_pipeline_run=True,
        structured_summary=structured_summary,
    )

    # Let's also add variables to evidence metadata manually
    ev_file = storage_dir / tenant_id / "evidences.jsonl"
    lines = ev_file.read_text(encoding="utf-8").splitlines()
    if lines:
        last_line = json.loads(lines[-1])
        last_line["metadata"]["detected_variables"] = {"caja_total": 200.0}
        lines[-1] = json.dumps(last_line, ensure_ascii=False)
        ev_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    snapshot = build_snapshot_from_replay(
        storage_dir=storage_dir,
        tenant_id=tenant_id,
        intake_id=intake_id,
    )

    # We expect:
    # - ventas_total (source: pipeline_output)
    # - costos_total (source: owner_declared)
    # - caja_total (source: structured_evidence)
    avail_vars = {v["variable"]: v for v in snapshot.available_variables}
    assert "ventas_total" in avail_vars
    assert avail_vars["ventas_total"]["source"] == "pipeline_output"
    assert avail_vars["ventas_total"]["value"] == 1000.0

    assert "costos_total" in avail_vars
    assert avail_vars["costos_total"]["source"] == "owner_declared"
    assert avail_vars["costos_total"]["value"] == "500.0"

    assert "caja_total" in avail_vars
    assert avail_vars["caja_total"]["source"] == "structured_evidence"
    assert avail_vars["caja_total"]["value"] == 200.0


def test_extracts_missing_variables_only_when_present_in_replay_outputs(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    tenant_id = "tenant_test"
    intake_id = "intake_test"

    # Request "ventas_del_periodo" and "costos_del_periodo"
    # Seed evidence for "ventas_del_periodo" but NOT "costos_del_periodo"
    _seed_basic_case(
        storage_dir=storage_dir,
        tmp_path=tmp_path,
        tenant_id=tenant_id,
        intake_id=intake_id,
        with_evidence_request=True,
        requested_evidence=["ventas_del_periodo", "costos_del_periodo"],
        with_evidence=True,
        evidence_type="ventas_del_periodo",
    )

    snapshot = build_snapshot_from_replay(
        storage_dir=storage_dir,
        tenant_id=tenant_id,
        intake_id=intake_id,
    )

    # Only "costos_del_periodo" should be missing
    assert len(snapshot.missing_variables) == 1
    assert snapshot.missing_variables[0]["variable"] == "costos_del_periodo"
    assert snapshot.missing_variables[0]["reason"] == "Falta archivo de ventas."


def test_propagates_replay_warnings(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    tenant_id = "tenant_test"
    intake_id = "intake_test"
    _seed_basic_case(storage_dir=storage_dir, tmp_path=tmp_path, tenant_id=tenant_id, intake_id=intake_id)

    # Append a corrupt line to evidence request jsonl
    req_file = storage_dir / tenant_id / "evidence_requests.jsonl"
    with req_file.open("a", encoding="utf-8") as fh:
        fh.write("corrupt JSON line here\n")

    snapshot = build_snapshot_from_replay(
        storage_dir=storage_dir,
        tenant_id=tenant_id,
        intake_id=intake_id,
    )
    assert any("Malformed JSONL line ignored" in w for w in snapshot.warnings)


def test_does_not_write_jsonl_or_storage(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    tenant_id = "tenant_test"
    intake_id = "intake_test"
    _seed_basic_case(storage_dir=storage_dir, tmp_path=tmp_path, tenant_id=tenant_id, intake_id=intake_id)

    # Snapshot state of files before building snapshot
    def get_dir_state(d: Path) -> dict[str, tuple[int, float]]:
        return {
            str(p.relative_to(d)): (p.stat().st_size, p.stat().st_mtime)
            for p in d.rglob("*")
            if p.is_file()
        }

    state_before = get_dir_state(storage_dir)

    # Call snapshot
    build_snapshot_from_replay(
        storage_dir=storage_dir,
        tenant_id=tenant_id,
        intake_id=intake_id,
    )

    state_after = get_dir_state(storage_dir)
    assert state_before == state_after


def test_does_not_import_or_call_vertical_pipeline(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    tenant_id = "tenant_test"
    intake_id = "intake_test"
    _seed_basic_case(storage_dir=storage_dir, tmp_path=tmp_path, tenant_id=tenant_id, intake_id=intake_id)

    # Clean sys.modules from vertical_pipeline if loaded
    if "pymia.application.vertical_pipeline" in sys.modules:
        del sys.modules["pymia.application.vertical_pipeline"]

    build_snapshot_from_replay(
        storage_dir=storage_dir,
        tenant_id=tenant_id,
        intake_id=intake_id,
    )

    assert "pymia.application.vertical_pipeline" not in sys.modules


def test_does_not_import_diagnostic_core(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    tenant_id = "tenant_test"
    intake_id = "intake_test"
    _seed_basic_case(storage_dir=storage_dir, tmp_path=tmp_path, tenant_id=tenant_id, intake_id=intake_id)

    # Clean sys.modules from diagnostic_core
    for mod in list(sys.modules.keys()):
        if mod.startswith("pymia.diagnostic_core"):
            del sys.modules[mod]

    build_snapshot_from_replay(
        storage_dir=storage_dir,
        tenant_id=tenant_id,
        intake_id=intake_id,
    )

    assert not any(mod.startswith("pymia.diagnostic_core") for mod in sys.modules)


def test_raises_snapshot_build_error_for_missing_required_identity_fields(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    with pytest.raises(SnapshotBuildError) as exc_info1:
        build_snapshot_from_replay(
            storage_dir=storage_dir,
            tenant_id="",
            intake_id="intake_test",
        )
    assert exc_info1.value.missing_field == "tenant_id"

    with pytest.raises(SnapshotBuildError) as exc_info2:
        build_snapshot_from_replay(
            storage_dir=storage_dir,
            tenant_id="tenant_test",
            intake_id="",
        )
    assert exc_info2.value.missing_field == "intake_id"


def test_keeps_heuristic_ratio_at_or_below_20_percent(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    tenant_id = "tenant_test"
    intake_id = "intake_test"
    _seed_basic_case(
        storage_dir=storage_dir,
        tmp_path=tmp_path,
        tenant_id=tenant_id,
        intake_id=intake_id,
        with_owner_answer=True,
        raw_owner_answer="No se bien de donde sale esa diferencia.",
    )

    snapshot = build_snapshot_from_replay(
        storage_dir=storage_dir,
        tenant_id=tenant_id,
        intake_id=intake_id,
    )
    assert snapshot.coverage["heuristic_ratio"] <= 0.20


def test_next_questions_are_not_counted_as_raw_replay(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    _seed_basic_case(
        storage_dir=storage_dir,
        tmp_path=tmp_path,
        with_evidence_request=True,
        requested_evidence=["ventas_del_periodo"],
    )

    snapshot = build_snapshot_from_replay(
        storage_dir=storage_dir,
        tenant_id="tenant_test",
        intake_id="intake_test",
    )

    assert snapshot.next_questions
    assert snapshot.coverage["field_provenance"]["next_questions"] == "derived_from_replay"
    assert snapshot.coverage["field_provenance"]["missing_variables"] == "derived_from_replay"


def test_keyword_uncertainty_is_not_counted_as_raw_replay(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    _seed_basic_case(
        storage_dir=storage_dir,
        tmp_path=tmp_path,
        with_owner_answer=True,
        raw_owner_answer="No estoy seguro del saldo final.",
    )

    snapshot = build_snapshot_from_replay(
        storage_dir=storage_dir,
        tenant_id="tenant_test",
        intake_id="intake_test",
    )

    assert any(item["unknown"].startswith("Duda declarada:") for item in snapshot.open_unknowns)
    assert snapshot.coverage["field_provenance"]["open_unknowns"] == "inferred_or_heuristic"
    assert snapshot.coverage["inferred_or_heuristic"] >= 1


def test_question_ref_variables_are_not_counted_as_raw_replay(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    _seed_basic_case(
        storage_dir=storage_dir,
        tmp_path=tmp_path,
        with_owner_answer=True,
        question_ref="owner_question:costos_total",
        raw_owner_answer="500.0",
    )

    snapshot = build_snapshot_from_replay(
        storage_dir=storage_dir,
        tenant_id="tenant_test",
        intake_id="intake_test",
    )

    assert any(item["variable"] == "costos_total" for item in snapshot.available_variables)
    assert snapshot.coverage["field_provenance"]["available_variables"] == "derived_from_replay"


def test_compose_ocf_snapshot_returns_dict(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    tenant_id = "tenant_test"
    intake_id = "intake_test"
    _seed_basic_case(storage_dir=storage_dir, tmp_path=tmp_path, tenant_id=tenant_id, intake_id=intake_id)

    snapshot_dict = compose_ocf_snapshot(
        storage_dir=storage_dir,
        tenant_id=tenant_id,
        intake_id=intake_id,
    )
    assert isinstance(snapshot_dict, dict)
    assert snapshot_dict["case_id"] == intake_id
    assert snapshot_dict["tenant_id"] == tenant_id
    assert snapshot_dict["intake_id"] == intake_id
    assert "coverage" in snapshot_dict
    assert isinstance(snapshot_dict["coverage"], dict)
