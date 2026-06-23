from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pymia.smartpyme.service_1_operator_delivery_package_v1 import (
    build_service_1_operator_delivery_package_v1,
)
from pymia.smartpyme.service_1_operator_harness_v1 import (
    build_service_1_operator_harness_sample_case_v1,
    run_service_1_operator_harness_v1,
)


def _build_manifest(tmp_path: Path):
    harness_root = tmp_path / "harness"
    package_root = tmp_path / "packages"
    harness_root.mkdir()
    package_root.mkdir()

    harness_run = run_service_1_operator_harness_v1(
        case=build_service_1_operator_harness_sample_case_v1(),
        output_root=harness_root,
    )
    package = build_service_1_operator_delivery_package_v1(
        harness_run=harness_run,
        package_root=package_root,
    )
    manifest = json.loads(Path(package["manifest_path"]).read_text(encoding="utf-8"))
    return package, manifest


def test_manifest_audit_validates_integrity_and_visible_limits(tmp_path: Path) -> None:
    package, manifest = _build_manifest(tmp_path)

    assert manifest["schema_version"] == "1.0"
    assert manifest["service_name"] == "SERVICE_1"
    assert manifest["runtime_authorized"] is False
    assert manifest["artifact_count"] == 8
    assert len(manifest["artifacts"]) == 8
    assert "Entrega preliminar basada en datos declarados." in manifest["limitations"]
    assert "No confirma stock fisico real." in manifest["limitations"]

    package_dir = Path(package["package_dir"])
    assert Path(package["readme_path"]).exists()
    assert package_dir.exists()

    for artifact in manifest["artifacts"]:
        package_path = Path(artifact["package_path"])
        source_path = Path(artifact["source_path"])
        assert package_path.exists()
        assert source_path.exists()
        payload = package_path.read_bytes()
        assert hashlib.sha256(payload).hexdigest() == artifact["sha256"]
        assert len(payload) == artifact["bytes"]


def test_manifest_audit_includes_readme_summary_report_and_xlsx_inventory(tmp_path: Path) -> None:
    _, manifest = _build_manifest(tmp_path)

    filenames = [artifact["filename"] for artifact in manifest["artifacts"]]
    assert filenames == [
        "first_aid_001_precio_margen_basico.xlsx",
        "first_aid_002_caja_diaria_triage.xlsx",
        "first_aid_003_stock_alertas_basicas.xlsx",
        "first_aid_004_gastos_triage.xlsx",
        "first_aid_005_proveedores_precio_variacion_triage.xlsx",
        "summary.txt",
        "operator_report.txt",
        "README_ENTREGA.md",
    ]
