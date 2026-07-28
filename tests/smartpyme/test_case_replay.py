from __future__ import annotations

import json
from pathlib import Path

import pytest
from openpyxl import Workbook

from pymia.application.vertical_pipeline import inspect_excel
from pymia.cli import vertical_slice
from pymia.contracts.pipeline_run_v1 import build_pipeline_run_record
from pymia.smartpyme.case_replay import replay_case_from_jsonl
from pymia.smartpyme.pipeline_registration import (
    register_anamnesis_record,
    register_evidence_record,
    register_evidence_request_record,
    register_investigation_record,
    register_owner_answer_record,
    register_pipeline_run_record,
)


def _write_excel(path: Path, rows: list[list[object]]) -> None:
    workbook = Workbook()
    worksheet = workbook.active
    for row in rows:
        worksheet.append(row)
    workbook.save(path)


def _append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _snapshot_tree(root: Path) -> dict[str, bytes]:
    if not root.exists():
        return {}
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def _seed_case_trace(
    *,
    storage_dir: Path,
    tmp_path: Path,
    tenant_id: str = "tenant_demo",
    intake_id: str = "intake_demo",
    with_owner_answer: bool = True,
    with_evidence_request: bool = True,
    with_pipeline_run: bool = True,
    business_taxonomy: dict | None = None,
) -> dict:
    evidence_path = tmp_path / f"{tenant_id}_{intake_id}.xlsx"
    evidence_path.write_bytes(b"fake-xlsx-content")

    anamnesis_record = register_anamnesis_record(
        "Necesito entender si tengo problema de caja.",
        tenant_id,
        intake_id,
        storage_dir,
        business_taxonomy=business_taxonomy,
    )
    investigation_record = register_investigation_record(
        "Necesito entender si tengo problema de caja.",
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
            question_ref="owner_question:cash_gap",
            raw_owner_answer="La caja cae cuando pago proveedores.",
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
            requested_evidence=["ventas_del_periodo", "pagos_a_proveedores"],
            request_reason="Falta contraste operativo.",
            storage_dir=storage_dir,
        )
    evidence_record = register_evidence_record(
        evidence_path,
        tenant_id,
        intake_id,
        storage_dir,
        request_id=evidence_request_record["request_id"] if evidence_request_record else None,
    )
    pipeline_run_record = None
    if with_pipeline_run:
        pipeline_run_record = register_pipeline_run_record(
            tenant_id=tenant_id,
            intake_id=intake_id,
            message="Necesito entender si tengo problema de caja.",
            anamnesis_record=anamnesis_record,
            investigation_record=investigation_record,
            owner_answer_record=owner_answer_record,
            evidence_request_record=evidence_request_record,
            evidence_record=evidence_record,
            structured_summary={"status": "available"},
            blocked=False,
            storage_dir=storage_dir,
        )
    return {
        "anamnesis_record": anamnesis_record,
        "investigation_record": investigation_record,
        "owner_answer_record": owner_answer_record,
        "evidence_request_record": evidence_request_record,
        "evidence_record": evidence_record,
        "pipeline_run_record": pipeline_run_record,
    }


def test_replay_returns_not_found_for_nonexistent_tenant(tmp_path: Path) -> None:
    replay = replay_case_from_jsonl(
        storage_dir=tmp_path / "storage",
        tenant_id="tenant_missing",
        intake_id="intake_demo",
    )

    assert replay["status"] == "NOT_FOUND"
    assert replay["anamnesis_record"] is None
    assert replay["investigation_record"] is None
    assert replay["owner_answer_records"] == []
    assert replay["evidence_request_records"] == []
    assert replay["evidence_records"] == []
    assert replay["pipeline_run_records"] == []
    assert replay["latest_pipeline_run_record"] is None
    assert replay["missing_links"] == []
    assert replay["warnings"] == []


