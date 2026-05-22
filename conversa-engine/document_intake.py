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

    # Triage Semántico de Metadatos mediante DocumentContextClassifier v1
    from tools.document_context_classifier import DocumentContextClassifier, DocumentContextInput
    
    payload = DocumentContextInput(
        file_name=file_name,
        mime_type=actual_mime_type,
        extension=Path(file_name).suffix.lower() if file_name else None,
        entropy_level=entropy_level,
        source_type="file_upload"
    )
    classification = DocumentContextClassifier.classify(payload)
    
    is_blocked = False
    if route == IngestionRoute.INTERNAL_FACT:
        # Classifier can degrade to BEM_AI, but NEVER promote BEM_AI to INTERNAL_FACT
        if classification.decision_code == "ADMINISTRATIVE_BYPASS":
            route = IngestionRoute.BEM_AI
            is_blocked = True
        elif classification.confidence == "low" and classification.decision_code != "NO_KEYWORDS_DETECTED":
            route = IngestionRoute.BEM_AI
            is_blocked = True

    # Persistir metadata liviana del clasificador en el objeto event
    object.__setattr__(event, "document_context", classification.document_context)
    object.__setattr__(event, "classification_confidence", classification.confidence)
    object.__setattr__(event, "evidence_candidate_type", classification.evidence_candidate_type)
    object.__setattr__(event, "classification_reasons", classification.reasons)
    object.__setattr__(event, "classification_decision_code", classification.decision_code)
    object.__setattr__(event, "classification_clarification_type", classification.clarification_type)

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
            
            # Record initial state: RECEIVED
            state.last_file_name = file_name
            state.last_lifecycle_state = "RECEIVED"
            
            repo.save(session_id=session_id, state=state)
            chosen_state_path = state_path
            break
        except PermissionError:
            continue

    # Record DOWNLOADED state
    if chosen_state_path is not None:
        try:
            repo = DocumentIntakeRepository(base_path=chosen_state_path, stale_lock_seconds=60.0)
            state = repo.load(session_id=session_id)
            state.last_lifecycle_state = "DOWNLOADED"
            repo.save(session_id=session_id, state=state)
        except Exception:
            pass

    route_label = {
        IngestionRoute.BEM_AI: "BEM_AI",
        IngestionRoute.INTERNAL_FACT: "INTERNAL_FACT",
        IngestionRoute.NARRATIVE: "NARRATIVE",
    }[route]

    if route != IngestionRoute.INTERNAL_FACT:
        return "Recibí el archivo, pero todavía no fue procesado."

    reason = "archivo estructurado compatible con ingesta interna"

    # Record PARSE_ATTEMPTED if we are running the parser
    if route == IngestionRoute.INTERNAL_FACT and chosen_state_path is not None:
        try:
            repo = DocumentIntakeRepository(base_path=chosen_state_path, stale_lock_seconds=60.0)
            state = repo.load(session_id=session_id)
            state.last_lifecycle_state = "PARSE_ATTEMPTED"
            repo.save(session_id=session_id, state=state)
        except Exception:
            pass

    audit_active = False
    kernel_msg = None
    if route == IngestionRoute.INTERNAL_FACT and chosen_state_path is not None:
        from operational_audit_runner import run_excel_operational_audit
        import json
        audits_dir = chosen_state_path / "audits"
        try:
            audit_res = run_excel_operational_audit(
                excel_path=file_path,
                tenant_id=tenant_id,
                session_id=session_id,
                output_dir=audits_dir,
            )
            audit_active = audit_res.ok

            # Load status from evidence.json and sync back to intake state
            if audit_res.evidence_path.exists():
                with open(audit_res.evidence_path, "r", encoding="utf-8") as f:
                    status_data = json.load(f)
                
                repo = DocumentIntakeRepository(base_path=chosen_state_path, stale_lock_seconds=60.0)
                state = repo.load(session_id=session_id)
                state.last_file_name = file_name
                state.last_lifecycle_state = status_data.get("lifecycle_state")
                state.last_parse_status = status_data.get("parse_status")
                state.last_parse_error = status_data.get("parse_error")
                state.last_root_cause = status_data.get("root_cause")
                state.last_user_message = status_data.get("user_message")
                repo.save(session_id=session_id, state=state)

            # If not active (failed), read clinical port message
            if not audit_active and audit_res.kernel_path.exists():
                with open(audit_res.kernel_path, "r", encoding="utf-8") as f:
                    kernel_data = json.load(f)
                kernel_msg = kernel_data.get("kernel", {}).get("message")
        except Exception:
            audit_active = False

    # Block textual fallback if attachments parsing failed
    if route == IngestionRoute.INTERNAL_FACT and not audit_active:
        if kernel_msg:
            return kernel_msg
        return f"Error al procesar el archivo '{file_name}'."

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

    if is_blocked and classification.required_followup:
        lines.extend([
            "",
            "Aclaración sugerida:",
            classification.required_followup,
        ])

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
