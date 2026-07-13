from __future__ import annotations

import json
from pathlib import Path

import pytest

from pymia.smartpyme.ocf_snapshot import (
    OrganizationalCaseFileSnapshot,
    SnapshotBuildError,
    build_snapshot_from_replay,
)


def _write_jsonl_records(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _seed_full_trace(
    storage_dir: Path,
    *,
    tenant_id: str = "tenant_demo",
    intake_id: str = "intake_demo",
    anamnesis_id: str = "anamnesis_001",
    investigation_id: str = "investigation_001",
    answer_id: str = "answer_001",
    request_id: str = "request_001",
    evidence_id: str = "evidence_001",
    run_id: str = "run_001",
    with_pipeline_run: bool = True,
) -> None:
    root = storage_dir / tenant_id
    root.mkdir(parents=True, exist_ok=True)

    _write_jsonl_records(root / "anamnesis.jsonl", [
        {
            "tenant_id": tenant_id,
            "intake_id": intake_id,
            "anamnesis_id": anamnesis_id,
            "created_at": "2026-06-01T10:00:00",
            "raw_owner_message": "Necesito entender si tengo problema de caja.",
        }
    ])
    _write_jsonl_records(root / "investigations.jsonl", [
        {
            "tenant_id": tenant_id,
            "intake_id": intake_id,
            "investigation_id": investigation_id,
            "created_at": "2026-06-01T10:01:00",
            "anamnesis_id": anamnesis_id,
            "investigation_goal": "Entender si hay descalce de caja entre cobros y pagos.",
        }
    ])
    _write_jsonl_records(root / "owner_answers.jsonl", [
        {
            "tenant_id": tenant_id,
            "intake_id": intake_id,
            "answer_id": answer_id,
            "created_at": "2026-06-01T10:02:00",
            "anamnesis_id": anamnesis_id,
            "investigation_id": investigation_id,
            "question_ref": "owner_question:cash_gap",
            "raw_owner_answer": "La caja cae cuando pago proveedores.",
            "answer_kind": "ANSWER_TO_PENDING_QUESTION",
        }
    ])
    _write_jsonl_records(root / "evidence_requests.jsonl", [
        {
            "tenant_id": tenant_id,
            "intake_id": intake_id,
            "request_id": request_id,
            "created_at": "2026-06-01T10:03:00",
            "anamnesis_id": anamnesis_id,
            "investigation_id": investigation_id,
            "owner_answer_id": answer_id,
            "requested_evidence": ["ventas_del_periodo", "pagos_a_proveedores"],
            "request_reason": "Falta contraste operativo para verificar descalce.",
            "status": "WAITING_UPLOAD",
        }
    ])
    _write_jsonl_records(root / "evidences.jsonl", [
        {
            "tenant_id": tenant_id,
            "intake_id": intake_id,
            "evidence_id": evidence_id,
            "received_at": "2026-06-01T10:04:00",
            "request_id": request_id,
            "evidence_type": "xlsx_upload",
            "content_hash": "content_hash_001",
            "source_kind": "uploaded_file",
            "source_ref": str(root / "caso.xlsx"),
            "status": "REGISTERED",
        }
    ])
    if with_pipeline_run:
        _write_jsonl_records(root / "pipeline_runs.jsonl", [
            {
                "tenant_id": tenant_id,
                "intake_id": intake_id,
                "run_id": run_id,
                "started_at": "2026-06-01T10:05:00",
                "pipeline_name": "vertical_pipeline_evidence_spine",
                "pipeline_version": "v1",
                "status": "COMPLETED",
                "evidence_ids": [evidence_id],
                "steps_executed": ["evidence_record_registered", "structured_evidence_built"],
                "output_artifact_id": "owner_facing_markdown",
                "output_hash": "abc123",
                "metadata": {
                    "anamnesis_id": anamnesis_id,
                    "investigation_id": investigation_id,
                    "computed_variables": {
                        "ventas_totales": 100000.0,
                        "costo_mercaderia": 60000.0,
                        "margen_bruto": 40000.0,
                        "plazo_cobro_dias": 30.0,
                        "plazo_pago_dias": 45.0,
                        "stock_promedio": 50000.0,
                        "gastos_fijos": 20000.0,
                        "resultado_neto": 20000.0,
                    },
                },
            }
        ])


def _write_excel(path: Path, rows: list[list[object]]) -> None:
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    wb.save(path)


def _snapshot_tree(root: Path) -> dict[str, bytes]:
    if not root.exists():
        return {}
    return {
        str(p.relative_to(root)): p.read_bytes()
        for p in root.rglob("*")
        if p.is_file()
    }


class TestNotFound:
    def test_returns_not_found_for_missing_case(self, tmp_path: Path) -> None:
        snapshot = build_snapshot_from_replay(
            storage_dir=tmp_path / "storage",
            tenant_id="tenant_missing",
            intake_id="intake_missing",
        )
        assert snapshot.case_status == "NOT_FOUND"
        assert snapshot.tenant_id == "tenant_missing"
        assert snapshot.intake_id == "intake_missing"
        assert snapshot.evidence_refs == []
        assert snapshot.run_refs == []
        assert snapshot.owner_answer_refs == []
        assert snapshot.evidence_request_refs == []


class TestPartialSnapshot:
    def test_returns_partial_snapshot_when_pipeline_run_missing(self, tmp_path: Path) -> None:
        storage_dir = tmp_path / "storage"
        _seed_full_trace(storage_dir, with_pipeline_run=False)

        snapshot = build_snapshot_from_replay(
            storage_dir=storage_dir,
            tenant_id="tenant_demo",
            intake_id="intake_demo",
        )
        assert snapshot.case_status == "PARTIAL_SNAPSHOT"
        assert snapshot.evidence_refs != []
        assert snapshot.run_refs == []


class TestSnapshotReady:
    def test_returns_snapshot_ready_for_completed_replay(self, tmp_path: Path) -> None:
        storage_dir = tmp_path / "storage"
        _seed_full_trace(storage_dir)

        snapshot = build_snapshot_from_replay(
            storage_dir=storage_dir,
            tenant_id="tenant_demo",
            intake_id="intake_demo",
        )
        assert snapshot.case_status == "SNAPSHOT_READY"
        assert snapshot.case_id == "intake_demo"
        assert snapshot.tenant_id == "tenant_demo"
        assert snapshot.intake_id == "intake_demo"

    def test_includes_evidence_refs_with_trace_fields(self, tmp_path: Path) -> None:
        storage_dir = tmp_path / "storage"
        _seed_full_trace(storage_dir)

        snapshot = build_snapshot_from_replay(
            storage_dir=storage_dir,
            tenant_id="tenant_demo",
            intake_id="intake_demo",
        )
        assert len(snapshot.evidence_refs) >= 1
        ref = snapshot.evidence_refs[0]
        assert "evidence_id" in ref
        assert "evidence_type" in ref
        assert "content_hash" in ref
        assert "source_kind" in ref
        assert "status" in ref
        assert "trace_ref" in ref
        assert ref["content_hash"] == "content_hash_001"
        assert ref["trace_ref"].startswith("evidences.jsonl:")

    def test_includes_run_refs_with_run_id_and_output_hash(self, tmp_path: Path) -> None:
        storage_dir = tmp_path / "storage"
        _seed_full_trace(storage_dir)

        snapshot = build_snapshot_from_replay(
            storage_dir=storage_dir,
            tenant_id="tenant_demo",
            intake_id="intake_demo",
        )
        assert len(snapshot.run_refs) >= 1
        ref = snapshot.run_refs[0]
        assert "run_id" in ref
        assert "pipeline_name" in ref
        assert "output_hash" in ref
        assert "output_artifact_id" in ref
        assert "status" in ref
        assert ref["output_hash"] == "abc123"
        assert ref["output_artifact_id"] == "owner_facing_markdown"
        assert ref["trace_ref"].startswith("pipeline_runs.jsonl:")

    def test_extracts_available_variables_only_when_present(self, tmp_path: Path) -> None:
        storage_dir = tmp_path / "storage"
        _seed_full_trace(storage_dir)

        snapshot = build_snapshot_from_replay(
            storage_dir=storage_dir,
            tenant_id="tenant_demo",
            intake_id="intake_demo",
        )
        assert len(snapshot.available_variables) >= 1
        var = snapshot.available_variables[0]
        assert "variable" in var
        assert "source" in var
        assert "trace_ref" in var
        assert var["trace_ref"].startswith("pipeline_runs.jsonl:")

    def test_extracts_missing_variables_when_evidence_unmatched(self, tmp_path: Path) -> None:
        storage_dir = tmp_path / "storage"
        _seed_full_trace(storage_dir)

        snapshot = build_snapshot_from_replay(
            storage_dir=storage_dir,
            tenant_id="tenant_demo",
            intake_id="intake_demo",
        )
        assert len(snapshot.missing_variables) >= 1
        missing = snapshot.missing_variables[0]
        assert "variable" in missing
        assert "reason" in missing
        assert "requested_in" in missing

    def test_propagates_replay_warnings(self, tmp_path: Path) -> None:
        storage_dir = tmp_path / "storage"
        _seed_full_trace(storage_dir)

        malformed_path = storage_dir / "tenant_demo" / "owner_answers.jsonl"
        with malformed_path.open("a", encoding="utf-8") as handle:
            handle.write("{bad json\n")

        snapshot = build_snapshot_from_replay(
            storage_dir=storage_dir,
            tenant_id="tenant_demo",
            intake_id="intake_demo",
        )
        assert any("malformed" in w.lower() for w in snapshot.warnings)


class TestReadOnly:
    def test_does_not_write_jsonl_or_storage(self, tmp_path: Path) -> None:
        storage_dir = tmp_path / "storage"
        _seed_full_trace(storage_dir)
        before = _snapshot_tree(storage_dir)

        snapshot = build_snapshot_from_replay(
            storage_dir=storage_dir,
            tenant_id="tenant_demo",
            intake_id="intake_demo",
        )
        after = _snapshot_tree(storage_dir)

        assert snapshot.case_status == "SNAPSHOT_READY"
        assert after == before


class TestForbiddenImports:
    def test_does_not_import_or_call_vertical_pipeline(self) -> None:
        import pymia.smartpyme.ocf_snapshot as snap_mod
        source = str(snap_mod.__file__)
        content = source  # file path reference; check source text
        with open(source, encoding="utf-8") as handle:
            text = handle.read()
        assert "vertical_pipeline" not in text
        assert "diagnostic_core" not in text

    def test_does_not_import_diagnostic_core(self) -> None:
        import pymia.smartpyme.ocf_snapshot as snap_mod
        with open(snap_mod.__file__, encoding="utf-8") as handle:
            text = handle.read()
        assert "diagnostic_core" not in text


class TestErrors:
    def test_raises_snapshot_build_error_for_missing_identity(self, tmp_path: Path) -> None:
        with pytest.raises(SnapshotBuildError) as exc_info:
            build_snapshot_from_replay(
                storage_dir=tmp_path / "storage",
                tenant_id="",
                intake_id="",
            )


class TestCoverage:
    def test_keeps_heuristic_ratio_at_zero(self, tmp_path: Path) -> None:
        storage_dir = tmp_path / "storage"
        _seed_full_trace(storage_dir)

        snapshot = build_snapshot_from_replay(
            storage_dir=storage_dir,
            tenant_id="tenant_demo",
            intake_id="intake_demo",
        )
        assert snapshot.coverage["heuristic_ratio"] == 0.0
        assert snapshot.coverage["coverage_from_replay"] > 0.0
        assert snapshot.coverage["total_fields"] > 0
        assert snapshot.coverage["inferred_or_heuristic"] == 0