def test_replay_returns_not_found_for_nonexistent_intake(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    _seed_case_trace(storage_dir=storage_dir, tmp_path=tmp_path, tenant_id="tenant_demo", intake_id="intake_a")

    replay = replay_case_from_jsonl(
        storage_dir=storage_dir,
        tenant_id="tenant_demo",
        intake_id="intake_b",
    )

    assert replay["status"] == "NOT_FOUND"
    assert replay["anamnesis_record"] is None
    assert replay["pipeline_run_records"] == []


def test_replay_returns_replay_ready_after_vertical_slice_run(tmp_path: Path) -> None:
    excel = tmp_path / "caso.xlsx"
    storage_dir = tmp_path / "storage"
    _write_excel(excel, [["fecha", "producto", "ventas", "costo"], ["2026-06-01", "A", 100, 60]])
    profile = inspect_excel(excel)

    report = vertical_slice.build_report(
        excel,
        "vendo mas pero no me queda plata",
        profile,
        tenant_id="tenant_textil_001",
        intake_id="intake_textil_001",
        storage_dir=storage_dir,
    )

    replay = replay_case_from_jsonl(
        storage_dir=storage_dir,
        tenant_id="tenant_textil_001",
        intake_id="intake_textil_001",
    )

    assert replay["status"] == "REPLAY_READY"
    assert replay["anamnesis_record"]["anamnesis_id"] == report["anamnesis_record"]["anamnesis_id"]
    assert replay["investigation_record"]["anamnesis_id"] == report["anamnesis_record"]["anamnesis_id"]
    assert replay["evidence_records"][0]["evidence_id"] == report["evidence_record"]["evidence_id"]
    assert replay["latest_pipeline_run_record"]["run_id"] == report["pipeline_run_record"]["run_id"]
    assert len(replay["missing_links"]) == 0


def test_replay_includes_all_record_types(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    seeded = _seed_case_trace(storage_dir=storage_dir, tmp_path=tmp_path)

    replay = replay_case_from_jsonl(
        storage_dir=storage_dir,
        tenant_id="tenant_demo",
        intake_id="intake_demo",
    )

    assert replay["anamnesis_record"]["anamnesis_id"] == seeded["anamnesis_record"]["anamnesis_id"]
    assert replay["investigation_record"]["investigation_id"] == seeded["investigation_record"]["investigation_id"]
    assert [record["answer_id"] for record in replay["owner_answer_records"]] == [
        seeded["owner_answer_record"]["answer_id"]
    ]
    assert [record["request_id"] for record in replay["evidence_request_records"]] == [
        seeded["evidence_request_record"]["request_id"]
    ]
    assert [record["evidence_id"] for record in replay["evidence_records"]] == [
        seeded["evidence_record"]["evidence_id"]
    ]
    assert [record["run_id"] for record in replay["pipeline_run_records"]] == [
        seeded["pipeline_run_record"]["run_id"]
    ]


def test_replay_does_not_mix_tenants(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    target = _seed_case_trace(storage_dir=storage_dir, tmp_path=tmp_path, tenant_id="tenant_a", intake_id="case_1")
    other = _seed_case_trace(storage_dir=storage_dir, tmp_path=tmp_path, tenant_id="tenant_b", intake_id="case_1")

    replay = replay_case_from_jsonl(
        storage_dir=storage_dir,
        tenant_id="tenant_a",
        intake_id="case_1",
    )

    assert replay["anamnesis_record"]["anamnesis_id"] == target["anamnesis_record"]["anamnesis_id"]
    assert replay["anamnesis_record"]["anamnesis_id"] != other["anamnesis_record"]["anamnesis_id"]
    assert replay["latest_pipeline_run_record"]["run_id"] == target["pipeline_run_record"]["run_id"]
    assert replay["latest_pipeline_run_record"]["run_id"] != other["pipeline_run_record"]["run_id"]


def test_replay_does_not_mix_intake_ids(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    target = _seed_case_trace(storage_dir=storage_dir, tmp_path=tmp_path, tenant_id="tenant_demo", intake_id="case_1")
    other = _seed_case_trace(storage_dir=storage_dir, tmp_path=tmp_path, tenant_id="tenant_demo", intake_id="case_2")

    replay = replay_case_from_jsonl(
        storage_dir=storage_dir,
        tenant_id="tenant_demo",
        intake_id="case_1",
    )

    assert replay["investigation_record"]["investigation_id"] == target["investigation_record"]["investigation_id"]
    assert replay["investigation_record"]["investigation_id"] != other["investigation_record"]["investigation_id"]
    assert [record["evidence_id"] for record in replay["evidence_records"]] == [
        target["evidence_record"]["evidence_id"]
    ]


def test_replay_partial_when_pipeline_runs_missing(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    _seed_case_trace(storage_dir=storage_dir, tmp_path=tmp_path)
    pipeline_runs_path = storage_dir / "tenant_demo" / "pipeline_runs.jsonl"
    pipeline_runs_path.unlink()

    replay = replay_case_from_jsonl(
        storage_dir=storage_dir,
        tenant_id="tenant_demo",
        intake_id="intake_demo",
    )

    assert replay["status"] == "PARTIAL_REPLAY"
    assert replay["pipeline_run_records"] == []
    assert replay["latest_pipeline_run_record"] is None
    assert "pipeline_run_records" in replay["missing_links"]


def test_replay_handles_malformed_jsonl_lines(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    seeded = _seed_case_trace(storage_dir=storage_dir, tmp_path=tmp_path)
    owner_answers_path = storage_dir / "tenant_demo" / "owner_answers.jsonl"
    with owner_answers_path.open("a", encoding="utf-8") as handle:
        handle.write("{bad json\n")

    replay = replay_case_from_jsonl(
        storage_dir=storage_dir,
        tenant_id="tenant_demo",
        intake_id="intake_demo",
    )

    assert replay["status"] == "REPLAY_READY"
    assert replay["owner_answer_records"][0]["answer_id"] == seeded["owner_answer_record"]["answer_id"]
    assert any("owner_answers.jsonl" in warning and "malformed" in warning.lower() for warning in replay["warnings"])


def test_replay_is_read_only(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    _seed_case_trace(storage_dir=storage_dir, tmp_path=tmp_path)
    before = _snapshot_tree(storage_dir)

    replay = replay_case_from_jsonl(
        storage_dir=storage_dir,
        tenant_id="tenant_demo",
        intake_id="intake_demo",
    )
    after = _snapshot_tree(storage_dir)

    assert replay["status"] == "REPLAY_READY"
    assert after == before


def test_replay_pipeline_runs_sorted_by_started_at(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    seeded = _seed_case_trace(
        storage_dir=storage_dir,
        tmp_path=tmp_path,
        with_owner_answer=False,
        with_evidence_request=False,
        with_pipeline_run=False,
    )
    pipeline_runs_path = storage_dir / "tenant_demo" / "pipeline_runs.jsonl"

    for run_id, started_at in (
        ("run_c", "2026-01-02T10:00:00+00:00"),
        ("run_a", "2026-01-01T10:00:00+00:00"),
        ("run_b", "2026-01-02T10:00:00+00:00"),
    ):
        payload = build_pipeline_run_record(
            tenant_id="tenant_demo",
            intake_id="intake_demo",
            message=f"msg-{run_id}",
            evidence_ids=[seeded["evidence_record"]["evidence_id"]],
            status="COMPLETED",
            output_payload={},
            steps_executed=["seeded"],
        ).model_dump(mode="json")
        payload["run_id"] = run_id
        payload["started_at"] = started_at
        payload["metadata"]["anamnesis_id"] = seeded["anamnesis_record"]["anamnesis_id"]
        payload["metadata"]["investigation_id"] = seeded["investigation_record"]["investigation_id"]
        _append_jsonl(pipeline_runs_path, payload)

    replay = replay_case_from_jsonl(
        storage_dir=storage_dir,
        tenant_id="tenant_demo",
        intake_id="intake_demo",
    )

    assert [record["run_id"] for record in replay["pipeline_run_records"]] == ["run_a", "run_b", "run_c"]
    assert replay["latest_pipeline_run_record"]["run_id"] == "run_c"


def test_replay_tenant_id_traversal_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="invalid path traversal"):
        replay_case_from_jsonl(
            storage_dir=tmp_path / "storage",
            tenant_id="../tenant_demo",
            intake_id="intake_demo",
        )


def test_replay_returns_taxonomic_intake_from_anamnesis(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    _seed_case_trace(
        storage_dir=storage_dir,
        tmp_path=tmp_path,
        business_taxonomy={
            "empresa_tipo": "comercio",
            "industria": "retail",
            "modelo_comercial": "b2c",
            "canales_venta": ["local"],
            "maneja_stock": True,
            "produce": False,
            "presta_servicios": False,
            "areas_criticas": ["margen"],
            "dolores_declarados": ["no se si gano"],
            "documentos_disponibles": ["ventas.xlsx"],
        },
    )

    replay = replay_case_from_jsonl(
        storage_dir=storage_dir,
        tenant_id="tenant_demo",
        intake_id="intake_demo",
    )

    assert replay["taxonomic_intake"]["empresa_tipo"] == "comercio"
    assert replay["taxonomic_intake"]["dolores_declarados"] == ["no se si gano"]
    assert replay["taxonomic_intake"]["documentos_disponibles"] == ["ventas.xlsx"]


def test_replay_does_not_mix_taxonomic_intake_between_tenants(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    _seed_case_trace(
        storage_dir=storage_dir,
        tmp_path=tmp_path,
        tenant_id="tenant_a",
        intake_id="case_1",
        business_taxonomy={"empresa_tipo": "comercio", "dolores_declarados": ["margen"]},
    )
    _seed_case_trace(
        storage_dir=storage_dir,
        tmp_path=tmp_path,
        tenant_id="tenant_b",
        intake_id="case_1",
        business_taxonomy={"empresa_tipo": "servicios", "dolores_declarados": ["tiempo"]},
    )

    replay = replay_case_from_jsonl(
        storage_dir=storage_dir,
        tenant_id="tenant_a",
        intake_id="case_1",
    )

    assert replay["taxonomic_intake"]["empresa_tipo"] == "comercio"
    assert replay["taxonomic_intake"]["dolores_declarados"] == ["margen"]


def test_replay_does_not_mix_taxonomic_intake_between_intakes(tmp_path: Path) -> None:
    storage_dir = tmp_path / "storage"
    _seed_case_trace(
        storage_dir=storage_dir,
        tmp_path=tmp_path,
        tenant_id="tenant_demo",
        intake_id="case_1",
        business_taxonomy={"empresa_tipo": "comercio", "dolores_declarados": ["margen"]},
    )
    _seed_case_trace(
        storage_dir=storage_dir,
        tmp_path=tmp_path,
        tenant_id="tenant_demo",
        intake_id="case_2",
        business_taxonomy={"empresa_tipo": "servicios", "dolores_declarados": ["tiempo"]},
    )

    replay = replay_case_from_jsonl(
        storage_dir=storage_dir,
        tenant_id="tenant_demo",
        intake_id="case_1",
    )

    assert replay["taxonomic_intake"]["empresa_tipo"] == "comercio"
    assert replay["taxonomic_intake"]["dolores_declarados"] == ["margen"]
