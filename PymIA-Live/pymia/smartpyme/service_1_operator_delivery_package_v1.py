from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Final, TypedDict

from pymia.smartpyme.service_1_operator_harness_v1 import Service1OperatorHarnessRunV1

PACKAGE_SCHEMA_VERSION: Final[str] = "1.0"
SERVICE_NAME: Final[str] = "SERVICE_1"


class Service1OperatorDeliveryPackageFileV1(TypedDict):
    filename: str
    source_path: str
    package_path: str
    sha256: str
    bytes: int


class Service1OperatorDeliveryPackageV1(TypedDict):
    schema_version: str
    service_name: str
    case_id: str
    case_name: str
    package_dir: str
    readme_path: str
    manifest_path: str
    files: list[Service1OperatorDeliveryPackageFileV1]
    file_count: int
    runtime_authorized: bool
    notes: list[str]


def build_service_1_operator_delivery_package_v1(
    *,
    harness_run: Service1OperatorHarnessRunV1,
    package_root: str | Path,
) -> Service1OperatorDeliveryPackageV1:
    package_root_path = Path(package_root)
    if not package_root_path.exists():
        raise FileNotFoundError(f"Package root does not exist: {package_root_path}")

    case_id = str(harness_run["case_id"])
    if not case_id:
        raise ValueError("SERVICE_1_OPERATOR_DELIVERY_PACKAGE_V1 requires case_id.")
    if harness_run["runtime_authorized"]:
        raise ValueError("SERVICE_1_OPERATOR_DELIVERY_PACKAGE_V1 rejects runtime_authorized=True.")

    package_dir = package_root_path / f"{case_id}_delivery_package"
    package_dir.mkdir(exist_ok=True)

    source_paths = _collect_source_paths(harness_run)
    copied_files: list[Service1OperatorDeliveryPackageFileV1] = []
    for source_path in source_paths:
        if not source_path.exists():
            raise FileNotFoundError(f"Delivery artifact does not exist: {source_path}")
        target_path = package_dir / source_path.name
        shutil.copy2(source_path, target_path)
        copied_files.append(_build_file_record(source_path=source_path, package_path=target_path))

    readme_path = package_dir / "README_ENTREGA.md"
    readme_path.write_text(
        _build_readme(harness_run=harness_run, files=copied_files),
        encoding="utf-8",
    )

    manifest_path = package_dir / "manifest.json"
    manifest_payload = _build_manifest_payload(
        harness_run=harness_run,
        package_dir=package_dir,
        files=copied_files,
        readme_path=readme_path,
    )
    manifest_path.write_text(
        json.dumps(manifest_payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    final_files = copied_files + [
        _build_file_record(source_path=readme_path, package_path=readme_path),
        _build_file_record(source_path=manifest_path, package_path=manifest_path),
    ]

    return {
        "schema_version": PACKAGE_SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "case_id": case_id,
        "case_name": harness_run["case_name"],
        "package_dir": str(package_dir.resolve()),
        "readme_path": str(readme_path.resolve()),
        "manifest_path": str(manifest_path.resolve()),
        "files": final_files,
        "file_count": len(final_files),
        "runtime_authorized": False,
        "notes": [
            "Operator delivery package created from audited harness output.",
            "Package includes XLSX files, summary, operator report, README, and manifest.",
        ],
    }


def _collect_source_paths(harness_run: Service1OperatorHarnessRunV1) -> list[Path]:
    paths = [Path(path) for path in harness_run["generated_files"]]
    paths.append(Path(harness_run["summary_path"]))
    paths.append(Path(harness_run["operator_report_path"]))
    return paths


def _build_file_record(*, source_path: Path, package_path: Path) -> Service1OperatorDeliveryPackageFileV1:
    payload = package_path.read_bytes()
    return {
        "filename": package_path.name,
        "source_path": str(source_path.resolve()),
        "package_path": str(package_path.resolve()),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
    }


def _build_readme(
    *,
    harness_run: Service1OperatorHarnessRunV1,
    files: list[Service1OperatorDeliveryPackageFileV1],
) -> str:
    lines: list[str] = [
        "# Entrega preliminar — Servicio 1 First Aid",
        "",
        f"Caso: {harness_run['case_name']}",
        f"Case ID: {harness_run['case_id']}",
        "",
        "## Archivos incluidos",
    ]
    for file_record in files:
        lines.append(f"- {file_record['filename']}")

    lines.extend(
        [
            "",
            "## Cómo leer esta entrega",
            "",
            "1. Revisar `summary.txt` para una lectura rápida.",
            "2. Revisar `operator_report.txt` para control interno del operador.",
            "3. Abrir los XLSX para ver datos usados, resultados, limitaciones y claims prohibidos.",
            "4. Usar `manifest.json` para verificar inventario e integridad de archivos.",
            "",
            "## Alcance",
            "",
            "Entrega preliminar basada en datos declarados.",
            "No es un diagnostico integral de la empresa.",
            "No confirma rentabilidad real.",
            "No confirma saldo bancario real.",
            "No confirma stock fisico real.",
            "No confirma conciliacion cerrada.",
        ]
    )
    return "\n".join(lines)


def _build_manifest_payload(
    *,
    harness_run: Service1OperatorHarnessRunV1,
    package_dir: Path,
    files: list[Service1OperatorDeliveryPackageFileV1],
    readme_path: Path,
) -> dict[str, object]:
    return {
        "schema_version": PACKAGE_SCHEMA_VERSION,
        "service_name": SERVICE_NAME,
        "case_id": harness_run["case_id"],
        "case_name": harness_run["case_name"],
        "package_dir": str(package_dir.resolve()),
        "readme": readme_path.name,
        "artifact_count": len(files),
        "artifacts": files,
        "runtime_authorized": False,
        "limitations": [
            "Entrega preliminar basada en datos declarados.",
            "No es un diagnostico integral de la empresa.",
            "No confirma rentabilidad real.",
            "No confirma saldo bancario real.",
            "No confirma stock fisico real.",
            "No confirma conciliacion cerrada.",
        ],
    }
