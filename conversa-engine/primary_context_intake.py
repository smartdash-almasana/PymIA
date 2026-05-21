from __future__ import annotations

import base64
import json
from pathlib import Path

from pymia.contracts.primary_context_v1 import (
    EvidenceGap,
    PrimaryContextRecord,
    PrimaryContextSignal,
)


def load_primary_context_taxonomy() -> dict:
    repo_root = Path(__file__).resolve().parents[1]
    path = repo_root / "docs" / "catalogo" / "primary_context_taxonomy.v1.json"
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(k in text for k in keywords)


def build_primary_context_record(*, tenant_id: str, message_text: str) -> PrimaryContextRecord:
    text = message_text.strip().lower()
    evidence_mentions: list[str] = []
    if "excel" in text:
        evidence_mentions.append("excel")
    if "pdf" in text:
        evidence_mentions.append("pdf")
    if "factura" in text:
        evidence_mentions.append("facturas")

    expressed_pain: list[PrimaryContextSignal] = []
    suspected_domains: list[PrimaryContextSignal] = []
    initial_hypotheses: list[PrimaryContextSignal] = []

    if _contains_any(text, ["vendo mucho", "no se si gano", "no sé si gano", "margen"]):
        expressed_pain.append(
            PrimaryContextSignal(
                code="margin_uncertainty",
                confidence_level="high",
                evidence=["message_pattern"],
            )
        )
        suspected_domains.append(
            PrimaryContextSignal(
                code="rentabilidad",
                confidence_level="medium",
                evidence=["narrative_signal"],
            )
        )
        initial_hypotheses.append(
            PrimaryContextSignal(
                code="cost_price_misalignment_possible",
                confidence_level="low",
                evidence=["requires_data_validation"],
            )
        )

    linguistic_signals = [
        PrimaryContextSignal(
            code="lenguaje_no_tecnico",
            confidence_level="medium",
            evidence=["free_text"],
        ),
        PrimaryContextSignal(
            code="intuicion_sin_evidencia",
            confidence_level="medium",
            evidence=["free_text"],
        ),
    ]

    operational_signals: list[PrimaryContextSignal] = []
    maturity_hints = [
        PrimaryContextSignal(
            code="reactiva",
            confidence_level="medium",
            evidence=["primary_contact_only"],
        )
    ]

    gap = EvidenceGap(
        required_evidence=["ventas", "costos", "lista_precios"],
        missing_evidence=["ventas", "costos", "lista_precios"],
        optional_evidence=["stock", "cobranzas"],
    )

    return PrimaryContextRecord(
        tenant_id=tenant_id,
        raw_message=message_text,
        expressed_pain=expressed_pain,
        suspected_domains=suspected_domains,
        urgency_level="medium",
        evidence_mentions=evidence_mentions,
        operational_signals=operational_signals,
        linguistic_signals=linguistic_signals,
        maturity_hints=maturity_hints,
        initial_hypotheses=initial_hypotheses,
        requested_outcome="diagnostic_clarity_request",
        evidence_gap=gap,
        state="pending_data",
    )


def persist_primary_context_record(
    *,
    record: PrimaryContextRecord,
    tenant_id: str,
    user_id: str,
    base_path: Path | None = None,
) -> Path:
    if base_path is None:
        base_path = Path(__file__).resolve().parent / ".intake_state"
    session_id = f"{tenant_id}/{user_id}"
    encoded = base64.urlsafe_b64encode(session_id.encode("utf-8")).decode("ascii").rstrip("=")
    out_dir = base_path / "primary_context"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{encoded}.primary_context.json"
    out_path.write_text(record.model_dump_json(indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path

