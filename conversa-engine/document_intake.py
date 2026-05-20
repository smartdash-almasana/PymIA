from __future__ import annotations

import argparse
from pathlib import Path
from uuid import uuid4

from evidence_router import IngestionRoute
from inbound_event import RawInboundEvent
from intake_repository import DocumentIntakeRepository


def _mime_from_extension(file_name: str) -> str:
    ext = Path(file_name).suffix.lower()
    if ext == ".pdf":
        return "application/pdf"
    if ext == ".xlsx":
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if ext == ".xls":
        return "application/vnd.ms-excel"
    if ext == ".csv":
        return "text/csv"
    if ext in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    return "application/octet-stream"


def _session_id(tenant_id: str, user_id: str) -> str:
    return f"{tenant_id}/{user_id}"


def intake_document(
    *,
    tenant_id: str,
    user_id: str,
    file_path: str,
    file_name: str,
    mime_type: str | None,
    expected_schema: str,
    entropy_level: float,
    base_path: Path | None = None,
    fallback_path: Path | None = None,
) -> str:
    actual_mime_type = mime_type or _mime_from_extension(file_name)
    event = RawInboundEvent.file(
        event_id=f"evt-{uuid4()}",
        tenant_id=tenant_id,
        user_id=user_id,
        file_name=file_name,
        mime_type=actual_mime_type,
        expected_schema=expected_schema,
        entropy_level=entropy_level,
    )
    route = event.get_ingestion_route()

    if base_path is None:
        base_path = Path(__file__).resolve().parent / ".intake_state"
    if fallback_path is None:
        fallback_path = Path.home() / ".cache" / "pymia" / "conversa-intake-state"
    session_id = _session_id(tenant_id, user_id)

    chosen_state_path = None
    for state_path in (base_path, fallback_path):
        try:
            repo = DocumentIntakeRepository(base_path=state_path, stale_lock_seconds=60.0)
            state = repo.load(session_id=session_id)
            state.register(event)
            repo.save(session_id=session_id, state=state)
            chosen_state_path = state_path
            break
        except PermissionError:
            continue

    route_label = {
        IngestionRoute.BEM_AI: "BEM_AI",
        IngestionRoute.INTERNAL_FACT: "INTERNAL_FACT",
        IngestionRoute.NARRATIVE: "NARRATIVE",
    }[route]

    if route == IngestionRoute.BEM_AI:
        reason = "archivo no normalizado o con estructura que requiere extracción o curaduría previa"
    elif route == IngestionRoute.INTERNAL_FACT:
        reason = "archivo estructurado compatible con ingesta interna"
    else:
        reason = "evidencia narrativa o relato operacional"

    audit_active = False
    if route == IngestionRoute.INTERNAL_FACT and chosen_state_path is not None:
        from operational_audit_runner import run_excel_operational_audit
        audits_dir = chosen_state_path / "audits"
        try:
            audit_res = run_excel_operational_audit(
                excel_path=file_path,
                tenant_id=tenant_id,
                session_id=session_id,
                output_dir=audits_dir,
            )
            audit_active = audit_res.ok
        except Exception:
            audit_active = False

    lines = [
        f"Archivo registrado: {file_name}",
        "",
        f"Clasificación de ingesta: {route_label}",
        f"Criterio: {reason}.",
        "",
        "Estado clínico-operacional: evidencia incorporada al laboratorio inicial.",
        "",
        "Regla epistemológica: un archivo aislado no confirma patologías ni hallazgos sin contraste contra evidencia suficiente.",
    ]

    if audit_active:
        lines.extend([
            "",
            "[Auditoría Operacional Activa]",
            "Se ha analizado la planilla de forma segura y se generaron los hilos de diagnóstico.",
            "Podés preguntarme sobre:",
            "- Concentración de SKU (PYME_033)",
            "- Caja y Liquidez (LIQ_001)",
            "- Análisis de Margen (REN_001)",
        ])

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Register document evidence for conversa-engine")
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--file-path", required=True)
    parser.add_argument("--file-name", required=True)
    parser.add_argument("--mime-type", default=None)
    parser.add_argument("--expected-schema", default="unknown")
    parser.add_argument("--entropy-level", type=float, default=0.5)
    args = parser.parse_args()

    print(
        intake_document(
            tenant_id=args.tenant_id,
            user_id=args.user_id,
            file_path=args.file_path,
            file_name=args.file_name,
            mime_type=args.mime_type,
            expected_schema=args.expected_schema,
            entropy_level=args.entropy_level,
        )
    )


if __name__ == "__main__":
    main()
